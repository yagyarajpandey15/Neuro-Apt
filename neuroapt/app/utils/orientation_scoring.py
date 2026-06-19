"""
Orientation Style Scoring Utilities

This module provides functions to calculate and analyze orientation style scores
based on user answers to the orientation questions.
"""

from neuroapt.app import db
from neuroapt.app.models import TestResult, Question, QuestionOption, UserAnswer

# Define orientation styles
ORIENTATION_STYLES = ["People", "Information", "Administrative", "Creative"]

# Map database field names to styles
FIELD_TO_STYLE = {
    "people_oriented_score": "People",
    "analytical_score": "Information",
    "communication_score": "Administrative",
    "creativity_score": "Creative"
}

# Map styles to database field names
STYLE_TO_FIELD = {
    "People": "people_oriented_score",
    "Information": "analytical_score", 
    "Administrative": "communication_score",
    "Creative": "creativity_score"
}

# Style descriptions with career suggestions
STYLE_DESCRIPTIONS = {
    'People': {
        'title': 'People Orientation',
        'description': 'You are primarily oriented towards working with and helping others. Your strength lies in understanding people\'s needs, facilitating teamwork, and building relationships. You thrive in roles that involve mentoring, counseling, or providing direct service to people.',
        'careers': [
            'Therapist/Counselor', 
            'Human Resources Manager', 
            'Social Worker',
            'Teacher/Educator', 
            'Sales Representative', 
            'Customer Success Manager',
            'Healthcare Professional'
        ],
        'strengths': [
            'Empathy and emotional intelligence',
            'Interpersonal communication',
            'Conflict resolution',
            'Team building',
            'Leadership through influence'
        ]
    },
    'Information': {
        'title': 'Information Orientation',
        'description': 'You are primarily oriented towards gathering, analyzing, and working with data and information. Your strength lies in research, logical thinking, and finding evidence-based solutions. You excel in roles that involve deep analysis, investigation, or theoretical work.',
        'careers': [
            'Data Scientist/Analyst', 
            'Researcher', 
            'Engineer',
            'Financial Analyst', 
            'Accountant', 
            'Software Developer',
            'Strategic Planner'
        ],
        'strengths': [
            'Analytical thinking',
            'Logical reasoning',
            'Information processing',
            'Pattern recognition',
            'Attention to detail'
        ]
    },
    'Administrative': {
        'title': 'Administrative Orientation',
        'description': 'You are primarily oriented towards creating and maintaining structure and order. Your strength lies in organization, efficiency, and systematic approaches. You excel in roles that require careful planning, adherence to protocols, and attention to detail.',
        'careers': [
            'Project Manager', 
            'Operations Manager', 
            'Quality Assurance Specialist',
            'Executive Assistant', 
            'Process Improvement Analyst', 
            'Compliance Officer',
            'Logistics Coordinator'
        ],
        'strengths': [
            'Organization and planning',
            'Process optimization',
            'Time management',
            'Policy implementation',
            'Methodical problem-solving'
        ]
    },
    'Creative': {
        'title': 'Creative Orientation',
        'description': 'You are primarily oriented towards innovation and novel approaches. Your strength lies in thinking outside the box, generating new ideas, and envisioning possibilities. You thrive in roles that allow for experimentation, design thinking, and artistic expression.',
        'careers': [
            'Designer', 
            'Marketing Creative', 
            'Artist/Performer',
            'Entrepreneur', 
            'Innovation Consultant', 
            'Product Developer',
            'Content Creator'
        ],
        'strengths': [
            'Innovative thinking',
            'Adaptability',
            'Idea generation',
            'Visual/spatial reasoning',
            'Comfort with ambiguity'
        ]
    }
}

def calculate_orientation_scores(test_result_id):
    """
    Calculate and update orientation style scores for a test result
    
    Args:
        test_result_id: ID of the TestResult to update
    
    Returns:
        Updated TestResult object
    """
    test_result = TestResult.query.get_or_404(test_result_id)
    
    # Initialize scores for each style
    scores = {
        "People": 0,
        "Information": 0,
        "Administrative": 0,
        "Creative": 0
    }
    
    # Get all user answers for orientation questions
    user_answers = UserAnswer.query.join(Question).filter(
        UserAnswer.test_result_id == test_result_id,
        Question.category == 'orientation'
    ).all()
    
    # Calculate scores based on answers
    for answer in user_answers:
        option = QuestionOption.query.get(answer.selected_option_id)
        if option and option.trait_impact in scores:
            scores[option.trait_impact] += option.trait_value
    
    # Update the test result with scores
    test_result.people_oriented_score = scores["People"]
    test_result.analytical_score = scores["Information"]
    test_result.communication_score = scores["Administrative"]
    test_result.creativity_score = scores["Creative"]
    
    db.session.commit()
    
    return test_result

def get_orientation_styles(test_result):
    """
    Get the orientation styles for a test result, including dominant and secondary styles
    
    Args:
        test_result: TestResult object
    
    Returns:
        Dictionary with orientation style information
    """
    # Get scores for each style
    scores = {
        "People": test_result.people_oriented_score,
        "Information": test_result.analytical_score,
        "Administrative": test_result.communication_score,
        "Creative": test_result.creativity_score
    }
    
    # Sort scores in descending order
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get dominant style
    dominant_style = sorted_scores[0][0]
    dominant_score = sorted_scores[0][1]
    
    # Check for secondary style (tie or within 1 point)
    secondary_style = None
    secondary_score = None
    
    if len(sorted_scores) > 1:
        second_style = sorted_scores[1][0]
        second_score = sorted_scores[1][1]
        
        if second_score == dominant_score or second_score >= (dominant_score - 1):
            secondary_style = second_style
            secondary_score = second_score
    
    # Build result
    result = {
        'scores': scores,
        'dominant_style': dominant_style,
        'dominant_score': dominant_score,
        'secondary_style': secondary_style,
        'secondary_score': secondary_score,
        'style_descriptions': STYLE_DESCRIPTIONS
    }
    
    return result

def get_orientation_career_suggestions(test_result):
    """
    Get career suggestions based on orientation styles
    
    Args:
        test_result: TestResult object
    
    Returns:
        List of career suggestions
    """
    styles = get_orientation_styles(test_result)
    
    recommendations = []
    
    # Add careers from dominant style
    if styles['dominant_style'] and styles['dominant_style'] in STYLE_DESCRIPTIONS:
        recommendations.extend(STYLE_DESCRIPTIONS[styles['dominant_style']]['careers'])
    
    # Add careers from secondary style if it exists
    if styles['secondary_style'] and styles['secondary_style'] in STYLE_DESCRIPTIONS:
        recommendations.extend(STYLE_DESCRIPTIONS[styles['secondary_style']]['careers'])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = [x for x in recommendations if not (x in seen or seen.add(x))]
    
    return unique_recommendations 