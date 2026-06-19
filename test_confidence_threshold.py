"""
Property-Based Test for Confidence Threshold Classification

**Property 3: Confidence Threshold Classification**
**Validates: Requirements 1.4, 4.2**

This test verifies that for any pattern analysis data, the confidence classifier
correctly categorizes scores as HIGH (≥80), MODERATE (60-79), LOW (40-59),
or UNRELIABLE (<40).

The test generates pattern analysis data with scores around threshold boundaries
(39, 40, 59, 60, 79, 80) to ensure correct classification at edge cases.
"""

from hypothesis import given, strategies as st, settings
from neuroapt.app.utils.confidence_scorer import calculate_confidence_score, classify_confidence_level


# Strategy for generating pattern analysis data with specific consistency scores
@st.composite
def pattern_analysis_with_score(draw, consistency_score):
    """
    Generate a pattern analysis dict with a specific consistency score.
    
    Args:
        consistency_score: The consistency score to use (0-100)
    
    Returns:
        Dict with pattern analysis data
    """
    # Generate random number of contradictions (0-20)
    num_contradictions = draw(st.integers(min_value=0, max_value=20))
    
    # Generate contradictions list
    contradictions = [
        {
            'question_1_id': draw(st.integers(min_value=1, max_value=100)),
            'question_2_id': draw(st.integers(min_value=1, max_value=100)),
            'description': draw(st.text(min_size=5, max_size=50)),
            'severity': draw(st.sampled_from(['low', 'medium', 'high']))
        }
        for _ in range(num_contradictions)
    ]
    
    # Generate pattern classification
    pattern_classification = draw(st.sampled_from(['decisive', 'ambivalent', 'random']))
    
    return {
        'consistency_score': consistency_score,
        'contradictions': contradictions,
        'pattern_classification': pattern_classification
    }


# Strategy for generating scores around threshold boundaries
threshold_scores_strategy = st.sampled_from([
    # Below LOW threshold (UNRELIABLE)
    0, 10, 20, 30, 39,
    # At LOW threshold boundary
    40, 41, 45, 50, 55, 59,
    # At MODERATE threshold boundary
    60, 61, 65, 70, 75, 79,
    # At HIGH threshold boundary
    80, 81, 85, 90, 95, 100
])


@given(consistency_score=threshold_scores_strategy)
@settings(max_examples=200)  # Extra examples to cover all boundary cases
def test_confidence_threshold_classification_boundaries(consistency_score):
    """
    Property Test: Confidence threshold classification at boundaries.
    
    For any pattern analysis data with consistency scores around thresholds,
    verify that the confidence classifier correctly categorizes the score.
    
    Thresholds:
        - HIGH: score >= 80
        - MODERATE: score 60-79
        - LOW: score 40-59
        - UNRELIABLE: score < 40
    """
    # Generate pattern analysis data with the specific consistency score
    pattern_analysis = {
        'consistency_score': float(consistency_score),
        'contradictions': [],  # No contradictions for pure threshold testing
        'pattern_classification': 'decisive'
    }
    
    # Calculate confidence score (with no contradictions and full completion)
    result = calculate_confidence_score(pattern_analysis, test_result=None)
    
    # Extract the confidence score and level
    calculated_score = result['confidence_score']
    confidence_level = result['confidence_level']
    
    # The calculated score should be consistency_score + completion_bonus (10)
    # Since there are no contradictions
    expected_score = min(100, consistency_score + 10)
    
    # Verify the calculated score matches expectation
    assert calculated_score == expected_score, \
        f"Expected score {expected_score}, got {calculated_score}"
    
    # Verify correct classification based on thresholds
    if calculated_score >= 80:
        assert confidence_level == "HIGH", \
            f"Score {calculated_score} should be HIGH, got {confidence_level}"
    elif calculated_score >= 60:
        assert confidence_level == "MODERATE", \
            f"Score {calculated_score} should be MODERATE, got {confidence_level}"
    elif calculated_score >= 40:
        assert confidence_level == "LOW", \
            f"Score {calculated_score} should be LOW, got {confidence_level}"
    else:
        assert confidence_level == "UNRELIABLE", \
            f"Score {calculated_score} should be UNRELIABLE, got {confidence_level}"


@given(
    consistency_score=st.floats(min_value=0.0, max_value=100.0),
    num_contradictions=st.integers(min_value=0, max_value=50)
)
@settings(max_examples=200)
def test_confidence_classification_consistency(consistency_score, num_contradictions):
    """
    Property Test: Confidence classification is consistent across all inputs.
    
    For any valid pattern analysis data (consistency score 0-100, any number of
    contradictions), verify that classification follows the threshold rules.
    """
    # Generate pattern analysis data
    contradictions = [
        {
            'question_1_id': i,
            'question_2_id': i + 1,
            'description': f'Contradiction {i}',
            'severity': 'medium'
        }
        for i in range(num_contradictions)
    ]
    
    pattern_analysis = {
        'consistency_score': consistency_score,
        'contradictions': contradictions,
        'pattern_classification': 'ambivalent'
    }
    
    # Calculate confidence score
    result = calculate_confidence_score(pattern_analysis, test_result=None)
    calculated_score = result['confidence_score']
    confidence_level = result['confidence_level']
    
    # Verify score is in valid range
    assert 0 <= calculated_score <= 100, \
        f"Confidence score {calculated_score} out of range [0, 100]"
    
    # Verify classification matches the score
    if calculated_score >= 80:
        assert confidence_level == "HIGH", \
            f"Score {calculated_score} should be HIGH, got {confidence_level}"
    elif calculated_score >= 60:
        assert confidence_level == "MODERATE", \
            f"Score {calculated_score} should be MODERATE, got {confidence_level}"
    elif calculated_score >= 40:
        assert confidence_level == "LOW", \
            f"Score {calculated_score} should be LOW, got {confidence_level}"
    else:
        assert confidence_level == "UNRELIABLE", \
            f"Score {calculated_score} should be UNRELIABLE, got {confidence_level}"


@given(confidence_score=st.integers(min_value=0, max_value=100))
@settings(max_examples=101)  # Cover all possible integer scores
def test_classify_confidence_level_direct(confidence_score):
    """
    Property Test: Direct classification utility function.
    
    Test the classify_confidence_level utility function for all possible
    score values to ensure it correctly applies thresholds.
    """
    level = classify_confidence_level(confidence_score)
    
    # Verify correct classification
    if confidence_score >= 80:
        assert level == "HIGH", \
            f"Score {confidence_score} should be HIGH, got {level}"
    elif confidence_score >= 60:
        assert level == "MODERATE", \
            f"Score {confidence_score} should be MODERATE, got {level}"
    elif confidence_score >= 40:
        assert level == "LOW", \
            f"Score {confidence_score} should be LOW, got {level}"
    else:
        assert level == "UNRELIABLE", \
            f"Score {confidence_score} should be UNRELIABLE, got {level}"


def test_specific_threshold_boundaries():
    """
    Unit Test: Verify exact threshold boundary values.
    
    Test the specific boundary values mentioned in the task:
    39, 40, 59, 60, 79, 80
    """
    print("\nTesting specific threshold boundaries...")
    
    # Test boundary values using classify_confidence_level
    test_cases = [
        (39, "UNRELIABLE"),
        (40, "LOW"),
        (59, "LOW"),
        (60, "MODERATE"),
        (79, "MODERATE"),
        (80, "HIGH"),
    ]
    
    for score, expected_level in test_cases:
        level = classify_confidence_level(score)
        assert level == expected_level, \
            f"Score {score}: expected {expected_level}, got {level}"
        print(f"  ✓ Score {score} correctly classified as {expected_level}")
    
    print("✓ All threshold boundaries verified")


def test_confidence_calculation_with_thresholds():
    """
    Unit Test: Test confidence calculation produces correct classifications.
    
    Test pattern analysis data that produces scores around thresholds after
    applying the formula: base_score - (contradiction_rate * 50) + completion_bonus
    """
    print("\nTesting confidence calculation with threshold scores...")
    
    # Test case 1: Base score 70, no contradictions -> 70 + 10 = 80 (HIGH)
    pattern = {
        'consistency_score': 70.0,
        'contradictions': [],
        'pattern_classification': 'decisive'
    }
    result = calculate_confidence_score(pattern)
    assert result['confidence_score'] == 80, \
        f"Expected 80, got {result['confidence_score']}"
    assert result['confidence_level'] == "HIGH", \
        f"Expected HIGH, got {result['confidence_level']}"
    print("  ✓ Score 70 + bonus -> 80 (HIGH)")
    
    # Test case 2: Base score 50, no contradictions -> 50 + 10 = 60 (MODERATE)
    pattern = {
        'consistency_score': 50.0,
        'contradictions': [],
        'pattern_classification': 'decisive'
    }
    result = calculate_confidence_score(pattern)
    assert result['confidence_score'] == 60, \
        f"Expected 60, got {result['confidence_score']}"
    assert result['confidence_level'] == "MODERATE", \
        f"Expected MODERATE, got {result['confidence_level']}"
    print("  ✓ Score 50 + bonus -> 60 (MODERATE)")
    
    # Test case 3: Base score 30, no contradictions -> 30 + 10 = 40 (LOW)
    pattern = {
        'consistency_score': 30.0,
        'contradictions': [],
        'pattern_classification': 'decisive'
    }
    result = calculate_confidence_score(pattern)
    assert result['confidence_score'] == 40, \
        f"Expected 40, got {result['confidence_score']}"
    assert result['confidence_level'] == "LOW", \
        f"Expected LOW, got {result['confidence_level']}"
    print("  ✓ Score 30 + bonus -> 40 (LOW)")
    
    # Test case 4: Base score 20, no contradictions -> 20 + 10 = 30 (UNRELIABLE)
    pattern = {
        'consistency_score': 20.0,
        'contradictions': [],
        'pattern_classification': 'random'
    }
    result = calculate_confidence_score(pattern)
    assert result['confidence_score'] == 30, \
        f"Expected 30, got {result['confidence_score']}"
    assert result['confidence_level'] == "UNRELIABLE", \
        f"Expected UNRELIABLE, got {result['confidence_level']}"
    print("  ✓ Score 20 + bonus -> 30 (UNRELIABLE)")
    
    print("✓ All threshold calculation tests passed")


if __name__ == '__main__':
    print("=" * 80)
    print("Property-Based Test: Confidence Threshold Classification")
    print("=" * 80)
    
    try:
        # Run unit tests first
        test_specific_threshold_boundaries()
        test_confidence_calculation_with_thresholds()
        
        print("\nRunning property-based tests...")
        print("(This may take a moment as Hypothesis generates test cases)")
        
        # Run property tests
        test_confidence_threshold_classification_boundaries()
        print("  ✓ Boundary classification property verified")
        
        test_confidence_classification_consistency()
        print("  ✓ Classification consistency property verified")
        
        test_classify_confidence_level_direct()
        print("  ✓ Direct classification utility property verified")
        
        print("\n" + "=" * 80)
        print("✓ All property tests passed!")
        print("=" * 80)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
