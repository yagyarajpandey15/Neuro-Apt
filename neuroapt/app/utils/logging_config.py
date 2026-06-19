"""
Centralized Logging Configuration for AI Components

This module provides standardized logging configuration for all AI-related
components in the NeurApt system. It ensures consistent error tracking,
debugging support, and operational visibility.

Requirements: 12.1, 12.2
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


# Logging configuration constants
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs')
AI_ERROR_LOG = 'openai_errors.log'
AI_DEBUG_LOG = 'ai_debug.log'
PATTERN_ANALYSIS_LOG = 'pattern_analysis.log'

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DETAILED_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'


def setup_logging_directory():
    """
    Create logs directory if it doesn't exist.
    
    Returns:
        Path to the logs directory
    """
    log_path = Path(LOG_DIR)
    log_path.mkdir(parents=True, exist_ok=True)
    return log_path


def get_ai_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger for AI components.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    
    Usage:
        from neuroapt.app.utils.logging_config import get_ai_logger
        logger = get_ai_logger(__name__)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler for persistent logging
    setup_logging_directory()
    log_file = os.path.join(LOG_DIR, AI_DEBUG_LOG)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(DETAILED_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def log_ai_error(
    component: str,
    operation: str,
    error_type: str,
    error_message: str,
    user_id: Optional[int] = None,
    test_result_id: Optional[int] = None,
    details: Optional[str] = None,
    stack_trace: Optional[str] = None,
    fallback_triggered: bool = False
):
    """
    Log AI component errors in standardized format.
    
    This function writes detailed error information to the AI error log
    file, following the format specified in the design document.
    
    Args:
        component: Component name (e.g., "AI Career Analyzer")
        operation: Operation being performed (e.g., "generate_ai_career_analysis")
        error_type: Type of error (e.g., "OpenAI API Timeout")
        error_message: Detailed error message
        user_id: Optional user ID
        test_result_id: Optional test result ID
        details: Optional additional details
        stack_trace: Optional stack trace
        fallback_triggered: Whether fallback was triggered (default: False)
    
    Requirements: 12.1, 12.2
    
    Usage:
        log_ai_error(
            component="AI Career Analyzer",
            operation="generate_ai_career_analysis",
            error_type="OpenAI API Timeout",
            error_message="Request timeout after 30 seconds",
            user_id=123,
            test_result_id=456,
            fallback_triggered=True
        )
    """
    setup_logging_directory()
    log_file = os.path.join(LOG_DIR, AI_ERROR_LOG)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Component: {component}\n")
            f.write(f"Operation: {operation}\n")
            f.write(f"Error Type: {error_type}\n")
            
            if user_id:
                f.write(f"User ID: {user_id}\n")
            if test_result_id:
                f.write(f"Test Result ID: {test_result_id}\n")
            
            f.write(f"Error Message: {error_message}\n")
            
            if details:
                f.write(f"Details: {details}\n")
            
            if stack_trace:
                f.write(f"Stack Trace:\n{stack_trace}\n")
            
            f.write(f"Fallback Triggered: {'Yes' if fallback_triggered else 'No'}\n")
            f.write(f"{'='*80}\n")
            
    except Exception as e:
        # Fallback to basic logging if file write fails
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to write to AI error log: {str(e)}")
        logger.error(f"Original error - Component: {component}, Operation: {operation}, Error: {error_message}")


def log_pattern_analysis(
    test_result_id: int,
    pattern_classification: str,
    consistency_score: float,
    contradiction_count: int,
    confidence_score: int,
    confidence_level: str,
    additional_info: Optional[Dict[str, Any]] = None
):
    """
    Log pattern analysis results for debugging and monitoring.
    
    Args:
        test_result_id: Test result ID
        pattern_classification: Pattern classification (decisive/ambivalent/random)
        consistency_score: Consistency score (0-100)
        contradiction_count: Number of contradictions detected
        confidence_score: Overall confidence score (0-100)
        confidence_level: Confidence level (HIGH/MODERATE/LOW/UNRELIABLE)
        additional_info: Optional additional information
    
    Usage:
        log_pattern_analysis(
            test_result_id=456,
            pattern_classification="decisive",
            consistency_score=85.5,
            contradiction_count=2,
            confidence_score=78,
            confidence_level="MODERATE"
        )
    """
    setup_logging_directory()
    log_file = os.path.join(LOG_DIR, PATTERN_ANALYSIS_LOG)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'-'*80}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Test Result ID: {test_result_id}\n")
            f.write(f"Pattern Classification: {pattern_classification}\n")
            f.write(f"Consistency Score: {consistency_score:.2f}\n")
            f.write(f"Contradiction Count: {contradiction_count}\n")
            f.write(f"Confidence Score: {confidence_score}\n")
            f.write(f"Confidence Level: {confidence_level}\n")
            
            if additional_info:
                f.write(f"Additional Info: {additional_info}\n")
            
            f.write(f"{'-'*80}\n")
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to write to pattern analysis log: {str(e)}")


def log_api_call(
    model: str,
    operation: str,
    profile_id: Optional[int] = None,
    response_time: Optional[float] = None,
    tokens_used: Optional[int] = None,
    cache_hit: bool = False,
    success: bool = True,
    error: Optional[str] = None
):
    """
    Log API call information for monitoring and performance analysis.
    
    Args:
        model: Model used (e.g., "gpt-4o", "gpt-4o-mini")
        operation: Operation performed
        profile_id: Optional test result/profile ID
        response_time: Response time in seconds
        tokens_used: Number of tokens used
        cache_hit: Whether cache was used
        success: Whether the call succeeded
        error: Error message if failed
    
    Usage:
        log_api_call(
            model="gpt-4o",
            operation="generate_career_analysis",
            profile_id=456,
            response_time=2.5,
            tokens_used=1500,
            success=True
        )
    """
    logger = get_ai_logger('neuroapt.api_calls')
    
    log_message = f"API Call - Model: {model}, Operation: {operation}"
    
    if profile_id:
        log_message += f", Profile: {profile_id}"
    
    if cache_hit:
        log_message += ", Cache: HIT"
    elif response_time:
        log_message += f", Response Time: {response_time:.2f}s"
    
    if tokens_used:
        log_message += f", Tokens: {tokens_used}"
    
    if success:
        logger.info(log_message)
    else:
        log_message += f", Error: {error}" if error else ", Error: Unknown"
        logger.error(log_message)


def configure_root_logger(level: int = logging.INFO):
    """
    Configure the root logger with basic settings.
    
    This should be called once during application initialization.
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                os.path.join(LOG_DIR, 'neuroapt.log'),
                encoding='utf-8'
            )
        ]
    )
