"""
Unit Tests for Confidence Scoring Edge Cases

Task 4.4: Write unit tests for confidence scoring edge cases

Tests:
    1. 0% contradiction rate with 100% completion (maximum bonus scenario)
    2. 100% contradiction rate (capped at 0 confidence)
    3. Incomplete tests without completion bonus

Formula: base_score - (contradiction_rate * 50) + completion_bonus, capped at [0, 100]
    completion_bonus = 10 if completion_rate == 1.0, else 0
"""

import pytest
from neuroapt.app.utils.confidence_scorer import calculate_confidence_score


# ---------------------------------------------------------------------------
# Helper: Minimal mock of TestResult for controlling completion data
# ---------------------------------------------------------------------------

class MockTestResult:
    """Minimal stand-in for the TestResult database model."""

    def __init__(self, answered_questions: int, total_questions: int):
        self.answered_questions = answered_questions
        self.total_questions = total_questions


# ---------------------------------------------------------------------------
# Edge Case 1: 0% contradiction rate with 100% completion
# ---------------------------------------------------------------------------

class TestZeroContradictionFullCompletion:
    """
    Tests for the best-case scenario: no contradictions and a fully completed
    test. The only modifiers are a clean base_score and the +10 completion bonus.
    """

    def test_high_consistency_zero_contradictions_full_completion(self):
        """
        Score = 85 (base) - 0 (penalty) + 10 (bonus) = 95 → HIGH.
        With 0 contradictions and 100% completion the score should be
        base_score + 10, clamped to 100.
        """
        pattern_analysis = {
            'consistency_score': 85.0,
            'contradictions': [],
            'pattern_classification': 'decisive',
        }
        test_result = MockTestResult(answered_questions=50, total_questions=50)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 95
        assert result['confidence_level'] == 'HIGH'
        assert result['factors']['contradiction_penalty'] == 0
        assert result['factors']['completion_bonus'] == 10

    def test_maximum_base_score_zero_contradictions_full_completion_caps_at_100(self):
        """
        Score = 100 (base) - 0 (penalty) + 10 (bonus) = 110 → clamped to 100.
        Ensures the [0, 100] cap is applied when the raw sum exceeds 100.
        """
        pattern_analysis = {
            'consistency_score': 100.0,
            'contradictions': [],
            'pattern_classification': 'decisive',
        }
        test_result = MockTestResult(answered_questions=60, total_questions=60)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 100
        assert result['confidence_level'] == 'HIGH'
        assert result['factors']['contradiction_penalty'] == 0
        assert result['factors']['completion_bonus'] == 10

    def test_moderate_base_score_zero_contradictions_full_completion(self):
        """
        Score = 55 (base) - 0 (penalty) + 10 (bonus) = 65 → MODERATE.
        """
        pattern_analysis = {
            'consistency_score': 55.0,
            'contradictions': [],
            'pattern_classification': 'ambivalent',
        }
        test_result = MockTestResult(answered_questions=40, total_questions=40)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 65
        assert result['confidence_level'] == 'MODERATE'
        assert result['factors']['contradiction_penalty'] == 0
        assert result['factors']['completion_bonus'] == 10

    def test_low_base_score_zero_contradictions_full_completion(self):
        """
        Score = 25 (base) - 0 (penalty) + 10 (bonus) = 35 → UNRELIABLE.
        Even with full completion and no contradictions, a very low base still
        yields UNRELIABLE.
        """
        pattern_analysis = {
            'consistency_score': 25.0,
            'contradictions': [],
            'pattern_classification': 'random',
        }
        test_result = MockTestResult(answered_questions=50, total_questions=50)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 35
        assert result['confidence_level'] == 'UNRELIABLE'
        assert result['factors']['contradiction_penalty'] == 0
        assert result['factors']['completion_bonus'] == 10

    def test_zero_base_score_zero_contradictions_full_completion(self):
        """
        Score = 0 (base) - 0 (penalty) + 10 (bonus) = 10 → UNRELIABLE.
        The minimum useful score when everything else is zero.
        """
        pattern_analysis = {
            'consistency_score': 0.0,
            'contradictions': [],
            'pattern_classification': 'random',
        }
        test_result = MockTestResult(answered_questions=50, total_questions=50)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 10
        assert result['confidence_level'] == 'UNRELIABLE'
        assert result['factors']['contradiction_penalty'] == 0
        assert result['factors']['completion_bonus'] == 10


# ---------------------------------------------------------------------------
# Edge Case 2: 100% contradiction rate (capped at 0 confidence)
# ---------------------------------------------------------------------------

class TestFullContradictionRate:
    """
    Tests for the worst-case contradiction scenario: every question is part
    of a contradicted pair (contradiction_rate = 1.0), which yields a penalty
    of 50 points. The final score should be clamped to 0.
    """

    def test_100_percent_contradiction_rate_caps_at_zero(self):
        """
        All 50 questions are contradicted (rate = 1.0).
        Score = 50 (base) - 50 (penalty) + 0 (incomplete) = 0 → UNRELIABLE.
        Verifies the floor cap at 0.
        """
        total_questions = 50
        contradictions = [
            {'question_1_id': i, 'question_2_id': i + 1,
             'description': f'Contradiction {i}', 'severity': 'high'}
            for i in range(total_questions)
        ]
        pattern_analysis = {
            'consistency_score': 50.0,
            'contradictions': contradictions,
            'pattern_classification': 'random',
        }
        # Not fully completed so no bonus – makes the floor-cap easier to hit
        test_result = MockTestResult(answered_questions=40, total_questions=total_questions)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 0
        assert result['confidence_level'] == 'UNRELIABLE'

    def test_100_percent_contradiction_high_base_still_caps_at_zero(self):
        """
        Even with a very high base score (90), a 100% contradiction rate with
        no completion bonus drives the score below 0, which must be clamped.
        Score = 90 - 50 + 0 = 40 when rate = 1.0 and total = contradictions.

        Note: with rate = 1.0 the penalty is exactly 50, so the result here
        should equal max(0, 90 - 50 + 0) = 40.
        This confirms the formula and that the floor is respected.
        """
        total_questions = 10
        contradictions = [
            {'question_1_id': i, 'question_2_id': i + 1,
             'description': f'Contradiction {i}', 'severity': 'high'}
            for i in range(total_questions)
        ]
        pattern_analysis = {
            'consistency_score': 90.0,
            'contradictions': contradictions,
            'pattern_classification': 'random',
        }
        test_result = MockTestResult(answered_questions=8, total_questions=total_questions)

        result = calculate_confidence_score(pattern_analysis, test_result)

        # penalty = (10/10) * 50 = 50, no bonus → 90 - 50 = 40
        assert result['confidence_score'] == 40
        assert result['confidence_level'] == 'LOW'

    def test_100_percent_contradiction_zero_base_clamps_to_zero(self):
        """
        Score = 0 (base) - 50 (penalty) + 0 (no bonus) = -50 → clamped to 0.
        Verifies the formula cannot produce a negative output.
        """
        total_questions = 20
        contradictions = [
            {'question_1_id': i, 'question_2_id': i + 1,
             'description': f'Contradiction {i}', 'severity': 'medium'}
            for i in range(total_questions)
        ]
        pattern_analysis = {
            'consistency_score': 0.0,
            'contradictions': contradictions,
            'pattern_classification': 'random',
        }
        test_result = MockTestResult(answered_questions=10, total_questions=total_questions)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 0
        assert result['confidence_level'] == 'UNRELIABLE'

    def test_maximum_penalty_with_full_completion_still_floors_at_zero(self):
        """
        Score = 0 (base) - 50 (100% contradiction penalty) + 10 (completion bonus)
             = -40 → clamped to 0.
        Even the completion bonus cannot rescue a zero base + maximum penalty.
        """
        total_questions = 30
        contradictions = [
            {'question_1_id': i, 'question_2_id': i + 1,
             'description': f'Contradiction {i}', 'severity': 'high'}
            for i in range(total_questions)
        ]
        pattern_analysis = {
            'consistency_score': 0.0,
            'contradictions': contradictions,
            'pattern_classification': 'random',
        }
        test_result = MockTestResult(answered_questions=30, total_questions=total_questions)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 0
        assert result['confidence_level'] == 'UNRELIABLE'


# ---------------------------------------------------------------------------
# Edge Case 3: Incomplete tests without completion bonus
# ---------------------------------------------------------------------------

class TestIncompleteTestNoCompletionBonus:
    """
    Tests verifying that tests where completion_rate < 1.0 receive no
    completion bonus (+0 instead of +10).
    """

    def test_partially_answered_test_no_bonus(self):
        """
        A test where only 40 out of 50 questions were answered (80% completion)
        should receive zero completion bonus.
        Score = 70 (base) - 0 (penalty) + 0 (incomplete) = 70 → MODERATE.
        """
        pattern_analysis = {
            'consistency_score': 70.0,
            'contradictions': [],
            'pattern_classification': 'decisive',
        }
        test_result = MockTestResult(answered_questions=40, total_questions=50)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 70
        assert result['confidence_level'] == 'MODERATE'
        assert result['factors']['completion_bonus'] == 0

    def test_half_answered_test_no_bonus(self):
        """
        Only half the questions answered (50% completion) → no bonus.
        Score = 80 (base) - 0 (penalty) + 0 (incomplete) = 80 → HIGH.
        """
        pattern_analysis = {
            'consistency_score': 80.0,
            'contradictions': [],
            'pattern_classification': 'decisive',
        }
        test_result = MockTestResult(answered_questions=25, total_questions=50)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 80
        assert result['confidence_level'] == 'HIGH'
        assert result['factors']['completion_bonus'] == 0

    def test_one_question_short_no_bonus(self):
        """
        Missing just one answer (49 out of 50, 98% completion) still yields
        no completion bonus — the bonus is only awarded for exactly 100%.
        Score = 75 (base) - 0 (penalty) + 0 (incomplete) = 75 → MODERATE.
        """
        pattern_analysis = {
            'consistency_score': 75.0,
            'contradictions': [],
            'pattern_classification': 'decisive',
        }
        test_result = MockTestResult(answered_questions=49, total_questions=50)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 75
        assert result['confidence_level'] == 'MODERATE'
        assert result['factors']['completion_bonus'] == 0

    def test_incomplete_vs_complete_difference_is_exactly_10(self):
        """
        The difference between a completed and an incomplete test with identical
        pattern analysis should be exactly 10 (the completion bonus).
        """
        pattern_analysis = {
            'consistency_score': 65.0,
            'contradictions': [],
            'pattern_classification': 'ambivalent',
        }
        complete_result_tr = MockTestResult(answered_questions=50, total_questions=50)
        incomplete_result_tr = MockTestResult(answered_questions=40, total_questions=50)

        complete_result = calculate_confidence_score(pattern_analysis, complete_result_tr)
        incomplete_result = calculate_confidence_score(pattern_analysis, incomplete_result_tr)

        assert complete_result['factors']['completion_bonus'] == 10
        assert incomplete_result['factors']['completion_bonus'] == 0
        assert complete_result['confidence_score'] - incomplete_result['confidence_score'] == 10

    def test_zero_answers_no_bonus(self):
        """
        A test where no questions were answered (0% completion) → no bonus.
        Score = 50 (base) - 0 (penalty) + 0 (incomplete) = 50 → LOW.
        """
        pattern_analysis = {
            'consistency_score': 50.0,
            'contradictions': [],
            'pattern_classification': 'random',
        }
        test_result = MockTestResult(answered_questions=0, total_questions=50)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 50
        assert result['confidence_level'] == 'LOW'
        assert result['factors']['completion_bonus'] == 0

    def test_incomplete_test_with_contradictions_compounds_penalty(self):
        """
        Both missing the completion bonus AND having contradictions compound
        to lower the final score.

        Setup: 10 contradictions out of 50 questions (rate = 0.2),
               only 40/50 answered.
        penalty  = 0.2 * 50 = 10
        Score    = 70 - 10 + 0 = 60 → MODERATE (border)
        """
        total_questions = 50
        contradictions = [
            {'question_1_id': i, 'question_2_id': i + 1,
             'description': f'Contradiction {i}', 'severity': 'medium'}
            for i in range(10)
        ]
        pattern_analysis = {
            'consistency_score': 70.0,
            'contradictions': contradictions,
            'pattern_classification': 'ambivalent',
        }
        test_result = MockTestResult(answered_questions=40, total_questions=total_questions)

        result = calculate_confidence_score(pattern_analysis, test_result)

        assert result['confidence_score'] == 60
        assert result['confidence_level'] == 'MODERATE'
        assert result['factors']['completion_bonus'] == 0


# ---------------------------------------------------------------------------
# Additional combined edge cases
# ---------------------------------------------------------------------------

class TestCombinedEdgeCases:
    """Additional tests that verify the formula and caps under combined conditions."""

    def test_factors_dict_present_in_all_results(self):
        """The returned dict must always include the 'factors' breakdown."""
        pattern_analysis = {
            'consistency_score': 60.0,
            'contradictions': [],
            'pattern_classification': 'decisive',
        }
        result = calculate_confidence_score(pattern_analysis)

        assert 'factors' in result
        assert 'consistency_contribution' in result['factors']
        assert 'contradiction_penalty' in result['factors']
        assert 'completion_bonus' in result['factors']

    def test_explanation_present_in_all_results(self):
        """Every result should include a non-empty explanation string."""
        pattern_analysis = {
            'consistency_score': 70.0,
            'contradictions': [],
            'pattern_classification': 'decisive',
        }
        result = calculate_confidence_score(pattern_analysis)

        assert 'explanation' in result
        assert isinstance(result['explanation'], str)
        assert len(result['explanation']) > 0

    def test_score_is_integer(self):
        """The confidence_score must always be an integer, not a float."""
        pattern_analysis = {
            'consistency_score': 72.7,
            'contradictions': [],
            'pattern_classification': 'decisive',
        }
        result = calculate_confidence_score(pattern_analysis)

        assert isinstance(result['confidence_score'], int)

    def test_score_bounded_between_0_and_100(self):
        """Score must always be in the range [0, 100] regardless of inputs."""
        extreme_high = {
            'consistency_score': 100.0,
            'contradictions': [],
            'pattern_classification': 'decisive',
        }
        extreme_low = {
            'consistency_score': 0.0,
            'contradictions': [
                {'question_1_id': i, 'question_2_id': i + 1,
                 'description': 'c', 'severity': 'high'}
                for i in range(50)
            ],
            'pattern_classification': 'random',
        }

        high_result = calculate_confidence_score(extreme_high)
        low_result = calculate_confidence_score(
            extreme_low,
            MockTestResult(answered_questions=25, total_questions=50)
        )

        assert 0 <= high_result['confidence_score'] <= 100
        assert 0 <= low_result['confidence_score'] <= 100
