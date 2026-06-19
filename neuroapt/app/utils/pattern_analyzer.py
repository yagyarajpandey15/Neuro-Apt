"""
Pattern Analyzer Module

This module analyzes student response patterns across test sections to detect
behavioral authenticity and consistency. It detects contradictions in related
question pairs and classifies answer patterns as decisive, ambivalent, or random.

Requirements: 1.1, 1.2, 1.3
"""

from typing import Dict, Any, List, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# RELATED QUESTION PAIR MAPPINGS
# ============================================================================
# These mappings define trait-based relationships for detecting contradictions.
# Instead of hardcoding question IDs (which vary by database), we identify
# related questions by their trait_impact patterns.
#
# Structure: category -> list of trait relationship rules
# Each rule is: (trait_1, trait_2, relationship_type, threshold)
# ============================================================================

TRAIT_RELATIONSHIP_RULES = {
    'personality': [
        # Extraversion vs Introversion (opposite traits)
        ('extraversion', 'introversion', 'opposite', 7),
        # Thinking vs Feeling (opposite decision-making styles)
        ('thinking', 'feeling', 'opposite', 7),
        # Conscientiousness consistency (similar questions should align)
        ('conscientiousness', 'conscientiousness', 'similar', 5),
        # Openness consistency
        ('openness', 'openness', 'similar', 5),
        # Agreeableness consistency
        ('agreeableness', 'agreeableness', 'similar', 5),
        # Neuroticism consistency (stress responses)
        ('neuroticism', 'neuroticism', 'similar', 5),
    ],
    'interest': [
        # STEM vs Creative interests (can coexist but need checking)
        ('stem_tech', 'creative_media', 'independent', 0),
        # People-oriented consistency
        ('people_oriented', 'people_oriented', 'similar', 5),
        # Business/Management consistency
        ('business_management', 'business_management', 'similar', 5),
        # STEM consistency
        ('stem_tech', 'stem_tech', 'similar', 5),
        # Creative consistency
        ('creative_media', 'creative_media', 'similar', 5),
    ],
    'aptitude': [
        # Logical reasoning dependency (advanced requires basic)
        ('logical_reasoning', 'basic_logic', 'dependency', 3),
        # Math skills dependency
        ('advanced_math', 'basic_math', 'dependency', 3),
        # Verbal ability consistency
        ('verbal', 'verbal', 'similar', 5),
        # Numerical ability consistency
        ('numerical', 'numerical', 'similar', 5),
        # Abstract reasoning consistency
        ('abstract', 'abstract', 'similar', 5),
    ],
    'work_style': [
        # Leadership vs Support roles (can be opposite)
        ('assertiveness', 'agreeableness', 'tension', 7),
        # Independent work vs Team collaboration
        ('introversion', 'agreeableness', 'tension', 7),
        # Structure vs Flexibility
        ('conscientiousness', 'perceiving', 'opposite', 7),
    ]
}

# Legacy structure maintained for backward compatibility
# This will be dynamically populated based on actual questions in the database
RELATED_QUESTION_PAIRS = {
    'personality': [],
    'interest': [],
    'aptitude': [],
    'work_style': []
}

# Define psychological pattern violations
# These represent known incompatible trait combinations
PSYCHOLOGICAL_PATTERNS = {
    'teamwork_solo_conflict': {
        'high_teamwork_threshold': 70,
        'high_solo_threshold': 70,
        'description': 'Claims both high teamwork preference and strong solo work preference'
    },
    'leadership_following_conflict': {
        'high_leadership_threshold': 70,
        'high_following_threshold': 70,
        'description': 'Claims both strong leadership preference and preference for following'
    }
}


# ============================================================================
# CORE PATTERN ANALYSIS FUNCTIONS
# ============================================================================

def analyze_answer_patterns(test_result) -> Dict[str, Any]:
    """
    Analyze response patterns across test sections.
    
    This function examines a completed test result to identify patterns in how
    the student answered questions, including consistency, contradictions, and
    cross-section alignment.
    
    Args:
        test_result: TestResult object with completed answers
        
    Returns:
        Dictionary containing:
            - pattern_classification: 'decisive' | 'ambivalent' | 'random'
            - consistency_score: float (0-100)
            - contradictions: List[Dict] of detected contradictions
            - cross_section_alignment: Dict[str, float] alignment scores by section
            
    Validates: Requirements 1.1, 1.2, 1.3
    """
    logger.info(f"Analyzing answer patterns for test result {test_result.id}")
    
    # Get all user answers with related questions
    answers = test_result.answers
    
    if not answers or len(answers) == 0:
        logger.warning(f"No answers found for test result {test_result.id}")
        return {
            'pattern_classification': 'ambivalent',
            'consistency_score': 50.0,
            'contradictions': [],
            'cross_section_alignment': {}
        }
    
    # Detect contradictions in related question pairs
    contradictions = detect_contradictions(answers, [answer.question for answer in answers])
    
    # Calculate consistency score based on response patterns
    consistency_score = calculate_consistency_score(test_result, answers)
    
    # Analyze cross-section alignment
    cross_section_alignment = analyze_cross_section_alignment(test_result)
    
    # Classify the overall pattern
    contradiction_rate = len(contradictions) / len(answers) if len(answers) > 0 else 0
    pattern_classification = classify_pattern(consistency_score, contradiction_rate)
    
    logger.info(f"Pattern analysis complete: {pattern_classification}, "
                f"consistency={consistency_score:.2f}, "
                f"contradictions={len(contradictions)}")
    
    return {
        'pattern_classification': pattern_classification,
        'consistency_score': consistency_score,
        'contradictions': contradictions,
        'cross_section_alignment': cross_section_alignment
    }


def detect_contradictions(answers: List, questions: List) -> List[Dict[str, Any]]:
    """
    Detect contradictory responses in related question pairs.
    
    This function examines user answers for inconsistencies in related questions
    (e.g., claiming high teamwork but preferring solo work). It checks both
    trait-based question pairs and psychological pattern violations.
    
    Args:
        answers: List of UserAnswer objects
        questions: List of Question objects corresponding to answers
        
    Returns:
        List of contradiction objects, each containing:
            - question_1_id: int
            - question_2_id: int
            - description: str explaining the contradiction
            - severity: 'low' | 'medium' | 'high'
            
    Validates: Requirements 1.2
    """
    logger.debug(f"Detecting contradictions in {len(answers)} answers")
    
    contradictions = []
    
    # Build answer lookup with trait information for quick access
    answer_lookup = {}
    trait_answers = {}  # Maps trait -> list of (answer, question) tuples
    
    for answer in answers:
        if hasattr(answer, 'question_id') and hasattr(answer, 'selected_option'):
            answer_lookup[answer.question_id] = answer
            
            # Group answers by trait impact
            if hasattr(answer.selected_option, 'trait_impact') and answer.selected_option.trait_impact:
                trait = answer.selected_option.trait_impact
                if trait not in trait_answers:
                    trait_answers[trait] = []
                trait_answers[trait].append((answer, answer.question))
    
    # Detect trait-based contradictions using the new rule system
    trait_contradictions = detect_trait_based_contradictions(trait_answers)
    contradictions.extend(trait_contradictions)
    
    # Check for psychological pattern violations using test result scores
    # This requires access to the test result, which we need to infer from answers
    if answers and hasattr(answers[0], 'test_result'):
        test_result = answers[0].test_result
        pattern_contradictions = detect_psychological_pattern_violations(test_result)
        contradictions.extend(pattern_contradictions)
    
    logger.debug(f"Found {len(contradictions)} contradictions")
    return contradictions


def classify_pattern(consistency_score: float, contradiction_rate: float) -> str:
    """
    Classify answer pattern based on consistency metrics.
    
    This function categorizes a student's answer pattern into one of three
    classifications based on their consistency score and contradiction rate.
    
    Args:
        consistency_score: Float 0-100 indicating answer consistency
        contradiction_rate: Float 0-1 indicating proportion of contradictions
        
    Returns:
        One of: 'decisive', 'ambivalent', 'random'
        
    Classification Rules:
        - decisive: consistency >= 80 AND contradictions < 10%
        - ambivalent: consistency 50-79 AND contradictions 10-20%
        - random: consistency < 50 OR contradictions > 20%
        
    Validates: Requirements 1.3
    """
    # Convert contradiction_rate to percentage
    contradiction_pct = contradiction_rate * 100
    
    # Apply classification rules
    if consistency_score >= 80 and contradiction_pct < 10:
        return 'decisive'
    elif consistency_score < 50 or contradiction_pct > 20:
        return 'random'
    else:
        return 'ambivalent'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_consistency_score(test_result, answers: List) -> float:
    """
    Calculate consistency score based on response patterns.
    
    This analyzes how consistently the student answered questions within
    each test category. Higher scores indicate more consistent responses.
    
    Args:
        test_result: TestResult object
        answers: List of UserAnswer objects
        
    Returns:
        Float between 0-100 indicating consistency
    """
    if not answers or len(answers) == 0:
        return 50.0  # Default neutral score
    
    # Group answers by category
    category_answers = {}
    for answer in answers:
        if hasattr(answer, 'question') and hasattr(answer.question, 'category'):
            category = answer.question.category
            if category not in category_answers:
                category_answers[category] = []
            category_answers[category].append(answer)
    
    # Calculate variance in responses within each category
    # Lower variance = higher consistency
    consistency_scores = []
    
    for category, cat_answers in category_answers.items():
        if len(cat_answers) < 2:
            continue
            
        # Extract score values from selected options
        scores = []
        for answer in cat_answers:
            if hasattr(answer, 'selected_option') and hasattr(answer.selected_option, 'score_value'):
                scores.append(answer.selected_option.score_value)
        
        if len(scores) >= 2:
            # Calculate coefficient of variation (normalized standard deviation)
            mean_score = sum(scores) / len(scores)
            if mean_score > 0:
                variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
                std_dev = variance ** 0.5
                cv = std_dev / mean_score if mean_score != 0 else 0
                
                # Convert to consistency score (lower CV = higher consistency)
                # CV of 0 = 100% consistency, CV of 1+ = 0% consistency
                category_consistency = max(0, min(100, 100 * (1 - cv)))
                consistency_scores.append(category_consistency)
    
    # Return average consistency across categories
    if consistency_scores:
        return sum(consistency_scores) / len(consistency_scores)
    else:
        return 50.0  # Default neutral score if no valid data


def analyze_cross_section_alignment(test_result) -> Dict[str, float]:
    """
    Analyze alignment between different test sections.
    
    This examines whether personality traits align with interests and aptitudes
    (e.g., analytical personality matching STEM interests).
    
    Args:
        test_result: TestResult object with all scores
        
    Returns:
        Dictionary mapping section pairs to alignment scores (0-100)
    """
    alignment = {}
    
    # Check personality-interest alignment
    # High analytical personality should align with STEM interests
    if hasattr(test_result, 'analytical_score') and hasattr(test_result, 'stem_tech_score'):
        if test_result.analytical_score > 0:
            analytical_stem_alignment = min(100, (
                test_result.stem_tech_score / test_result.analytical_score
            ) * 100)
            alignment['analytical_stem'] = analytical_stem_alignment
    
    # High creativity personality should align with creative interests
    if hasattr(test_result, 'creativity_score') and hasattr(test_result, 'creative_media_score'):
        if test_result.creativity_score > 0:
            creativity_arts_alignment = min(100, (
                test_result.creative_media_score / test_result.creativity_score
            ) * 100)
            alignment['creativity_arts'] = creativity_arts_alignment
    
    # High communication/teamwork should align with people-oriented interests
    if (hasattr(test_result, 'communication_score') and 
        hasattr(test_result, 'teamwork_score') and 
        hasattr(test_result, 'people_oriented_score')):
        
        people_skills = (test_result.communication_score + test_result.teamwork_score) / 2
        if people_skills > 0:
            people_alignment = min(100, (
                test_result.people_oriented_score / people_skills
            ) * 100)
            alignment['people_skills'] = people_alignment
    
    return alignment




def detect_trait_based_contradictions(trait_answers: Dict[str, List]) -> List[Dict[str, Any]]:
    """
    Detect contradictions based on trait relationship rules.
    
    This function analyzes answers grouped by their trait impact and identifies
    contradictions according to TRAIT_RELATIONSHIP_RULES.
    
    Args:
        trait_answers: Dictionary mapping trait names to lists of (answer, question) tuples
        
    Returns:
        List of contradiction objects
    """
    contradictions = []
    
    # Check each category's trait relationship rules
    for category, rules in TRAIT_RELATIONSHIP_RULES.items():
        for trait_1, trait_2, relationship_type, threshold in rules:
            # Get answers for both traits
            answers_1 = trait_answers.get(trait_1, [])
            answers_2 = trait_answers.get(trait_2, [])
            
            # Check relationships between trait pairs
            if relationship_type == 'opposite':
                # For opposite traits, high scores on both indicate contradiction
                contradictions.extend(
                    check_opposite_traits(answers_1, answers_2, trait_1, trait_2, threshold)
                )
            
            elif relationship_type == 'similar':
                # For similar traits (same trait across questions), check consistency
                if trait_1 == trait_2 and len(answers_1) >= 2:
                    contradictions.extend(
                        check_trait_consistency(answers_1, trait_1, threshold)
                    )
            
            elif relationship_type == 'dependency':
                # For dependency (advanced requires basic), check prerequisites
                contradictions.extend(
                    check_trait_dependency(answers_1, answers_2, trait_1, trait_2, threshold)
                )
            
            elif relationship_type == 'tension':
                # For tension traits, extreme scores on both may indicate conflict
                contradictions.extend(
                    check_trait_tension(answers_1, answers_2, trait_1, trait_2, threshold)
                )
    
    return contradictions


def check_opposite_traits(answers_1: List, answers_2: List, 
                          trait_1: str, trait_2: str, threshold: int) -> List[Dict[str, Any]]:
    """
    Check for contradictions in opposite traits.
    
    Args:
        answers_1: List of (answer, question) for first trait
        answers_2: List of (answer, question) for second trait
        trait_1: First trait name
        trait_2: Second trait name
        threshold: Minimum score value to consider "high"
        
    Returns:
        List of contradiction objects
    """
    contradictions = []
    
    for ans1, q1 in answers_1:
        if not (hasattr(ans1, 'selected_option') and hasattr(ans1.selected_option, 'trait_value')):
            continue
            
        score1 = ans1.selected_option.trait_value or 0
        
        for ans2, q2 in answers_2:
            if not (hasattr(ans2, 'selected_option') and hasattr(ans2.selected_option, 'trait_value')):
                continue
                
            score2 = ans2.selected_option.trait_value or 0
            
            # Check if both scores are high (indicating contradiction)
            if score1 >= threshold and score2 >= threshold:
                contradictions.append({
                    'question_1_id': ans1.question_id,
                    'question_2_id': ans2.question_id,
                    'description': f'High scores on opposite traits: {trait_1} ({score1}) and {trait_2} ({score2})',
                    'severity': 'high'
                })
    
    return contradictions


def check_trait_consistency(answers: List, trait: str, threshold: int) -> List[Dict[str, Any]]:
    """
    Check for consistency within the same trait across multiple questions.
    
    Args:
        answers: List of (answer, question) tuples for the same trait
        trait: Trait name
        threshold: Maximum acceptable difference between scores
        
    Returns:
        List of contradiction objects
    """
    contradictions = []
    
    # Compare pairs of answers for the same trait
    for i in range(len(answers)):
        for j in range(i + 1, len(answers)):
            ans1, q1 = answers[i]
            ans2, q2 = answers[j]
            
            if not (hasattr(ans1, 'selected_option') and hasattr(ans2, 'selected_option')):
                continue
            if not (hasattr(ans1.selected_option, 'trait_value') and hasattr(ans2.selected_option, 'trait_value')):
                continue
            
            score1 = ans1.selected_option.trait_value or 0
            score2 = ans2.selected_option.trait_value or 0
            
            # Check if scores are inconsistent
            score_diff = abs(score1 - score2)
            if score_diff > threshold:
                contradictions.append({
                    'question_1_id': ans1.question_id,
                    'question_2_id': ans2.question_id,
                    'description': f'Inconsistent scores for {trait}: {score1} vs {score2} (difference: {score_diff})',
                    'severity': 'medium' if score_diff > threshold + 2 else 'low'
                })
    
    return contradictions


def check_trait_dependency(answers_advanced: List, answers_basic: List,
                           trait_advanced: str, trait_basic: str, threshold: int) -> List[Dict[str, Any]]:
    """
    Check for dependency violations (high advanced score without basic skills).
    
    Args:
        answers_advanced: List of (answer, question) for advanced trait
        answers_basic: List of (answer, question) for basic trait
        trait_advanced: Advanced trait name
        trait_basic: Basic/prerequisite trait name
        threshold: Minimum basic score required for advanced
        
    Returns:
        List of contradiction objects
    """
    contradictions = []
    
    for ans_adv, q_adv in answers_advanced:
        if not (hasattr(ans_adv, 'selected_option') and hasattr(ans_adv.selected_option, 'trait_value')):
            continue
            
        score_adv = ans_adv.selected_option.trait_value or 0
        
        # Only check if advanced score is high
        if score_adv >= 7:  # High advanced score
            for ans_basic, q_basic in answers_basic:
                if not (hasattr(ans_basic, 'selected_option') and hasattr(ans_basic.selected_option, 'trait_value')):
                    continue
                    
                score_basic = ans_basic.selected_option.trait_value or 0
                
                # Check if basic score is too low
                if score_basic < threshold:
                    contradictions.append({
                        'question_1_id': ans_adv.question_id,
                        'question_2_id': ans_basic.question_id,
                        'description': f'High {trait_advanced} score ({score_adv}) without adequate {trait_basic} ({score_basic})',
                        'severity': 'high'
                    })
    
    return contradictions


def check_trait_tension(answers_1: List, answers_2: List,
                       trait_1: str, trait_2: str, threshold: int) -> List[Dict[str, Any]]:
    """
    Check for tension between traits that can coexist but may indicate conflict when both extreme.
    
    Args:
        answers_1: List of (answer, question) for first trait
        answers_2: List of (answer, question) for second trait
        trait_1: First trait name
        trait_2: Second trait name
        threshold: Minimum score to consider extreme
        
    Returns:
        List of contradiction objects
    """
    contradictions = []
    
    for ans1, q1 in answers_1:
        if not (hasattr(ans1, 'selected_option') and hasattr(ans1.selected_option, 'trait_value')):
            continue
            
        score1 = ans1.selected_option.trait_value or 0
        
        for ans2, q2 in answers_2:
            if not (hasattr(ans2, 'selected_option') and hasattr(ans2.selected_option, 'trait_value')):
                continue
                
            score2 = ans2.selected_option.trait_value or 0
            
            # Check if both scores are extreme (indicating potential tension)
            if score1 >= threshold and score2 >= threshold:
                contradictions.append({
                    'question_1_id': ans1.question_id,
                    'question_2_id': ans2.question_id,
                    'description': f'Potential tension between {trait_1} ({score1}) and {trait_2} ({score2})',
                    'severity': 'medium'
                })
    
    return contradictions


def check_pair_contradiction(answer1, answer2, relationship_type: str) -> Dict[str, Any]:
    """
    Check if two related answers contradict each other.
    
    Args:
        answer1: First UserAnswer object
        answer2: Second UserAnswer object
        relationship_type: Type of relationship ('opposite', 'similar', 'dependency')
        
    Returns:
        Contradiction dict if found, None otherwise
    """
    # Extract score values
    if not (hasattr(answer1, 'selected_option') and hasattr(answer2, 'selected_option')):
        return None
    
    if not (hasattr(answer1.selected_option, 'score_value') and 
            hasattr(answer2.selected_option, 'score_value')):
        return None
    
    score1 = answer1.selected_option.score_value
    score2 = answer2.selected_option.score_value
    
    # Check based on relationship type
    if relationship_type == 'opposite':
        # For opposite questions, high scores on both indicate contradiction
        if score1 > 7 and score2 > 7:  # Assuming 10-point scale
            return {
                'question_1_id': answer1.question_id,
                'question_2_id': answer2.question_id,
                'description': 'High scores on opposite-direction questions',
                'severity': 'high'
            }
    
    elif relationship_type == 'similar':
        # For similar questions, large score differences indicate contradiction
        score_diff = abs(score1 - score2)
        if score_diff > 5:  # Assuming 10-point scale
            return {
                'question_1_id': answer1.question_id,
                'question_2_id': answer2.question_id,
                'description': 'Large score difference on similar questions',
                'severity': 'medium'
            }
    
    elif relationship_type == 'dependency':
        # For dependency questions, low prerequisite + high advanced = contradiction
        if score1 < 3 and score2 > 7:
            return {
                'question_1_id': answer1.question_id,
                'question_2_id': answer2.question_id,
                'description': 'Advanced skill claimed without prerequisite',
                'severity': 'high'
            }
    
    return None


def detect_psychological_pattern_violations(test_result) -> List[Dict[str, Any]]:
    """
    Detect violations of known psychological patterns.
    
    This checks for incompatible trait combinations based on test scores
    (e.g., claiming both high teamwork and high solo preference).
    
    Args:
        test_result: TestResult object with all scores
        
    Returns:
        List of contradiction objects for pattern violations
    """
    violations = []
    
    # Check teamwork vs solo work conflict
    if (hasattr(test_result, 'teamwork_score') and 
        hasattr(test_result, 'adaptability_score')):
        
        pattern = PSYCHOLOGICAL_PATTERNS['teamwork_solo_conflict']
        # Note: Using adaptability as proxy for independence since no direct solo_work score
        # In production, this would need proper solo work scoring
        
        if (test_result.teamwork_score >= pattern['high_teamwork_threshold'] and
            test_result.adaptability_score < 30):  # Low adaptability may suggest rigidity
            
            violations.append({
                'question_1_id': -1,  # Derived from scores, not specific questions
                'question_2_id': -2,
                'description': pattern['description'],
                'severity': 'medium'
            })
    
    # Check leadership vs following conflict
    if (hasattr(test_result, 'leadership_score') and
        hasattr(test_result, 'teamwork_score')):
        
        pattern = PSYCHOLOGICAL_PATTERNS['leadership_following_conflict']
        # High teamwork with very low leadership might indicate following preference
        
        if (test_result.leadership_score >= pattern['high_leadership_threshold'] and
            test_result.teamwork_score < 30):  # Low teamwork with high leadership is unusual
            
            violations.append({
                'question_1_id': -3,
                'question_2_id': -4,
                'description': 'High leadership but very low teamwork suggests potential inconsistency',
                'severity': 'low'
            })
    
    return violations


# ============================================================================
# UTILITY FUNCTIONS FOR TESTING AND DYNAMIC CONFIGURATION
# ============================================================================

def get_related_question_pairs() -> Dict[str, List[Tuple]]:
    """
    Get the related question pair mappings.
    
    Returns:
        Copy of RELATED_QUESTION_PAIRS dictionary
    """
    return RELATED_QUESTION_PAIRS.copy()


def get_trait_relationship_rules() -> Dict[str, List[Tuple]]:
    """
    Get the trait relationship rules used for contradiction detection.
    
    Returns:
        Copy of TRAIT_RELATIONSHIP_RULES dictionary
    """
    return {k: list(v) for k, v in TRAIT_RELATIONSHIP_RULES.items()}


def add_related_question_pair(category: str, question_1_id: int, 
                              question_2_id: int, relationship_type: str):
    """
    Add a related question pair to the mappings.
    
    This is useful for dynamic configuration or testing.
    
    Args:
        category: Question category ('personality', 'interest', etc.)
        question_1_id: First question ID
        question_2_id: Second question ID
        relationship_type: 'opposite', 'similar', or 'dependency'
    """
    if category not in RELATED_QUESTION_PAIRS:
        RELATED_QUESTION_PAIRS[category] = []
    
    RELATED_QUESTION_PAIRS[category].append(
        (question_1_id, question_2_id, relationship_type)
    )
    
    logger.info(f"Added related pair: {question_1_id} <-> {question_2_id} "
                f"({relationship_type}) in category {category}")


def add_trait_relationship_rule(category: str, trait_1: str, trait_2: str,
                                relationship_type: str, threshold: int):
    """
    Add a trait relationship rule for contradiction detection.
    
    Args:
        category: Question category ('personality', 'interest', 'aptitude', 'work_style')
        trait_1: First trait name
        trait_2: Second trait name
        relationship_type: 'opposite', 'similar', 'dependency', or 'tension'
        threshold: Score threshold for the rule
    """
    if category not in TRAIT_RELATIONSHIP_RULES:
        TRAIT_RELATIONSHIP_RULES[category] = []
    
    TRAIT_RELATIONSHIP_RULES[category].append(
        (trait_1, trait_2, relationship_type, threshold)
    )
    
    logger.info(f"Added trait rule: {trait_1} <-> {trait_2} "
                f"({relationship_type}, threshold={threshold}) in category {category}")


def populate_question_pairs_from_database(db_session=None):
    """
    Dynamically populate RELATED_QUESTION_PAIRS from database questions.
    
    This function queries the database and builds question pairs based on
    trait_impact patterns found in the questions.
    
    Args:
        db_session: SQLAlchemy database session (optional)
    """
    try:
        from neuroapt.app.models import Question, QuestionOption
        from neuroapt.app import db
        
        session = db_session or db.session
        
        # Query all questions with their options
        all_questions = session.query(Question).all()
        
        # Group questions by category and trait_impact
        trait_question_map = {}
        
        for question in all_questions:
            category = question.category
            if category not in trait_question_map:
                trait_question_map[category] = {}
            
            # Get unique trait impacts from this question's options
            traits = set()
            for option in question.options:
                if option.trait_impact:
                    traits.add(option.trait_impact)
            
            # Map each trait to this question
            for trait in traits:
                if trait not in trait_question_map[category]:
                    trait_question_map[category][trait] = []
                trait_question_map[category][trait].append(question.id)
        
        # Build pairs based on trait relationship rules
        for category, rules in TRAIT_RELATIONSHIP_RULES.items():
            if category not in RELATED_QUESTION_PAIRS:
                RELATED_QUESTION_PAIRS[category] = []
            
            if category not in trait_question_map:
                continue
            
            for trait_1, trait_2, relationship_type, _ in rules:
                # Get questions for each trait
                q1_list = trait_question_map[category].get(trait_1, [])
                q2_list = trait_question_map[category].get(trait_2, [])
                
                # Create pairs
                if relationship_type == 'similar' and trait_1 == trait_2:
                    # For similar traits, pair questions within the same trait
                    for i in range(len(q1_list)):
                        for j in range(i + 1, len(q1_list)):
                            RELATED_QUESTION_PAIRS[category].append(
                                (q1_list[i], q1_list[j], relationship_type)
                            )
                else:
                    # For opposite, dependency, or tension, pair across traits
                    for q1_id in q1_list:
                        for q2_id in q2_list:
                            if q1_id != q2_id:
                                RELATED_QUESTION_PAIRS[category].append(
                                    (q1_id, q2_id, relationship_type)
                                )
        
        logger.info("Successfully populated question pairs from database")
        
    except Exception as e:
        logger.error(f"Error populating question pairs from database: {str(e)}")
        # Don't raise - system should work without dynamic population
