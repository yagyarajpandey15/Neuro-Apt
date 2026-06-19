import json
import time
import os
import pytest
from unittest.mock import MagicMock, patch
from hypothesis import given, settings
from hypothesis import strategies as st
from neuroapt.app.utils.ai_error_handler import classify_openai_error, with_retry_and_fallback, log_ai_error

FAILURE_MODES = ["timeout", "rate_limit", "auth_error", "malformed_json", "connection_error"]

def get_exception_for_mode(mode):
    try:
        import openai
        mapping = {
            "timeout": openai.APITimeoutError("timeout"),
            "rate_limit": openai.RateLimitError("rate limit", response=MagicMock(), body={}),
            "auth_error": openai.AuthenticationError("auth", response=MagicMock(), body={}),
            "connection_error": openai.APIConnectionError(request=MagicMock()),
        }
        if mode in mapping:
            return mapping[mode]
    except (ImportError, Exception):
        pass
    return json.JSONDecodeError("malformed", "", 0)

@given(mode=st.sampled_from(FAILURE_MODES))
@settings(max_examples=50)
def test_error_handling_never_raises(mode):
    exc = get_exception_for_mode(mode)
    func = MagicMock(side_effect=exc)
    fallback = MagicMock(return_value={"careers": [], "source": "fallback"})
    
    with patch("neuroapt.app.utils.ai_error_handler.time.sleep"):
        result = with_retry_and_fallback(func, fallback, max_retries=1, base_delay=0.01)
    
    assert result["fallback_triggered"] is True
    assert "result" in result

@given(n_failures=st.integers(1, 3))
@settings(max_examples=30)
def test_retry_logic_correctness(n_failures):
    call_count = {"n": 0}
    
    def flaky_func():
        call_count["n"] += 1
        try:
            import openai
            if call_count["n"] <= n_failures:
                raise openai.RateLimitError("rate limit", response=MagicMock(), body={})
        except ImportError:
            if call_count["n"] <= n_failures:
                raise Exception("transient")
        return {"careers": [{"title": "Test"}]}
    
    fallback = MagicMock(return_value={"careers": [], "source": "fallback"})
    
    with patch("neuroapt.app.utils.ai_error_handler.time.sleep"):
        result = with_retry_and_fallback(flaky_func, fallback, max_retries=2, base_delay=0.01)
    
    if n_failures <= 2:
        assert result["fallback_triggered"] is False
    else:
        assert result["fallback_triggered"] is True

def test_malformed_json_classified_correctly():
    exc = json.JSONDecodeError("err", "", 0)
    result = classify_openai_error(exc)
    assert result["error_type"] == "MALFORMED"
    assert result["should_retry"] is False

def test_user_message_is_friendly():
    exc = json.JSONDecodeError("err", "", 0)
    result = classify_openai_error(exc)
    assert "JSONDecodeError" not in result["user_message"]
    assert len(result["user_message"]) > 10

def test_log_written_to_file():
    log_ai_error("test_component", "test_op", "TRANSIENT", "user_123", "test_456", "test details")
    assert os.path.exists("logs/openai_errors.log")
