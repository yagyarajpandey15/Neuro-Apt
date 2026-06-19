"""
Property-Based Tests for AI Response Validator

This test suite uses Hypothesis for property-based testing of the ai_response_validator
module. It validates that the validator correctly handles valid and invalid AI response
structures across a wide range of generated inputs.

**Property 5: Response Validation Correctness**
**Validates: Requirements 2.3, 8.4, 12.4**

Task 8.2: Write property test for response validation correctness
"""

import pytest
from hypothesis import given, strategies as st
from neuroapt.app.utils.ai_response_validator import (
    validate_and_format_ai_response,
    validate_roadmap,
    validate_reality_check,
    validate_career_match
)


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

@st.composite
def valid_roadmap_strategy(draw):
    """
    Generate a valid roadmap with all required timeframes.
    Each timeframe contains 1-6 action items.
    """
    return {
        'immediate_1_month': draw(st.lists(st.text(min_size=5, max_size=100), min_size=1, max_size=6)),
        'short_term_3_6_months': draw(st.lists(st.text(min_size=5, max_size=100), min_size=1, max_size=6)),
        'medium_term_6_12_months': draw(st.lists(st.text(min_size=5, max_size=100), min_size=1, max_size=6)),
        'skill_development': draw(st.lists(st.text(min_size=3, max_size=50), min_size=0, max_size=8)),
        'resources': draw(st.lists(st.text(min_size=3, max_size=50), min_size=0, max_size=8))
    }


@st.composite
def valid_reality_check_strategy(draw):
    """
    Generate a valid reality check with required descriptive fields.
    """
    return {
        'daily_life': draw(st.text(min_size=10, max_size=200)),
        'work_environment': draw(st.text(min_size=10, max_size=200)),
        'common_challenges': draw(st.text(min_size=10, max_size=200)),
        'stress_factors': draw(st.text(min_size=10, max_size=200)),
        'work_life_balance': draw(st.text(min_size=10, max_size=200))
    }


@st.composite
def valid_career_match_strategy(draw):
    """
    Generate a valid career match with all required fields.
    Match percentage is constrained to 0-100 range.
    """
    return {
        'title': draw(st.text(min_size=3, max_size=50).filter(lambda x: x.strip() != '')),
        'match_percentage': draw(st.integers(min_value=0, max_value=100)),
        'category': draw(st.text(min_size=0, max_size=50)),
        'why_this_fits': draw(st.text(min_size=10, max_size=500).filter(lambda x: x.strip() != '')),
        'challenges': draw(st.text(min_size=5, max_size=500)),
        'ability_breakdown': {
            'cognitive_match': draw(st.integers(min_value=0, max_value=100)),
            'personality_match': draw(st.integers(min_value=0, max_value=100)),
            'emotional_intelligence_match': draw(st.integers(min_value=0, max_value=100)),
            'work_style_match': draw(st.integers(min_value=0, max_value=100)),
            'interest_alignment': draw(st.integers(min_value=0, max_value=100))
        },
        'matching_traits': draw(st.lists(st.text(min_size=3, max_size=30), min_size=0, max_size=8)),
        'reality_check': draw(valid_reality_check_strategy()),
        'roadmap': draw(valid_roadmap_strategy()),
        'confidence_score': draw(st.integers(min_value=0, max_value=100))
    }


@st.composite
def valid_ai_response_strategy(draw):
    """
    Generate a valid AI response dict with all required keys and valid counts.
    - top_careers: 3-5 items
    - alternate_careers: 2-4 items
    """
    num_top_careers = draw(st.integers(min_value=3, max_value=5))
    num_alternate_careers = draw(st.integers(min_value=2, max_value=4))
    
    return {
        'top_careers': [draw(valid_career_match_strategy()) for _ in range(num_top_careers)],
        'alternate_careers': [draw(valid_career_match_strategy()) for _ in range(num_alternate_careers)],
        'confidence_analysis': {
            'score': draw(st.integers(min_value=0, max_value=100)),
            'level': draw(st.sampled_from(['HIGH', 'MODERATE', 'LOW', 'UNRELIABLE'])),
            'explanation': draw(st.text(min_size=10, max_size=300))
        },
        'personality_summary': draw(st.text(min_size=10, max_size=500)),
        'unique_strengths': draw(st.lists(st.text(min_size=5, max_size=100), min_size=0, max_size=10)),
        'growth_areas': draw(st.lists(st.text(min_size=5, max_size=100), min_size=0, max_size=10)),
        'emotional_readiness': {
            'summary': draw(st.text(min_size=10, max_size=200)),
            'stress_tolerance': draw(st.sampled_from(['Low', 'Medium', 'High'])),
            'leadership_potential': draw(st.sampled_from(['Low', 'Medium', 'High'])),
            'teamwork_fit': draw(st.sampled_from(['Independent', 'Mixed', 'Team-oriented']))
        },
        'contradiction_analysis': draw(st.text(min_size=10, max_size=300)),
        'parent_report': {
            'summary': draw(st.text(min_size=10, max_size=300)),
            'what_child_is_good_at': draw(st.lists(st.text(min_size=5, max_size=100), min_size=0, max_size=8)),
            'recommended_support': draw(st.lists(st.text(min_size=5, max_size=100), min_size=0, max_size=8)),
            'careers_to_discuss': draw(st.lists(st.text(min_size=3, max_size=50), min_size=0, max_size=8))
        }
    }


@st.composite
def invalid_ai_response_strategy(draw):
    """
    Generate INVALID AI response dicts by removing one or more required keys
    or violating count constraints.
    
    Invalid scenarios:
    1. Missing required top-level keys (top_careers, alternate_careers, etc.)
    2. Wrong number of top_careers (not 3-5)
    3. Wrong number of alternate_careers (not 2-4)
    4. Invalid career match (missing required fields)
    5. Invalid match_percentage (outside 0-100 range)
    6. Missing roadmap timeframes
    """
    invalid_type = draw(st.sampled_from([
        'missing_top_careers',
        'missing_alternate_careers', 
        'missing_confidence_analysis',
        'missing_personality_summary',
        'too_few_top_careers',
        'too_many_top_careers',
        'too_few_alternate_careers',
        'too_many_alternate_careers',
        'invalid_career_missing_title',
        'invalid_career_missing_match_percentage',
        'invalid_career_missing_why_fits',
        'invalid_career_missing_roadmap',
        'invalid_career_missing_reality_check',
        'invalid_match_percentage_negative',
        'invalid_match_percentage_over_100',
        'invalid_roadmap_missing_immediate',
        'invalid_roadmap_missing_short_term',
        'invalid_roadmap_missing_medium_term'
    ]))
    
    # Start with a valid response
    base_response = draw(valid_ai_response_strategy())
    
    # Apply invalidation based on type
    if invalid_type == 'missing_top_careers':
        del base_response['top_careers']
    elif invalid_type == 'missing_alternate_careers':
        del base_response['alternate_careers']
    elif invalid_type == 'missing_confidence_analysis':
        del base_response['confidence_analysis']
    elif invalid_type == 'missing_personality_summary':
        del base_response['personality_summary']
    elif invalid_type == 'too_few_top_careers':
        base_response['top_careers'] = [draw(valid_career_match_strategy()) for _ in range(draw(st.integers(min_value=0, max_value=2)))]
    elif invalid_type == 'too_many_top_careers':
        base_response['top_careers'] = [draw(valid_career_match_strategy()) for _ in range(draw(st.integers(min_value=6, max_value=10)))]
    elif invalid_type == 'too_few_alternate_careers':
        base_response['alternate_careers'] = [draw(valid_career_match_strategy()) for _ in range(draw(st.integers(min_value=0, max_value=1)))]
    elif invalid_type == 'too_many_alternate_careers':
        base_response['alternate_careers'] = [draw(valid_career_match_strategy()) for _ in range(draw(st.integers(min_value=5, max_value=10)))]
    elif invalid_type == 'invalid_career_missing_title':
        if base_response['top_careers']:
            del base_response['top_careers'][0]['title']
    elif invalid_type == 'invalid_career_missing_match_percentage':
        if base_response['top_careers']:
            del base_response['top_careers'][0]['match_percentage']
    elif invalid_type == 'invalid_career_missing_why_fits':
        if base_response['top_careers']:
            del base_response['top_careers'][0]['why_this_fits']
    elif invalid_type == 'invalid_career_missing_roadmap':
        if base_response['top_careers']:
            del base_response['top_careers'][0]['roadmap']
    elif invalid_type == 'invalid_career_missing_reality_check':
        if base_response['top_careers']:
            del base_response['top_careers'][0]['reality_check']
    elif invalid_type == 'invalid_match_percentage_negative':
        if base_response['top_careers']:
            base_response['top_careers'][0]['match_percentage'] = draw(st.integers(min_value=-100, max_value=-1))
    elif invalid_type == 'invalid_match_percentage_over_100':
        if base_response['top_careers']:
            base_response['top_careers'][0]['match_percentage'] = draw(st.integers(min_value=101, max_value=200))
    elif invalid_type == 'invalid_roadmap_missing_immediate':
        if base_response['top_careers']:
            del base_response['top_careers'][0]['roadmap']['immediate_1_month']
    elif invalid_type == 'invalid_roadmap_missing_short_term':
        if base_response['top_careers']:
            del base_response['top_careers'][0]['roadmap']['short_term_3_6_months']
    elif invalid_type == 'invalid_roadmap_missing_medium_term':
        if base_response['top_careers']:
            del base_response['top_careers'][0]['roadmap']['medium_term_6_12_months']
    
    return base_response


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestResponseValidationCorrectness:
    """
    Property 5: Response Validation Correctness
    
    For any AI response JSON structure, the validator should accept only those
    containing required fields (top_careers with 3-5 items, alternate_careers
    with 2-4 items, all career match required fields) and reject malformed responses.
    
    Validates: Requirements 2.3, 8.4, 12.4
    """
    
    @given(valid_ai_response_strategy())
    def test_valid_responses_pass_validation(self, response_dict):
        """
        Property: All valid AI responses should pass validation.
        
        Valid responses have:
        - All required top-level keys
        - 3-5 top careers
        - 2-4 alternate careers
        - Each career has all required fields
        - Match percentages in 0-100 range
        - All roadmap timeframes present
        """
        result = validate_and_format_ai_response(response_dict)
        
        # Valid responses should NOT return None
        assert result is not None, f"Valid response was rejected: {response_dict}"
        
        # Check structure is preserved
        assert 'top_careers' in result
        assert 'alternate_careers' in result
        assert 'confidence_analysis' in result
        assert 'personality_summary' in result
        
        # Check counts are correct
        assert 3 <= len(result['top_careers']) <= 5, f"Expected 3-5 top careers, got {len(result['top_careers'])}"
        assert 2 <= len(result['alternate_careers']) <= 4, f"Expected 2-4 alternate careers, got {len(result['alternate_careers'])}"
        
        # Check each career has required fields
        for career in result['top_careers']:
            assert 'title' in career
            assert 'match_percentage' in career
            assert 'why_this_fits' in career
            assert 'roadmap' in career
            assert 'reality_check' in career
            assert 0 <= career['match_percentage'] <= 100
    
    @given(invalid_ai_response_strategy())
    def test_invalid_responses_fail_validation(self, response_dict):
        """
        Property: All invalid AI responses should fail validation (return None).
        
        Invalid responses have one or more of:
        - Missing required top-level keys
        - Wrong number of careers (not 3-5 top, not 2-4 alternate)
        - Missing required career fields
        - Match percentages outside 0-100 range
        - Missing roadmap timeframes
        """
        result = validate_and_format_ai_response(response_dict)
        
        # Invalid responses should return None
        assert result is None, f"Invalid response was accepted: {response_dict}"
    
    @given(st.sampled_from([None, {}, [], "", 123, True]))
    def test_completely_invalid_input_rejected(self, invalid_input):
        """
        Property: Non-dict inputs or empty dicts should be rejected.
        """
        result = validate_and_format_ai_response(invalid_input)
        assert result is None, f"Invalid input type was accepted: {invalid_input}"


class TestRoadmapValidation:
    """
    Property 10: Roadmap Structure Validation
    
    For any generated roadmap, the validator should accept only roadmaps
    containing all three required timeframes.
    
    Validates: Requirements 6.2
    """
    
    @given(valid_roadmap_strategy())
    def test_valid_roadmaps_pass_validation(self, roadmap):
        """
        Property: All roadmaps with all three timeframes should be valid.
        """
        result = validate_roadmap(roadmap)
        assert result is True, f"Valid roadmap was rejected: {roadmap}"
    
    @given(valid_roadmap_strategy(), st.sampled_from(['immediate_1_month', 'short_term_3_6_months', 'medium_term_6_12_months']))
    def test_roadmaps_missing_timeframe_fail_validation(self, roadmap, missing_key):
        """
        Property: Roadmaps missing any required timeframe should be invalid.
        """
        # Remove one required timeframe
        del roadmap[missing_key]
        
        result = validate_roadmap(roadmap)
        assert result is False, f"Roadmap missing {missing_key} was accepted: {roadmap}"
    
    @given(st.sampled_from([None, {}, [], "", 123, True]))
    def test_invalid_roadmap_input_rejected(self, invalid_input):
        """
        Property: Non-dict inputs or empty dicts should be rejected as roadmaps.
        """
        result = validate_roadmap(invalid_input)
        assert result is False, f"Invalid roadmap input was accepted: {invalid_input}"


class TestCareerMatchValidation:
    """
    Additional property tests for individual career match validation.
    """
    
    @given(valid_career_match_strategy())
    def test_valid_career_matches_pass_validation(self, career):
        """
        Property: All valid career matches should pass validation.
        """
        result = validate_career_match(career)
        
        assert result is not None, f"Valid career match was rejected: {career}"
        assert result['title'] == career['title'].strip()
        assert 0 <= result['match_percentage'] <= 100
    
    @given(valid_career_match_strategy(), st.sampled_from(['title', 'match_percentage', 'why_this_fits', 'roadmap', 'reality_check']))
    def test_career_matches_missing_required_field_fail(self, career, missing_field):
        """
        Property: Career matches missing any required field should be invalid.
        """
        del career[missing_field]
        
        result = validate_career_match(career)
        assert result is None, f"Career match missing {missing_field} was accepted: {career}"
    
    @given(valid_career_match_strategy(), st.integers(min_value=-100, max_value=-1) | st.integers(min_value=101, max_value=200))
    def test_career_matches_with_invalid_percentage_fail(self, career, invalid_percentage):
        """
        Property: Career matches with match_percentage outside 0-100 should be invalid.
        """
        career['match_percentage'] = invalid_percentage
        
        result = validate_career_match(career)
        assert result is None, f"Career match with invalid percentage {invalid_percentage} was accepted"


class TestRealityCheckValidation:
    """
    Property tests for reality check validation.
    """
    
    @given(valid_reality_check_strategy())
    def test_valid_reality_checks_pass_validation(self, reality_check):
        """
        Property: All valid reality checks should pass validation.
        """
        result = validate_reality_check(reality_check)
        assert result is True, f"Valid reality check was rejected: {reality_check}"
    
    @given(st.sampled_from([None, {}, [], "", 123, True]))
    def test_invalid_reality_check_input_rejected(self, invalid_input):
        """
        Property: Non-dict inputs or empty dicts should be rejected as reality checks.
        """
        result = validate_reality_check(invalid_input)
        assert result is False, f"Invalid reality check input was accepted: {invalid_input}"


class TestEdgeCases:
    """
    Edge case tests for boundary conditions.
    """
    
    @given(st.integers(min_value=3, max_value=5))
    def test_top_careers_boundary_counts(self, count):
        """
        Property: Exactly 3, 4, or 5 top careers should be valid.
        """
        response = {
            'top_careers': [self._create_minimal_valid_career() for _ in range(count)],
            'alternate_careers': [self._create_minimal_valid_career() for _ in range(2)],
            'confidence_analysis': {},
            'personality_summary': 'Test'
        }
        
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert len(result['top_careers']) == count
    
    @given(st.integers(min_value=2, max_value=4))
    def test_alternate_careers_boundary_counts(self, count):
        """
        Property: Exactly 2, 3, or 4 alternate careers should be valid.
        """
        response = {
            'top_careers': [self._create_minimal_valid_career() for _ in range(3)],
            'alternate_careers': [self._create_minimal_valid_career() for _ in range(count)],
            'confidence_analysis': {},
            'personality_summary': 'Test'
        }
        
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert len(result['alternate_careers']) == count
    
    @given(st.integers(min_value=0, max_value=100))
    def test_match_percentage_all_valid_values(self, percentage):
        """
        Property: All match percentages from 0-100 should be valid.
        """
        career = self._create_minimal_valid_career()
        career['match_percentage'] = percentage
        
        response = {
            'top_careers': [career] + [self._create_minimal_valid_career() for _ in range(2)],
            'alternate_careers': [self._create_minimal_valid_career() for _ in range(2)],
            'confidence_analysis': {},
            'personality_summary': 'Test'
        }
        
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert result['top_careers'][0]['match_percentage'] == percentage
    
    def _create_minimal_valid_career(self):
        """Helper to create a minimal valid career for boundary tests."""
        return {
            'title': 'Test Career',
            'match_percentage': 50,
            'why_this_fits': 'Test explanation',
            'challenges': 'Test challenges',
            'roadmap': {
                'immediate_1_month': ['Step 1'],
                'short_term_3_6_months': ['Step 2'],
                'medium_term_6_12_months': ['Step 3']
            },
            'reality_check': {
                'daily_life': 'Test daily life',
                'work_environment': 'Test environment',
                'common_challenges': 'Test challenges'
            }
        }


from hypothesis import given, settings
from hypothesis import strategies as st
import json
from neuroapt.app.utils.ai_response_validator import validate_and_format_ai_response, format_career_matches

def make_valid_roadmap():
    return {
        "immediate_1_month": "Start here",
        "short_term_3_6_months": "Build skills",
        "medium_term_6_12_months": "Get job"
    }

def make_valid_career(title="Engineer", pct=75):
    return {
        "title": title,
        "match_percentage": pct,
        "why_this_fits": "Good fit",
        "challenges": "Hard work",
        "roadmap": make_valid_roadmap(),
        "reality_check": {
            "daily_life": "Busy",
            "work_environment": "Office",
            "stress_factors": "Deadlines",
            "work_life_balance": "Moderate"
        }
    }

def make_valid_response(n_top=4, n_alt=3):
    return {
        "top_careers": [make_valid_career(f"Career {i}", 70+i) for i in range(n_top)],
        "alternate_careers": [make_valid_career(f"Alt {i}", 55+i) for i in range(n_alt)],
        "confidence_analysis": {"level": "HIGH", "score": 85},
        "personality_summary": "Analytical and creative"
    }

@given(n_top=st.integers(3, 5), n_alt=st.integers(2, 4))
@settings(max_examples=100)
def test_valid_response_passes_validation_property(n_top, n_alt):
    response = make_valid_response(n_top, n_alt)
    result = validate_and_format_ai_response(response)
    assert result is True or result == response or result is not None

@given(missing_key=st.sampled_from(["top_careers", "alternate_careers", "confidence_analysis", "personality_summary"]))
@settings(max_examples=100)
def test_missing_top_level_key_fails_property(missing_key):
    response = make_valid_response()
    del response[missing_key]
    result = validate_and_format_ai_response(response)
    assert result is False or result is None

@given(present_keys=st.sets(st.sampled_from(["immediate_1_month", "short_term_3_6_months", "medium_term_6_12_months"]), min_size=1, max_size=2))
@settings(max_examples=100)
def test_incomplete_roadmap_fails_property(present_keys):
    roadmap = {k: "content" for k in present_keys}
    career = make_valid_career()
    career["roadmap"] = roadmap
    response = make_valid_response()
    response["top_careers"][0] = career
    result = validate_and_format_ai_response(response)
    assert result is False or result is None

@given(n_careers=st.integers(1, 5))
@settings(max_examples=100)
def test_format_career_matches_produces_valid_json_property(n_careers):
    careers = [make_valid_career(f"Career {i}", 60+i*5) for i in range(n_careers)]
    result = format_career_matches(careers)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    for c in parsed:
        assert "title" in c
        assert 0 <= c["match_percentage"] <= 100

@given(
    cognitive=st.floats(0, 100),
    personality=st.floats(0, 100),
    eq=st.floats(0, 100),
    work_style=st.floats(0, 100)
)
@settings(max_examples=100)
def test_serialization_roundtrip_integrity_property(cognitive, personality, eq, work_style):
    profile = {
        "cognitive_score": cognitive,
        "personality_score": personality,
        "eq_score": eq,
        "work_style_score": work_style,
        "interest_domains": {"stem": 75, "arts": 60}
    }
    serialized = json.dumps(profile)
    deserialized = json.loads(serialized)
    assert abs(deserialized["cognitive_score"] - cognitive) < 1e-6
    assert abs(deserialized["personality_score"] - personality) < 1e-6

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
