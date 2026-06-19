"""
Unit Tests for Score Normalization in build_student_profile()

Task 3.3: Write unit tests for score normalization
- Test normalization of scores outside 0-100 range
- Test handling of None values
- Test validation of pattern classification values

These tests target the low-level helper functions directly as well as
the full build_student_profile() pipeline via a lightweight mock.
"""

import json
from datetime import datetime

import pytest

from neuroapt.app.utils.profile_builder import (
    build_student_profile,
    normalize_score,
    validate_pattern_classification,
    validate_required_fields,
)


# ---------------------------------------------------------------------------
# Minimal test-result stub
# ---------------------------------------------------------------------------

class _TR:
    """Minimal stand-in for the SQLAlchemy TestResult model."""

    _DEFAULTS = dict(
        id=1, user_id=1,
        test_date=datetime(2024, 6, 1),
        verbal_score=50, numerical_score=50, abstract_score=50, aptitude_score=50,
        openness_score=50, conscientiousness_score=50, extraversion_score=50,
        agreeableness_score=50, neuroticism_score=50,
        leadership_score=50, teamwork_score=50, creativity_score=50,
        analytical_score=50, communication_score=50, adaptability_score=50,
        stem_tech_score=50, creative_media_score=50, people_oriented_score=50,
        business_management_score=50, legal_governance_score=50,
        logistics_distribution_score=50,
        eq_score=50,
        answer_pattern_flag='decisive',
        contradictions_detected='[]',
        interest_intersection='',
    )

    def __init__(self, **overrides):
        values = dict(self._DEFAULTS)
        values.update(overrides)
        for k, v in values.items():
            setattr(self, k, v)

    @property
    def contradictions_list(self):
        try:
            return json.loads(self.contradictions_detected)
        except Exception:
            return []


# ===========================================================================
# 1. Tests for normalize_score()
# ===========================================================================

class TestNormalizeScore:
    """Unit tests for the normalize_score() helper."""

    # --- Boundary and in-range values ----------------------------------------

    def test_zero_is_returned_as_zero(self):
        assert normalize_score(0) == 0

    def test_hundred_is_returned_as_hundred(self):
        assert normalize_score(100) == 100

    def test_midpoint_is_returned_unchanged(self):
        assert normalize_score(50) == 50

    def test_valid_score_in_range_passes_through(self):
        for v in range(0, 101, 10):
            assert normalize_score(v) == v

    # --- Scores above 100 (over-range) ---------------------------------------

    def test_score_above_100_is_clamped_to_100(self):
        """A score of 101 must be normalised to 100."""
        assert normalize_score(101) == 100

    def test_large_score_is_clamped_to_100(self):
        """Very large scores must be normalised to 100."""
        assert normalize_score(999) == 100

    def test_score_150_is_clamped_to_100(self):
        assert normalize_score(150) == 100

    # --- Scores below 0 (under-range) ----------------------------------------

    def test_negative_score_is_clamped_to_zero(self):
        """A score of -1 must be normalised to 0."""
        assert normalize_score(-1) == 0

    def test_large_negative_score_is_clamped_to_zero(self):
        assert normalize_score(-500) == 0

    # --- None handling -------------------------------------------------------

    def test_none_score_returns_zero(self):
        """None input must be treated as 0, not raise an exception."""
        assert normalize_score(None) == 0

    # --- Custom max_value ----------------------------------------------------

    def test_custom_max_value_normalises_correctly(self):
        """score=40, max_value=80 → (40/80)*100 = 50."""
        assert normalize_score(40, max_value=80) == 50

    def test_zero_max_value_returns_zero(self):
        """Division by zero must be handled gracefully."""
        assert normalize_score(50, max_value=0) == 0

    def test_score_equal_to_max_value_returns_100(self):
        assert normalize_score(200, max_value=200) == 100


# ===========================================================================
# 2. Tests for validate_pattern_classification()
# ===========================================================================

class TestValidatePatternClassification:
    """Unit tests for the validate_pattern_classification() helper."""

    # --- Valid values --------------------------------------------------------

    def test_decisive_is_accepted(self):
        assert validate_pattern_classification('decisive') == 'decisive'

    def test_ambivalent_is_accepted(self):
        assert validate_pattern_classification('ambivalent') == 'ambivalent'

    def test_random_is_accepted(self):
        assert validate_pattern_classification('random') == 'random'

    # --- Case insensitivity --------------------------------------------------

    def test_uppercase_decisive_is_normalised(self):
        assert validate_pattern_classification('DECISIVE') == 'decisive'

    def test_mixed_case_ambivalent_is_normalised(self):
        assert validate_pattern_classification('Ambivalent') == 'ambivalent'

    def test_uppercase_random_is_normalised(self):
        assert validate_pattern_classification('RANDOM') == 'random'

    # --- Whitespace stripping ------------------------------------------------

    def test_padded_decisive_is_normalised(self):
        assert validate_pattern_classification('  decisive  ') == 'decisive'

    def test_padded_ambivalent_is_normalised(self):
        assert validate_pattern_classification('  ambivalent  ') == 'ambivalent'

    # --- None handling -------------------------------------------------------

    def test_none_defaults_to_ambivalent(self):
        """None must default to 'ambivalent', the conservative fallback."""
        result = validate_pattern_classification(None)
        assert result == 'ambivalent'

    # --- Invalid string values -----------------------------------------------

    def test_empty_string_defaults_to_ambivalent(self):
        assert validate_pattern_classification('') == 'ambivalent'

    def test_unknown_string_defaults_to_ambivalent(self):
        assert validate_pattern_classification('unknown') == 'ambivalent'

    def test_numeric_string_defaults_to_ambivalent(self):
        assert validate_pattern_classification('42') == 'ambivalent'

    def test_partial_match_defaults_to_ambivalent(self):
        """'dec' is not a valid classification even though it starts with 'dec'."""
        assert validate_pattern_classification('dec') == 'ambivalent'


# ===========================================================================
# 3. Tests for build_student_profile() – score normalization end-to-end
# ===========================================================================

class TestBuildStudentProfileScoreNormalization:
    """
    End-to-end tests that pass out-of-range or None scores into
    build_student_profile() and verify the output is always clamped to [0, 100].
    """

    # --- Out-of-range scores (above 100) -------------------------------------

    def test_verbal_score_above_100_is_clamped(self):
        tr = _TR(verbal_score=150)
        profile = build_student_profile(tr)
        assert profile['cognitive_abilities']['verbal'] == 100

    def test_numerical_score_above_100_is_clamped(self):
        tr = _TR(numerical_score=200)
        profile = build_student_profile(tr)
        assert profile['cognitive_abilities']['numerical'] == 100

    def test_eq_score_above_100_is_clamped(self):
        tr = _TR(eq_score=999)
        profile = build_student_profile(tr)
        assert profile['emotional_intelligence'] == 100

    def test_personality_score_above_100_is_clamped(self):
        tr = _TR(openness_score=110)
        profile = build_student_profile(tr)
        assert profile['personality_traits']['openness'] == 100

    def test_work_attribute_above_100_is_clamped(self):
        tr = _TR(leadership_score=120)
        profile = build_student_profile(tr)
        assert profile['work_attributes']['leadership'] == 100

    def test_interest_domain_above_100_is_clamped(self):
        tr = _TR(stem_tech_score=500)
        profile = build_student_profile(tr)
        assert profile['interest_domains']['stem_tech'] == 100

    # --- Out-of-range scores (below 0) ----------------------------------------

    def test_verbal_score_negative_is_clamped_to_zero(self):
        tr = _TR(verbal_score=-10)
        profile = build_student_profile(tr)
        assert profile['cognitive_abilities']['verbal'] == 0

    def test_eq_score_negative_is_clamped_to_zero(self):
        tr = _TR(eq_score=-50)
        profile = build_student_profile(tr)
        assert profile['emotional_intelligence'] == 0

    def test_personality_score_negative_is_clamped_to_zero(self):
        tr = _TR(neuroticism_score=-1)
        profile = build_student_profile(tr)
        assert profile['personality_traits']['neuroticism'] == 0

    # --- None score values ---------------------------------------------------

    def test_none_verbal_score_becomes_zero(self):
        tr = _TR(verbal_score=None)
        profile = build_student_profile(tr)
        assert profile['cognitive_abilities']['verbal'] == 0

    def test_none_numerical_score_becomes_zero(self):
        tr = _TR(numerical_score=None)
        profile = build_student_profile(tr)
        assert profile['cognitive_abilities']['numerical'] == 0

    def test_none_abstract_score_becomes_zero(self):
        tr = _TR(abstract_score=None)
        profile = build_student_profile(tr)
        assert profile['cognitive_abilities']['abstract'] == 0

    def test_none_aptitude_score_becomes_zero(self):
        tr = _TR(aptitude_score=None)
        profile = build_student_profile(tr)
        assert profile['cognitive_abilities']['overall_aptitude'] == 0

    def test_none_openness_score_becomes_zero(self):
        tr = _TR(openness_score=None)
        profile = build_student_profile(tr)
        assert profile['personality_traits']['openness'] == 0

    def test_none_eq_score_becomes_zero(self):
        tr = _TR(eq_score=None)
        profile = build_student_profile(tr)
        assert profile['emotional_intelligence'] == 0

    def test_none_leadership_score_becomes_zero(self):
        tr = _TR(leadership_score=None)
        profile = build_student_profile(tr)
        assert profile['work_attributes']['leadership'] == 0

    def test_none_stem_tech_score_becomes_zero(self):
        tr = _TR(stem_tech_score=None)
        profile = build_student_profile(tr)
        assert profile['interest_domains']['stem_tech'] == 0

    def test_profile_with_all_none_scores_is_valid(self):
        """A profile where every score is None must still pass validation."""
        tr = _TR(
            verbal_score=None, numerical_score=None,
            abstract_score=None, aptitude_score=None,
            openness_score=None, conscientiousness_score=None,
            extraversion_score=None, agreeableness_score=None,
            neuroticism_score=None,
            leadership_score=None, teamwork_score=None,
            creativity_score=None, analytical_score=None,
            communication_score=None, adaptability_score=None,
            stem_tech_score=None, creative_media_score=None,
            people_oriented_score=None, business_management_score=None,
            legal_governance_score=None, logistics_distribution_score=None,
            eq_score=None,
        )
        profile = build_student_profile(tr)
        assert validate_required_fields(profile)
        # All numeric values must be 0
        for v in profile['cognitive_abilities'].values():
            assert v == 0
        for v in profile['personality_traits'].values():
            assert v == 0
        for v in profile['work_attributes'].values():
            assert v == 0
        for v in profile['interest_domains'].values():
            assert v == 0
        assert profile['emotional_intelligence'] == 0


# ===========================================================================
# 4. Tests for build_student_profile() – pattern classification validation
# ===========================================================================

class TestBuildStudentProfilePatternClassification:
    """
    Tests that build_student_profile() always stores a valid pattern
    classification in the metadata, even when the source flag is invalid.
    """

    VALID = {'decisive', 'ambivalent', 'random'}

    def test_decisive_flag_is_preserved(self):
        tr = _TR(answer_pattern_flag='decisive')
        profile = build_student_profile(tr)
        assert profile['metadata']['pattern_classification'] == 'decisive'

    def test_ambivalent_flag_is_preserved(self):
        tr = _TR(answer_pattern_flag='ambivalent')
        profile = build_student_profile(tr)
        assert profile['metadata']['pattern_classification'] == 'ambivalent'

    def test_random_flag_is_preserved(self):
        tr = _TR(answer_pattern_flag='random')
        profile = build_student_profile(tr)
        assert profile['metadata']['pattern_classification'] == 'random'

    def test_none_flag_defaults_to_ambivalent(self):
        tr = _TR(answer_pattern_flag=None)
        profile = build_student_profile(tr)
        assert profile['metadata']['pattern_classification'] == 'ambivalent'

    def test_empty_string_flag_defaults_to_ambivalent(self):
        tr = _TR(answer_pattern_flag='')
        profile = build_student_profile(tr)
        assert profile['metadata']['pattern_classification'] == 'ambivalent'

    def test_invalid_string_flag_defaults_to_ambivalent(self):
        tr = _TR(answer_pattern_flag='completely_invalid')
        profile = build_student_profile(tr)
        assert profile['metadata']['pattern_classification'] == 'ambivalent'

    def test_uppercase_flag_is_normalised(self):
        tr = _TR(answer_pattern_flag='DECISIVE')
        profile = build_student_profile(tr)
        assert profile['metadata']['pattern_classification'] == 'decisive'

    def test_pattern_classification_is_always_valid(self):
        """For every flag variant tested, the output must be in the valid set."""
        flags = ['decisive', 'ambivalent', 'random', None, '', 'bad', 'RANDOM']
        for flag in flags:
            tr = _TR(answer_pattern_flag=flag)
            profile = build_student_profile(tr)
            assert profile['metadata']['pattern_classification'] in self.VALID, (
                f"Invalid classification for flag={flag!r}: "
                f"{profile['metadata']['pattern_classification']}"
            )
