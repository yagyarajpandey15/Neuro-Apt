"""
OpenAI API Integration for NeurApt
Replaces Gemini API with OpenAI GPT-4o and GPT-4o-mini
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from flask import current_app

# Use centralized logging configuration
from neuroapt.app.utils.logging_config import get_ai_logger, log_ai_error as log_error_detailed

logger = get_ai_logger(__name__)

# Initialize OpenAI client (will be configured from Flask app context)
client = None

def init_openai_client():
    """Initialize OpenAI client with API key from config"""
    global client
    try:
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY not found in configuration")
            return False
        client = OpenAI(api_key=api_key)
        logger.info("OpenAI client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        return False

def get_openai_client():
    """Get or initialize OpenAI client"""
    global client
    if client is None:
        init_openai_client()
    return client

def call_gpt4o(system_prompt: str, user_prompt: str, response_format: str = "json_object") -> Optional[Dict[str, Any]]:
    """
    Call GPT-4o for complex reasoning tasks
    
    Args:
        system_prompt: System instructions for the model
        user_prompt: User query/data
        response_format: "json_object" for structured JSON, "text" for plain text
        
    Returns:
        Parsed JSON response or None if failed
    """
    try:
        client = get_openai_client()
        if not client:
            logger.error("OpenAI client not initialized")
            return None
            
        model = current_app.config.get('OPENAI_MODEL_PRIMARY', 'gpt-4o')
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        if response_format == "json_object":
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4000
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )
        
        content = response.choices[0].message.content
        
        if response_format == "json_object":
            return json.loads(content)
        return {"text": content}
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in GPT-4o response: {str(e)}")
        logger.error(f"Raw response: {content if 'content' in locals() else 'No response'}")
        return None
    except Exception as e:
        logger.error(f"Error calling GPT-4o: {str(e)}")
        # Log to error file
        log_openai_error("gpt4o", str(e), system_prompt[:100])
        return None

def call_gpt4o_mini(system_prompt: str, user_prompt: str, response_format: str = "json_object") -> Optional[Dict[str, Any]]:
    """
    Call GPT-4o-mini for faster, cheaper tasks
    
    Args:
        system_prompt: System instructions for the model
        user_prompt: User query/data
        response_format: "json_object" for structured JSON, "text" for plain text
        
    Returns:
        Parsed JSON response or None if failed
    """
    try:
        client = get_openai_client()
        if not client:
            logger.error("OpenAI client not initialized")
            return None
            
        model = current_app.config.get('OPENAI_MODEL_FAST', 'gpt-4o-mini')
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        if response_format == "json_object":
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
        
        content = response.choices[0].message.content
        
        if response_format == "json_object":
            return json.loads(content)
        return {"text": content}
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in GPT-4o-mini response: {str(e)}")
        logger.error(f"Raw response: {content if 'content' in locals() else 'No response'}")
        return None
    except Exception as e:
        logger.error(f"Error calling GPT-4o-mini: {str(e)}")
        # Log to error file
        log_openai_error("gpt4o-mini", str(e), system_prompt[:100])
        return None

def log_openai_error(model: str, error: str, context: str):
    """
    Log OpenAI errors to file using centralized logging.
    
    DEPRECATED: Use log_error_detailed from logging_config instead.
    This function is maintained for backward compatibility.
    """
    log_error_detailed(
        component="OpenAI API",
        operation=f"call_{model}",
        error_type="API Error",
        error_message=error,
        details=context,
        fallback_triggered=False
    )

# ============================================================================
# SPECIFIC API FUNCTIONS
# ============================================================================

def generate_ai_career_analysis(student_profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate comprehensive AI-powered career analysis using GPT-4o.
    
    This is the main result generation function that uses GPT-4o for complex reasoning
    to analyze student psychometric profiles and generate personalized career recommendations.
    
    Enhanced features:
    - Comprehensive system prompt with detailed instructions
    - Career matching with 3-5 top careers and 2-4 alternatives
    - Ability breakdown calculation guidance (cognitive, personality, EQ, work style, interest)
    - Personalized fit explanations referencing specific scores
    - Challenge identification based on lower-scoring traits
    - Reality check generation (daily_life, work_environment, stress_factors, work_life_balance)
    - Career roadmap generation with timeframes (1-month, 3-6 months, 6-12 months)
    - Interest intersection handling and alternative career discovery
    - Retry logic with exponential backoff (2 attempts, 1s, 2s intervals)
    
    Args:
        student_profile: Complete psychometric profile dictionary with structure:
            {
                'user_id': int,
                'test_id': int,
                'cognitive_abilities': {
                    'verbal': int, 'numerical': int, 'abstract': int, 'overall_aptitude': int
                },
                'personality_traits': {
                    'openness': int, 'conscientiousness': int, 'extraversion': int,
                    'agreeableness': int, 'neuroticism': int
                },
                'work_attributes': {
                    'leadership': int, 'teamwork': int, 'creativity': int,
                    'analytical': int, 'communication': int, 'adaptability': int
                },
                'interest_domains': {
                    'stem_tech': int, 'creative_media': int, 'people_oriented': int,
                    'business_management': int, 'legal_governance': int, 'logistics_distribution': int
                },
                'emotional_intelligence': int,
                'metadata': {
                    'test_date': str, 'pattern_classification': str,
                    'contradictions': List[Dict], 'consistency_score': float,
                    'interest_intersection': str
                }
            }
        
    Returns:
        Comprehensive career analysis JSON with structure:
        {
            'top_careers': List[CareerMatch],  # 3-5 careers
            'alternate_careers': List[AlternateCareer],  # 2-4 careers
            'confidence_analysis': ConfidenceData,
            'personality_summary': str,
            'unique_strengths': List[str],
            'growth_areas': List[str],
            'emotional_readiness': EmotionalData,
            'contradiction_analysis': str,
            'parent_report': ParentReportData
        }
        Or None if generation fails after retries
        
    Validates Requirements: 2.1, 2.2, 2.3, 2.4, 2.6, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6,
                           5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 6.4, 6.5,
                           7.1, 7.2, 7.3, 7.4, 7.5, 12.5
    """
    # Build comprehensive system prompt with detailed guidance
    system_prompt = """You are an expert psychometric career counsellor with 20 years of experience guiding students in India. You deeply understand the Indian education system, entrance exams, college landscape, and job market.

CORE RESPONSIBILITIES:
1. Analyze the student's complete psychometric profile across ALL dimensions (cognitive, personality, work style, interests, EQ)
2. Generate 3-5 primary career recommendations ranked by comprehensive fit percentage
3. Generate 2-4 alternative career recommendations that leverage non-obvious skill combinations
4. Provide detailed ability breakdowns for each career showing match across all dimensions
5. Create personalized, actionable career roadmaps with specific timeframes
6. Provide realistic daily life descriptions and challenge assessments

CRITICAL ANALYSIS GUIDELINES:

**Career Matching:**
- Match careers based on multi-dimensional analysis, not just interest scores
- Calculate match percentage considering: cognitive abilities (weighted by career requirements), personality alignment, EQ fit, work style compatibility, interest alignment
- For technical careers: weight cognitive 45%, personality 20%, EQ 10%, work style 15%, interest 10%
- For creative careers: weight cognitive 15%, personality 35%, EQ 15%, work style 25%, interest 10%
- For people-oriented careers: weight cognitive 20%, personality 25%, EQ 35%, work style 10%, interest 10%
- For business careers: weight cognitive 30%, personality 25%, EQ 20%, work style 15%, interest 10%

**Ability Breakdown:**
For each career, calculate match percentages for each dimension:
- cognitive_match: (student_score / career_requirement) * 100, capped at 100%
- personality_match: alignment of Big Five traits with career requirements
- emotional_intelligence_match: EQ score relative to career needs
- work_style_match: leadership, teamwork, creativity, analytical, communication, adaptability alignment
- interest_alignment: interest domain score relative to career category

**Personalized Fit Explanations:**
- Reference SPECIFIC scores from the profile (e.g., "Your high verbal score of 85/100 combined with strong communication score of 82/100...")
- Identify synergies between dimensions (e.g., "high analytical + high creativity + moderate teamwork suggests...")
- Highlight tensions between dimensions (e.g., "While your interests favor creative fields, your personality traits suggest...")

**Challenge Identification:**
- Base challenges on lower-scoring traits (scores below 60/100 are significant gaps)
- Be honest but constructive (e.g., "Your moderate teamwork score of 55/100 may require intentional development...")
- Frame gaps as growth areas, not disqualifiers for careers with 50-70% match in that dimension

**Reality Check Generation:**
Must include for each top career:
- daily_life: Typical daily tasks and work rhythm (2-3 sentences)
- work_environment: Physical/social setting characteristics
- stress_factors: Common sources of stress in this career
- work_life_balance: Typical work hours and lifestyle implications
- competition_level: Low/Medium/High/Very High for Indian job market

**Career Roadmap:**
Create actionable roadmaps with THREE required timeframes:
- immediate_1_month: 3-4 immediate actions they can start now
- short_term_3_6_months: Skills to develop, courses to take, experiences to gain
- medium_term_6_12_months: Preparation for exams/applications, portfolio building, networking
Include specific resources: courses, certifications, entrance exams relevant to India

**Interest Intersection Handling:**
If student has interest_intersection (e.g., "STEM+Creative", "Business+People-Oriented"):
- Actively search for hybrid careers that leverage both domains
- Include these as primary or alternate recommendations
- Explain how the combination creates unique opportunities

**Alternative Career Discovery:**
Generate 2-4 alternatives that are:
- Outside the student's top interest category BUT match personality-aptitude combinations
- Leverage transferable skill combinations
- Have confidence ≥50% (only include strong alternatives, not weak suggestions)
- Include rationale explaining the non-obvious fit

**Contradiction Analysis:**
If contradictions are detected in metadata:
- Explain what the contradictions mean (e.g., "You showed inconsistency between questions about teamwork preference...")
- Note if this affects confidence in recommendations
- Suggest areas for self-reflection

RESPONSE FORMAT:
Always respond in valid JSON only. No explanation outside JSON. Be honest about career difficulty and competition. Be encouraging but realistic. Every insight must directly reference specific scores from the profile."""

    # Format student profile data for AI consumption
    # Extract key metadata for easier reference in prompt
    pattern_classification = student_profile.get('metadata', {}).get('pattern_classification', 'unknown')
    consistency_score = student_profile.get('metadata', {}).get('consistency_score', 0)
    contradictions = student_profile.get('metadata', {}).get('contradictions', [])
    interest_intersection = student_profile.get('metadata', {}).get('interest_intersection', '')
    
    # Build user prompt with structured profile data
    user_prompt = f"""Analyze this student's complete psychometric profile and provide comprehensive career guidance.

STUDENT PROFILE DATA:
{json.dumps(student_profile, indent=2)}

KEY OBSERVATIONS:
- Pattern Classification: {pattern_classification}
- Response Consistency: {consistency_score:.1f}/100
- Contradictions Detected: {len(contradictions)}
- Interest Intersection: {interest_intersection if interest_intersection else 'None detected'}

REQUIRED JSON RESPONSE STRUCTURE:
{{
    "top_careers": [
        {{
            "title": "<career title>",
            "match_percentage": <0-100>,
            "category": "<career category>",
            "why_this_fits": "<2-3 sentences referencing SPECIFIC scores and trait combinations>",
            "why_you_might_struggle": "<honest challenges based on lower-scoring traits with specific scores>",
            "ability_breakdown": {{
                "cognitive_match": <0-100>,
                "personality_match": <0-100>,
                "emotional_intelligence_match": <0-100>,
                "work_style_match": <0-100>,
                "interest_alignment": <0-100>
            }},
            "matching_traits": ["<top matching trait 1>", "<top matching trait 2>", "<top matching trait 3>"],
            "reality_check": {{
                "daily_life": "<2-3 sentences describing typical daily tasks>",
                "work_environment": "<office/remote/field/lab/etc with details>",
                "stress_factors": "<common stress sources in this career>",
                "work_life_balance": "<typical hours and lifestyle>",
                "competition_level": "<Low|Medium|High|Very High>"
            }},
            "roadmap": {{
                "immediate_1_month": ["<action 1>", "<action 2>", "<action 3>"],
                "short_term_3_6_months": ["<skill/course 1>", "<skill/course 2>", "<experience to gain>"],
                "medium_term_6_12_months": ["<exam prep>", "<portfolio building>", "<networking/applications>"],
                "skill_development": ["<specific skill 1>", "<specific skill 2>"],
                "resources": ["<specific course/certification>", "<specific resource>"]
            }},
            "confidence_score": <0-100>
        }}
    ],
    "alternate_careers": [
        {{
            "title": "<career outside top interest category>",
            "match_percentage": <50-100>,
            "category": "<career category>",
            "why_this_fits": "<rationale for non-obvious fit>",
            "one_line_reason": "<brief explanation>",
            "confidence_score": <50-100>
        }}
    ],
    "confidence_analysis": {{
        "overall_confidence": <0-100>,
        "factors": {{
            "consistency_contribution": <points from consistency>,
            "contradiction_penalty": <negative points from contradictions>,
            "completion_bonus": <bonus points>
        }},
        "explanation": "<what the confidence score means for this student>"
    }},
    "personality_summary": "<3-4 sentences about who this student is based on Big Five and work attributes>",
    "unique_strengths": ["<strength 1 with score>", "<strength 2 with score>", "<strength 3 with score>"],
    "growth_areas": ["<area 1 with score>", "<area 2 with score>"],
    "emotional_readiness": {{
        "summary": "<how emotionally prepared for career challenges>",
        "stress_tolerance": "<Low|Medium|High based on neuroticism score>",
        "leadership_potential": "<Low|Medium|High based on leadership score>",
        "teamwork_fit": "<Independent|Mixed|Team-oriented based on teamwork score>"
    }},
    "contradiction_analysis": "<if contradictions detected, explain what they mean; otherwise state 'No significant contradictions detected'>",
    "parent_report": {{
        "summary": "<simple 3-4 sentences for parents, no jargon>",
        "what_child_is_good_at": ["<observable strength 1>", "<observable strength 2>"],
        "recommended_support": ["<how parents can help 1>", "<how parents can help 2>"],
        "careers_to_discuss": ["<top 3 careers in simple language>"]
    }}
}}

REQUIREMENTS:
- Provide exactly 3-5 top_careers (ranked by match_percentage descending)
- Provide exactly 2-4 alternate_careers (only include if confidence_score ≥ 50)
- All match_percentages must be 0-100
- Reference specific scores in explanations
- Base challenges on scores below 60/100
- Include all three roadmap timeframes for each top career
- Ensure reality_check includes all required fields
"""

    # Implement retry logic with exponential backoff
    max_retries = 2
    retry_delays = [1.0, 2.0]  # 1s, 2s intervals
    
    for attempt in range(max_retries + 1):
        try:
            result = call_gpt4o(system_prompt, user_prompt, "json_object")
            
            if result is not None:
                # Success - return result
                return result
            
            # If result is None and we have retries left, log and retry
            if attempt < max_retries:
                logger.warning(f"AI career analysis attempt {attempt + 1} returned None, retrying in {retry_delays[attempt]}s...")
                import time
                time.sleep(retry_delays[attempt])
            
        except Exception as e:
            error_message = str(e)
            
            # Determine if this is a transient error that should be retried
            transient_errors = ['timeout', 'rate limit', 'service unavailable', 'connection', 'temporary']
            is_transient = any(err_type in error_message.lower() for err_type in transient_errors)
            
            if is_transient and attempt < max_retries:
                # Transient error - retry with backoff
                logger.warning(f"Transient error on attempt {attempt + 1}: {error_message}. Retrying in {retry_delays[attempt]}s...")
                
                # Log the retry attempt
                log_error_detailed(
                    component="AI Career Analyzer",
                    operation="generate_ai_career_analysis",
                    error_type=f"Transient Error (Attempt {attempt + 1})",
                    error_message=error_message,
                    details=f"Retrying after {retry_delays[attempt]}s delay",
                    fallback_triggered=False
                )
                
                import time
                time.sleep(retry_delays[attempt])
                continue
            else:
                # Permanent error or retries exhausted - log and return None
                logger.error(f"AI career analysis failed on attempt {attempt + 1}: {error_message}")
                
                log_error_detailed(
                    component="AI Career Analyzer",
                    operation="generate_ai_career_analysis",
                    error_type="API Error" if not is_transient else "Exhausted Retries",
                    error_message=error_message,
                    details=f"Failed after {attempt + 1} attempts",
                    fallback_triggered=True
                )
                
                return None
    
    # All retries exhausted
    logger.error("AI career analysis failed after all retry attempts")
    return None

def explore_alternate_career(student_profile: Dict[str, Any], target_career: str) -> Optional[Dict[str, Any]]:
    """
    Explore student's fit for a specific alternate career using GPT-4o-mini
    
    Args:
        student_profile: Student's psychometric profile
        target_career: Career to analyze
        
    Returns:
        Career fit analysis JSON or None if failed
    """
    system_prompt = """You are a career counsellor analyzing a student's fit for a specific career path they're interested in."""
    
    user_prompt = f"""Given this student's psychometric profile, analyse their fit for {target_career} even though it wasn't their top match.

Student Profile:
{json.dumps(student_profile, indent=2)}

Return JSON:
{{
    "fit_score": <0-100>,
    "what_aligns": ["<traits that match>"],
    "what_doesnt_align": ["<gaps>"],
    "gap_analysis": "<what they would need to develop>",
    "is_achievable": <true or false>,
    "honest_assessment": "<2-3 sentences being completely honest>",
    "if_they_pursue_it": {{
        "timeline": "<realistic timeline>",
        "hardest_part": "<biggest challenge for this student>",
        "advantage_they_have": "<genuine strength they bring>"
    }}
}}"""

    return call_gpt4o_mini(system_prompt, user_prompt, "json_object")

def generate_skill_suggestions(weak_areas: List[str], student_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate personalized skill development suggestions using GPT-4o-mini
    
    Args:
        weak_areas: List of areas needing improvement
        student_context: Basic student info and learning style
        
    Returns:
        Skill development plan JSON or None if failed
    """
    system_prompt = """You are a learning coach creating personalized skill development plans for students."""
    
    user_prompt = f"""Create specific, actionable skill development suggestions for these weak areas:

Weak Areas: {', '.join(weak_areas)}

Student Context:
{json.dumps(student_context, indent=2)}

Return JSON:
{{
    "priority_areas": [
        {{
            "area": "<skill area>",
            "why_important": "<brief explanation>",
            "activities": ["<activity 1>", "<activity 2>", "<activity 3>"],
            "timeline": "<realistic timeframe>",
            "resources": ["<resource 1>", "<resource 2>"]
        }}
    ],
    "quick_wins": ["<easy actions they can do today>"],
    "encouragement": "<motivational message specific to their situation>"
}}"""

    return call_gpt4o_mini(system_prompt, user_prompt, "json_object")

def analyze_micro_assessment(questions_answers: List[Dict], career_a: str, career_b: str) -> Optional[Dict[str, Any]]:
    """
    Analyze micro assessment results using GPT-4o-mini
    
    Args:
        questions_answers: List of Q&A pairs
        career_a: First career option
        career_b: Second career option
        
    Returns:
        Career comparison analysis JSON or None if failed
    """
    system_prompt = """You are a career counsellor analyzing focused career comparison assessments."""
    
    user_prompt = f"""Based on these 10 focused answers comparing {career_a} vs {career_b}, determine which is the stronger fit and why.

Questions and Answers:
{json.dumps(questions_answers, indent=2)}

Return JSON:
{{
    "recommended": "<{career_a} or {career_b}>",
    "confidence": <percentage 0-100>,
    "key_reason": "<the single most important deciding factor>",
    "detailed_reasoning": "<3-4 sentences>",
    "surprising_insight": "<something they might not have considered>"
}}"""

    return call_gpt4o_mini(system_prompt, user_prompt, "json_object")

def map_subjects_to_careers(subjects: List[str], profile_summary: str) -> Optional[Dict[str, Any]]:
    """
    Map student's strongest subjects to career paths using GPT-4o-mini
    
    Args:
        subjects: List of favorite/strongest subjects
        profile_summary: Brief psychometric profile summary
        
    Returns:
        Subject-career mapping JSON or None if failed
    """
    system_prompt = """You are a career counsellor mapping academic subjects to career paths in the Indian education context."""
    
    user_prompt = f"""A student's favourite/strongest subjects are: {', '.join(subjects)}

Their psychometric profile summary: {profile_summary}

Map these subjects to specific career paths and return JSON:
{{
    "primary_careers": [
        {{
            "career": "<title>",
            "subject_connection": "<which subjects lead here and how>",
            "match_strength": "<Strong|Medium|Exploratory>"
        }}
    ],
    "hidden_careers": [
        {{
            "career": "<unexpected but valid option>",
            "why_surprising": "<explain the non-obvious connection>"
        }}
    ],
    "subject_combination_insight": "<what this combination of subjects says about the student>"
}}"""

    return call_gpt4o_mini(system_prompt, user_prompt, "json_object")

def generate_growth_analysis(user_id: int, results_history: List[Dict]) -> Optional[Dict[str, Any]]:
    """
    Analyze student growth across multiple test attempts using GPT-4o
    
    Args:
        user_id: User ID
        results_history: List of past test results with scores
        
    Returns:
        Growth analysis JSON or None if failed
    """
    system_prompt = """You are a developmental psychologist analyzing a student's growth and changes over time through repeated psychometric assessments."""
    
    user_prompt = f"""This student has taken the assessment {len(results_history)} times.

Score history (chronological order):
{json.dumps(results_history, indent=2)}

Analyse their growth and return JSON:
{{
    "growth_summary": "<what has genuinely changed>",
    "improving_areas": ["<areas with positive trend>"],
    "stagnant_areas": ["<areas with no change>"],
    "personality_evolution": "<how their profile has shifted>",
    "recommendation_change": "<should their career recommendation change based on growth>",
    "encouragement": "<genuine, specific encouragement>",
    "next_steps": ["<what to focus on next based on trajectory>"]
}}"""

    return call_gpt4o(system_prompt, user_prompt, "json_object")


def get_career_insights(career_query: str) -> Optional[str]:
    """
    Get AI-powered career insights for general career questions using GPT-4o-mini
    
    Args:
        career_query: User's question about careers
        
    Returns:
        Plain text career insights (not JSON) or None if failed
    """
    system_prompt = """You are an expert career counselor in India with deep knowledge of:
- Indian education system and career paths
- Entrance exams (JEE, NEET, CLAT, CAT, UPSC, etc.)
- College admissions and top institutions
- Job market trends in India
- Salary ranges and career growth in Indian context

Provide clear, actionable, honest advice. Reference specific Indian colleges, exams, and salary ranges (in LPA).
Be encouraging but realistic. Format your response in clean, readable paragraphs with proper line breaks."""

    user_prompt = f"""Question: {career_query}

Provide a comprehensive answer covering:
- Direct answer to their question
- Relevant education paths in India
- Entrance exams if applicable
- Top colleges/institutions
- Career prospects and salary ranges (LPA)
- Realistic timeline
- Honest pros and cons

Keep it conversational and helpful. Use 3-5 paragraphs. Use line breaks between paragraphs for readability."""

    result = call_gpt4o_mini(system_prompt, user_prompt, "text")
    
    if result and 'text' in result:
        return result['text']
    return None

