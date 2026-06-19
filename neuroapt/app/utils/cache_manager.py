"""
Cache Manager for AI Career Analysis
Handles caching, retrieval, and invalidation of AI-generated career analysis results
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Use centralized logging configuration
from neuroapt.app.utils.logging_config import get_ai_logger

logger = get_ai_logger(__name__)


def get_cached_analysis(test_result) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached AI analysis from TestResult.ai_analysis field.
    
    Args:
        test_result: TestResult object with ai_analysis field
        
    Returns:
        Parsed JSON analysis data or None if cache miss/invalid
        
    Behavior:
        - Returns None if ai_analysis field is empty/None
        - Returns None if JSON deserialization fails (logs error)
        - Returns parsed dictionary if valid cache exists
    """
    if not test_result or not test_result.ai_analysis:
        logger.debug(f"Cache miss: No cached analysis for test result {getattr(test_result, 'id', 'unknown')}")
        return None
    
    try:
        # Use existing TestResult property accessor for JSON parsing
        cached_data = test_result.ai_analysis_dict
        
        if cached_data is None:
            logger.warning(f"Cache deserialization failed for test result {test_result.id}")
            return None
        
        logger.info(f"Cache hit: Retrieved analysis for test result {test_result.id}")
        return cached_data
        
    except Exception as e:
        logger.error(f"Error retrieving cached analysis for test result {test_result.id}: {str(e)}")
        return None


def cache_analysis(test_result, analysis: Dict[str, Any], db_session) -> bool:
    """
    Store AI analysis in database with metadata.
    
    Args:
        test_result: TestResult object to update
        analysis: AI analysis dictionary to cache
        db_session: SQLAlchemy database session for committing changes
        
    Returns:
        True if caching succeeded, False otherwise
        
    Storage Format:
        {
            'generated_at': '<ISO timestamp>',
            'version': '1.0',
            'data': <actual analysis dictionary>
        }
    """
    if not test_result or analysis is None:
        logger.error("Cache storage failed: test_result or analysis is None")
        return False
    
    try:
        # Wrap analysis with metadata
        cache_payload = {
            'generated_at': datetime.utcnow().isoformat(),
            'version': '1.0',
            'data': analysis
        }
        
        # Use existing TestResult property setter for JSON serialization
        test_result.ai_analysis_dict = cache_payload
        
        # Commit to database
        db_session.commit()
        
        logger.info(f"Successfully cached analysis for test result {test_result.id}")
        return True
        
    except Exception as e:
        logger.error(f"Error caching analysis for test result {test_result.id}: {str(e)}")
        # Rollback on failure
        try:
            db_session.rollback()
        except Exception as rollback_error:
            logger.error(f"Rollback failed: {str(rollback_error)}")
        return False


def invalidate_cache(test_result, db_session) -> bool:
    """
    Clear cached AI analysis to force regeneration.
    Used for admin-triggered analysis regeneration.
    
    Args:
        test_result: TestResult object to clear cache for
        db_session: SQLAlchemy database session for committing changes
        
    Returns:
        True if invalidation succeeded, False otherwise
    """
    if not test_result:
        logger.error("Cache invalidation failed: test_result is None")
        return False
    
    try:
        # Clear the ai_analysis field
        test_result.ai_analysis = None
        
        # Commit to database
        db_session.commit()
        
        logger.info(f"Successfully invalidated cache for test result {test_result.id}")
        return True
        
    except Exception as e:
        logger.error(f"Error invalidating cache for test result {test_result.id}: {str(e)}")
        # Rollback on failure
        try:
            db_session.rollback()
        except Exception as rollback_error:
            logger.error(f"Rollback failed: {str(rollback_error)}")
        return False
