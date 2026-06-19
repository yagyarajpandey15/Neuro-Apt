from hypothesis import given, settings
from hypothesis import strategies as st
from unittest.mock import MagicMock
from neuroapt.app.utils.statistical_fallback import get_statistical_recommendations

def make_mock_result(stem=50, arts=50, business=50, social=50, healthcare=50, aptitude=60):
    m = MagicMock()
    m.interest_stem = stem
    m.interest_arts = arts
    m.interest_business = business
    m.interest_social = social
    m.interest_healthcare = healthcare
    m.aptitude_score = aptitude
    return m

@given(
    stem=st.floats(0, 100),
    arts=st.floats(0, 100),
    business=st.floats(0, 100),
    social=st.floats(0, 100),
    healthcare=st.floats(0, 100),
    aptitude=st.floats(0, 100)
)
@settings(max_examples=100)
def test_statistical_fallback_always_returns_list(stem, arts, business, social, healthcare, aptitude):
    mock = make_mock_result(stem, arts, business, social, healthcare, aptitude)
    result = get_statistical_recommendations(mock)
    assert isinstance(result, list)
    assert len(result) >= 1
    for item in result:
        assert "title" in item
        assert "category" in item
        assert "match_type" in item
        assert item["match_type"] == "statistical"

def test_selects_from_top_interest_categories():
    mock = make_mock_result(stem=90, arts=20, business=30, social=15, healthcare=10, aptitude=70)
    result = get_statistical_recommendations(mock)
    assert len(result) >= 1

def test_none_returns_empty():
    assert get_statistical_recommendations(None) == []

def test_no_ai_fields_in_output():
    mock = make_mock_result()
    result = get_statistical_recommendations(mock)
    for item in result:
        assert "why_this_fits" not in item
        assert "roadmap" not in item
        assert "reality_check" not in item
