"""
Unit tests for cache_manager module
Tests cache retrieval, storage, and invalidation functionality
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from neuroapt.app.utils.cache_manager import (
    get_cached_analysis,
    cache_analysis,
    invalidate_cache
)


class TestGetCachedAnalysis:
    """Test cache retrieval functionality"""
    
    def test_cache_miss_empty_field(self):
        """Test cache miss when ai_analysis field is empty"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis = None
        
        result = get_cached_analysis(test_result)
        
        assert result is None
    
    def test_cache_miss_no_test_result(self):
        """Test cache miss when test_result is None"""
        result = get_cached_analysis(None)
        
        assert result is None
    
    def test_cache_hit_valid_json(self):
        """Test successful cache retrieval with valid JSON"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis = '{"top_careers": [], "confidence": 85}'
        test_result.ai_analysis_dict = {"top_careers": [], "confidence": 85}
        
        result = get_cached_analysis(test_result)
        
        assert result is not None
        assert result == {"top_careers": [], "confidence": 85}
    
    def test_cache_hit_with_metadata(self):
        """Test cache retrieval with metadata wrapper"""
        cached_data = {
            'generated_at': '2024-01-15T10:30:00',
            'version': '1.0',
            'data': {'top_careers': ['Engineer'], 'confidence': 90}
        }
        
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis = json.dumps(cached_data)
        test_result.ai_analysis_dict = cached_data
        
        result = get_cached_analysis(test_result)
        
        assert result is not None
        assert 'generated_at' in result
        assert 'version' in result
        assert 'data' in result
    
    def test_deserialization_error_handling(self):
        """Test handling of corrupted cache JSON"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis = '{invalid json'
        test_result.ai_analysis_dict = None  # Property returns None on parse error
        
        result = get_cached_analysis(test_result)
        
        assert result is None
    
    def test_exception_handling(self):
        """Test graceful handling of unexpected exceptions"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis = '{"valid": "json"}'
        # Simulate exception when accessing property
        type(test_result).ai_analysis_dict = property(
            lambda self: (_ for _ in ()).throw(RuntimeError("Unexpected error"))
        )
        
        result = get_cached_analysis(test_result)
        
        assert result is None


class TestCacheAnalysis:
    """Test cache storage functionality"""
    
    def test_successful_cache_storage(self):
        """Test successful storage of analysis data"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis_dict = None
        
        db_session = Mock()
        
        analysis = {
            'top_careers': ['Software Engineer', 'Data Scientist'],
            'confidence': 85
        }
        
        result = cache_analysis(test_result, analysis, db_session)
        
        assert result is True
        db_session.commit.assert_called_once()
        # Verify metadata wrapper was applied
        stored_data = test_result.ai_analysis_dict
        assert stored_data is not None
        assert 'generated_at' in stored_data
        assert 'version' in stored_data
        assert stored_data['version'] == '1.0'
        assert 'data' in stored_data
        assert stored_data['data'] == analysis
    
    def test_metadata_timestamp_format(self):
        """Test that generated_at timestamp is in ISO format"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis_dict = None
        
        db_session = Mock()
        analysis = {'top_careers': []}
        
        with patch('neuroapt.app.utils.cache_manager.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 15, 10, 30, 45)
            cache_analysis(test_result, analysis, db_session)
        
        stored_data = test_result.ai_analysis_dict
        assert stored_data['generated_at'] == '2024-01-15T10:30:45'
    
    def test_cache_storage_none_test_result(self):
        """Test cache storage fails gracefully when test_result is None"""
        db_session = Mock()
        analysis = {'top_careers': []}
        
        result = cache_analysis(None, analysis, db_session)
        
        assert result is False
        db_session.commit.assert_not_called()
    
    def test_cache_storage_none_analysis(self):
        """Test cache storage fails gracefully when analysis is None"""
        test_result = Mock()
        test_result.id = 1
        db_session = Mock()
        
        result = cache_analysis(test_result, None, db_session)
        
        assert result is False
        db_session.commit.assert_not_called()
    
    def test_database_commit_failure(self):
        """Test rollback on database commit failure"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis_dict = None
        
        db_session = Mock()
        db_session.commit.side_effect = Exception("Database error")
        
        analysis = {'top_careers': []}
        
        result = cache_analysis(test_result, analysis, db_session)
        
        assert result is False
        db_session.rollback.assert_called_once()
    
    def test_rollback_failure_handling(self):
        """Test graceful handling when rollback itself fails"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis_dict = None
        
        db_session = Mock()
        db_session.commit.side_effect = Exception("Database error")
        db_session.rollback.side_effect = Exception("Rollback error")
        
        analysis = {'top_careers': []}
        
        # Should not raise exception despite rollback failure
        result = cache_analysis(test_result, analysis, db_session)
        
        assert result is False


class TestInvalidateCache:
    """Test cache invalidation functionality"""
    
    def test_successful_invalidation(self):
        """Test successful cache invalidation"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis = '{"cached": "data"}'
        
        db_session = Mock()
        
        result = invalidate_cache(test_result, db_session)
        
        assert result is True
        assert test_result.ai_analysis is None
        db_session.commit.assert_called_once()
    
    def test_invalidation_none_test_result(self):
        """Test invalidation fails gracefully when test_result is None"""
        db_session = Mock()
        
        result = invalidate_cache(None, db_session)
        
        assert result is False
        db_session.commit.assert_not_called()
    
    def test_invalidation_database_failure(self):
        """Test rollback on database commit failure during invalidation"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis = '{"cached": "data"}'
        
        db_session = Mock()
        db_session.commit.side_effect = Exception("Database error")
        
        result = invalidate_cache(test_result, db_session)
        
        assert result is False
        db_session.rollback.assert_called_once()
    
    def test_invalidation_already_empty(self):
        """Test invalidation succeeds even when cache already empty"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis = None
        
        db_session = Mock()
        
        result = invalidate_cache(test_result, db_session)
        
        assert result is True
        db_session.commit.assert_called_once()
    
    def test_invalidation_rollback_failure(self):
        """Test graceful handling when rollback fails during invalidation"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis = '{"cached": "data"}'
        
        db_session = Mock()
        db_session.commit.side_effect = Exception("Database error")
        db_session.rollback.side_effect = Exception("Rollback error")
        
        # Should not raise exception despite rollback failure
        result = invalidate_cache(test_result, db_session)
        
        assert result is False


class TestCacheErrorHandling:
    """Test error handling across cache operations"""
    
    def test_cache_retrieval_with_empty_string(self):
        """Test cache retrieval handles empty string"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis = ''
        
        result = get_cached_analysis(test_result)
        
        assert result is None
    
    def test_cache_storage_with_empty_dict(self):
        """Test cache storage handles empty analysis dictionary"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis_dict = None
        
        db_session = Mock()
        analysis = {}
        
        result = cache_analysis(test_result, analysis, db_session)
        
        # Empty dict is still valid data
        assert result is True
        db_session.commit.assert_called_once()
    
    def test_cache_operations_with_complex_analysis(self):
        """Test cache operations with complex nested analysis structure"""
        test_result = Mock()
        test_result.id = 1
        test_result.ai_analysis_dict = None
        
        db_session = Mock()
        
        complex_analysis = {
            'top_careers': [
                {
                    'title': 'Software Engineer',
                    'match_percentage': 92,
                    'ability_breakdown': {
                        'cognitive_match': 95,
                        'personality_match': 88
                    },
                    'roadmap': {
                        'immediate_1_month': ['Learn Python', 'Build portfolio'],
                        'short_term_3_6_months': ['Complete course', 'Internship']
                    }
                }
            ],
            'confidence': {
                'score': 85,
                'level': 'HIGH'
            }
        }
        
        result = cache_analysis(test_result, complex_analysis, db_session)
        
        assert result is True
        stored_data = test_result.ai_analysis_dict
        assert stored_data['data'] == complex_analysis
