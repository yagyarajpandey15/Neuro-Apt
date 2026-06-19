"""
Ability Match Calculator Module

This module provides functionality to calculate granular ability-career fit scores
with career-specific weighting for AI-enhanced career matching.

Validates Requirements: 2.4, 10.1, 10.2, 10.3, 10.4
"""

from typing import Dict, Any


# Career requirement constants (0-100 scale)
# These represent baseline skill requirements for each career type
CAREER_REQUIREMENTS = {
    'technical': {
        'cognitive': 75,
        'personality': 60,
        'emotional_intelligence': 50,
        'work_style': 65,
        'interest': 70
    },
    'creative': {
        'cognitive': 60,
        'personality': 70,
        'emotional_intelligence': 65,
        'work_style': 75,
        'interest': 80
    },
    'business': {
        'cognitive': 70,
        'personality': 70,
        'emotional_intelligence': 75,
        'work_style': 65,
        'interest': 70
    },
    'research': {
        'cognitive': 80,
        'personality': 65,
        'emotional_intelligence': 55,
        'work_style': 70,
        'interest': 75
    },
    'healthcare': {
        'cognitive': 70,
        'personality': 65,
        'emotional_intelligence': 85,
        'work_style': 60,
        'interest': 75
    },
    'people_oriented': {
        'cognitive': 65,
        'personality': 70,
        'emotional_intelligence': 85,
        'work_style': 60,
        'interest': 75
    }
}

# Career-specific weights for computing overall match
CAREER_WEIGHTS = {
    'technical': {
        'cognitive': 0.45,
        'personality': 0.20,
        'emotional_intelligence': 0.10,
        'work_style': 0.15,
        'interest': 0.10
    },
    'creative': {
        'cognitive': 0.15,
        'personality': 0.35,
        'emotional_intelligence': 0.15,
        'work_style': 0.25,
        'interest': 0.10
    },
    'business': {
        'cognitive': 0.30,
        'personality': 0.25,
        'emotional_intelligence': 0.20,
        'work_style': 0.15,
        'interest': 0.10
    },
    'research': {
        'cognitive': 0.45,
        'personality': 0.20,
        'emotional_intelligence': 0.10,
        'work_style': 0.15,
        'interest': 0.10
    },
    'healthcare': {
        'cognitive': 0.25,
        'personality': 0.20,
        'emotional_intelligence': 0.35,
        'work_style': 0.10,
        'interest': 0.10
    },
    'people_oriented': {
        'cognitive': 0.20,
        'personality': 0.25,
        'emotional_intelligence': 0.35,
        'work_style': 0.10,
        'interest': 0.10
    }
}

# Keywords for career type detection
CAREER_TYPE_KEYWORDS = {
    'technical': [
        'software', 'engineer', 'developer', 'programmer', 'architect', 'technician',
        'IT', 'technology', 'systems', 'network', 'database', 'DevOps', 'data scientist',
        'cybersecurity', 'technical', 'coding', 'programming', 'computer science',
        'electronics', 'mechanical', 'electrical', 'civil engineer'
    ],
    'creative': [
        'design', 'designer', 'artist', 'creative', 'media', 'graphic', 'UX', 'UI',
        'photographer', 'videographer', 'animator', 'illustrator', 'writer', 'content',
        'marketing creative', 'art director', 'fashion', 'interior design', 'architect',
        'musician', 'film', 'video', 'advertising creative', 'copywriter'
    ],
    'business': [
        'management', 'manager', 'business', 'finance', 'financial', 'accounting',
        'accountant', 'consultant', 'strategy', 'operations', 'analyst', 'executive',
        'entrepreneur', 'MBA', 'sales', 'marketing', 'product manager', 'project manager',
        'business development', 'investment', 'banking', 'economist', 'commerce'
    ],
    'research': [
        'research', 'researcher', 'scientist', 'academic', 'professor', 'PhD',
        'laboratory', 'analyst', 'statistician', 'data analyst', 'biologist',
        'chemist', 'physicist', 'mathematician', 'social scientist', 'psychologist',
        'economist research', 'clinical research', 'R&D', 'scholar'
    ],
    'healthcare': [
        'medical', 'doctor', 'physician', 'nurse', 'healthcare', 'therapy', 'therapist',
        'clinical', 'surgeon', 'dentist', 'pharmacist', 'paramedic', 'health',
        'hospital', 'patient care', 'medical assistant', 'radiologist', 'psychiatrist',
        'physical therapy', 'occupational therapy', 'mental health', 'counselor'
    ],
    'people_oriented': [
        'teacher', 'teaching', 'education', 'educator', 'instructor', 'trainer',
        'HR', 'human resources', 'social work', 'counselor', 'coach', 'mentor',
        'community', 'nonprofit', 'customer service', 'customer success', 'support',
        'recruiting', 'recruiter', 'training', 'facilitator', 'coordinator'
    ]
}


def detect_career_type(career_title: str, career_category: str = '') -> str:
    """
    Detect career type using keyword matching on titles and categories.
    
    Args:
        career_title: Career name (e.g., "Software Engineer")
        career_category: Broad category (e.g., "STEM+Tech")
        
    Returns:
        Career type: 'technical', 'creative', 'business', 'research', 'healthcare', or 'people_oriented'
        Defaults to 'business' if no match found
        
    Validates Requirements: 10.4
    """
    # Combine title and category for matching
    combined_text = f"{career_title} {career_category}".lower()
    
    # Track matches for each career type
    match_scores = {career_type: 0 for career_type in CAREER_TYPE_KEYWORDS.keys()}
    
    # Count keyword matches for each career type
    for career_type, keywords in CAREER_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in combined_text:
                match_scores[career_type] += 1
    
    # Find the career type with the highest match score
    max_score = max(match_scores.values())
    
    if max_score > 0:
        # Return the career type with the highest score
        for career_type, score in match_scores.items():
            if score == max_score:
                return career_type
    
    # Default to business if no matches found
    return 'business'


def calculate_dimension_score(student_profile: Dict[str, Any], dimension: str) -> int:
    """
    Calculate aggregated score for a dimension from student profile.
    
    Args:
        student_profile: Complete profile from build_student_profile()
        dimension: Dimension name ('cognitive', 'personality', 'emotional_intelligence', 'work_style', 'interest')
        
    Returns:
        Aggregated score (0-100)
    """
    if dimension == 'cognitive':
        # Average of cognitive ability scores
        cognitive = student_profile.get('cognitive_abilities', {})
        scores = [
            cognitive.get('verbal', 0),
            cognitive.get('numerical', 0),
            cognitive.get('abstract', 0),
            cognitive.get('overall_aptitude', 0)
        ]
        return int(sum(scores) / len(scores)) if scores else 0
    
    elif dimension == 'personality':
        # Average of personality trait scores
        personality = student_profile.get('personality_traits', {})
        scores = [
            personality.get('openness', 0),
            personality.get('conscientiousness', 0),
            personality.get('extraversion', 0),
            personality.get('agreeableness', 0),
            # Note: neuroticism is inverted (high neuroticism = negative trait)
            100 - personality.get('neuroticism', 0)
        ]
        return int(sum(scores) / len(scores)) if scores else 0
    
    elif dimension == 'emotional_intelligence':
        # Direct EQ score
        return student_profile.get('emotional_intelligence', 0)
    
    elif dimension == 'work_style':
        # Average of work attribute scores
        work_attrs = student_profile.get('work_attributes', {})
        scores = [
            work_attrs.get('leadership', 0),
            work_attrs.get('teamwork', 0),
            work_attrs.get('creativity', 0),
            work_attrs.get('analytical', 0),
            work_attrs.get('communication', 0),
            work_attrs.get('adaptability', 0)
        ]
        return int(sum(scores) / len(scores)) if scores else 0
    
    elif dimension == 'interest':
        # Average of interest domain scores
        interests = student_profile.get('interest_domains', {})
        scores = [
            interests.get('stem_tech', 0),
            interests.get('creative_media', 0),
            interests.get('people_oriented', 0),
            interests.get('business_management', 0),
            interests.get('legal_governance', 0),
            interests.get('logistics_distribution', 0)
        ]
        return int(sum(scores) / len(scores)) if scores else 0
    
    return 0


def calculate_dimension_match(student_score: int, career_requirement: int) -> int:
    """
    Calculate match percentage for a single dimension.
    
    Formula: min(100, (student_score / career_requirement) * 100)
    
    Args:
        student_score: Student's score (0-100)
        career_requirement: Career's requirement score (0-100)
        
    Returns:
        Match percentage (0-100)
        
    Validates Requirements: 10.2, 10.3
    """
    if career_requirement == 0:
        return 100  # If no requirement, perfect match
    
    # Calculate match percentage
    match_percentage = (student_score / career_requirement) * 100
    
    # Cap at 100
    return min(100, int(match_percentage))


def calculate_ability_match_for_career(student_profile: Dict[str, Any],
                                       career_title: str,
                                       career_category: str = '') -> Dict[str, int]:
    """
    Calculate multi-dimensional ability match for a specific career.
    
    This function computes match percentages across five dimensions (cognitive abilities,
    personality traits, emotional intelligence, work style, and interest alignment) using
    career-specific weights and requirements.
    
    Args:
        student_profile: Complete profile from build_student_profile()
        career_title: Career name (e.g., "Software Engineer")
        career_category: Broad category (e.g., "STEM+Tech")
    
    Returns:
        Dictionary containing:
        {
            'cognitive_match': int (0-100),
            'personality_match': int (0-100),
            'emotional_intelligence_match': int (0-100),
            'work_style_match': int (0-100),
            'interest_alignment': int (0-100),
            'overall_match': int (0-100)  # Weighted average
        }
        
    Validates Requirements: 2.4, 10.1, 10.2, 10.3, 10.4
    """
    # Detect career type
    career_type = detect_career_type(career_title, career_category)
    
    # Get requirements and weights for this career type
    requirements = CAREER_REQUIREMENTS.get(career_type, CAREER_REQUIREMENTS['business'])
    weights = CAREER_WEIGHTS.get(career_type, CAREER_WEIGHTS['business'])
    
    # Calculate student scores for each dimension
    dimensions = ['cognitive', 'personality', 'emotional_intelligence', 'work_style', 'interest']
    dimension_scores = {}
    dimension_matches = {}
    
    for dimension in dimensions:
        student_score = calculate_dimension_score(student_profile, dimension)
        dimension_scores[dimension] = student_score
        
        career_requirement = requirements.get(dimension, 50)
        dimension_matches[dimension] = calculate_dimension_match(student_score, career_requirement)
    
    # Calculate weighted overall match
    overall_match = (
        dimension_matches['cognitive'] * weights['cognitive'] +
        dimension_matches['personality'] * weights['personality'] +
        dimension_matches['emotional_intelligence'] * weights['emotional_intelligence'] +
        dimension_matches['work_style'] * weights['work_style'] +
        dimension_matches['interest'] * weights['interest']
    )
    
    return {
        'cognitive_match': dimension_matches['cognitive'],
        'personality_match': dimension_matches['personality'],
        'emotional_intelligence_match': dimension_matches['emotional_intelligence'],
        'work_style_match': dimension_matches['work_style'],
        'interest_alignment': dimension_matches['interest'],
        'overall_match': int(overall_match)
    }
