"""
Property-Based Test for Confidence Score Calculation

**Property 8: Confidence Score Calculation**
**Validates: Requirements 4.1, 4.5**

This test verifies that for any pattern analysis with known consistency score,
contradiction count, and completion rate, the confidence scorer applies the
correct formula:

    base_score - (contradiction_rate * 50) + completion_bonus

where:
    - base_score = consistency_score (0-100)
    - contradiction_rate = contradiction_count / total_questions
    - contradiction_penalty = contradiction_rate * 50
    - completion_bonus = 10 if completion_rate == 1.0, else 0
    - final score = max(0, min(100, base_score - contradiction_penalty + completion_bonus))
"""

import math
from typing import Any, Dict, Optional
from hypothesis import given, strategies as st, settings, assume
from neuroapt.app.utils.confidence_scorer import calculate_confidence_score


# ---------------------------------------------------------------------------
# Minimal stub for TestResult that the confidence scorer reads from
# ---------------------------------------------------------------------------

class _MockTestResult:
    """Minimal test result stub exposing the fields the confidence scorer uses."""

    def __init__(self, answered_questions: int, total_questions: int):
        self.answered_questions = answered_questions
        self.total_questions = total_questions


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

# Consistency score strategy: floats in [0, 100]
consistency_score_strategy = st.floats(
    min_value=0.0,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
)

# Total questions strategy: between 10 and 200
total_questions_strategy = st.integers(min_value=10, max_value=200)


@st.composite
def confidence_inputs(draw):
    """
    Composite strategy that draws a fully-consistent set of confidence scorer inputs.

    Returns a tuple of:
        (pattern_analysis, mock_test_result, expected_score)

    The expected_score is computed from the formula so the test can assert the
    scorer agrees.
    """
    consistency_score = draw(consistency_score_strategy)
    total_questions = draw(total_questions_strategy)

    # Number of contradictions must not exceed total questions
    contradiction_count = draw(
        st.integers(min_value=0, max_value=total_questions)
    )

    # Completion: either fully complete (rate == 1.0) or partially complete
    # We draw answered_questions from [0, total_questions]
    answered_questions = draw(
        st.integers(min_value=0, max_value=total_questions)
    )

    pattern_classification = draw(
        st.sampled_from(["decisive", "ambivalent", "random"])
    )

    # Build the pattern analysis dict
    contradictions = [
        {
            "question_1_id": i + 1,
            "question_2_id": i + 2,
            "description": f"Contradiction {i}",
            "severity": "medium",
        }
        for i in range(contradiction_count)
    ]

    pattern_analysis = {
        "consistency_score": consistency_score,
        "contradictions": contradictions,
        "pattern_classification": pattern_classification,
    }

    mock_test_result = _MockTestResult(
        answered_questions=answered_questions,
        total_questions=total_questions,
    )

    # ------------------------------------------------------------------
    # Compute expected value using the documented formula
    # ------------------------------------------------------------------
    base_score = consistency_score
    contradiction_rate = contradiction_count / total_questions  # total > 0 by strategy
    contradiction_penalty = contradiction_rate * 50

    completion_rate = answered_questions / total_questions
    completion_bonus = 10 if completion_rate >= 1.0 else 0

    raw = base_score - contradiction_penalty + completion_bonus
    expected_score = int(round(max(0.0, min(100.0, raw))))

    return pattern_analysis, mock_test_result, expected_score


# ---------------------------------------------------------------------------
# Property 8: Confidence Score Calculation
# ---------------------------------------------------------------------------

@given(inputs=confidence_inputs())
@settings(max_examples=500)
def test_confidence_score_formula_applied_correctly(inputs):
    """
    **Property 8: Confidence Score Calculation**
    **Validates: Requirements 4.1, 4.5**

    For any pattern analysis with known consistency score, contradiction count,
    and completion rate, the confidence scorer must apply the formula:

        base_score - (contradiction_rate * 50) + completion_bonus

    capped to [0, 100], where completion_bonus = 10 iff completion_rate == 1.0.
    """
    pattern_analysis, mock_test_result, expected_score = inputs

    result = calculate_confidence_score(pattern_analysis, test_result=mock_test_result)

    calculated_score = result["confidence_score"]

    assert calculated_score == expected_score, (
        f"Formula mismatch.\n"
        f"  consistency_score={pattern_analysis['consistency_score']}\n"
        f"  contradiction_count={len(pattern_analysis['contradictions'])}\n"
        f"  total_questions={mock_test_result.total_questions}\n"
        f"  answered_questions={mock_test_result.answered_questions}\n"
        f"  expected_score={expected_score}, got={calculated_score}"
    )


@given(inputs=confidence_inputs())
@settings(max_examples=300)
def test_confidence_score_is_capped_to_valid_range(inputs):
    """
    **Property 8: Confidence Score Calculation**
    **Validates: Requirements 4.1, 4.5**

    The final confidence score must always be an integer in [0, 100],
    regardless of the raw formula result.
    """
    pattern_analysis, mock_test_result, _ = inputs

    result = calculate_confidence_score(pattern_analysis, test_result=mock_test_result)
    score = result["confidence_score"]

    assert isinstance(score, int), (
        f"confidence_score should be an int, got {type(score)}"
    )
    assert 0 <= score <= 100, (
        f"confidence_score {score} is out of the valid range [0, 100]"
    )


@given(inputs=confidence_inputs())
@settings(max_examples=300)
def test_completion_bonus_applied_only_for_full_completion(inputs):
    """
    **Property 8: Confidence Score Calculation**
    **Validates: Requirements 4.1, 4.5**

    The completion_bonus of 10 must be applied if and only if
    completion_rate == 1.0 (all questions answered).
    """
    pattern_analysis, mock_test_result, _ = inputs

    result = calculate_confidence_score(pattern_analysis, test_result=mock_test_result)
    factors = result["factors"]

    completion_rate = (
        mock_test_result.answered_questions / mock_test_result.total_questions
        if mock_test_result.total_questions > 0
        else 0.0
    )

    if completion_rate >= 1.0:
        assert factors["completion_bonus"] == 10, (
            f"Expected completion_bonus=10 for completion_rate={completion_rate:.4f}, "
            f"got {factors['completion_bonus']}"
        )
    else:
        assert factors["completion_bonus"] == 0, (
            f"Expected completion_bonus=0 for completion_rate={completion_rate:.4f}, "
            f"got {factors['completion_bonus']}"
        )


@given(
    consistency_score=consistency_score_strategy,
    total_questions=total_questions_strategy,
)
@settings(max_examples=300)
def test_higher_contradiction_rate_decreases_score(
    consistency_score, total_questions
):
    """
    **Property 8: Confidence Score Calculation**
    **Validates: Requirements 4.1, 4.5**

    For the same consistency score and full completion, a higher contradiction
    rate must yield a lower or equal confidence score (monotonicity of penalty).
    """
    # Two contradiction counts: low and high
    low_count = 0
    high_count = total_questions  # maximum possible contradictions

    def make_inputs(contradiction_count: int):
        contradictions = [
            {"question_1_id": i, "question_2_id": i + 1, "description": "", "severity": "medium"}
            for i in range(contradiction_count)
        ]
        pattern_analysis = {
            "consistency_score": consistency_score,
            "contradictions": contradictions,
            "pattern_classification": "ambivalent",
        }
        # Full completion so bonus is the same in both cases
        mock_tr = _MockTestResult(
            answered_questions=total_questions,
            total_questions=total_questions,
        )
        return pattern_analysis, mock_tr

    pa_low, tr_low = make_inputs(low_count)
    pa_high, tr_high = make_inputs(high_count)

    result_low = calculate_confidence_score(pa_low, test_result=tr_low)
    result_high = calculate_confidence_score(pa_high, test_result=tr_high)

    assert result_low["confidence_score"] >= result_high["confidence_score"], (
        f"More contradictions should not increase confidence score.\n"
        f"  low contradiction score={result_low['confidence_score']}\n"
        f"  high contradiction score={result_high['confidence_score']}\n"
        f"  consistency_score={consistency_score}, total_questions={total_questions}"
    )


@given(
    consistency_score=consistency_score_strategy,
    total_questions=total_questions_strategy,
    contradiction_count=st.integers(min_value=0, max_value=200),
)
@settings(max_examples=300)
def test_full_completion_gives_higher_or_equal_score_than_partial(
    consistency_score, total_questions, contradiction_count
):
    """
    **Property 8: Confidence Score Calculation**
    **Validates: Requirements 4.1, 4.5**

    For the same consistency score and contradiction count, a fully completed
    test must produce a score >= the score for a partially completed test,
    because full completion adds +10 and partial adds +0.
    """
    assume(contradiction_count <= total_questions)

    contradictions = [
        {"question_1_id": i, "question_2_id": i + 1, "description": "", "severity": "low"}
        for i in range(contradiction_count)
    ]
    pattern_analysis = {
        "consistency_score": consistency_score,
        "contradictions": contradictions,
        "pattern_classification": "decisive",
    }

    # Full completion
    full_tr = _MockTestResult(
        answered_questions=total_questions,
        total_questions=total_questions,
    )
    # Partial completion (at least one question unanswered, if possible)
    partial_answered = max(0, total_questions - 1)
    partial_tr = _MockTestResult(
        answered_questions=partial_answered,
        total_questions=total_questions,
    )

    result_full = calculate_confidence_score(pattern_analysis, test_result=full_tr)
    result_partial = calculate_confidence_score(pattern_analysis, test_result=partial_tr)

    assert result_full["confidence_score"] >= result_partial["confidence_score"], (
        f"Full completion should produce score >= partial completion score.\n"
        f"  full score={result_full['confidence_score']}\n"
        f"  partial score={result_partial['confidence_score']}\n"
        f"  consistency_score={consistency_score}, total_questions={total_questions}, "
        f"  contradiction_count={contradiction_count}"
    )


@given(inputs=confidence_inputs())
@settings(max_examples=300)
def test_factors_dict_matches_formula_components(inputs):
    """
    **Property 8: Confidence Score Calculation**
    **Validates: Requirements 4.1, 4.5**

    The 'factors' dict in the result must reflect the individual components
    of the formula: consistency_contribution matches base_score, and
    contradiction_penalty matches (contradiction_count / total_questions) * 50.
    """
    pattern_analysis, mock_test_result, _ = inputs

    result = calculate_confidence_score(pattern_analysis, test_result=mock_test_result)
    factors = result["factors"]

    base_score = pattern_analysis["consistency_score"]
    contradiction_count = len(pattern_analysis["contradictions"])
    total_questions = mock_test_result.total_questions

    expected_consistency_contribution = int(round(base_score))
    expected_contradiction_penalty = int(
        round((contradiction_count / total_questions) * 50)
    )

    assert factors["consistency_contribution"] == expected_consistency_contribution, (
        f"consistency_contribution mismatch: "
        f"expected {expected_consistency_contribution}, got {factors['consistency_contribution']}"
    )

    assert factors["contradiction_penalty"] == expected_contradiction_penalty, (
        f"contradiction_penalty mismatch: "
        f"expected {expected_contradiction_penalty}, got {factors['contradiction_penalty']}"
    )
