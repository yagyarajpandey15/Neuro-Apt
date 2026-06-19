"""
AI Error Handler Module

Provides error classification, logging, and retry logic with fallback for AI operations.
"""

import logging
import time
import os
import json
from datetime import datetime

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("neuroapt.ai")
logger.setLevel(logging.ERROR)

if not logger.handlers:
    fh = logging.FileHandler("logs/openai_errors.log")
    fh.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)s | component=%(component)s | operation=%(operation)s | '
        'error_type=%(error_type)s | user_id=%(user_id)s | test_id=%(test_id)s | details=%(details)s'
    ))
    logger.addHandler(fh)


def log_ai_error(component, operation, error_type, user_id, test_id, details):
    """
    Log AI error with structured format.
    
    Parameters:
        component (str): Component where error occurred
        operation (str): Operation being performed
        error_type (str): TRANSIENT, PERMANENT, or MALFORMED
        user_id: User ID or None
        test_id: Test result ID or None
        details (str): Error details
    """
    logger.error("AI Error", extra={
        "component": component,
        "operation": operation,
        "error_type": error_type,
        "user_id": user_id,
        "test_id": test_id,
        "details": str(details)
    })


def classify_openai_error(exception):
    """
    Classify OpenAI API errors into categories with retry recommendations.
    
    Parameters:
        exception: The exception to classify
        
    Returns:
        dict: {"error_type": str, "should_retry": bool, "user_message": str}
    """
    try:
        import openai
        if isinstance(exception, (openai.APITimeoutError, openai.RateLimitError, openai.APIConnectionError)):
            return {
                "error_type": "TRANSIENT",
                "should_retry": True,
                "user_message": "The AI service is temporarily busy. Please wait a moment."
            }
        if isinstance(exception, (openai.AuthenticationError, openai.PermissionDeniedError)):
            return {
                "error_type": "PERMANENT",
                "should_retry": False,
                "user_message": "AI service configuration error. Using fallback recommendations."
            }
    except ImportError:
        pass
    
    if isinstance(exception, (json.JSONDecodeError, KeyError, ValueError)):
        return {
            "error_type": "MALFORMED",
            "should_retry": False,
            "user_message": "AI response could not be processed. Using fallback recommendations."
        }
    
    return {
        "error_type": "TRANSIENT",
        "should_retry": True,
        "user_message": "An unexpected error occurred. Retrying..."
    }


def with_retry_and_fallback(func, fallback_func, max_retries=2, base_delay=1.0, user_id=None, test_id=None):
    """
    Execute function with retry logic and fallback on failure.
    
    Parameters:
        func: Function to execute
        fallback_func: Fallback function to call on failure
        max_retries (int): Maximum number of retries (default 2)
        base_delay (float): Base delay for exponential backoff (default 1.0)
        user_id: User ID for logging
        test_id: Test result ID for logging
        
    Returns:
        dict: {"result": any, "source": "ai"|"fallback", "fallback_triggered": bool}
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            result = func()
            return {
                "result": result,
                "source": "ai",
                "fallback_triggered": False
            }
        except Exception as e:
            last_exception = e
            classification = classify_openai_error(e)
            
            log_ai_error(
                "ai_analyzer",
                "generate",
                classification["error_type"],
                user_id,
                test_id,
                str(type(e).__name__)
            )
            
            if not classification["should_retry"] or attempt >= max_retries:
                break
            
            time.sleep(base_delay * (2 ** attempt))
    
    # All retries exhausted, try fallback
    try:
        fallback_result = fallback_func()
        return {
            "result": fallback_result,
            "source": "fallback",
            "fallback_triggered": True
        }
    except Exception as fe:
        log_ai_error("ai_analyzer", "fallback", "PERMANENT", user_id, test_id, str(fe))
        return {
            "result": {"careers": [], "source": "error"},
            "source": "error",
            "fallback_triggered": True
        }
