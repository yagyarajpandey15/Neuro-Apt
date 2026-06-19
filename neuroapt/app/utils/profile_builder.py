"""
Student Profile Builder Module

This module provides functionality to extract and build standardized student profiles
from TestResult database objects for AI-powered career analysis.

Validates Requirements: 2.1, 8.1, 8.2
"""

from typing import Dict, Any, Optional
from datetime import datetime


def normalize_score(score: int, max_value: int = 100) -> int:
    """
    Normalize a score to the 0-100 range.
    
    Args:
        score: The raw score value
        max_value: The maximum possible value for the score
        
    Returns:
        Normalized score in 0-100 range
    """
    if score is None:
        return 0
    
    if max_value == 0:
        return 0
    
    # If max_value is 100 and score is already in valid range, return as-is
    # This avoids unnecessary rounding from floating-point division
    if max_value == 100:
        return max(0, min(100, score))
    
    # Normalize to 0-100 range using floating-point division
    # Round to nearest integer to avoid precision loss
    normalized = round((score / max_value) * 100)
    
    # Clamp to 0-100 range
    return max(0, min(100, normalized))


def validate_pattern_classification(classification: Optional[str]) -> str:
    """
    Validate and normalize pattern classification values.
    
    Args:
        classification: Pattern classification string
        
    Returns:
        Valid pattern classification (decisive/ambivalent/random)
    """
    valid_classifications = ['decisive', 'ambivalent', 'random']
    
    if classification is None:
        return 'ambivalent'  # Default to ambivalent if not set
    
    classification_lower = classification.lower().strip()
    
    if classification_lower in valid_classifications:
        return classification_lower
    
    # Default to ambivalent for invalid values
    return 'ambivalent'


def extract_cognitive_abilities(test_result) -> Dict[str, int]:
    """
    Extract cognitive ability scores from TestResult.
    
    Args:
        test_result: TestResult database object
        
    Returns:
        Dictionary with normalized cognitive ability scores
    """
    return {
        'verbal': normalize_score(test_result.verbal_score),
        'numerical': normalize_score(test_result.numerical_score),
        'abstract': normalize_score(test_result.abstract_score),
        'overall_aptitude': normalize_score(test_result.aptitude_score)
    }


def extract_personality_traits(test_result) -> Dict[str, int]:
    """
    Extract Big Five personality trait scores from TestResult.
    
    Args:
        test_result: TestResult database object
        
    Returns:
        Dictionary with normalized personality trait scores
    """
    return {
        'openness': normalize_score(test_result.openness_score),
        'conscientiousness': normalize_score(test_result.conscientiousness_score),
        'extraversion': normalize_score(test_result.extraversion_score),
        'agreeableness': normalize_score(test_result.agreeableness_score),
        'neuroticism': normalize_score(test_result.neuroticism_score)
    }


def extract_work_attributes(test_result) -> Dict[str, int]:
    """
    Extract work attribute scores from TestResult.
    
    Args:
        test_result: TestResult database object
        
    Returns:
        Dictionary with normalized work attribute scores
    """
    return {
        'leadership': normalize_score(test_result.leadership_score),
        'teamwork': normalize_score(test_result.teamwork_score),
        'creativity': normalize_score(test_result.creativity_score),
        'analytical': normalize_score(test_result.analytical_score),
        'communication': normalize_score(test_result.communication_score),
        'adaptability': normalize_score(test_result.adaptability_score)
    }


def extract_interest_domains(test_result) -> Dict[str, int]:
    """
    Extract interest domain scores from TestResult.
    
    Args:
        test_result: TestResult database object
        
    Returns:
        Dictionary with normalized interest domain scores
    """
    return {
        'stem_tech': normalize_score(test_result.stem_tech_score),
        'creative_media': normalize_score(test_result.creative_media_score),
        'people_oriented': normalize_score(test_result.people_oriented_score),
        'business_management': normalize_score(test_result.business_management_score),
        'legal_governance': normalize_score(test_result.legal_governance_score),
        'logistics_distribution': normalize_score(test_result.logistics_distribution_score)
    }


def detect_interest_intersections(interest_domains: Dict[str, int]) -> str:
    """
    Identify cross-domain patterns when multiple interest domains score ≥70.
    
    This function detects when a student has high scores (≥70) across multiple
    interest domains and labels the intersection pattern with a descriptive string.
    
    Args:
        interest_domains: Dictionary with interest domain scores (0-100)
        
    Returns:
        Intersection label string (e.g., "STEM+Creative", "Business+People-Oriented")
        Empty string if fewer than 2 domains score ≥70
        
    Validates Requirements: 2.5
    """
    # Threshold for considering a domain "high"
    THRESHOLD = 70
    
    # Find all high-scoring domains
    high_domains = {domain: score for domain, score in interest_domains.items() if score >= THRESHOLD}
    
    # If fewer than 2 high domains, no intersection
    if len(high_domains) < 2:
        return ''
    
    # Sort high domains by score (descending) to get consistent ordering
    sorted_domains = sorted(high_domains.items(), key=lambda x: x[1], reverse=True)
    
    # Extract domain names
    domain_names = [domain for domain, score in sorted_domains]
    
    # Define specific pattern mappings (order matters - check most specific first)
    # Using sets for domain combinations to handle any order
    patterns = {
        frozenset(['stem_tech', 'creative_media']): 'STEM+Creative',
        frozenset(['business_management', 'people_oriented']): 'Business+People-Oriented',
        frozenset(['stem_tech', 'business_management']): 'STEM+Business',
        frozenset(['legal_governance', 'people_oriented']): 'Legal+People-Oriented',
        frozenset(['creative_media', 'people_oriented']): 'Creative+People-Oriented',
        frozenset(['legal_governance', 'business_management']): 'Legal+Business',
        frozenset(['logistics_distribution', 'business_management']): 'Logistics+Business',
    }
    
    # For 2 high domains, check if there's a specific pattern match
    if len(domain_names) == 2:
        domain_set = frozenset(domain_names)
        if domain_set in patterns:
            return patterns[domain_set]
        else:
            # Generic pattern for unlisted pairs
            return format_generic_intersection(domain_names[:2])
    
    # For 3+ high domains, try to find best matching pair from patterns
    # Check all pairs in order of score
    for i in range(len(domain_names)):
        for j in range(i + 1, len(domain_names)):
            pair = frozenset([domain_names[i], domain_names[j]])
            if pair in patterns:
                return patterns[pair]
    
    # If no pattern match found, use generic format for top 2 domains
    return format_generic_intersection(domain_names[:2])


def format_generic_intersection(domains: list) -> str:
    """
    Format generic intersection label from domain names.
    
    Args:
        domains: List of domain names (2 elements expected)
        
    Returns:
        Formatted intersection string with proper capitalization
    """
    # Map domain names to display names
    display_names = {
        'stem_tech': 'STEM',
        'creative_media': 'Creative',
        'people_oriented': 'People-Oriented',
        'business_management': 'Business',
        'legal_governance': 'Legal',
        'logistics_distribution': 'Logistics'
    }
    
    formatted = [display_names.get(domain, domain.title()) for domain in domains]
    return '+'.join(formatted)


def extract_metadata(test_result, interest_domains: Dict[str, int]) -> Dict[str, Any]:
    """
    Extract metadata including test date and pattern analysis results.
    
    Args:
        test_result: TestResult database object
        interest_domains: Dictionary with interest domain scores for intersection detection
        
    Returns:
        Dictionary with metadata fields
    """
    # Extract contradictions list
    contradictions = test_result.contradictions_list if hasattr(test_result, 'contradictions_list') else []
    
    # Calculate consistency score from contradictions
    # If no contradictions detected, assume high consistency
    consistency_score = 100.0
    if contradictions:
        # Each contradiction reduces consistency by 10 points (capped at 0)
        consistency_score = max(0.0, 100.0 - (len(contradictions) * 10))
    
    # Format test date
    test_date_str = test_result.test_date.isoformat() if test_result.test_date else datetime.utcnow().isoformat()
    
    # Detect interest intersections from the scores
    # Use the stored value if available, otherwise compute it
    interest_intersection = test_result.interest_intersection or detect_interest_intersections(interest_domains)
    
    return {
        'test_date': test_date_str,
        'pattern_classification': validate_pattern_classification(test_result.answer_pattern_flag),
        'contradictions': contradictions,
        'consistency_score': consistency_score,
        'interest_intersection': interest_intersection
    }


def validate_required_fields(profile: Dict[str, Any]) -> bool:
    """
    Validate that all required fields are present in the profile.
    
    Args:
        profile: Student profile dictionary
        
    Returns:
        True if all required fields are present, False otherwise
    """
    required_top_level = ['user_id', 'test_id', 'cognitive_abilities', 'personality_traits',
                          'work_attributes', 'interest_domains', 'emotional_intelligence', 'metadata']
    
    # Check top-level keys
    for field in required_top_level:
        if field not in profile:
            return False
    
    # Check cognitive abilities
    required_cognitive = ['verbal', 'numerical', 'abstract', 'overall_aptitude']
    for field in required_cognitive:
        if field not in profile['cognitive_abilities']:
            return False
    
    # Check personality traits
    required_personality = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
    for field in required_personality:
        if field not in profile['personality_traits']:
            return False
    
    # Check work attributes
    required_work = ['leadership', 'teamwork', 'creativity', 'analytical', 'communication', 'adaptability']
    for field in required_work:
        if field not in profile['work_attributes']:
            return False
    
    # Check interest domains
    required_interests = ['stem_tech', 'creative_media', 'people_oriented', 'business_management',
                          'legal_governance', 'logistics_distribution']
    for field in required_interests:
        if field not in profile['interest_domains']:
            return False
    
    # Check metadata
    required_metadata = ['test_date', 'pattern_classification', 'contradictions', 'consistency_score']
    for field in required_metadata:
        if field not in profile['metadata']:
            return False
    
    # Validate pattern classification value
    valid_patterns = ['decisive', 'ambivalent', 'random']
    if profile['metadata']['pattern_classification'] not in valid_patterns:
        return False
    
    return True


def build_student_profile(test_result) -> Dict[str, Any]:
    """
    Extract complete student profile from TestResult object.
    
    This function parses a TestResult database object into a standardized dictionary
    format suitable for AI analysis. All scores are normalized to 0-100 range.
    
    Args:
        test_result: TestResult database object with completed assessment data
        
    Returns:
        Standardized profile dictionary with structure:
        {
            'user_id': int,
            'test_id': int,
            'cognitive_abilities': {
                'verbal': int (0-100),
                'numerical': int (0-100),
                'abstract': int (0-100),
                'overall_aptitude': int (0-100)
            },
            'personality_traits': {
                'openness': int (0-100),
                'conscientiousness': int (0-100),
                'extraversion': int (0-100),
                'agreeableness': int (0-100),
                'neuroticism': int (0-100)
            },
            'work_attributes': {
                'leadership': int (0-100),
                'teamwork': int (0-100),
                'creativity': int (0-100),
                'analytical': int (0-100),
                'communication': int (0-100),
                'adaptability': int (0-100)
            },
            'interest_domains': {
                'stem_tech': int (0-100),
                'creative_media': int (0-100),
                'people_oriented': int (0-100),
                'business_management': int (0-100),
                'legal_governance': int (0-100),
                'logistics_distribution': int (0-100)
            },
            'emotional_intelligence': int (0-100),
            'metadata': {
                'test_date': str (ISO format),
                'pattern_classification': str (decisive/ambivalent/random),
                'contradictions': List[Dict],
                'consistency_score': float (0-100),
                'interest_intersection': str
            }
        }
        
    Raises:
        ValueError: If test_result is None or validation fails
        
    Validates Requirements: 2.1, 8.1, 8.2
    """
    if test_result is None:
        raise ValueError("test_result cannot be None")
    
    # Extract interest domains first since metadata needs it
    interest_domains = extract_interest_domains(test_result)
    
    # Build the profile dictionary
    profile = {
        'user_id': test_result.user_id,
        'test_id': test_result.id,
        'cognitive_abilities': extract_cognitive_abilities(test_result),
        'personality_traits': extract_personality_traits(test_result),
        'work_attributes': extract_work_attributes(test_result),
        'interest_domains': interest_domains,
        'emotional_intelligence': normalize_score(test_result.eq_score),
        'metadata': extract_metadata(test_result, interest_domains)
    }
    
    # Validate the profile
    if not validate_required_fields(profile):
        raise ValueError("Profile validation failed: missing required fields")
    
    return profile
