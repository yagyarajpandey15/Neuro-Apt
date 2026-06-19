"""
Property-Based Test for Profile Extraction Completeness

**Property 4: Profile Extraction Completeness**
**Validates: Requirements 2.1, 8.1, 8.2**

This test verifies that for any valid TestResult object, the build_student_profile
function extracts all required fields (cognitive abilities, personality traits,
work attributes, interest domains, EQ) without omissions.

The test generates TestResult objects with all score fields populated and verifies
that build_student_profile() produces complete profiles with all required fields.
"""

from hypothesis import given, strategies as st, settings, assume
from datetime import datetime
from neuroapt.app.utils.profile_builder import build_student_profile, validate_required_fields


class MockTestResult:
    """
    Mock TestResult object for property-based testing.
    
    This class simulates the TestResult database model with all required
    score fields and pattern analysis attributes.
    """
    def __init__(
        self,
        user_id,
        test_id,
        test_date,
        # Cognitive scores
        verbal_score,
        numerical_score,
        abstract_score,
        aptitude_score,
        # Personality scores
        openness_score,
        conscientiousness_score,
        extraversion_score,
        agreeableness_score,
        neuroticism_score,
        # Work attributes
        leadership_score,
        teamwork_score,
        creativity_score,
        analytical_score,
        communication_score,
        adaptability_score,
        # Interest domains
        stem_tech_score,
        creative_media_score,
        people_oriented_score,
        business_management_score,
        legal_governance_score,
        logistics_distribution_score,
        # EQ
        eq_score,
        # Pattern analysis fields
        answer_pattern_flag='decisive',
        contradictions_detected='[]',
        interest_intersection=''
    ):
        self.id = test_id
        self.user_id = user_id
        self.test_date = test_date
        
        # Cognitive scores
        self.verbal_score = verbal_score
        self.numerical_score = numerical_score
        self.abstract_score = abstract_score
        self.aptitude_score = aptitude_score
        
        # Personality scores
        self.openness_score = openness_score
        self.conscientiousness_score = conscientiousness_score
        self.extraversion_score = extraversion_score
        self.agreeableness_score = agreeableness_score
        self.neuroticism_score = neuroticism_score
        
        # Work attributes
        self.leadership_score = leadership_score
        self.teamwork_score = teamwork_score
        self.creativity_score = creativity_score
        self.analytical_score = analytical_score
        self.communication_score = communication_score
        self.adaptability_score = adaptability_score
        
        # Interest domains
        self.stem_tech_score = stem_tech_score
        self.creative_media_score = creative_media_score
        self.people_oriented_score = people_oriented_score
        self.business_management_score = business_management_score
        self.legal_governance_score = legal_governance_score
        self.logistics_distribution_score = logistics_distribution_score
        
        # EQ
        self.eq_score = eq_score
        
        # Pattern analysis fields
        self.answer_pattern_flag = answer_pattern_flag
        self.contradictions_detected = contradictions_detected
        self.interest_intersection = interest_intersection
        
    @property
    def contradictions_list(self):
        """Parse contradictions from JSON string"""
        import json
        try:
            return json.loads(self.contradictions_detected)
        except:
            return []


# Strategy for generating valid test scores (0-100 range)
score_strategy = st.integers(min_value=0, max_value=100)

# Strategy for generating pattern classifications
pattern_classification_strategy = st.sampled_from(['decisive', 'ambivalent', 'random'])

# Strategy for generating interest intersections
interest_intersection_strategy = st.sampled_from([
    '',
    'STEM+Creative',
    'STEM+Business',
    'Business+People-Oriented',
    'Creative+People-Oriented',
    'Legal+Business',
    'STEM+Creative+Business'
])


@st.composite
def mock_test_result_strategy(draw):
    """
    Hypothesis composite strategy for generating MockTestResult objects.
    
    Generates complete TestResult objects with all score fields populated
    with valid values (0-100 range).
    """
    return MockTestResult(
        user_id=draw(st.integers(min_value=1, max_value=10000)),
        test_id=draw(st.integers(min_value=1, max_value=100000)),
        test_date=draw(st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2025, 12, 31)
        )),
        # Cognitive scores
        verbal_score=draw(score_strategy),
        numerical_score=draw(score_strategy),
        abstract_score=draw(score_strategy),
        aptitude_score=draw(score_strategy),
        # Personality scores
        openness_score=draw(score_strategy),
        conscientiousness_score=draw(score_strategy),
        extraversion_score=draw(score_strategy),
        agreeableness_score=draw(score_strategy),
        neuroticism_score=draw(score_strategy),
        # Work attributes
        leadership_score=draw(score_strategy),
        teamwork_score=draw(score_strategy),
        creativity_score=draw(score_strategy),
        analytical_score=draw(score_strategy),
        communication_score=draw(score_strategy),
        adaptability_score=draw(score_strategy),
        # Interest domains
        stem_tech_score=draw(score_strategy),
        creative_media_score=draw(score_strategy),
        people_oriented_score=draw(score_strategy),
        business_management_score=draw(score_strategy),
        legal_governance_score=draw(score_strategy),
        logistics_distribution_score=draw(score_strategy),
        # EQ
        eq_score=draw(score_strategy),
        # Pattern analysis fields
        answer_pattern_flag=draw(pattern_classification_strategy),
        contradictions_detected='[]',
        interest_intersection=draw(interest_intersection_strategy)
    )


@given(test_result=mock_test_result_strategy())
@settings(max_examples=100)
def test_profile_extraction_completeness(test_result):
    """
    Property Test: Profile extraction completeness.
    
    For any valid TestResult object, verify that build_student_profile()
    extracts all required fields without omissions.
    
    Required fields:
    - user_id, test_id
    - cognitive_abilities: verbal, numerical, abstract, overall_aptitude
    - personality_traits: openness, conscientiousness, extraversion, agreeableness, neuroticism
    - work_attributes: leadership, teamwork, creativity, analytical, communication, adaptability
    - interest_domains: stem_tech, creative_media, people_oriented, business_management,
                        legal_governance, logistics_distribution
    - emotional_intelligence
    - metadata: test_date, pattern_classification, contradictions, consistency_score,
                interest_intersection
    """
    # Build the student profile
    profile = build_student_profile(test_result)
    
    # Verify all top-level fields are present
    assert 'user_id' in profile, "Missing user_id"
    assert 'test_id' in profile, "Missing test_id"
    assert 'cognitive_abilities' in profile, "Missing cognitive_abilities"
    assert 'personality_traits' in profile, "Missing personality_traits"
    assert 'work_attributes' in profile, "Missing work_attributes"
    assert 'interest_domains' in profile, "Missing interest_domains"
    assert 'emotional_intelligence' in profile, "Missing emotional_intelligence"
    assert 'metadata' in profile, "Missing metadata"
    
    # Verify cognitive abilities fields
    cognitive = profile['cognitive_abilities']
    assert 'verbal' in cognitive, "Missing cognitive_abilities.verbal"
    assert 'numerical' in cognitive, "Missing cognitive_abilities.numerical"
    assert 'abstract' in cognitive, "Missing cognitive_abilities.abstract"
    assert 'overall_aptitude' in cognitive, "Missing cognitive_abilities.overall_aptitude"
    
    # Verify personality traits fields
    personality = profile['personality_traits']
    assert 'openness' in personality, "Missing personality_traits.openness"
    assert 'conscientiousness' in personality, "Missing personality_traits.conscientiousness"
    assert 'extraversion' in personality, "Missing personality_traits.extraversion"
    assert 'agreeableness' in personality, "Missing personality_traits.agreeableness"
    assert 'neuroticism' in personality, "Missing personality_traits.neuroticism"
    
    # Verify work attributes fields
    work = profile['work_attributes']
    assert 'leadership' in work, "Missing work_attributes.leadership"
    assert 'teamwork' in work, "Missing work_attributes.teamwork"
    assert 'creativity' in work, "Missing work_attributes.creativity"
    assert 'analytical' in work, "Missing work_attributes.analytical"
    assert 'communication' in work, "Missing work_attributes.communication"
    assert 'adaptability' in work, "Missing work_attributes.adaptability"
    
    # Verify interest domains fields
    interests = profile['interest_domains']
    assert 'stem_tech' in interests, "Missing interest_domains.stem_tech"
    assert 'creative_media' in interests, "Missing interest_domains.creative_media"
    assert 'people_oriented' in interests, "Missing interest_domains.people_oriented"
    assert 'business_management' in interests, "Missing interest_domains.business_management"
    assert 'legal_governance' in interests, "Missing interest_domains.legal_governance"
    assert 'logistics_distribution' in interests, "Missing interest_domains.logistics_distribution"
    
    # Verify metadata fields
    metadata = profile['metadata']
    assert 'test_date' in metadata, "Missing metadata.test_date"
    assert 'pattern_classification' in metadata, "Missing metadata.pattern_classification"
    assert 'contradictions' in metadata, "Missing metadata.contradictions"
    assert 'consistency_score' in metadata, "Missing metadata.consistency_score"
    assert 'interest_intersection' in metadata, "Missing metadata.interest_intersection"
    
    # Verify using the built-in validation function
    assert validate_required_fields(profile), \
        "Profile failed validate_required_fields check"


@given(test_result=mock_test_result_strategy())
@settings(max_examples=100)
def test_profile_extraction_score_normalization(test_result):
    """
    Property Test: All extracted scores are normalized to 0-100 range.
    
    For any valid TestResult object, verify that all numeric score fields
    in the extracted profile are within the valid 0-100 range.
    """
    # Build the student profile
    profile = build_student_profile(test_result)
    
    # Check cognitive abilities scores
    for field, value in profile['cognitive_abilities'].items():
        assert 0 <= value <= 100, \
            f"cognitive_abilities.{field} = {value} is out of range [0, 100]"
    
    # Check personality traits scores
    for field, value in profile['personality_traits'].items():
        assert 0 <= value <= 100, \
            f"personality_traits.{field} = {value} is out of range [0, 100]"
    
    # Check work attributes scores
    for field, value in profile['work_attributes'].items():
        assert 0 <= value <= 100, \
            f"work_attributes.{field} = {value} is out of range [0, 100]"
    
    # Check interest domains scores
    for field, value in profile['interest_domains'].items():
        assert 0 <= value <= 100, \
            f"interest_domains.{field} = {value} is out of range [0, 100]"
    
    # Check emotional intelligence score
    assert 0 <= profile['emotional_intelligence'] <= 100, \
        f"emotional_intelligence = {profile['emotional_intelligence']} is out of range [0, 100]"


@given(test_result=mock_test_result_strategy())
@settings(max_examples=100)
def test_profile_extraction_pattern_classification_validity(test_result):
    """
    Property Test: Pattern classification is always valid.
    
    For any valid TestResult object, verify that the extracted pattern
    classification is one of the valid values: 'decisive', 'ambivalent', 'random'.
    """
    # Build the student profile
    profile = build_student_profile(test_result)
    
    pattern = profile['metadata']['pattern_classification']
    valid_patterns = ['decisive', 'ambivalent', 'random']
    
    assert pattern in valid_patterns, \
        f"Invalid pattern classification: {pattern}. Must be one of {valid_patterns}"


@given(test_result=mock_test_result_strategy())
@settings(max_examples=100)
def test_profile_extraction_metadata_consistency(test_result):
    """
    Property Test: Metadata fields are consistent with source data.
    
    For any valid TestResult object, verify that metadata fields accurately
    reflect the source test result data.
    """
    # Build the student profile
    profile = build_student_profile(test_result)
    
    metadata = profile['metadata']
    
    # Verify user_id and test_id match
    assert profile['user_id'] == test_result.user_id, \
        f"user_id mismatch: {profile['user_id']} != {test_result.user_id}"
    assert profile['test_id'] == test_result.id, \
        f"test_id mismatch: {profile['test_id']} != {test_result.id}"
    
    # Verify test_date is a valid ISO format string
    try:
        datetime.fromisoformat(metadata['test_date'])
    except ValueError:
        assert False, f"test_date is not valid ISO format: {metadata['test_date']}"
    
    # Verify consistency_score is in valid range
    assert 0.0 <= metadata['consistency_score'] <= 100.0, \
        f"consistency_score {metadata['consistency_score']} is out of range [0, 100]"
    
    # Verify contradictions is a list
    assert isinstance(metadata['contradictions'], list), \
        f"contradictions should be a list, got {type(metadata['contradictions'])}"
    
    # Verify interest_intersection is a string
    assert isinstance(metadata['interest_intersection'], str), \
        f"interest_intersection should be a string, got {type(metadata['interest_intersection'])}"


@given(test_result=mock_test_result_strategy())
@settings(max_examples=100)
def test_profile_extraction_score_mapping(test_result):
    """
    Property Test: Scores are correctly mapped from TestResult to profile.
    
    For any valid TestResult object, verify that scores in the profile
    match the corresponding scores in the test result (after normalization).
    """
    # Build the student profile
    profile = build_student_profile(test_result)
    
    # Verify cognitive abilities mapping
    assert profile['cognitive_abilities']['verbal'] == test_result.verbal_score, \
        f"Verbal score mismatch: {profile['cognitive_abilities']['verbal']} != {test_result.verbal_score}"
    assert profile['cognitive_abilities']['numerical'] == test_result.numerical_score, \
        f"Numerical score mismatch"
    assert profile['cognitive_abilities']['abstract'] == test_result.abstract_score, \
        f"Abstract score mismatch"
    assert profile['cognitive_abilities']['overall_aptitude'] == test_result.aptitude_score, \
        f"Overall aptitude score mismatch"
    
    # Verify personality traits mapping
    assert profile['personality_traits']['openness'] == test_result.openness_score, \
        f"Openness score mismatch"
    assert profile['personality_traits']['conscientiousness'] == test_result.conscientiousness_score, \
        f"Conscientiousness score mismatch"
    assert profile['personality_traits']['extraversion'] == test_result.extraversion_score, \
        f"Extraversion score mismatch"
    assert profile['personality_traits']['agreeableness'] == test_result.agreeableness_score, \
        f"Agreeableness score mismatch"
    assert profile['personality_traits']['neuroticism'] == test_result.neuroticism_score, \
        f"Neuroticism score mismatch"
    
    # Verify work attributes mapping
    assert profile['work_attributes']['leadership'] == test_result.leadership_score, \
        f"Leadership score mismatch"
    assert profile['work_attributes']['teamwork'] == test_result.teamwork_score, \
        f"Teamwork score mismatch"
    assert profile['work_attributes']['creativity'] == test_result.creativity_score, \
        f"Creativity score mismatch"
    assert profile['work_attributes']['analytical'] == test_result.analytical_score, \
        f"Analytical score mismatch"
    assert profile['work_attributes']['communication'] == test_result.communication_score, \
        f"Communication score mismatch"
    assert profile['work_attributes']['adaptability'] == test_result.adaptability_score, \
        f"Adaptability score mismatch"
    
    # Verify interest domains mapping
    assert profile['interest_domains']['stem_tech'] == test_result.stem_tech_score, \
        f"STEM+Tech score mismatch"
    assert profile['interest_domains']['creative_media'] == test_result.creative_media_score, \
        f"Creative Media score mismatch"
    assert profile['interest_domains']['people_oriented'] == test_result.people_oriented_score, \
        f"People Oriented score mismatch"
    assert profile['interest_domains']['business_management'] == test_result.business_management_score, \
        f"Business Management score mismatch"
    assert profile['interest_domains']['legal_governance'] == test_result.legal_governance_score, \
        f"Legal Governance score mismatch"
    assert profile['interest_domains']['logistics_distribution'] == test_result.logistics_distribution_score, \
        f"Logistics Distribution score mismatch"
    
    # Verify EQ mapping
    assert profile['emotional_intelligence'] == test_result.eq_score, \
        f"EQ score mismatch: {profile['emotional_intelligence']} != {test_result.eq_score}"


def test_profile_extraction_edge_cases():
    """
    Unit Test: Test edge cases for profile extraction.
    
    Test specific edge cases:
    - All scores at minimum (0)
    - All scores at maximum (100)
    - Mixed scores across the range
    """
    print("\nTesting profile extraction edge cases...")
    
    # Test case 1: All zeros
    test_result_zeros = MockTestResult(
        user_id=1,
        test_id=1,
        test_date=datetime(2024, 1, 1),
        verbal_score=0, numerical_score=0, abstract_score=0, aptitude_score=0,
        openness_score=0, conscientiousness_score=0, extraversion_score=0,
        agreeableness_score=0, neuroticism_score=0,
        leadership_score=0, teamwork_score=0, creativity_score=0,
        analytical_score=0, communication_score=0, adaptability_score=0,
        stem_tech_score=0, creative_media_score=0, people_oriented_score=0,
        business_management_score=0, legal_governance_score=0,
        logistics_distribution_score=0,
        eq_score=0
    )
    
    profile = build_student_profile(test_result_zeros)
    assert validate_required_fields(profile), "Profile with all zeros failed validation"
    print("  ✓ All zero scores profile is valid")
    
    # Test case 2: All maximum values
    test_result_max = MockTestResult(
        user_id=2,
        test_id=2,
        test_date=datetime(2024, 1, 1),
        verbal_score=100, numerical_score=100, abstract_score=100, aptitude_score=100,
        openness_score=100, conscientiousness_score=100, extraversion_score=100,
        agreeableness_score=100, neuroticism_score=100,
        leadership_score=100, teamwork_score=100, creativity_score=100,
        analytical_score=100, communication_score=100, adaptability_score=100,
        stem_tech_score=100, creative_media_score=100, people_oriented_score=100,
        business_management_score=100, legal_governance_score=100,
        logistics_distribution_score=100,
        eq_score=100
    )
    
    profile = build_student_profile(test_result_max)
    assert validate_required_fields(profile), "Profile with all max scores failed validation"
    assert profile['cognitive_abilities']['verbal'] == 100
    assert profile['emotional_intelligence'] == 100
    print("  ✓ All maximum scores profile is valid")
    
    # Test case 3: Mixed scores
    test_result_mixed = MockTestResult(
        user_id=3,
        test_id=3,
        test_date=datetime(2024, 1, 1),
        verbal_score=45, numerical_score=78, abstract_score=23, aptitude_score=90,
        openness_score=12, conscientiousness_score=56, extraversion_score=89,
        agreeableness_score=34, neuroticism_score=67,
        leadership_score=50, teamwork_score=25, creativity_score=75,
        analytical_score=88, communication_score=42, adaptability_score=61,
        stem_tech_score=30, creative_media_score=70, people_oriented_score=55,
        business_management_score=85, legal_governance_score=40,
        logistics_distribution_score=15,
        eq_score=63
    )
    
    profile = build_student_profile(test_result_mixed)
    assert validate_required_fields(profile), "Profile with mixed scores failed validation"
    assert profile['cognitive_abilities']['verbal'] == 45
    assert profile['cognitive_abilities']['numerical'] == 78
    assert profile['emotional_intelligence'] == 63
    print("  ✓ Mixed scores profile is valid")
    
    print("✓ All edge cases passed")


if __name__ == '__main__':
    print("=" * 80)
    print("Property-Based Test: Profile Extraction Completeness")
    print("=" * 80)
    
    try:
        # Run unit test for edge cases first
        test_profile_extraction_edge_cases()
        
        print("\nRunning property-based tests...")
        print("(This may take a moment as Hypothesis generates test cases)")
        
        # Run property tests
        test_profile_extraction_completeness()
        print("  ✓ Profile extraction completeness property verified")
        
        test_profile_extraction_score_normalization()
        print("  ✓ Score normalization property verified")
        
        test_profile_extraction_pattern_classification_validity()
        print("  ✓ Pattern classification validity property verified")
        
        test_profile_extraction_metadata_consistency()
        print("  ✓ Metadata consistency property verified")
        
        test_profile_extraction_score_mapping()
        print("  ✓ Score mapping property verified")
        
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
