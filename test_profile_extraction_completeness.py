"""
Property-Based Test for Profile Extraction Completeness.

Property 4: Profile Extraction Completeness
For any valid TestResult object, build_student_profile() must extract all
required fields (cognitive abilities, personality traits, work attributes,
interest domains, EQ, metadata) without omissions.

**Validates: Requirements 2.1, 8.1, 8.2**
"""

from datetime import datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from neuroapt.app.utils.profile_builder import (
    build_student_profile,
    validate_required_fields,
)


# ---------------------------------------------------------------------------
# Helper: minimal TestResult-like object
# ---------------------------------------------------------------------------

class GeneratedTestResult:
    """Lightweight stand-in for the SQLAlchemy TestResult model."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def contradictions_list(self):
        return []


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

score_st = st.integers(min_value=0, max_value=100)
pattern_st = st.sampled_from(['decisive', 'ambivalent', 'random'])


@st.composite
def build_test_result_strategy(draw):
    """
    Composite strategy that builds a fully-populated TestResult-like object.
    Every score field is drawn independently to exercise the full 0-100 space.
    """
    return GeneratedTestResult(
        id=draw(st.integers(min_value=1, max_value=10_000)),
        user_id=draw(st.integers(min_value=1, max_value=10_000)),
        test_date=datetime(2024, 1, 1),

        # Cognitive abilities
        verbal_score=draw(score_st),
        numerical_score=draw(score_st),
        abstract_score=draw(score_st),
        aptitude_score=draw(score_st),

        # Personality traits
        openness_score=draw(score_st),
        conscientiousness_score=draw(score_st),
        extraversion_score=draw(score_st),
        agreeableness_score=draw(score_st),
        neuroticism_score=draw(score_st),

        # Work attributes
        leadership_score=draw(score_st),
        teamwork_score=draw(score_st),
        creativity_score=draw(score_st),
        analytical_score=draw(score_st),
        communication_score=draw(score_st),
        adaptability_score=draw(score_st),

        # Interest domains
        stem_tech_score=draw(score_st),
        creative_media_score=draw(score_st),
        people_oriented_score=draw(score_st),
        business_management_score=draw(score_st),
        legal_governance_score=draw(score_st),
        logistics_distribution_score=draw(score_st),

        # Emotional intelligence
        eq_score=draw(score_st),

        # Pattern / metadata
        answer_pattern_flag=draw(pattern_st),
        contradictions_detected='[]',
        interest_intersection=draw(st.text(min_size=0, max_size=50)),
    )


# ---------------------------------------------------------------------------
# Property 4: Profile Extraction Completeness
# ---------------------------------------------------------------------------

@given(test_result=build_test_result_strategy())
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
