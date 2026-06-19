"""
Interest Category Scoring Utilities

This module provides functions to calculate and analyze interest category scores
based on user answers to the interest_category questions.
"""

from neuroapt.app import db
from neuroapt.app.models import TestResult, Question, QuestionOption, UserAnswer

# Define career suggestions for each interest cluster
CAREER_SUGGESTIONS = {
    "STEM & Tech": [
        "Software Engineer", 
        "AI Researcher", 
        "Robotics Developer",
        "Data Scientist",
        "Network Engineer",
        "Cybersecurity Analyst"
    ],
    "Creative & Media": [
        "Filmmaker", 
        "Animator", 
        "Content Creator",
        "Graphic Designer",
        "UX/UI Designer",
        "Digital Artist"
    ],
    "People-Oriented": [
        "Teacher", 
        "Psychologist", 
        "HR", 
        "Social Worker",
        "Counselor",
        "Healthcare Professional"
    ],
    "Business & Management": [
        "Entrepreneur", 
        "Marketing Manager", 
        "Analyst",
        "Business Consultant",
        "Project Manager",
        "Financial Advisor"
    ],
    "Legal & Governance": [
        "Lawyer", 
        "Civil Servant", 
        "Policy Advisor",
        "Corporate Counsel",
        "Regulatory Affairs Specialist",
        "Compliance Officer"
    ],
    "Logistics & Distribution": [
        "Supply Chain Manager", 
        "Operations Executive",
        "Logistics Coordinator",
        "Inventory Manager",
        "Procurement Specialist",
        "Transportation Manager"
    ]
}

# Translate cluster names to database field names
CLUSTER_TO_FIELD = {
    "STEM & Tech": "stem_tech_score",
    "Creative & Media": "creative_media_score",
    "People-Oriented": "people_oriented_score",
    "Business & Management": "business_management_score",
    "Legal & Governance": "legal_governance_score",
    "Logistics & Distribution": "logistics_distribution_score"
}

# Translation from database field names to readable cluster names
FIELD_TO_CLUSTER = {
    "stem_tech_score": "STEM & Tech",
    "creative_media_score": "Creative & Media", 
    "people_oriented_score": "People-Oriented",
    "business_management_score": "Business & Management",
    "legal_governance_score": "Legal & Governance",
    "logistics_distribution_score": "Logistics & Distribution"
}

def calculate_interest_category_scores(test_result_id):
    """
    Calculate and update interest category scores for a test result
    
    Args:
        test_result_id: ID of the TestResult to update
    
    Returns:
        Updated TestResult object
    """
    test_result = TestResult.query.get_or_404(test_result_id)
    
    # Initialize scores for each cluster
    scores = {
        "STEM & Tech": 0,
        "Creative & Media": 0,
        "People-Oriented": 0,
        "Business & Management": 0,
        "Legal & Governance": 0,
        "Logistics & Distribution": 0
    }
    
    # Get all user answers for interest_category questions
    user_answers = UserAnswer.query.join(Question).filter(
        UserAnswer.test_result_id == test_result_id,
        Question.category == 'interest_category'
    ).all()
    
    # Calculate scores based on answers
    for answer in user_answers:
        option = QuestionOption.query.get(answer.selected_option_id)
        if option and option.trait_impact in scores:
            scores[option.trait_impact] += option.trait_value
    
    # Update the test result with scores
    for cluster, score in scores.items():
        field_name = CLUSTER_TO_FIELD.get(cluster)
        if field_name:
            setattr(test_result, field_name, score)
    
    db.session.commit()
    
    return test_result

def get_top_interest_categories(test_result, limit=2):
    """
    Get the top interest categories for a test result
    
    Args:
        test_result: TestResult object
        limit: Maximum number of categories to return
    
    Returns:
        List of tuples (category_name, score) sorted by score
    """
    categories = [
        ("STEM & Tech", test_result.stem_tech_score),
        ("Creative & Media", test_result.creative_media_score),
        ("People-Oriented", test_result.people_oriented_score),
        ("Business & Management", test_result.business_management_score),
        ("Legal & Governance", test_result.legal_governance_score),
        ("Logistics & Distribution", test_result.logistics_distribution_score)
    ]
    
    # Sort by score in descending order
    return sorted(categories, key=lambda x: x[1], reverse=True)[:limit]

def get_career_suggestions_by_category(category_name):
    """
    Get career suggestions for a specific category
    
    Args:
        category_name: Name of the category
        
    Returns:
        List of career suggestions
    """
    return CAREER_SUGGESTIONS.get(category_name, [])

def get_interest_based_career_recommendations(test_result, limit=10):
    """
    Get career recommendations based on interest categories
    
    Args:
        test_result: TestResult object
        limit: Maximum number of careers to recommend
    
    Returns:
        List of career recommendations
    """
    # Get top categories
    top_categories = get_top_interest_categories(test_result)
    
    # Get career suggestions for each category
    recommendations = []
    for category, score in top_categories:
        recommendations.extend(get_career_suggestions_by_category(category))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = [x for x in recommendations if not (x in seen or seen.add(x))]
    
    return unique_recommendations[:limit] 