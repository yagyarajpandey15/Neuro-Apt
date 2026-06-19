from hypothesis import given, settings
from hypothesis import strategies as st
from unittest.mock import MagicMock, patch
import json
from datetime import datetime
import pytest
from neuroapt.app.utils.cache_manager import get_cached_analysis, cache_analysis, invalidate_cache

def make_mock_result(ai_analysis=None):
    m = MagicMock()
    m.ai_analysis = ai_analysis
    return m

@given(
    data=st.fixed_dictionaries({
        "careers": st.lists(st.text(min_size=1), min_size=1, max_size=5),
        "score": st.integers(0, 100)
    })
)
@settings(max_examples=100)
def test_cache_store_and_retrieve(data):
    mock_result = make_mock_result()
    with patch("neuroapt.app.utils.cache_manager.db"):
        cache_analysis(mock_result, data)
        assert mock_result.ai_analysis is not None
        
        mock_result2 = make_mock_result(ai_analysis=mock_result.ai_analysis)
        retrieved = get_cached_analysis(mock_result2)
        assert retrieved is not None
        assert retrieved.get("data") == data or retrieved == data

@given(
    data=st.fixed_dictionaries({
        "careers": st.lists(st.text(min_size=1), min_size=1, max_size=3)
    })
)
@settings(max_examples=100)
def test_cached_data_has_iso_timestamp(data):
    mock_result = make_mock_result()
    with patch("neuroapt.app.utils.cache_manager.db"):
        cache_analysis(mock_result, data)
        stored = json.loads(mock_result.ai_analysis)
        assert "generated_at" in stored
        assert "version" in stored
        datetime.fromisoformat(stored["generated_at"])

def test_corrupted_cache_returns_none():
    mock_result = make_mock_result(ai_analysis="NOT VALID JSON {{{")
    result = get_cached_analysis(mock_result)
    assert result is None

def test_db_write_failure_handled():
    mock_result = make_mock_result()
    with patch("neuroapt.app.utils.cache_manager.db") as mock_db:
        mock_db.session.commit.side_effect = Exception("DB error")
        try:
            cache_analysis(mock_result, {"test": "data"})
        except Exception:
            pytest.fail("cache_analysis raised unexpectedly on DB failure")

def test_invalidate_cache_clears_field():
    mock_result = make_mock_result(ai_analysis='{"data": "exists"}')
    with patch("neuroapt.app.utils.cache_manager.db") as mock_db:
        invalidate_cache(mock_result)
        assert mock_result.ai_analysis is None
        mock_db.session.commit.assert_called()
