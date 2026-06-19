"""
Statistical Fallback Matcher Module

Provides simplified career recommendations when AI analysis is unavailable.
Ranks interest domains and selects careers based on aptitude scores.
"""

CAREER_DATABASE = {
    "stem": [
        {"title": "Software Developer", "category": "Technology", "aptitude_requirement": 65},
        {"title": "Data Analyst", "category": "Analytics", "aptitude_requirement": 60},
        {"title": "Civil Engineer", "category": "Engineering", "aptitude_requirement": 65},
        {"title": "Biomedical Researcher", "category": "Science", "aptitude_requirement": 70},
    ],
    "arts": [
        {"title": "Graphic Designer", "category": "Design", "aptitude_requirement": 45},
        {"title": "Content Writer", "category": "Media", "aptitude_requirement": 50},
        {"title": "UX Designer", "category": "Design", "aptitude_requirement": 55},
        {"title": "Animator", "category": "Media", "aptitude_requirement": 50},
    ],
    "business": [
        {"title": "Business Analyst", "category": "Business", "aptitude_requirement": 60},
        {"title": "Marketing Manager", "category": "Marketing", "aptitude_requirement": 55},
        {"title": "Entrepreneur", "category": "Business", "aptitude_requirement": 50},
        {"title": "Financial Advisor", "category": "Finance", "aptitude_requirement": 60},
    ],
    "social": [
        {"title": "Social Worker", "category": "Social Services", "aptitude_requirement": 45},
        {"title": "HR Manager", "category": "Human Resources", "aptitude_requirement": 50},
        {"title": "Counselor", "category": "Mental Health", "aptitude_requirement": 50},
        {"title": "Teacher", "category": "Education", "aptitude_requirement": 50},
    ],
    "healthcare": [
        {"title": "Nurse", "category": "Healthcare", "aptitude_requirement": 60},
        {"title": "Physiotherapist", "category": "Healthcare", "aptitude_requirement": 55},
        {"title": "Pharmacist", "category": "Healthcare", "aptitude_requirement": 65},
        {"title": "Dentist", "category": "Healthcare", "aptitude_requirement": 70},
    ],
}


def get_statistical_recommendations(test_result):
    """
    Generate statistical career recommendations based on interest scores.
    
    Algorithm:
    1. Extract interest scores from test_result
    2. Rank domains by score descending
    3. Select top 2 domains
    4. Filter careers by aptitude_score >= aptitude_requirement
    5. Return up to 3 from top domain, up to 2 from second domain
    6. If empty, return top 2 careers from top domain regardless of aptitude
    
    Parameters:
        test_result: TestResult object or mock with interest and aptitude scores
        
    Returns:
        list: Career recommendation dicts with simplified format
    """
    if test_result is None:
        return []
    
    # Extract interest scores with defaults
    scores = {
        "stem": getattr(test_result, "interest_stem", 0) or 0,
        "arts": getattr(test_result, "interest_arts", 0) or 0,
        "business": getattr(test_result, "interest_business", 0) or 0,
        "social": getattr(test_result, "interest_social", 0) or 0,
        "healthcare": getattr(test_result, "interest_healthcare", 0) or 0,
    }
    
    # Get aptitude score
    aptitude = getattr(test_result, "aptitude_score", 50) or 50
    
    # Rank domains by score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_two = [domain for domain, _ in ranked[:2]]
    
    results = []
    
    # Process top 2 domains
    for i, domain in enumerate(top_two):
        limit = 3 if i == 0 else 2
        
        # Get careers from domain
        domain_careers = CAREER_DATABASE.get(domain, [])
        
        # Filter by aptitude
        filtered = [c for c in domain_careers if aptitude >= c["aptitude_requirement"]]
        
        # If no careers pass filter, use unfiltered list (fallback)
        careers_to_use = filtered if filtered else domain_careers[:limit]
        
        # Add careers to results
        for c in careers_to_use[:limit]:
            results.append({
                "title": c["title"],
                "category": c["category"],
                "match_type": "statistical",
                "confidence": "LOW",
                "note": "Generated without AI analysis"
            })
    
    # Ensure at least one result
    if not results and ranked:
        top_domain = ranked[0][0]
        top_careers = CAREER_DATABASE.get(top_domain, [])
        if top_careers:
            results.append({
                "title": top_careers[0]["title"],
                "category": top_careers[0]["category"],
                "match_type": "statistical",
                "confidence": "LOW",
                "note": "Generated without AI analysis"
            })
    
    return results
