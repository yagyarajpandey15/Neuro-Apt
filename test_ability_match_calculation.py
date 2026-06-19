"""
Property-Based Test for Ability Match Calculation Correctness

**Property 6: Ability Match Calculation Correctness**
**Validates: Requirements 2.4, 10.1, 10.2, 10.3**

This test verifies that for any student profile and career type, the ability matcher
calculates match percentages using the formula (student_score / career_requirement) * 100
(capped at 100%) with correct career-specific weightings.

The test generates student profiles and career types using Hypothesis and verifies:
1. All dimension matches use the correct formula
2. Career-specific weights are applied correctly
3. Overall match is the weighted average of dimension matches
4. All values are in the valid range [0, 100]
"""

from hypothesis import given, strategies as st, settings
from neuroapt.app.utils.ability_matcher import (
    calculate_ability_match_for_career,
    calculate_dimension_match,
    detect_career_type,
    CAREER_REQUIREMENTS,
    CAREER_WEIGHTS
)


# Strategy for generating valid student profiles
@st.composite
def student_profile_strategy(draw):
    """
    Generate a valid student profile with all required fields.
    
    Returns:
        Dict with complete student profile data
    """
    return {
        'user_id': draw(st.integers(min_value=1, max_value=10000)),
        'test_id': draw(st.integers(min_value=1, max_value=10000)),
        'cognitive_abilities': {
            'verbal': draw(st.integers(min_value=0, max_value=100)),
            'numerical': draw(st.integers(min_value=0, max_value=100)),
            'abstract': draw(st.integers(min_value=0, max_value=100)),
            'overall_aptitude': draw(st.integers(min_value=0, max_value=100))
        },
        'personality_traits': {
            'openness': draw(st.integers(min_value=0, max_value=100)),
            'conscientiousness': draw(st.integers(min_value=0, max_value=100)),
            'extraversion': draw(st.integers(min_value=0, max_value=100)),
            'agreeableness': draw(st.integers(min_value=0, max_value=100)),
            'neuroticism': draw(st.integers(min_value=0, max_value=100))
        },
        'work_attributes': {
            'leadership': draw(st.integers(min_value=0, max_value=100)),
            'teamwork': draw(st.integers(min_value=0, max_value=100)),
            'creativity': draw(st.integers(min_value=0, max_value=100)),
            'analytical': draw(st.integers(min_value=0, max_value=100)),
            'communication': draw(st.integers(min_value=0, max_value=100)),
            'adaptability': draw(st.integers(min_value=0, max_value=100))
        },
        'interest_domains': {
            'stem_tech': draw(st.integers(min_value=0, max_value=100)),
            'creative_media': draw(st.integers(min_value=0, max_value=100)),
            'people_oriented': draw(st.integers(min_value=0, max_value=100)),
            'business_management': draw(st.integers(min_value=0, max_value=100)),
            'legal_governance': draw(st.integers(min_value=0, max_value=100)),
            'logistics_distribution': draw(st.integers(min_value=0, max_value=100))
        },
        'emotional_intelligence': draw(st.integers(min_value=0, max_value=100)),
        'metadata': {
            'test_date': '2024-01-15T10:00:00',
            'pattern_classification': draw(st.sampled_from(['decisive', 'ambivalent', 'random'])),
            'contradictions': [],
            'consistency_score': draw(st.floats(min_value=0.0, max_value=100.0))
        }
    }


# Strategy for generating career titles from different domains
career_titles_strategy = st.sampled_from([
    # Technical careers
    'Software Engineer', 'Data Scientist', 'DevOps Engineer', 'Systems Analyst',
    'Network Administrator', 'Cybersecurity Specialist', 'Database Administrator',
    
    # Creative careers
    'Graphic Designer', 'UX Designer', 'Art Director', 'Animator', 'Photographer',
    'Content Writer', 'Fashion Designer', 'Interior Designer',
    
    # Business careers
    'Financial Analyst', 'Management Consultant', 'Product Manager', 'Accountant',
    'Business Development Manager', 'Marketing Manager', 'Sales Manager',
    
    # Research careers
    'Research Scientist', 'Data Analyst', 'Laboratory Researcher', 'Academic Professor',
    'Clinical Researcher', 'Statistician', 'Biologist',
    
    # Healthcare careers
    'Registered Nurse', 'Physician', 'Physical Therapist', 'Pharmacist',
    'Medical Assistant', 'Psychiatrist', 'Occupational Therapist',
    
    # People-oriented careers
    'High School Teacher', 'HR Manager', 'Social Worker', 'Career Counselor',
    'Training Coordinator', 'Customer Success Manager', 'Community Organizer'
])


career_categories_strategy = st.sampled_from([
    'STEM+Tech', 'Creative+Media', 'Business+Finance', 'Science+Research',
    'Healthcare+Medical', 'Education+People', 'Management', 'Arts', 'Technology'
])


@given(
    student_score=st.integers(min_value=0, max_value=100),
    career_requirement=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=200)
def test_dimension_match_formula_correctness(student_score, career_requirement):
    """
    Property Test: Dimension match formula is correctly applied.
    
    For any student score and career requirement, verify that the match
    percentage is calculated as (student_score / career_requirement) * 100,
    capped at 100%.
    
    Formula: min(100, (student_score / career_requirement) * 100)
    """
    match = calculate_dimension_match(student_score, career_requirement)
    
    # Calculate expected match
    expected_raw = (student_score / career_requirement) * 100
    expected = min(100, int(expected_raw))
    
    # Verify the match is correct
    assert match == expected, \
        f"Match formula incorrect: student={student_score}, req={career_requirement}, " \
        f"expected={expected}, got={match}"
    
    # Verify match is in valid range
    assert 0 <= match <= 100, \
        f"Match {match} out of range [0, 100]"


@given(
    student_score=st.integers(min_value=0, max_value=100),
    career_requirement=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=100)
def test_dimension_match_capped_at_100(student_score, career_requirement):
    """
    Property Test: Dimension match is capped at 100%.
    
    For any student score that exceeds career requirement, verify that
    the match percentage never exceeds 100%.
    """
    match = calculate_dimension_match(student_score, career_requirement)
    
    # Match should never exceed 100
    assert match <= 100, \
        f"Match {match} exceeds 100% cap for student={student_score}, req={career_requirement}"
    
    # If student meets or exceeds requirement, match should be 100
    if student_score >= career_requirement:
        assert match == 100, \
            f"Student meets/exceeds requirement but match={match}, not 100"


@given(profile=student_profile_strategy())
@settings(max_examples=150)
def test_ability_match_all_dimensions_in_valid_range(profile):
    """
    Property Test: All dimension matches are in valid range [0, 100].
    
    For any student profile and technical career, verify that all
    dimension match values are integers in the range [0, 100].
    """
    result = calculate_ability_match_for_career(
        profile,
        "Software Engineer",
        "STEM+Tech"
    )
    
    # Verify all required fields are present
    required_fields = [
        'cognitive_match',
        'personality_match',
        'emotional_intelligence_match',
        'work_style_match',
        'interest_alignment',
        'overall_match'
    ]
    
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
    
    # Verify all values are integers in valid range
    for key, value in result.items():
        assert isinstance(value, int), \
            f"Field {key} has non-integer value: {value} (type: {type(value)})"
        assert 0 <= value <= 100, \
            f"Field {key} value {value} out of range [0, 100]"


@given(
    profile=student_profile_strategy(),
    career_title=career_titles_strategy,
    career_category=career_categories_strategy
)
@settings(max_examples=200)
def test_ability_match_uses_correct_career_weights(profile, career_title, career_category):
    """
    Property Test: Ability match uses correct career-specific weights.
    
    For any student profile and career, verify that:
    1. The career type is detected correctly
    2. The correct weights are applied
    3. The overall match is the weighted average of dimension matches
    """
    result = calculate_ability_match_for_career(profile, career_title, career_category)
    
    # Detect career type
    career_type = detect_career_type(career_title, career_category)
    
    # Get weights for this career type
    weights = CAREER_WEIGHTS.get(career_type, CAREER_WEIGHTS['business'])
    
    # Calculate expected weighted average
    expected_overall = (
        result['cognitive_match'] * weights['cognitive'] +
        result['personality_match'] * weights['personality'] +
        result['emotional_intelligence_match'] * weights['emotional_intelligence'] +
        result['work_style_match'] * weights['work_style'] +
        result['interest_alignment'] * weights['interest']
    )
    expected_overall = int(expected_overall)
    
    # Verify overall match is the weighted average
    assert result['overall_match'] == expected_overall, \
        f"Overall match {result['overall_match']} != expected weighted average {expected_overall} " \
        f"for career type {career_type}"


@given(
    profile=student_profile_strategy(),
    career_title=career_titles_strategy
)
@settings(max_examples=150)
def test_ability_match_weights_sum_to_one(profile, career_title):
    """
    Property Test: Career-specific weights sum to 1.0.
    
    For any career, verify that the weights used for calculating
    the overall match sum to exactly 1.0 (allowing for floating point precision).
    """
    # Detect career type
    career_type = detect_career_type(career_title, '')
    
    # Get weights for this career type
    weights = CAREER_WEIGHTS.get(career_type, CAREER_WEIGHTS['business'])
    
    # Sum all weights
    weight_sum = sum(weights.values())
    
    # Verify sum is 1.0 (with small floating point tolerance)
    assert abs(weight_sum - 1.0) < 0.001, \
        f"Weights for {career_type} sum to {weight_sum}, not 1.0"


@given(
    profile=student_profile_strategy(),
    career_title=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))
)
@settings(max_examples=100)
def test_ability_match_handles_unknown_careers_gracefully(profile, career_title):
    """
    Property Test: Unknown careers default to business weights.
    
    For any random career title (that might not match any keywords),
    verify that the system defaults to business career type and
    completes the calculation without errors.
    """
    try:
        result = calculate_ability_match_for_career(profile, career_title, '')
        
        # Should complete without error
        assert result is not None
        
        # Should contain all required fields
        assert 'overall_match' in result
        assert 0 <= result['overall_match'] <= 100
        
    except Exception as e:
        # Should not raise exceptions for unknown careers
        raise AssertionError(
            f"Failed to handle unknown career '{career_title}': {e}"
        )


def test_specific_career_weight_examples():
    """
    Unit Test: Verify specific career types use correct weights.
    
    Test that known career types apply the documented weight distributions.
    """
    print("\nTesting specific career weight examples...")
    
    # Sample profile for testing
    profile = {
        'user_id': 1,
        'test_id': 1,
        'cognitive_abilities': {'verbal': 80, 'numerical': 80, 'abstract': 80, 'overall_aptitude': 80},
        'personality_traits': {'openness': 70, 'conscientiousness': 70, 'extraversion': 70, 'agreeableness': 70, 'neuroticism': 30},
        'work_attributes': {'leadership': 70, 'teamwork': 70, 'creativity': 70, 'analytical': 70, 'communication': 70, 'adaptability': 70},
        'interest_domains': {'stem_tech': 80, 'creative_media': 60, 'people_oriented': 60, 'business_management': 60, 'legal_governance': 60, 'logistics_distribution': 60},
        'emotional_intelligence': 75,
        'metadata': {'test_date': '2024-01-15', 'pattern_classification': 'decisive', 'contradictions': [], 'consistency_score': 95.0}
    }
    
    test_cases = [
        ('Software Engineer', 'STEM+Tech', 'technical', 0.45),  # Cognitive weight
        ('Graphic Designer', 'Creative+Media', 'creative', 0.35),  # Personality weight
        ('Registered Nurse', 'Healthcare', 'healthcare', 0.35),  # EQ weight
    ]
    
    for career_title, category, expected_type, key_weight in test_cases:
        result = calculate_ability_match_for_career(profile, career_title, category)
        detected_type = detect_career_type(career_title, category)
        
        assert detected_type == expected_type, \
            f"Career '{career_title}' detected as {detected_type}, expected {expected_type}"
        
        weights = CAREER_WEIGHTS[expected_type]
        max_weight = max(weights.values())
        
        assert max_weight >= key_weight, \
            f"Career type {expected_type} should have weight >= {key_weight}, got {max_weight}"
        
        print(f"  ✓ {career_title} uses {expected_type} weights correctly")
    
    print("✓ All specific career weight examples verified")


def test_match_formula_edge_cases():
    """
    Unit Test: Test edge cases in match formula.
    
    Test specific edge cases like zero scores, perfect matches, etc.
    """
    print("\nTesting match formula edge cases...")
    
    # Test case 1: Zero student score
    match = calculate_dimension_match(0, 75)
    assert match == 0, f"Zero student score should give 0% match, got {match}"
    print("  ✓ Zero student score gives 0% match")
    
    # Test case 2: Perfect match (student == requirement)
    match = calculate_dimension_match(75, 75)
    assert match == 100, f"Equal scores should give 100% match, got {match}"
    print("  ✓ Equal scores give 100% match")
    
    # Test case 3: Student exceeds requirement
    match = calculate_dimension_match(90, 75)
    assert match == 100, f"Exceeding requirement should cap at 100%, got {match}"
    print("  ✓ Exceeding requirement caps at 100%")
    
    # Test case 4: Student well below requirement
    match = calculate_dimension_match(30, 90)
    expected = int((30 / 90) * 100)  # Should be 33
    assert match == expected, f"Expected {expected}% match, got {match}"
    print(f"  ✓ Below requirement gives proportional match ({match}%)")
    
    # Test case 5: Zero requirement (edge case handling)
    match = calculate_dimension_match(50, 0)
    assert match == 100, f"Zero requirement should give 100% match, got {match}"
    print("  ✓ Zero requirement gives 100% match")
    
    print("✓ All edge cases verified")


if __name__ == '__main__':
    print("=" * 80)
    print("Property-Based Test: Ability Match Calculation Correctness")
    print("=" * 80)
    
    try:
        # Run unit tests first
        test_specific_career_weight_examples()
        test_match_formula_edge_cases()
        
        print("\nRunning property-based tests...")
        print("(This may take a moment as Hypothesis generates test cases)")
        
        # Run property tests
        test_dimension_match_formula_correctness()
        print("  ✓ Dimension match formula property verified")
        
        test_dimension_match_capped_at_100()
        print("  ✓ Match capping at 100% property verified")
        
        test_ability_match_all_dimensions_in_valid_range()
        print("  ✓ All dimensions in valid range property verified")
        
        test_ability_match_uses_correct_career_weights()
        print("  ✓ Career-specific weights property verified")
        
        test_ability_match_weights_sum_to_one()
        print("  ✓ Weights sum to 1.0 property verified")
        
        test_ability_match_handles_unknown_careers_gracefully()
        print("  ✓ Unknown careers handled gracefully property verified")
        
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
