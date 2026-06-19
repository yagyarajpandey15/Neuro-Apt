"""
NeurApt Utilities Package

This package contains utility modules for the NeurApt application:
- openai_api: OpenAI API integration for AI-powered career analysis
- pattern_analyzer: Response pattern analysis and contradiction detection
- profile_builder: Student profile construction from test results
- ability_matcher: Career-specific ability matching calculations
- confidence_scorer: Confidence score calculation for recommendations
- ai_response_validator: AI response validation and formatting
- cache_manager: AI analysis caching management
- scoring: Test scoring utilities
- interest_scoring: Interest domain scoring
- orientation_scoring: Career orientation scoring
- recommendation_engine: Career recommendation logic
"""

__version__ = "1.0.0"

# Import commonly used functions for convenience
try:
    from neuroapt.app.utils.openai_api import (
        generate_ai_career_analysis,
        get_career_insights,
        init_openai_client
    )
except ImportError:
    # Graceful handling if dependencies aren't loaded yet
    pass
