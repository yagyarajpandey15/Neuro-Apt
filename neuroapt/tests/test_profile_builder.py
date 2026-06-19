from hypothesis import given, settings
from hypothesis import strategies as st
from neuroapt.app.utils.profile_builder import detect_interest_intersections

KNOWN_INTERSECTIONS = [
    "STEM+Creative", "STEM+Business", "STEM+People-Oriented",
    "Creative+Business", "Creative+People-Oriented", "Business+People-Oriented",
    "Multi-Domain"
]

@given(
    stem=st.floats(70, 100),
    arts=st.floats(70, 100),
    business=st.floats(0, 50),
    social=st.floats(0, 50),
    healthcare=st.floats(0, 50)
)
@settings(max_examples=100)
def test_interest_intersection_detected_when_two_domains_high(stem, arts, business, social, healthcare):
    profile = {
        "interest_stem": stem,
        "interest_arts": arts,
        "interest_business": business,
        "interest_social": social,
        "interest_healthcare": healthcare
    }
    result = detect_interest_intersections(profile)
    assert result is not None and result != ""
    assert result in KNOWN_INTERSECTIONS or result == "Multi-Domain"

@given(
    stem=st.floats(0, 60),
    arts=st.floats(0, 60),
    business=st.floats(0, 60),
    social=st.floats(0, 60),
    healthcare=st.floats(0, 60)
)
@settings(max_examples=100)
def test_no_intersection_when_one_domain_high(stem, arts, business, social, healthcare):
    profile = {
        "interest_stem": stem,
        "interest_arts": arts,
        "interest_business": business,
        "interest_social": social,
        "interest_healthcare": healthcare
    }
    result = detect_interest_intersections(profile)
    assert result is None or result == ""
