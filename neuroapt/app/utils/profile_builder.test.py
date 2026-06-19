"""
Unit tests for profile_builder module.

Tests the build_student_profile function and supporting utilities.
"""

import pytest
from datetime import datetime
from neuroapt.app.utils.profile_builder import (
    build_student_profile,
    normalize_score,
    validate_pattern_classification,
    extract_cognitive_abilities,
    extract_personality_traits,
    extract_work_attributes,
    extract_interest_domains,
    extract_metadata,
    validate_required_fields
)


class MockTestResult:
    """Mock TestResult object for testing"""
    def __init__(self):
        self.id = 1
        self.user_id = 123
        self.test_date = datetime(2024, 1, 15, 10, 30, 0)
        
        # Cognitive scores
        self.verbal_score = 85
        self.numerical_score = 90
        self.abstract_score = 78
        self.aptitude_score = 84
        
        # Personality scores
        self.openness_score = 75
        self.conscientiousness_score = 88
        self.extraversion_score = 65
        self.agreeableness_score = 80
        self.neuroticism_score = 45
        
        # Work attributes
        self.leadership_score = 70
        self.teamwork_score = 85
        self.creativity_score = 72
        self.analytical_score = 90
        self.communication_score = 78
        self.adaptability_score = 82
        
        # Interest domains
        self.stem_tech_score = 88
        self.creative_media_score = 65
        self.people_oriented_score = 55
        self.business_management_score = 70
        self.legal_governance_score = 48
        self.logistics_distribution_score = 52
        
        # EQ
        self.eq_score = 76
        
        # Pattern analysis fields
        self.answer_pattern_flag = 'decisive'
        self.contradictions_detected = '[]'
        self.interest_intersection = 'STEM+Business'
        
    @property
    def contradictions_list(self):
        """Mock contradictions_list property"""
        return []


def test_normalize_score_within_range():
    """Test that normalize_score keeps scores in 0-100 range"""
    assert normalize_score(50) == 50
    assert normalize_score(0) == 0
    assert normalize_score(100) == 100


def test_normalize_score_clamps_values():
    """Test that normalize_score clamps values outside 0-100"""
    assert normalize_score(150) == 100
    assert normalize_score(-10) == 0


def test_normalize_score_handles_none():
    """Test that normalize_score handles None values"""
    assert normalize_score(None) == 0


def test_normalize_score_with_custom_max():
    """Test normalization with custom maximum value"""
    assert normalize_score(50, max_value=50) == 100
    assert normalize_score(25, max_value=50) == 50
    assert normalize_score(0, max_value=50) == 0


def test_validate_pattern_classification_valid():
    """Test pattern classification validation with valid values"""
    assert validate_pattern_classification('decisive') == 'decisive'
    assert validate_pattern_classification('ambivalent') == 'ambivalent'
    assert validate_pattern_classification('random') == 'random'


def test_validate_pattern_classification_case_insensitive():
    """Test pattern classification handles case variations"""
    assert validate_pattern_classification('DECISIVE') == 'decisive'
    assert validate_pattern_classification('Ambivalent') == 'ambivalent'
    assert validate_pattern_classification('  Random  ') == 'random'


def test_validate_pattern_classification_invalid():
    """Test pattern classification returns default for invalid values"""
    assert validate_pattern_classification('invalid') == 'ambivalent'
    assert validate_pattern_classification('') == 'ambivalent'
    assert validate_pattern_classification(None) == 'ambivalent'


def test_extract_cognitive_abilities():
    """Test cognitive abilities extraction"""
    mock_result = MockTestResult()
    abilities = extract_cognitive_abilities(mock_result)
    
    assert abilities['verbal'] == 85
    assert abilities['numerical'] == 90
    assert abilities['abstract'] == 78
    assert abilities['overall_aptitude'] == 84


def test_extract_personality_traits():
    """Test personality traits extraction"""
    mock_result = MockTestResult()
    traits = extract_personality_traits(mock_result)
    
    assert traits['openness'] == 75
    assert traits['conscientiousness'] == 88
    assert traits['extraversion'] == 65
    assert traits['agreeableness'] == 80
    assert traits['neuroticism'] == 45


def test_extract_work_attributes():
    """Test work attributes extraction"""
    mock_result = MockTestResult()
    attributes = extract_work_attributes(mock_result)
    
    assert attributes['leadership'] == 70
    assert attributes['teamwork'] == 85
    assert attributes['creativity'] == 72
    assert attributes['analytical'] == 90
    assert attributes['communication'] == 78
    assert attributes['adaptability'] == 82


def test_extract_interest_domains():
    """Test interest domains extraction"""
    mock_result = MockTestResult()
    domains = extract_interest_domains(mock_result)
    
    assert domains['stem_tech'] == 88
    assert domains['creative_media'] == 65
    assert domains['people_oriented'] == 55
    assert domains['business_management'] == 70
    assert domains['legal_governance'] == 48
    assert domains['logistics_distribution'] == 52


def test_extract_metadata():
    """Test metadata extraction"""
    mock_result = MockTestResult()
    metadata = extract_metadata(mock_result)
    
    assert metadata['test_date'] == '2024-01-15T10:30:00'
    assert metadata['pattern_classification'] == 'decisive'
    assert metadata['contradictions'] == []
    assert metadata['consistency_score'] == 100.0
    assert metadata['interest_intersection'] == 'STEM+Business'


def test_extract_metadata_with_contradictions():
    """Test metadata extraction with contradictions"""
    mock_result = MockTestResult()
    mock_result.contradictions_detected = '[{"q1": 1, "q2": 5}, {"q1": 3, "q2": 8}]'
    
    # Mock contradictions_list to return parsed list
    class MockWithContradictions(MockTestResult):
        @property
        def contradictions_list(self):
            return [{"q1": 1, "q2": 5}, {"q1": 3, "q2": 8}]
    
    mock_result_with_contradictions = MockWithContradictions()
    metadata = extract_metadata(mock_result_with_contradictions)
    
    assert len(metadata['contradictions']) == 2
    assert metadata['consistency_score'] == 80.0  # 100 - (2 * 10)


def test_validate_required_fields_valid_profile():
    """Test validation passes for complete profile"""
    mock_result = MockTestResult()
    profile = build_student_profile(mock_result)
    
    assert validate_required_fields(profile) == True


def test_validate_required_fields_missing_top_level():
    """Test validation fails when top-level field is missing"""
    profile = {
        'user_id': 1,
        'test_id': 1,
        # Missing cognitive_abilities
        'personality_traits': {},
        'work_attributes': {},
        'interest_domains': {},
        'emotional_intelligence': 50,
        'metadata': {}
    }
    
    assert validate_required_fields(profile) == False


def test_validate_required_fields_invalid_pattern():
    """Test validation fails for invalid pattern classification"""
    mock_result = MockTestResult()
    profile = build_student_profile(mock_result)
    profile['metadata']['pattern_classification'] = 'invalid'
    
    assert validate_required_fields(profile) == False


def test_build_student_profile_complete():
    """Test build_student_profile creates complete valid profile"""
    mock_result = MockTestResult()
    profile = build_student_profile(mock_result)
    
    # Check top-level structure
    assert profile['user_id'] == 123
    assert profile['test_id'] == 1
    assert 'cognitive_abilities' in profile
    assert 'personality_traits' in profile
    assert 'work_attributes' in profile
    assert 'interest_domains' in profile
    assert profile['emotional_intelligence'] == 76
    assert 'metadata' in profile
    
    # Validate it passes validation
    assert validate_required_fields(profile) == True


def test_build_student_profile_all_scores_normalized():
    """Test that all scores are in 0-100 range"""
    mock_result = MockTestResult()
    profile = build_student_profile(mock_result)
    
    # Check cognitive abilities
    for value in profile['cognitive_abilities'].values():
        assert 0 <= value <= 100
    
    # Check personality traits
    for value in profile['personality_traits'].values():
        assert 0 <= value <= 100
    
    # Check work attributes
    for value in profile['work_attributes'].values():
        assert 0 <= value <= 100
    
    # Check interest domains
    for value in profile['interest_domains'].values():
        assert 0 <= value <= 100
    
    # Check emotional intelligence
    assert 0 <= profile['emotional_intelligence'] <= 100


def test_build_student_profile_with_none_raises_error():
    """Test that build_student_profile raises error for None input"""
    with pytest.raises(ValueError, match="test_result cannot be None"):
        build_student_profile(None)


def test_build_student_profile_metadata_structure():
    """Test metadata contains all required fields"""
    mock_result = MockTestResult()
    profile = build_student_profile(mock_result)
    
    metadata = profile['metadata']
    assert 'test_date' in metadata
    assert 'pattern_classification' in metadata
    assert 'contradictions' in metadata
    assert 'consistency_score' in metadata
    assert 'interest_intersection' in metadata


def test_profile_with_zero_scores():
    """Test profile building with all zero scores"""
    mock_result = MockTestResult()
    
    # Set all scores to zero
    mock_result.verbal_score = 0
    mock_result.numerical_score = 0
    mock_result.abstract_score = 0
    mock_result.aptitude_score = 0
    mock_result.openness_score = 0
    mock_result.conscientiousness_score = 0
    mock_result.extraversion_score = 0
    mock_result.agreeableness_score = 0
    mock_result.neuroticism_score = 0
    mock_result.leadership_score = 0
    mock_result.teamwork_score = 0
    mock_result.creativity_score = 0
    mock_result.analytical_score = 0
    mock_result.communication_score = 0
    mock_result.adaptability_score = 0
    mock_result.stem_tech_score = 0
    mock_result.creative_media_score = 0
    mock_result.people_oriented_score = 0
    mock_result.business_management_score = 0
    mock_result.legal_governance_score = 0
    mock_result.logistics_distribution_score = 0
    mock_result.eq_score = 0
    
    profile = build_student_profile(mock_result)
    
    # Should still create valid profile with zeros
    assert validate_required_fields(profile) == True
    assert profile['emotional_intelligence'] == 0


def test_profile_with_max_scores():
    """Test profile building with maximum scores"""
    mock_result = MockTestResult()
    
    # Set all scores to 100
    mock_result.verbal_score = 100
    mock_result.numerical_score = 100
    mock_result.eq_score = 100
    
    profile = build_student_profile(mock_result)
    
    assert profile['cognitive_abilities']['verbal'] == 100
    assert profile['cognitive_abilities']['numerical'] == 100
    assert profile['emotional_intelligence'] == 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


# ---------------------------------------------------------------------------
# Property-Based Tests
# ---------------------------------------------------------------------------

from hypothesis import given, settings
from hypothesis import strategies as st


# ---- Strategies -----------------------------------------------------------

# All score fields on a TestResult are ints in 0-100.
score_st = st.integers(min_value=0, max_value=100)

# Pattern classification values accepted by validate_pattern_classification.
pattern_st = st.sampled_from(['decisive', 'ambivalent', 'random'])


def make_test_result(draw):
    """
    Composite strategy that builds a fully-populated MockTestResult via Hypothesis draw.
    All score fields are drawn independently from score_st.
    """

    class GeneratedTestResult:
        """Dynamically generated TestResult-like object."""
        pass

    obj = GeneratedTestResult()

    obj.id       = draw(st.integers(min_value=1, max_value=10_000))
    obj.user_id  = draw(st.integers(min_value=1, max_value=10_000))
    obj.test_date = datetime(2024, 1, 1)  # fixed; date format is covered by unit tests

    # Cognitive abilities
    obj.verbal_score    = draw(score_st)
    obj.numerical_score = draw(score_st)
    obj.abstract_score  = draw(score_st)
    obj.aptitude_score  = draw(score_st)

    # Personality traits
    obj.openness_score         = draw(score_st)
    obj.conscientiousness_score = draw(score_st)
    obj.extraversion_score     = draw(score_st)
    obj.agreeableness_score    = draw(score_st)
    obj.neuroticism_score      = draw(score_st)

    # Work attributes
    obj.leadership_score   = draw(score_st)
    obj.teamwork_score     = draw(score_st)
    obj.creativity_score   = draw(score_st)
    obj.analytical_score   = draw(score_st)
    obj.communication_score = draw(score_st)
    obj.adaptability_score = draw(score_st)

    # Interest domains
    obj.stem_tech_score           = draw(score_st)
    obj.creative_media_score      = draw(score_st)
    obj.people_oriented_score     = draw(score_st)
    obj.business_management_score = draw(score_st)
    obj.legal_governance_score    = draw(score_st)
    obj.logistics_distribution_score = draw(score_st)

    # EQ
    obj.eq_score = draw(score_st)

    # Pattern / metadata
    obj.answer_pattern_flag = draw(pattern_st)
    obj.contradictions_detected = '[]'
    obj.interest_intersection   = draw(st.text(min_size=0, max_size=50))

    # contradictions_list property expected by extract_metadata
    obj.contradictions_list = []

    return obj


test_result_st = st.composite(make_test_result)()


# ---- Property 4 -----------------------------------------------------------

@given(test_result=test_result_st)
@settings(max_examples=100)
def test_property4_profile_extraction_completeness(test_result):
    """
    **Property 4: Profile Extraction Completeness**

    For any valid TestResult object with all score fields populated,
    build_student_profile() must extract ALL required fields without omissions.

    **Validates: Requirements 2.1, 8.1, 8.2**
    """
    profile = build_student_profile(test_result)

    # ---- Top-level keys must all be present --------------------------------
    required_top_level = [
        'user_id',
        'test_id',
        'cognitive_abilities',
        'personality_traits',
        'work_attributes',
        'interest_domains',
        'emotional_intelligence',
        'metadata',
    ]
    for field in required_top_level:
        assert field in profile, f"Missing top-level field: {field}"

    # ---- cognitive_abilities sub-fields ------------------------------------
    required_cognitive = ['verbal', 'numerical', 'abstract', 'overall_aptitude']
    for field in required_cognitive:
        assert field in profile['cognitive_abilities'], (
            f"Missing cognitive_abilities field: {field}"
        )

    # ---- personality_traits sub-fields -------------------------------------
    required_personality = [
        'openness', 'conscientiousness', 'extraversion',
        'agreeableness', 'neuroticism',
    ]
    for field in required_personality:
        assert field in profile['personality_traits'], (
            f"Missing personality_traits field: {field}"
        )

    # ---- work_attributes sub-fields ----------------------------------------
    required_work = [
        'leadership', 'teamwork', 'creativity',
        'analytical', 'communication', 'adaptability',
    ]
    for field in required_work:
        assert field in profile['work_attributes'], (
            f"Missing work_attributes field: {field}"
        )

    # ---- interest_domains sub-fields ---------------------------------------
    required_interests = [
        'stem_tech', 'creative_media', 'people_oriented',
        'business_management', 'legal_governance', 'logistics_distribution',
    ]
    for field in required_interests:
        assert field in profile['interest_domains'], (
            f"Missing interest_domains field: {field}"
        )

    # ---- metadata sub-fields -----------------------------------------------
    required_metadata = [
        'test_date', 'pattern_classification',
        'contradictions', 'consistency_score',
    ]
    for field in required_metadata:
        assert field in profile['metadata'], (
            f"Missing metadata field: {field}"
        )

    # ---- No None values in numeric score fields ----------------------------
    assert profile['emotional_intelligence'] is not None

    for key, val in profile['cognitive_abilities'].items():
        assert val is not None, f"cognitive_abilities[{key}] is None"

    for key, val in profile['personality_traits'].items():
        assert val is not None, f"personality_traits[{key}] is None"

    for key, val in profile['work_attributes'].items():
        assert val is not None, f"work_attributes[{key}] is None"

    for key, val in profile['interest_domains'].items():
        assert val is not None, f"interest_domains[{key}] is None"

    # ---- All numeric scores must be in 0-100 range -------------------------
    assert 0 <= profile['emotional_intelligence'] <= 100

    for key, val in profile['cognitive_abilities'].items():
        assert 0 <= val <= 100, f"cognitive_abilities[{key}]={val} out of range"

    for key, val in profile['personality_traits'].items():
        assert 0 <= val <= 100, f"personality_traits[{key}]={val} out of range"

    for key, val in profile['work_attributes'].items():
        assert 0 <= val <= 100, f"work_attributes[{key}]={val} out of range"

    for key, val in profile['interest_domains'].items():
        assert 0 <= val <= 100, f"interest_domains[{key}]={val} out of range"

    # ---- Pattern classification must be one of the three valid values -------
    assert profile['metadata']['pattern_classification'] in (
        'decisive', 'ambivalent', 'random'
    ), (
        f"Invalid pattern_classification: "
        f"{profile['metadata']['pattern_classification']}"
    )

    # ---- Full validation helper must also pass ------------------------------
    assert validate_required_fields(profile), (
        "validate_required_fields() returned False for a generated profile"
    )
