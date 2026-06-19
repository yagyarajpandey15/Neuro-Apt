from hypothesis import given, settings
from hypothesis import strategies as st
import json
from neuroapt.app.utils.openai_api import filter_alternative_careers, format_profile_for_prompt, build_system_prompt

@given(
    careers=st.lists(
        st.fixed_dictionaries({
            "title": st.text(min_size=1, max_size=30),
            "match_percentage": st.integers(0, 100),
            "why_this_fits": st.text(min_size=1),
            "confidence": st.integers(0, 100)
        }),
        min_size=0, max_size=8
    )
)
@settings(max_examples=100)
def test_alternative_career_filtering(careers):
    result = filter_alternative_careers(careers)
    assert isinstance(result, list)
    for c in result:
        assert c["confidence"] >= 50
    for c in careers:
        if c["confidence"] < 50:
            assert c not in result

def test_profile_formatted_as_valid_json():
    profile = {
        "cognitive_score": 80,
        "personality_score": 75,
        "eq_score": 70,
        "work_style_score": 65,
        "interest_stem": 85,
        "interest_arts": 40,
        "contradiction_rate": 0.05
    }
    result = format_profile_for_prompt(profile)
    parsed = json.loads(result)
    assert "cognitive_score" in parsed

def test_system_prompt_contains_required_instructions():
    prompt = build_system_prompt()
    required = [
        "top_careers", "alternate_careers", "roadmap", "reality_check",
        "match_percentage", "why_this_fits",
        "immediate_1_month", "short_term_3_6_months", "medium_term_6_12_months"
    ]
    for keyword in required:
        assert keyword in prompt, f"Missing keyword in system prompt: {keyword}"

def test_contradictory_profile_handled():
    profile = {
        "cognitive_score": 70,
        "personality_score": 65,
        "eq_score": 60,
        "work_style_score": 55,
        "interest_stem": 80,
        "interest_arts": 75,
        "contradiction_rate": 0.4,
        "contradictions": ["teamwork vs solo", "leadership vs following"]
    }
    result = format_profile_for_prompt(profile)
    assert result is not None
    parsed = json.loads(result)
    assert "contradiction_rate" in parsed or "contradictions" in parsed
