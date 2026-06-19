"""
AI-Powered Career Recommendation Engine
Uses OpenAI GPT-4o for intelligent career analysis with fallback to statistical matching
"""

import json
import logging
from typing import Dict, List, Any, Optional
from neuroapt.app.models import TestResult
from neuroapt.app.utils.scoring import get_trait_descriptions
from neuroapt.app.utils.openai_api import generate_ai_career_analysis, generate_skill_suggestions
from neuroapt.app import db

# Configure logging
logger = logging.getLogger(__name__)


def build_student_profile(test_result: TestResult) -> Dict[str, Any]:
    """
    Build comprehensive student profile dictionary for AI analysis
    
    Args:
        test_result: TestResult object with all scores
        
    Returns:
        Complete student profile dictionary
    """
    profile = {
        # Test metadata
        "test_id": test_result.id,
        "test_date": test_result.test_date.strftime('%Y-%m-%d'),
        "user_id": test_result.user_id,
        
        # Overall scores
        "total_score": test_result.total_score,
        "confidence_level": test_result.confidence_level or "MODERATE",
        "answer_pattern": test_result.answer_pattern_flag or "balanced",
        "contradictions_detected": test_result.contradictions_detected or False,
        
        # Section scores (0-100 scale)
        "scores": {
            "orientation": test_result.orientation_score,
            "interest": test_result.interest_score,
            "personality": test_result.personality_score,
            "aptitude": test_result.aptitude_score,
            "eq": test_result.eq_score,
            "work_style": test_result.work_style_score
        },
        
        # Cognitive abilities
        "cognitive_abilities": {
            "verbal_reasoning": test_result.verbal_score,
            "numerical_reasoning": test_result.numerical_score,
            "abstract_reasoning": test_result.abstract_score,
            "analytical_thinking": test_result.analytical_score
        },
        
        # Big Five personality traits
        "personality_traits": {
            "openness": test_result.openness_score,
            "conscientiousness": test_result.conscientiousness_score,
            "extraversion": test_result.extraversion_score,
            "agreeableness": test_result.agreeableness_score,
            "neuroticism": test_result.neuroticism_score
        },
        
        # Work style attributes
        "work_style": {
            "leadership": test_result.leadership_score,
            "teamwork": test_result.teamwork_score,
            "communication": test_result.communication_score,
            "creativity": test_result.creativity_score,
            "adaptability": test_result.adaptability_score
        },
        
        # Emotional intelligence
        "emotional_intelligence": {
            "overall_eq": test_result.eq_score,
            "note": "Direct measurement from EQ section questions"
        },
        
        # Interest domains (if available from scoring)
        "interest_domains": test_result.interest_intersection or "Not analyzed",
        
        # Pattern analysis flags
        "analysis_flags": {
            "answer_consistency": test_result.answer_pattern_flag or "balanced",
            "cross_section_contradictions": test_result.contradictions_detected or False,
            "confidence_level": test_result.confidence_level or "MODERATE"
        }
    }
    
    return profile


def get_career_recommendations(test_result_id: int) -> Dict[str, Any]:
    """
    Generate AI-powered career recommendations with fallback to statistical matching
    
    Args:
        test_result_id: ID of the test result
        
    Returns:
        Career recommendations dictionary
    """
    test_result = TestResult.query.get_or_404(test_result_id)
    
    # Check if AI analysis is already cached
    if test_result.ai_analysis:
        try:
            cached_analysis = test_result.get_ai_analysis_dict()
            if cached_analysis and 'top_careers' in cached_analysis:
                logger.info(f"Using cached AI analysis for test_result {test_result_id}")
                return format_ai_recommendations(cached_analysis, test_result)
        except Exception as e:
            logger.warning(f"Failed to parse cached AI analysis: {str(e)}")
    
    # Try to generate new AI-powered analysis
    try:
        logger.info(f"Generating AI career analysis for test_result {test_result_id}")
        student_profile = build_student_profile(test_result)
        ai_analysis = generate_ai_career_analysis(student_profile)
        
        if ai_analysis and 'top_careers' in ai_analysis:
            # Cache the AI analysis in database
            test_result.set_ai_analysis_dict(ai_analysis)
            db.session.commit()
            logger.info(f"AI analysis generated and cached for test_result {test_result_id}")
            
            return format_ai_recommendations(ai_analysis, test_result)
        else:
            logger.warning(f"AI analysis returned invalid format, falling back to statistical")
    
    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}, falling back to statistical matching")
    
    # Fallback to statistical matching
    logger.info(f"Using statistical matching for test_result {test_result_id}")
    return get_statistical_career_recommendations(test_result)


def calculate_ability_match_for_career(test_result: TestResult, career_data: Dict[str, Any], career_type: str = 'general') -> Dict[str, int]:
    """
    Calculate ability match percentages for a specific career
    
    Args:
        test_result: TestResult object with all scores
        career_data: Career data from AI analysis
        career_type: Type of career for weighting (technical, creative, business, etc.)
        
    Returns:
        Dictionary with match percentages for each ability dimension
    """
    # Define career-specific ability requirements and weights
    career_weights = {
        'technical': {
            'cognitive_importance': 0.45,  # Very important
            'personality_importance': 0.20,
            'eq_importance': 0.10,
            'work_style_importance': 0.15,
            'interest_importance': 0.10,
            # Specific ability requirements (0-100 scale)
            'required_cognitive': 75,
            'required_personality': 60,
            'required_eq': 55,
        },
        'business': {
            'cognitive_importance': 0.25,
            'personality_importance': 0.30,
            'eq_importance': 0.25,
            'work_style_importance': 0.10,
            'interest_importance': 0.10,
            'required_cognitive': 70,
            'required_personality': 75,
            'required_eq': 75,
        },
        'creative': {
            'cognitive_importance': 0.20,
            'personality_importance': 0.35,
            'eq_importance': 0.15,
            'work_style_importance': 0.20,
            'interest_importance': 0.10,
            'required_cognitive': 65,
            'required_personality': 80,
            'required_eq': 65,
        },
        'research': {
            'cognitive_importance': 0.50,
            'personality_importance': 0.25,
            'eq_importance': 0.05,
            'work_style_importance': 0.10,
            'interest_importance': 0.10,
            'required_cognitive': 85,
            'required_personality': 65,
            'required_eq': 50,
        },
        'healthcare': {
            'cognitive_importance': 0.25,
            'personality_importance': 0.25,
            'eq_importance': 0.35,
            'work_style_importance': 0.10,
            'interest_importance': 0.05,
            'required_cognitive': 70,
            'required_personality': 75,
            'required_eq': 85,
        },
        'general': {  # Default/fallback
            'cognitive_importance': 0.30,
            'personality_importance': 0.25,
            'eq_importance': 0.20,
            'work_style_importance': 0.15,
            'interest_importance': 0.10,
            'required_cognitive': 70,
            'required_personality': 70,
            'required_eq': 70,
        }
    }
    
    # Detect career type from career data
    detected_type = 'general'
    career_title = career_data.get('title', '').lower() if isinstance(career_data, dict) else ''
    career_category = career_data.get('category', '').lower() if isinstance(career_data, dict) else ''
    
    # Simple keyword matching for career type
    if any(word in career_title or word in career_category for word in ['engineer', 'developer', 'data', 'technical', 'software', 'programmer']):
        detected_type = 'technical'
    elif any(word in career_title or word in career_category for word in ['business', 'manager', 'consultant', 'analyst', 'executive', 'entrepreneur']):
        detected_type = 'business'
    elif any(word in career_title or word in career_category for word in ['designer', 'creative', 'artist', 'writer', 'content', 'media']):
        detected_type = 'creative'
    elif any(word in career_title or word in career_category for word in ['research', 'scientist', 'academic', 'scholar']):
        detected_type = 'research'
    elif any(word in career_title or word in career_category for word in ['healthcare', 'medical', 'nurse', 'doctor', 'therapist', 'health']):
        detected_type = 'healthcare'
    
    # Get weights for this career type
    weights = career_weights.get(detected_type, career_weights['general'])
    
    # Calculate match percentage for each ability (how well student meets requirements)
    cognitive_match = min(100, int((test_result.aptitude_score / weights['required_cognitive']) * 100))
    personality_match = min(100, int((test_result.personality_score / weights['required_personality']) * 100))
    eq_match = min(100, int((test_result.eq_score / weights['required_eq']) * 100))
    work_style_match = min(100, int((test_result.work_style_score / 100) * 100))  # Already 0-100
    interest_match = min(100, int((test_result.interest_score / 100) * 100))  # Already 0-100
    
    return {
        'cognitive': cognitive_match,
        'personality': personality_match,
        'emotional_intelligence': eq_match,
        'work_style': work_style_match,
        'interest_alignment': interest_match
    }


def format_ai_recommendations(ai_analysis: Dict[str, Any], test_result: TestResult) -> Dict[str, Any]:
    """
    Format AI analysis into the expected recommendation structure
    
    Args:
        ai_analysis: Raw AI analysis from OpenAI
        test_result: TestResult object
        
    Returns:
        Formatted recommendations dictionary compatible with templates
    """
    formatted = {}
    
    # Process top careers
    for i, career in enumerate(ai_analysis.get('top_careers', [])[:3]):
        category_key = f"ai_career_{i+1}"
        
        # Calculate career-specific ability matches
        ability_matches = calculate_ability_match_for_career(test_result, career)
        
        formatted[category_key] = {
            'description': career.get('title', 'Unknown Career'),
            'match_percentage': career.get('match_percentage', 0),
            'category': career.get('category', 'General'),
            'careers': [career.get('title', 'Unknown Career')],
            'future_outlook': career.get('reality_check', {}).get('daily_life', 'Career outlook not available'),
            'key_skills': ['Analyze your strengths', 'Develop required skills', 'Follow career roadmap'],
            'matching_traits': [],
            'abilities_breakdown': ability_matches,  # Use calculated matches
            'ai_insights': {
                'why_fits': career.get('why_this_fits', ''),
                'challenges': career.get('why_you_might_struggle', ''),
                'reality_check': career.get('reality_check', {}),
                'roadmap': career.get('roadmap', {})
            },
            'confidence_score': 85  # High confidence for AI recommendations
        }
    
    # Add alternate careers if available
    alternate_careers = ai_analysis.get('alternate_careers', [])
    if alternate_careers:
        # Calculate average match for alternates (less specific than main careers)
        # Use a balanced/general approach for alternates
        alternate_ability_matches = calculate_ability_match_for_career(
            test_result, 
            {'title': 'General Alternative', 'category': 'general'}, 
            career_type='general'
        )
        
        formatted['alternates'] = {
            'description': 'Alternative Career Paths',
            'match_percentage': 70,
            'careers': [alt.get('title', '') for alt in alternate_careers],
            'future_outlook': 'Explore these alternatives based on your profile',
            'key_skills': [],
            'matching_traits': [],
            'abilities_breakdown': alternate_ability_matches,  # Use calculated matches
            'confidence_score': 70
        }
    
    return formatted


def get_statistical_career_recommendations(test_result: TestResult) -> Dict[str, Any]:
    """
    Fallback statistical career matching (original algorithm)
    Used when AI analysis is unavailable
    
    Args:
        test_result: TestResult object
        
    Returns:
        Career recommendations using statistical matching
    """
    # Define career categories and their requirements (original logic)
    career_categories = {
        'technical': {
            'description': 'Technical and Engineering Roles',
            'careers': [
                'Software Engineer', 'Data Scientist', 'Systems Analyst', 
                'Network Engineer', 'DevOps Engineer', 'Cloud Architect'
            ],
            'requirements': {
                'numerical': 70,
                'abstract': 65,
                'verbal': 50
            },
            'trait_requirements': {
                'analytical': 70,
                'conscientiousness': 60,
                'openness': 60
            },
            'test_weights': {
                'aptitude': 0.4,
                'personality': 0.25,
                'eq': 0.15,
                'interest': 0.1,
                'work_style': 0.1
            },
            'future_outlook': 'High demand with 22% growth projected over the next decade',
            'key_skills': ['Problem-solving', 'Analytical thinking', 'Technical expertise']
        },
        'business': {
            'description': 'Business and Management Roles',
            'careers': [
                'Business Analyst', 'Project Manager', 'Marketing Specialist', 
                'Financial Analyst', 'Management Consultant', 'Operations Manager'
            ],
            'requirements': {
                'numerical': 65,
                'verbal': 70,
                'abstract': 55
            },
            'trait_requirements': {
                'leadership': 70,
                'communication': 75,
                'extraversion': 60
            },
            'test_weights': {
                'aptitude': 0.25,
                'personality': 0.3,
                'eq': 0.2,
                'interest': 0.1,
                'work_style': 0.15
            },
            'future_outlook': 'Stable growth with 15% increase in positions expected',
            'key_skills': ['Leadership', 'Communication', 'Strategic thinking']
        },
        'creative': {
            'description': 'Creative and Design Roles',
            'careers': [
                'UX Designer', 'Content Creator', 'Graphic Designer', 
                'Product Designer', 'UI Developer', 'Creative Director'
            ],
            'requirements': {
                'abstract': 75,
                'verbal': 60,
                'numerical': 45
            },
            'trait_requirements': {
                'creativity': 80,
                'openness': 75,
                'adaptability': 65
            },
            'test_weights': {
                'aptitude': 0.2,
                'personality': 0.35,
                'eq': 0.15,
                'interest': 0.15,
                'work_style': 0.15
            },
            'future_outlook': 'Growing field with 18% increase in demand',
            'key_skills': ['Visual thinking', 'Innovation', 'User empathy']
        },
        'research': {
            'description': 'Research and Analysis Roles',
            'careers': [
                'Research Scientist', 'Market Researcher', 'Policy Analyst', 
                'Academic Researcher', 'Data Analyst', 'Biomedical Researcher'
            ],
            'requirements': {
                'numerical': 70,
                'verbal': 75,
                'abstract': 70
            },
            'trait_requirements': {
                'analytical': 80,
                'conscientiousness': 70,
                'openness': 65
            },
            'test_weights': {
                'aptitude': 0.45,
                'personality': 0.25,
                'eq': 0.1,
                'interest': 0.1,
                'work_style': 0.1
            },
            'future_outlook': 'Expanding field with 20% growth in specialized areas',
            'key_skills': ['Critical thinking', 'Attention to detail', 'Methodical approach']
        },
        'healthcare': {
            'description': 'Healthcare and Wellness Roles',
            'careers': [
                'Healthcare Administrator', 'Clinical Psychologist', 'Health Informatics Specialist',
                'Medical Researcher', 'Wellness Coordinator', 'Rehabilitation Specialist'
            ],
            'requirements': {
                'numerical': 60,
                'verbal': 80,
                'abstract': 65
            },
            'trait_requirements': {
                'agreeableness': 75,
                'communication': 70,
                'conscientiousness': 70
            },
            'test_weights': {
                'aptitude': 0.2,
                'personality': 0.3,
                'eq': 0.3,
                'interest': 0.1,
                'work_style': 0.1
            },
            'future_outlook': 'Rapidly growing sector with 25% projected increase',
            'key_skills': ['Empathy', 'Communication', 'Analytical thinking']
        }
    }
    
    # Calculate match scores
    matches = {}
    for category, data in career_categories.items():
        # Aptitude matching
        numerical_match = min(100, (test_result.numerical_score / data['requirements']['numerical']) * 100)
        verbal_match = min(100, (test_result.verbal_score / data['requirements']['verbal']) * 100)
        abstract_match = min(100, (test_result.abstract_score / data['requirements']['abstract']) * 100)
        cognitive_avg = (numerical_match + verbal_match + abstract_match) / 3
        
        # Trait matching (simplified from original)
        trait_scores = []
        for trait, required in data['trait_requirements'].items():
            actual = getattr(test_result, f"{trait}_score", 60)
            trait_match = min(100, (actual / required) * 100)
            trait_scores.append(trait_match)
        
        trait_avg = sum(trait_scores) / len(trait_scores) if trait_scores else 70
        
        # Weighted final score
        weights = data['test_weights']
        overall_match = (
            cognitive_avg * weights['aptitude'] +
            trait_avg * weights['personality'] +
            (test_result.eq_score / 100 * 100) * weights['eq'] +
            (test_result.interest_score / 100 * 100) * weights['interest'] +
            (test_result.work_style_score / 100 * 100) * weights['work_style']
        )
        
        matches[category] = {
            'description': data['description'],
            'match_percentage': round(overall_match, 1),
            'careers': data['careers'],
            'future_outlook': data['future_outlook'],
            'key_skills': data['key_skills'],
            'matching_traits': [],
            'abilities_breakdown': {
                'cognitive': round(cognitive_avg, 1),
                'personality': round(trait_avg, 1),
                'emotional_intelligence': round(test_result.eq_score, 1),
                'work_style': round(test_result.work_style_score, 1),
                'interest_alignment': round(test_result.interest_score, 1)
            },
            'confidence_score': 60  # Lower confidence for statistical matching
        }
    
    # Sort by match percentage
    sorted_matches = dict(sorted(matches.items(), key=lambda item: item[1]['match_percentage'], reverse=True))
    
    return sorted_matches


def get_skill_development_recommendations(test_result_id: int) -> List[Dict[str, Any]]:
    """
    Generate AI-powered skill development recommendations with fallback
    
    Args:
        test_result_id: ID of the test result
        
    Returns:
        List of skill development recommendations
    """
    test_result = TestResult.query.get_or_404(test_result_id)
    
    # Identify weak areas (scores below 60)
    weak_areas = []
    
    if test_result.verbal_score < 60:
        weak_areas.append("verbal reasoning")
    if test_result.numerical_score < 60:
        weak_areas.append("numerical reasoning")
    if test_result.abstract_score < 60:
        weak_areas.append("abstract reasoning")
    if test_result.openness_score < 60:
        weak_areas.append("openness to experience")
    if test_result.conscientiousness_score < 60:
        weak_areas.append("conscientiousness")
    if test_result.extraversion_score < 60:
        weak_areas.append("extraversion")
    if test_result.leadership_score < 60:
        weak_areas.append("leadership")
    if test_result.communication_score < 60:
        weak_areas.append("communication")
    if test_result.creativity_score < 60:
        weak_areas.append("creativity")
    
    # If no weak areas, focus on top strengths
    if not weak_areas:
        weak_areas = ["career readiness", "skill enhancement"]
    
    # Try AI-powered suggestions
    try:
        student_context = {
            "confidence_level": test_result.confidence_level or "MODERATE",
            "top_scores": {
                "best_cognitive": max(test_result.verbal_score, test_result.numerical_score, test_result.abstract_score),
                "eq_level": test_result.eq_score,
                "personality_standout": max(
                    test_result.openness_score, 
                    test_result.conscientiousness_score,
                    test_result.extraversion_score
                )
            }
        }
        
        ai_suggestions = generate_skill_suggestions(weak_areas, student_context)
        
        if ai_suggestions and 'priority_areas' in ai_suggestions:
            logger.info(f"AI skill suggestions generated for test_result {test_result_id}")
            return ai_suggestions['priority_areas']
    
    except Exception as e:
        logger.error(f"AI skill suggestions failed: {str(e)}, falling back to static recommendations")
    
    # Fallback to static recommendations
    return get_static_skill_recommendations(weak_areas)


def get_static_skill_recommendations(weak_areas: List[str]) -> List[Dict[str, Any]]:
    """
    Fallback static skill recommendations
    
    Args:
        weak_areas: List of identified weak areas
        
    Returns:
        List of skill development recommendations
    """
    recommendations_map = {
        'verbal reasoning': {
            'area': 'Verbal Reasoning',
            'description': 'Enhance your verbal reasoning skills to improve comprehension and communication.',
            'activities': [
                'Read diverse materials such as academic journals, news articles, and literature',
                'Practice summarizing complex texts in your own words',
                'Join a debate club or public speaking group',
                'Take courses in critical reading and writing'
            ]
        },
        'numerical reasoning': {
            'area': 'Numerical Reasoning',
            'description': 'Strengthen your numerical reasoning abilities to better analyze and interpret data.',
            'activities': [
                'Practice solving mathematical problems daily',
                'Take online courses in statistics and data analysis',
                'Use math-focused apps and games',
                'Apply numerical concepts to real-world scenarios'
            ]
        },
        'abstract reasoning': {
            'area': 'Abstract Reasoning',
            'description': 'Develop your abstract reasoning skills to improve pattern recognition and problem-solving.',
            'activities': [
                'Solve puzzles, riddles, and brain teasers regularly',
                'Practice identifying patterns in sequences and diagrams',
                'Learn to play strategic games like chess',
                'Study logic and critical thinking techniques'
            ]
        },
        'leadership': {
            'area': 'Leadership Skills',
            'description': 'Develop leadership capabilities to guide and inspire others.',
            'activities': [
                'Take on leadership roles in group projects',
                'Read books on leadership and management',
                'Attend leadership workshops and seminars',
                'Practice delegation and team coordination'
            ]
        },
        'communication': {
            'area': 'Communication Skills',
            'description': 'Improve your ability to express ideas clearly and effectively.',
            'activities': [
                'Join Toastmasters or similar public speaking groups',
                'Practice active listening in conversations',
                'Write regularly - blogs, journals, or articles',
                'Take courses in effective communication'
            ]
        }
    }
    
    recommendations = []
    for area in weak_areas[:3]:  # Top 3 priority areas
        if area in recommendations_map:
            recommendations.append(recommendations_map[area])
    
    # If no matches, provide generic recommendations
    if not recommendations:
        recommendations.append({
            'area': 'Overall Skill Development',
            'description': 'Continue developing your abilities across multiple dimensions.',
            'activities': [
                'Set specific, measurable goals for personal growth',
                'Seek feedback from mentors and peers regularly',
                'Take online courses in areas of interest',
                'Practice self-reflection and track your progress'
            ]
        })
    
    return recommendations
