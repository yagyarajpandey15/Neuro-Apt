"""
Career Analysis Orchestrator Module

Coordinates all AI career analysis components: pattern analysis, profile building,
confidence scoring, caching, AI generation, validation, and fallback.
"""

import json
from neuroapt.app.utils.pattern_analyzer import analyze_answer_patterns
from neuroapt.app.utils.profile_builder import build_student_profile, detect_interest_intersections
from neuroapt.app.utils.confidence_scorer import calculate_confidence_score
from neuroapt.app.utils.cache_manager import get_cached_analysis, cache_analysis
from neuroapt.app.utils.openai_api import generate_ai_career_analysis
from neuroapt.app.utils.ai_response_validator import validate_and_format_ai_response
from neuroapt.app.utils.statistical_fallback import get_statistical_recommendations
from neuroapt.app.utils.ai_error_handler import with_retry_and_fallback, log_ai_error


def analyze_student_profile(test_result, user_id=None, force_regenerate=False):
    """
    Orchestrate complete AI career analysis workflow.
    
    Workflow:
    1. Validate input
    2. Pattern analysis and contradiction detection
    3. Confidence scoring
    4. Profile building and interest intersection detection
    5. Cache check (skip if force_regenerate=True)
    6. AI generation with retry/fallback logic
    7. Store results in database
    8. Return comprehensive analysis result
    
    Parameters:
        test_result: TestResult object with assessment data
        user_id: User ID for logging (optional)
        force_regenerate (bool): Skip cache and force new AI generation
        
    Returns:
        dict: {
            "result": dict with career analysis,
            "source": "cache"|"ai"|"fallback",
            "fallback_triggered": bool,
            "confidence_level": str,
            "confidence_score": int,
            "pattern_flag": str,
            "interest_intersection": str,
            "user_message": str
        }
    """
    if test_result is None:
        return {"error": "Invalid test result", "source": "error"}
    
    # Import db inside function to avoid circular imports
    try:
        from neuroapt.app import db
    except ImportError:
        db = None
    
    # STEP 1: Pattern Analysis
    pattern_data = analyze_answer_patterns(test_result)
    test_result.answer_pattern_flag = pattern_data.get("classification", "UNKNOWN")
    test_result.contradictions_detected = json.dumps(pattern_data.get("contradictions", []))
    
    # STEP 2: Confidence Scoring
    confidence_result = calculate_confidence_score(pattern_data)
    test_result.confidence_level = confidence_result.get("level", "MODERATE")
    
    # STEP 3: Profile Building
    student_profile = build_student_profile(test_result)
    intersection = detect_interest_intersections(student_profile)
    test_result.interest_intersection = intersection
    
    # STEP 4: Cache Check (skip if force_regenerate)
    if not force_regenerate:
        cached = get_cached_analysis(test_result)
        if cached is not None:
            return {
                "result": cached,
                "source": "cache",
                "fallback_triggered": False,
                "confidence_level": confidence_result.get("level"),
                "confidence_score": confidence_result.get("score", 0),
                "pattern_flag": pattern_data.get("classification"),
                "interest_intersection": intersection,
                "user_message": "AI analysis complete"
            }
    
    # STEP 5: AI Generation with error handling
    def ai_call():
        raw = generate_ai_career_analysis(student_profile)
        validated = validate_and_format_ai_response(raw)
        return validated if validated else raw
    
    def fallback_call():
        return {
            "careers": get_statistical_recommendations(test_result),
            "source": "statistical",
            "confidence_analysis": {"level": "LOW"}
        }
    
    outcome = with_retry_and_fallback(
        ai_call,
        fallback_call,
        max_retries=2,
        base_delay=1.0,
        user_id=user_id,
        test_id=getattr(test_result, "id", None)
    )
    
    # STEP 6: Store Results (only if AI succeeded)
    if not outcome.get("fallback_triggered"):
        cache_analysis(test_result, outcome.get("result", {}))
    
    # STEP 7: Commit to database
    if db:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            log_ai_error(
                "orchestrator",
                "db_commit",
                "PERMANENT",
                user_id,
                getattr(test_result, "id", None),
                str(e)
            )
    
    # STEP 8: Return comprehensive result
    user_message = "AI analysis complete" if not outcome.get("fallback_triggered") else \
                   "Using statistical recommendations — AI temporarily unavailable."
    
    return {
        "result": outcome.get("result", {}),
        "source": outcome.get("source", "unknown"),
        "fallback_triggered": outcome.get("fallback_triggered", False),
        "confidence_level": confidence_result.get("level"),
        "confidence_score": confidence_result.get("score", 0),
        "pattern_flag": pattern_data.get("classification"),
        "interest_intersection": intersection,
        "user_message": user_message
    }
