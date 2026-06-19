import json
import pytest
from unittest.mock import MagicMock, patch
from hypothesis import given, settings
from hypothesis import strategies as st
from neuroapt.app.utils.orchestrator import analyze_student_profile

def make_mock_result():
    m = MagicMock()
    m.id = 1
    m.ai_analysis = None
    m.answer_pattern_flag = None
    m.contradictions_detected = None
    m.confidence_level = None
    m.interest_intersection = None
    return m

PATTERN_CLASSES = ["DECISIVE", "AMBIVALENT", "RANDOM", "CONSISTENT"]

@given(
    pattern=st.sampled_from(PATTERN_CLASSES),
    contradictions=st.lists(st.text(min_size=1, max_size=20), max_size=5)
)
@settings(max_examples=50)
def test_analysis_result_persistence(pattern, contradictions):
    mock_result = make_mock_result()
    
    with patch("neuroapt.app.utils.orchestrator.analyze_answer_patterns", return_value={
        "classification": pattern,
        "contradictions": contradictions,
        "consistency_score": 75,
        "contradiction_rate": 0.1,
        "completion_rate": 1.0
    }), \
    patch("neuroapt.app.utils.orchestrator.calculate_confidence_score", return_value={"level": "HIGH", "score": 85}), \
    patch("neuroapt.app.utils.orchestrator.build_student_profile", return_value={}), \
    patch("neuroapt.app.utils.orchestrator.detect_interest_intersections", return_value="STEM+Creative"), \
    patch("neuroapt.app.utils.orchestrator.get_cached_analysis", return_value=None), \
    patch("neuroapt.app.utils.orchestrator.generate_ai_career_analysis", return_value={"top_careers": []}), \
    patch("neuroapt.app.utils.orchestrator.validate_and_format_ai_response", return_value={"top_careers": []}), \
    patch("neuroapt.app.utils.orchestrator.cache_analysis"), \
    patch("neuroapt.app.utils.orchestrator.db", MagicMock()):
        
        analyze_student_profile(mock_result)
        
        assert mock_result.answer_pattern_flag == pattern
        assert json.loads(mock_result.contradictions_detected) == contradictions
        assert mock_result.confidence_level in ["HIGH", "MODERATE", "LOW", "UNRELIABLE"]

def test_cache_hit_skips_ai():
    mock_result = make_mock_result()
    cached_data = {"top_careers": [{"title": "Engineer"}]}
    
    with patch("neuroapt.app.utils.orchestrator.analyze_answer_patterns", return_value={
        "classification": "DECISIVE",
        "contradictions": [],
        "consistency_score": 80,
        "contradiction_rate": 0.0,
        "completion_rate": 1.0
    }), \
    patch("neuroapt.app.utils.orchestrator.calculate_confidence_score", return_value={"level": "HIGH", "score": 85}), \
    patch("neuroapt.app.utils.orchestrator.build_student_profile", return_value={}), \
    patch("neuroapt.app.utils.orchestrator.detect_interest_intersections", return_value=""), \
    patch("neuroapt.app.utils.orchestrator.get_cached_analysis", return_value=cached_data), \
    patch("neuroapt.app.utils.orchestrator.generate_ai_career_analysis") as mock_ai:
        
        result = analyze_student_profile(mock_result)
        
        mock_ai.assert_not_called()
        assert result["source"] == "cache"

def test_cache_miss_triggers_ai():
    mock_result = make_mock_result()
    
    with patch("neuroapt.app.utils.orchestrator.analyze_answer_patterns", return_value={
        "classification": "DECISIVE",
        "contradictions": [],
        "consistency_score": 80,
        "contradiction_rate": 0.0,
        "completion_rate": 1.0
    }), \
    patch("neuroapt.app.utils.orchestrator.calculate_confidence_score", return_value={"level": "HIGH", "score": 85}), \
    patch("neuroapt.app.utils.orchestrator.build_student_profile", return_value={}), \
    patch("neuroapt.app.utils.orchestrator.detect_interest_intersections", return_value=""), \
    patch("neuroapt.app.utils.orchestrator.get_cached_analysis", return_value=None), \
    patch("neuroapt.app.utils.orchestrator.generate_ai_career_analysis", return_value={"top_careers": []}) as mock_ai, \
    patch("neuroapt.app.utils.orchestrator.validate_and_format_ai_response", return_value={"top_careers": []}), \
    patch("neuroapt.app.utils.orchestrator.cache_analysis"), \
    patch("neuroapt.app.utils.orchestrator.db", MagicMock()):
        
        result = analyze_student_profile(mock_result)
        
        mock_ai.assert_called_once()
        assert result["source"] == "ai"

def test_ai_failure_triggers_fallback():
    mock_result = make_mock_result()
    
    try:
        import openai
        exc = openai.APITimeoutError("timeout")
    except (ImportError, Exception):
        exc = Exception("timeout")
    
    with patch("neuroapt.app.utils.orchestrator.analyze_answer_patterns", return_value={
        "classification": "DECISIVE",
        "contradictions": [],
        "consistency_score": 80,
        "contradiction_rate": 0.0,
        "completion_rate": 1.0
    }), \
    patch("neuroapt.app.utils.orchestrator.calculate_confidence_score", return_value={"level": "HIGH", "score": 85}), \
    patch("neuroapt.app.utils.orchestrator.build_student_profile", return_value={}), \
    patch("neuroapt.app.utils.orchestrator.detect_interest_intersections", return_value=""), \
    patch("neuroapt.app.utils.orchestrator.get_cached_analysis", return_value=None), \
    patch("neuroapt.app.utils.orchestrator.generate_ai_career_analysis", side_effect=exc), \
    patch("neuroapt.app.utils.orchestrator.get_statistical_recommendations", return_value=[{"title": "Fallback Career"}]), \
    patch("neuroapt.app.utils.orchestrator.time.sleep"), \
    patch("neuroapt.app.utils.orchestrator.db", MagicMock()):
        
        result = analyze_student_profile(mock_result, force_regenerate=True)
        
        assert result["fallback_triggered"] is True

def test_force_regenerate_bypasses_cache():
    mock_result = make_mock_result()
    
    with patch("neuroapt.app.utils.orchestrator.analyze_answer_patterns", return_value={
        "classification": "DECISIVE",
        "contradictions": [],
        "consistency_score": 80,
        "contradiction_rate": 0.0,
        "completion_rate": 1.0
    }), \
    patch("neuroapt.app.utils.orchestrator.calculate_confidence_score", return_value={"level": "HIGH", "score": 85}), \
    patch("neuroapt.app.utils.orchestrator.build_student_profile", return_value={}), \
    patch("neuroapt.app.utils.orchestrator.detect_interest_intersections", return_value=""), \
    patch("neuroapt.app.utils.orchestrator.get_cached_analysis", return_value={"top_careers": []}), \
    patch("neuroapt.app.utils.orchestrator.generate_ai_career_analysis", return_value={"top_careers": []}) as mock_ai, \
    patch("neuroapt.app.utils.orchestrator.validate_and_format_ai_response", return_value={"top_careers": []}), \
    patch("neuroapt.app.utils.orchestrator.cache_analysis"), \
    patch("neuroapt.app.utils.orchestrator.db", MagicMock()):
        
        analyze_student_profile(mock_result, force_regenerate=True)
        
        mock_ai.assert_called_once()
