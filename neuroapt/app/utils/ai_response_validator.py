"""
AI Response Validator and Formatter

This module provides validation and formatting functionality for AI-generated
career analysis responses. It ensures all required fields are present, validates
numeric ranges, and standardizes the response structure for storage and display.

Validates Requirements: 2.3, 6.2, 6.6, 8.4, 8.5, 12.4
"""

from typing import Dict, Any, List, Optional


def validate_and_format_ai_response(raw_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Validate AI response structure and format for storage.
    
    This function performs comprehensive validation of AI-generated career analysis
    responses to ensure they contain all required fields, have valid data types,
    and meet structural requirements before being stored in the database.
    
    Validation Checks:
        - Required top-level keys exist (top_careers, alternate_careers, etc.)
        - Each career match has required fields
        - Numeric values are in valid ranges
        - Arrays have expected element counts
        - Roadmaps contain all required timeframes
    
    Args:
        raw_response: Dictionary containing AI-generated analysis with structure:
            {
                'top_careers': List[Dict],  # 3-5 career matches
                'alternate_careers': List[Dict],  # 2-4 career matches
                'confidence_analysis': Dict,
                'personality_summary': str,
                'unique_strengths': List[str],
                'growth_areas': List[str],
                'emotional_readiness': Dict,
                'contradiction_analysis': str,
                'parent_report': Dict
            }
    
    Returns:
        Validated and formatted response dictionary, or None if validation fails
    
    Examples:
        >>> valid_response = {
        ...     'top_careers': [
        ...         {
        ...             'title': 'Software Engineer',
        ...             'match_percentage': 85,
        ...             'why_this_fits': 'Strong analytical skills',
        ...             'challenges': 'May require teamwork improvement',
        ...             'roadmap': {
        ...                 'immediate_1_month': ['Learn Python basics'],
        ...                 'short_term_3_6_months': ['Build portfolio'],
        ...                 'medium_term_6_12_months': ['Apply for internships']
        ...             },
        ...             'reality_check': {
        ...                 'daily_life': 'Coding and problem solving',
        ...                 'work_environment': 'Office or remote',
        ...                 'common_challenges': 'Debugging complex issues'
        ...             }
        ...         }
        ...     ] * 3,  # At least 3 careers
        ...     'alternate_careers': [...] * 2,  # At least 2 careers
        ...     'confidence_analysis': {...},
        ...     'personality_summary': 'Analytical and creative',
        ...     ...
        ... }
        >>> result = validate_and_format_ai_response(valid_response)
        >>> result is not None
        True
    """
    if not raw_response or not isinstance(raw_response, dict):
        return None
    
    # Validate required top-level keys
    required_top_level_keys = [
        'top_careers',
        'alternate_careers',
        'confidence_analysis',
        'personality_summary'
    ]
    
    for key in required_top_level_keys:
        if key not in raw_response:
            return None
    
    # Validate top careers
    top_careers = raw_response.get('top_careers', [])
    if not isinstance(top_careers, list):
        return None
    
    if len(top_careers) < 3 or len(top_careers) > 5:
        return None
    
    # Validate each top career
    formatted_top_careers = []
    for career in top_careers:
        formatted_career = validate_career_match(career)
        if formatted_career is None:
            return None
        formatted_top_careers.append(formatted_career)
    
    # Validate alternate careers
    alternate_careers = raw_response.get('alternate_careers', [])
    if not isinstance(alternate_careers, list):
        return None
    
    if len(alternate_careers) < 2 or len(alternate_careers) > 4:
        return None
    
    # Validate each alternate career
    formatted_alternate_careers = []
    for career in alternate_careers:
        formatted_career = validate_career_match(career, is_alternate=True)
        if formatted_career is None:
            return None
        formatted_alternate_careers.append(formatted_career)
    
    # Build validated response
    validated_response = {
        'top_careers': formatted_top_careers,
        'alternate_careers': formatted_alternate_careers,
        'confidence_analysis': raw_response.get('confidence_analysis', {}),
        'personality_summary': raw_response.get('personality_summary', ''),
        'unique_strengths': raw_response.get('unique_strengths', []),
        'growth_areas': raw_response.get('growth_areas', []),
        'emotional_readiness': raw_response.get('emotional_readiness', {}),
        'contradiction_analysis': raw_response.get('contradiction_analysis', ''),
        'parent_report': raw_response.get('parent_report', {})
    }
    
    return validated_response


def validate_career_match(career: Dict[str, Any], is_alternate: bool = False) -> Optional[Dict[str, Any]]:
    """
    Validate a single career match object.
    
    Ensures the career match contains all required fields with valid data types
    and values within acceptable ranges.
    
    Required Fields:
        - title (str): Career title
        - match_percentage (int): Match score 0-100
        - why_this_fits (str): Explanation of fit
        - challenges (str): Potential challenges (can be 'why_you_might_struggle')
        - roadmap (Dict): Action plan with timeframes
        - reality_check (Dict): Daily life description
    
    Args:
        career: Dictionary containing career match data
        is_alternate: If True, allows slightly relaxed validation for alternate careers
    
    Returns:
        Validated and formatted career match dictionary, or None if validation fails
    """
    if not career or not isinstance(career, dict):
        return None
    
    # Required fields for career matches
    required_fields = ['title', 'match_percentage', 'why_this_fits', 'roadmap', 'reality_check']
    
    # Check for required fields
    for field in required_fields:
        if field not in career:
            return None
    
    # Validate title
    title = career.get('title', '')
    if not isinstance(title, str) or len(title.strip()) == 0:
        return None
    
    # Validate match_percentage (must be 0-100)
    match_percentage = career.get('match_percentage')
    if not isinstance(match_percentage, (int, float)):
        return None
    
    match_percentage = int(match_percentage)
    if match_percentage < 0 or match_percentage > 100:
        return None
    
    # Validate why_this_fits
    why_fits = career.get('why_this_fits', '')
    if not isinstance(why_fits, str) or len(why_fits.strip()) == 0:
        return None
    
    # Validate challenges (accept both 'challenges' and 'why_you_might_struggle')
    challenges = career.get('challenges') or career.get('why_you_might_struggle', '')
    if not isinstance(challenges, str):
        challenges = ''
    
    # Validate roadmap
    roadmap = career.get('roadmap', {})
    if not validate_roadmap(roadmap):
        return None
    
    # Validate reality_check
    reality_check = career.get('reality_check', {})
    if not validate_reality_check(reality_check):
        return None
    
    # Build formatted career match
    formatted_career = {
        'title': title.strip(),
        'match_percentage': match_percentage,
        'category': career.get('category', ''),
        'why_this_fits': why_fits.strip(),
        'why_you_might_struggle': challenges.strip() if challenges else 'No significant challenges identified',
        'challenges': challenges.strip() if challenges else 'No significant challenges identified',
        'ability_breakdown': career.get('ability_breakdown', {}),
        'matching_traits': career.get('matching_traits', []),
        'reality_check': reality_check,
        'roadmap': roadmap,
        'confidence_score': career.get('confidence_score', match_percentage)
    }
    
    return formatted_career


def validate_roadmap(roadmap: Dict[str, Any]) -> bool:
    """
    Validate career roadmap structure.
    
    Ensures roadmap contains all three required timeframes with action lists.
    
    Required Timeframes:
        - immediate_1_month: Actions to take within 1 month
        - short_term_3_6_months: Actions for 3-6 months
        - medium_term_6_12_months: Actions for 6-12 months
    
    Args:
        roadmap: Dictionary containing roadmap data
    
    Returns:
        True if roadmap is valid, False otherwise
    
    Examples:
        >>> roadmap = {
        ...     'immediate_1_month': ['Learn basics', 'Research field'],
        ...     'short_term_3_6_months': ['Take course', 'Build project'],
        ...     'medium_term_6_12_months': ['Apply for roles', 'Network']
        ... }
        >>> validate_roadmap(roadmap)
        True
        
        >>> invalid_roadmap = {
        ...     'immediate_1_month': ['Learn basics']
        ... }
        >>> validate_roadmap(invalid_roadmap)
        False
    """
    if not roadmap or not isinstance(roadmap, dict):
        return False
    
    # Required timeframe keys
    required_timeframes = [
        'immediate_1_month',
        'short_term_3_6_months',
        'medium_term_6_12_months'
    ]
    
    # Check each required timeframe exists
    for timeframe in required_timeframes:
        if timeframe not in roadmap:
            return False
        
        # Timeframe value should be a list
        timeframe_value = roadmap[timeframe]
        if not isinstance(timeframe_value, list):
            return False
        
        # Timeframe should have at least one action item
        if len(timeframe_value) == 0:
            return False
    
    return True


def validate_reality_check(reality_check: Dict[str, Any]) -> bool:
    """
    Validate reality check structure.
    
    Ensures reality check contains required descriptive fields about the career.
    
    Required Fields:
        - daily_life: Description of typical daily tasks
        - work_environment: Description of work setting
        - common_challenges: Description of typical challenges
    
    Args:
        reality_check: Dictionary containing reality check data
    
    Returns:
        True if reality check is valid, False otherwise
    
    Examples:
        >>> reality_check = {
        ...     'daily_life': 'Coding and meetings',
        ...     'work_environment': 'Office setting',
        ...     'common_challenges': 'Tight deadlines'
        ... }
        >>> validate_reality_check(reality_check)
        True
    """
    if not reality_check or not isinstance(reality_check, dict):
        return False
    
    # Required fields (at least one must be present and non-empty)
    required_fields = ['daily_life', 'work_environment', 'common_challenges']
    
    # Check if at least one required field exists with content
    has_content = False
    for field in required_fields:
        if field in reality_check:
            value = reality_check[field]
            if isinstance(value, str) and len(value.strip()) > 0:
                has_content = True
                break
    
    return has_content


def format_career_matches(careers: List[Dict]) -> List[Dict]:
    """
    Standardize career match format, filling missing optional fields.
    
    This function takes a list of career match dictionaries and ensures they
    all have a consistent structure with default values for missing optional fields.
    
    Args:
        careers: List of career match dictionaries
    
    Returns:
        List of standardized career match dictionaries
    
    Examples:
        >>> careers = [
        ...     {
        ...         'title': 'Software Engineer',
        ...         'match_percentage': 85,
        ...         'why_this_fits': 'Good fit',
        ...         'challenges': 'Some challenges',
        ...         'roadmap': {...},
        ...         'reality_check': {...}
        ...     }
        ... ]
        >>> formatted = format_career_matches(careers)
        >>> 'ability_breakdown' in formatted[0]
        True
    """
    if not careers or not isinstance(careers, list):
        return []
    
    formatted_careers = []
    
    for career in careers:
        if not isinstance(career, dict):
            continue
        
        # Ensure all standard fields exist
        formatted_career = {
            'title': career.get('title', 'Unknown Career'),
            'match_percentage': max(0, min(100, int(career.get('match_percentage', 0)))),
            'category': career.get('category', ''),
            'why_this_fits': career.get('why_this_fits', ''),
            'why_you_might_struggle': career.get('why_you_might_struggle') or career.get('challenges', ''),
            'challenges': career.get('challenges') or career.get('why_you_might_struggle', ''),
            'ability_breakdown': career.get('ability_breakdown', {
                'cognitive_match': 0,
                'personality_match': 0,
                'emotional_intelligence_match': 0,
                'work_style_match': 0,
                'interest_alignment': 0
            }),
            'matching_traits': career.get('matching_traits', []),
            'reality_check': career.get('reality_check', {
                'daily_life': '',
                'work_environment': '',
                'common_challenges': '',
                'stress_factors': '',
                'work_life_balance': ''
            }),
            'roadmap': career.get('roadmap', {
                'immediate_1_month': [],
                'short_term_3_6_months': [],
                'medium_term_6_12_months': [],
                'skill_development': [],
                'resources': []
            }),
            'confidence_score': career.get('confidence_score', career.get('match_percentage', 0))
        }
        
        formatted_careers.append(formatted_career)
    
    return formatted_careers


def validate_numeric_range(value: Any, min_val: int = 0, max_val: int = 100) -> bool:
    """
    Validate that a numeric value is within a specified range.
    
    Args:
        value: Value to validate
        min_val: Minimum acceptable value (inclusive)
        max_val: Maximum acceptable value (inclusive)
    
    Returns:
        True if value is numeric and within range, False otherwise
    
    Examples:
        >>> validate_numeric_range(50, 0, 100)
        True
        >>> validate_numeric_range(150, 0, 100)
        False
        >>> validate_numeric_range('not a number', 0, 100)
        False
    """
    if not isinstance(value, (int, float)):
        return False
    
    return min_val <= value <= max_val


def validate_array_count(array: Any, min_count: int, max_count: int) -> bool:
    """
    Validate that an array has the expected number of elements.
    
    Args:
        array: Array to validate
        min_count: Minimum number of elements required
        max_count: Maximum number of elements allowed
    
    Returns:
        True if array has valid element count, False otherwise
    
    Examples:
        >>> validate_array_count([1, 2, 3], 2, 5)
        True
        >>> validate_array_count([1], 2, 5)
        False
        >>> validate_array_count([1, 2, 3, 4, 5, 6], 2, 5)
        False
    """
    if not isinstance(array, list):
        return False
    
    return min_count <= len(array) <= max_count
