"""
Property-Based Test for Confidence Score Calculation

**Property 8: Confidence Score Calculation**
**Validates: Requirements 4.1, 4.5**

Verifies that for any pattern analysis with known consistency score,
contradiction count, and completion rate, the confidence scorer applies
the correct formula:

    base_score - (contradiction_rate * 50) + completion_bonus

where:
    - base_score        = consistency_score (0-100)
    - contradiction_rate = contradiction_count / total_questions
    - contradiction_penalty = contradiction_rate * 50
    - completion_bonus  = 10 if completion_rate == 1.0, else 0
    - final score       = max(0, min(100, base_score - contradiction_penalty + completion_bonus))
"""

from hypothesis import given, strategies as st, settings, assume
from neuroapt.app.utils.confidence_scorer import calculate_confidence_score


# ---------------------------------------------------------------------------
# Minimal TestResult stub
# ---------------------------------------------------------------------------

class _MockTestResult:
    """Minimal stub that exposes only the fields the confidence scorer reads."""

    def __init__(self, answered_questions: int, total_questions: int):
        self.answered_questions = answered_questions
        self.total_questions = total_questions


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

consistency_score_strategy = st.floats(
    min_value=0.0,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
)

total_questions_strategy = st.integers(min_value=10, max_value=200)


@st.composite
def confidence_inputs(draw):
    """
    Composite strategy that generates a consistent set of confidence scorer inputs
    together with the expected score computed from the documented formula.

    Returns: (pattern_analysis, mock_test_result, expected_score)
    """
    consistency_score = draw(consistency_score_strategy)
    total_questions = draw(total_questions_strategy)
    contradiction_count = draw(st.integers(min_value=0, max_value=total_questions))
    answered_questions = draw(st.integers(min_value=0, max_value=total_questions))
    pattern_classification = draw(st.sampled_from(["decisive", "ambivalent", "random"]))

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

    # Compute the expected score using the documented formula
    base_score = consistency_score
    contradiction_rate = contradiction_count / total_questions  # total_questions >= 10
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
    and completion rate, the scorer must apply the formula:

        base_score - (contradiction_rate * 50) + completion_bonus

    capped to [0, 100].
    """
    pattern_analysis, mock_test_result, expected_score = inputs

    result = calculate_confidence_score(pattern_analysis, test_result=mock_test_result)

    assert result["confidence_score"] == expected_score, (
        f"Formula mismatch.\n"
        f"  consistency_score  = {pattern_analysis['consistency_score']}\n"
        f"  contradiction_count= {len(pattern_analysis['contradictions'])}\n"
        f"  total_questions    = {mock_test_result.total_questions}\n"
        f"  answered_questions = {mock_test_result.answered_questions}\n"
        f"  expected           = {expected_score}, got = {result['confidence_score']}"
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
        f"confidence_score should be int, got {type(score)}"
    )
    assert 0 <= score <= 100, (
        f"confidence_score {score} is outside valid range [0, 100]"
    )


@given(inputs=confidence_inputs())
@settings(max_examples=300)
def test_completion_bonus_applied_only_for_full_completion(inputs):
    """
    **Property 8: Confidence Score Calculation**
    **Validates: Requirements 4.1, 4.5**

    completion_bonus == 10 iff completion_rate == 1.0, else 0.
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
def test_higher_contradiction_rate_decreases_score(consistency_score, total_questions):
    """
    **Property 8: Confidence Score Calculation**
    **Validates: Requirements 4.1, 4.5**

    For the same consistency score and full completion, a higher contradiction
    rate must yield a lower or equal confidence score (penalty is monotone).
    """
    def make_inputs(contradiction_count: int):
        contradictions = [
            {"question_1_id": i, "question_2_id": i + 1, "description": "", "severity": "medium"}
            for i in range(contradiction_count)
        ]
        pa = {
            "consistency_score": consistency_score,
            "contradictions": contradictions,
            "pattern_classification": "ambivalent",
        }
        tr = _MockTestResult(answered_questions=total_questions, total_questions=total_questions)
        return pa, tr

    pa_low, tr_low = make_inputs(0)
    pa_high, tr_high = make_inputs(total_questions)

    score_low = calculate_confidence_score(pa_low, test_result=tr_low)["confidence_score"]
    score_high = calculate_confidence_score(pa_high, test_result=tr_high)["confidence_score"]

    assert score_low >= score_high, (
        f"More contradictions should not increase confidence.\n"
        f"  no-contradiction score = {score_low}\n"
        f"  max-contradiction score= {score_high}\n"
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
    test must produce score >= a partially completed test (+10 vs +0 bonus).
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

    full_tr = _MockTestResult(answered_questions=total_questions, total_questions=total_questions)
    partial_tr = _MockTestResult(answered_questions=max(0, total_questions - 1), total_questions=total_questions)

    score_full = calculate_confidence_score(pattern_analysis, test_result=full_tr)["confidence_score"]
    score_partial = calculate_confidence_score(pattern_analysis, test_result=partial_tr)["confidence_score"]

    assert score_full >= score_partial, (
        f"Full completion should produce score >= partial.\n"
        f"  full={score_full}, partial={score_partial}\n"
        f"  consistency_score={consistency_score}, total_questions={total_questions}, "
        f"  contradiction_count={contradiction_count}"
    )


@given(inputs=confidence_inputs())
@settings(max_examples=300)
def test_factors_dict_matches_formula_components(inputs):
    """
    **Property 8: Confidence Score Calculation**
    **Validates: Requirements 4.1, 4.5**

    The 'factors' dict must reflect the individual formula components:
      - consistency_contribution == round(base_score)
      - contradiction_penalty == round((contradiction_count / total_questions) * 50)
    """
    pattern_analysis, mock_test_result, _ = inputs

    result = calculate_confidence_score(pattern_analysis, test_result=mock_test_result)
    factors = result["factors"]

    base_score = pattern_analysis["consistency_score"]
    contradiction_count = len(pattern_analysis["contradictions"])
    total_questions = mock_test_result.total_questions

    expected_consistency_contribution = int(round(base_score))
    expected_contradiction_penalty = int(round((contradiction_count / total_questions) * 50))

    assert factors["consistency_contribution"] == expected_consistency_contribution, (
        f"consistency_contribution mismatch: "
        f"expected {expected_consistency_contribution}, got {factors['consistency_contribution']}"
    )

    assert factors["contradiction_penalty"] == expected_contradiction_penalty, (
        f"contradiction_penalty mismatch: "
        f"expected {expected_contradiction_penalty}, got {factors['contradiction_penalty']}"
    )
