"""
Confidence Scoring Engine for AI-Enhanced Career Matching

This module calculates confidence scores for career recommendations based on
answer pattern analysis. The confidence score indicates the reliability of
recommendations, factoring in response consistency, contradictions, and test completion.

Author: Neuro-Apt Development Team
Date: 2024
"""

from typing import Dict, Any, Optional


def calculate_confidence_score(
    pattern_analysis: Dict[str, Any],
    test_result: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Calculate overall confidence score and classification.
    
    The confidence score indicates how reliable the career recommendations are
    based on the student's answer patterns. Higher scores indicate more consistent
    and reliable responses.
    
    Scoring Algorithm:
        base_score = consistency_score from pattern analysis (0-100)
        contradiction_penalty = (contradiction_count / total_questions) * 50
        completion_bonus = 10 if fully completed, else 0
        confidence_score = max(0, min(100, base_score - contradiction_penalty + completion_bonus))
    
    Classification Thresholds:
        - HIGH: score >= 80
        - MODERATE: score 60-79
        - LOW: score 40-59
        - UNRELIABLE: score < 40
    
    Args:
        pattern_analysis: Output from analyze_answer_patterns() containing:
            - consistency_score (float): Base consistency score (0-100)
            - contradictions (List[Dict]): List of detected contradictions
            - pattern_classification (str): Pattern type (decisive/ambivalent/random)
        test_result: Optional TestResult database record for completion data.
                    If None, assumes 100% completion.
    
    Returns:
        Dict containing:
            - confidence_score (int): Final confidence score (0-100)
            - confidence_level (str): Classification (HIGH/MODERATE/LOW/UNRELIABLE)
            - factors (Dict): Breakdown of scoring components
            - explanation (str): Human-readable explanation of the score
    
    Examples:
        >>> pattern = {
        ...     'consistency_score': 85.0,
        ...     'contradictions': [],
        ...     'pattern_classification': 'decisive'
        ... }
        >>> result = calculate_confidence_score(pattern)
        >>> result['confidence_level']
        'HIGH'
        
        >>> pattern_with_issues = {
        ...     'consistency_score': 65.0,
        ...     'contradictions': [{'q1': 1, 'q2': 2}] * 10,  # 10 contradictions
        ...     'pattern_classification': 'ambivalent'
        ... }
        >>> result = calculate_confidence_score(pattern_with_issues)
        >>> result['confidence_level']
        'MODERATE'
    """
    # Extract base consistency score
    base_score = float(pattern_analysis.get('consistency_score', 50.0))
    
    # Calculate contradiction penalty
    contradictions = pattern_analysis.get('contradictions', [])
    contradiction_count = len(contradictions)
    
    # Estimate total questions (default to reasonable estimate if not provided)
    # Most psychometric tests have 50-100 questions
    if test_result is not None and hasattr(test_result, 'total_questions'):
        total_questions = test_result.total_questions
    else:
        # Use a conservative estimate based on typical test structure
        # If we have contradictions, assume at least 50 questions
        total_questions = max(50, contradiction_count * 5) if contradiction_count > 0 else 50
    
    # Calculate contradiction rate and penalty
    contradiction_rate = contradiction_count / total_questions if total_questions > 0 else 0
    contradiction_penalty = contradiction_rate * 50  # Up to -50 points
    
    # Calculate completion bonus
    completion_bonus = 0
    if test_result is not None:
        if hasattr(test_result, 'answered_questions') and hasattr(test_result, 'total_questions'):
            answered = test_result.answered_questions
            total = test_result.total_questions
            if total > 0:
                completion_rate = answered / total
                if completion_rate >= 1.0:
                    completion_bonus = 10
        else:
            # If no completion data available, assume full completion
            completion_bonus = 10
    else:
        # If no test_result provided, assume full completion
        completion_bonus = 10
    
    # Calculate final confidence score
    confidence_score = base_score - contradiction_penalty + completion_bonus
    confidence_score = max(0, min(100, confidence_score))  # Clamp to 0-100 range
    confidence_score = int(round(confidence_score))  # Round to integer
    
    # Classify confidence level based on thresholds
    if confidence_score >= 80:
        confidence_level = "HIGH"
    elif confidence_score >= 60:
        confidence_level = "MODERATE"
    elif confidence_score >= 40:
        confidence_level = "LOW"
    else:
        confidence_level = "UNRELIABLE"
    
    # Generate explanation
    explanation = _generate_explanation(
        confidence_level,
        base_score,
        contradiction_count,
        contradiction_penalty,
        completion_bonus,
        pattern_analysis.get('pattern_classification', 'unknown')
    )
    
    return {
        'confidence_score': confidence_score,
        'confidence_level': confidence_level,
        'factors': {
            'consistency_contribution': int(round(base_score)),
            'contradiction_penalty': int(round(contradiction_penalty)),
            'completion_bonus': completion_bonus
        },
        'explanation': explanation
    }


def _generate_explanation(
    confidence_level: str,
    base_score: float,
    contradiction_count: int,
    contradiction_penalty: float,
    completion_bonus: int,
    pattern_classification: str
) -> str:
    """
    Generate human-readable explanation of confidence score.
    
    Args:
        confidence_level: The calculated confidence level (HIGH/MODERATE/LOW/UNRELIABLE)
        base_score: The consistency score from pattern analysis
        contradiction_count: Number of contradictions detected
        contradiction_penalty: Points deducted for contradictions
        completion_bonus: Points added for test completion
        pattern_classification: Pattern type (decisive/ambivalent/random)
    
    Returns:
        Human-readable explanation string
    """
    explanations = {
        'HIGH': (
            f"Your responses show high consistency (base score: {base_score:.1f}/100) "
            f"with {pattern_classification} answer patterns. "
        ),
        'MODERATE': (
            f"Your responses show moderate consistency (base score: {base_score:.1f}/100) "
            f"with {pattern_classification} answer patterns. "
        ),
        'LOW': (
            f"Your responses show lower consistency (base score: {base_score:.1f}/100) "
            f"with {pattern_classification} answer patterns. "
        ),
        'UNRELIABLE': (
            f"Your responses show inconsistent patterns (base score: {base_score:.1f}/100) "
            f"with {pattern_classification} classification. "
        )
    }
    
    explanation = explanations.get(confidence_level, "Unable to determine confidence level. ")
    
    # Add contradiction information
    if contradiction_count > 0:
        explanation += (
            f"Detected {contradiction_count} contradictory response(s), "
            f"which reduced confidence by {contradiction_penalty:.1f} points. "
        )
    else:
        explanation += "No significant contradictions detected. "
    
    # Add completion information
    if completion_bonus > 0:
        explanation += f"Test completed fully (bonus: +{completion_bonus} points)."
    else:
        explanation += "Test not fully completed (no completion bonus)."
    
    return explanation


def classify_confidence_level(confidence_score: int) -> str:
    """
    Classify a numeric confidence score into a level category.
    
    This is a utility function for direct classification without full calculation.
    Useful when you already have a confidence score and just need the classification.
    
    Thresholds:
        - HIGH: score >= 80
        - MODERATE: score 60-79
        - LOW: score 40-59
        - UNRELIABLE: score < 40
    
    Args:
        confidence_score: Numeric confidence score (0-100)
    
    Returns:
        Confidence level string: "HIGH", "MODERATE", "LOW", or "UNRELIABLE"
    
    Examples:
        >>> classify_confidence_level(85)
        'HIGH'
        >>> classify_confidence_level(65)
        'MODERATE'
        >>> classify_confidence_level(45)
        'LOW'
        >>> classify_confidence_level(30)
        'UNRELIABLE'
    """
    if confidence_score >= 80:
        return "HIGH"
    elif confidence_score >= 60:
        return "MODERATE"
    elif confidence_score >= 40:
        return "LOW"
    else:
        return "UNRELIABLE"


def get_confidence_thresholds() -> Dict[str, int]:
    """
    Get the confidence score thresholds for each classification level.
    
    Returns:
        Dict mapping confidence levels to their minimum threshold scores
    
    Example:
        >>> thresholds = get_confidence_thresholds()
        >>> thresholds['HIGH']
        80
    """
    return {
        'HIGH': 80,
        'MODERATE': 60,
        'LOW': 40,
        'UNRELIABLE': 0
    }
