"""
Unit Tests for Specific Contradiction Patterns

Task 2.4: Write unit tests for specific contradiction patterns
- Test teamwork vs. solo work contradictions
- Test leadership vs. following contradictions
- Test personality trait consistency (e.g., two extraversion questions)

These tests exercise ``detect_contradictions()`` and
``detect_psychological_pattern_violations()`` directly using lightweight
stub objects — no database or Flask context required.

Contradiction detection works through two mechanisms:
1. Trait-based rules (``detect_trait_based_contradictions``) — compares
   trait_value fields on selected options for answers grouped by trait.
2. Psychological pattern violations (``detect_psychological_pattern_violations``)
   — checks aggregate scores on the test_result object against thresholds
   defined in PSYCHOLOGICAL_PATTERNS.

Thresholds used in these tests are read directly from the module to avoid
hard-coding values that might change.
"""

import pytest
from neuroapt.app.utils.pattern_analyzer import (
    detect_contradictions,
    detect_psychological_pattern_violations,
    TRAIT_RELATIONSHIP_RULES,
    PSYCHOLOGICAL_PATTERNS,
)


# ===========================================================================
# Stub helpers
# ===========================================================================

class _Option:
    """Minimal QuestionOption stub."""
    def __init__(self, score_value: int, trait_impact: str | None, trait_value: int):
        self.score_value = score_value
        self.trait_impact = trait_impact
        self.trait_value = trait_value


class _Question:
    """Minimal Question stub."""
    def __init__(self, question_id: int, category: str = "personality"):
        self.id = question_id
        self.category = category


class _TestResult:
    """
    Minimal TestResult stub carrying only the score attributes checked by
    detect_psychological_pattern_violations().
    """
    _id_seq = 0

    def __init__(self, teamwork_score=50, adaptability_score=50, leadership_score=50):
        _TestResult._id_seq += 1
        self.id = _TestResult._id_seq
        self.teamwork_score = teamwork_score
        self.adaptability_score = adaptability_score
        self.leadership_score = leadership_score


class _Answer:
    """Minimal UserAnswer stub."""
    _id_seq = 0

    def __init__(self, question: _Question, option: _Option, test_result: _TestResult):
        _Answer._id_seq += 1
        self.id = _Answer._id_seq
        self.question_id = question.id
        self.question = question
        self.selected_option = option
        self.selected_option_id = option.trait_value
        self.test_result = test_result


def _make_answer(q_id: int, trait: str, trait_value: int,
                 test_result: _TestResult, category: str = "personality") -> _Answer:
    """Convenience factory: build an _Answer with the given trait_value."""
    q = _Question(q_id, category=category)
    opt = _Option(score_value=trait_value, trait_impact=trait, trait_value=trait_value)
    return _Answer(q, opt, test_result)


def _detected_pairs(contradictions):
    """Return a set of frozensets of (q1_id, q2_id) from a contradiction list."""
    result = set()
    for c in contradictions:
        result.add(frozenset({c["question_1_id"], c["question_2_id"]}))
    return result


# ===========================================================================
# Constants pulled from the module under test
# ===========================================================================

# Threshold for extraversion/introversion opposite rule (personality)
_EXTRAV_THRESH = next(
    threshold
    for t1, t2, rel, threshold in TRAIT_RELATIONSHIP_RULES["personality"]
    if rel == "opposite" and t1 == "extraversion" and t2 == "introversion"
)

# Threshold for conscientiousness consistency (personality)
_CONSCIENT_THRESH = next(
    threshold
    for t1, t2, rel, threshold in TRAIT_RELATIONSHIP_RULES["personality"]
    if rel == "similar" and t1 == "conscientiousness"
)

# Threshold for assertiveness/agreeableness tension rule (work_style)
_TENSION_THRESH = next(
    threshold
    for t1, t2, rel, threshold in TRAIT_RELATIONSHIP_RULES["work_style"]
    if rel == "tension" and t1 == "assertiveness" and t2 == "agreeableness"
)

# Psychological pattern thresholds
_TEAMWORK_HIGH = PSYCHOLOGICAL_PATTERNS["teamwork_solo_conflict"]["high_teamwork_threshold"]
_TEAMWORK_LOW_ADAPTABILITY = 30   # hard-coded cut-off in detect_psychological_pattern_violations
_LEADERSHIP_HIGH = PSYCHOLOGICAL_PATTERNS["leadership_following_conflict"]["high_leadership_threshold"]
_LEADERSHIP_LOW_TEAMWORK = 30      # hard-coded cut-off in detect_psychological_pattern_violations


# ===========================================================================
# 1. Teamwork vs. solo work contradictions
#    (via detect_psychological_pattern_violations)
# ===========================================================================

class TestTeamworkSoloConflict:
    """Tests for the teamwork ↔ solo-work psychological pattern."""

    def test_high_teamwork_low_adaptability_flags_contradiction(self):
        """
        A student with very high teamwork AND low adaptability (proxy for
        solo/rigid preference) should trigger the teamwork_solo_conflict.
        """
        tr = _TestResult(
            teamwork_score=_TEAMWORK_HIGH,        # exactly at threshold
            adaptability_score=_TEAMWORK_LOW_ADAPTABILITY - 1,  # just below cut-off
        )
        violations = detect_psychological_pattern_violations(tr)
        descriptions = [v["description"] for v in violations]
        assert any("teamwork" in d.lower() for d in descriptions), (
            f"Expected teamwork_solo_conflict description in violations; got {descriptions}"
        )

    def test_high_teamwork_high_adaptability_no_contradiction(self):
        """
        A student with high teamwork AND adequate adaptability should NOT
        trigger the conflict.
        """
        tr = _TestResult(
            teamwork_score=_TEAMWORK_HIGH,
            adaptability_score=_TEAMWORK_LOW_ADAPTABILITY + 20,  # clearly above cut-off
        )
        violations = detect_psychological_pattern_violations(tr)
        teamwork_violations = [
            v for v in violations
            if "teamwork" in v.get("description", "").lower()
        ]
        assert teamwork_violations == [], (
            f"Unexpected teamwork violations: {teamwork_violations}"
        )

    def test_low_teamwork_low_adaptability_no_contradiction(self):
        """
        Low teamwork score should never trigger teamwork_solo_conflict regardless
        of adaptability.
        """
        tr = _TestResult(
            teamwork_score=_TEAMWORK_HIGH - 1,    # just below the trigger threshold
            adaptability_score=0,
        )
        violations = detect_psychological_pattern_violations(tr)
        teamwork_violations = [
            v for v in violations
            if "teamwork" in v.get("description", "").lower()
        ]
        assert teamwork_violations == [], (
            "Low teamwork score should not trigger conflict; "
            f"got {teamwork_violations}"
        )

    def test_contradiction_object_has_required_fields(self):
        """
        Every violation dict must contain question_1_id, question_2_id,
        description, and severity.
        """
        tr = _TestResult(
            teamwork_score=_TEAMWORK_HIGH,
            adaptability_score=0,
        )
        violations = detect_psychological_pattern_violations(tr)
        assert len(violations) >= 1, "Expected at least one violation"
        for v in violations:
            for key in ("question_1_id", "question_2_id", "description", "severity"):
                assert key in v, f"Missing key '{key}' in violation: {v}"
            assert v["severity"] in ("low", "medium", "high"), (
                f"Invalid severity value: {v['severity']!r}"
            )

    def test_via_detect_contradictions_with_teamwork_trigger(self):
        """
        detect_contradictions() must surface teamwork_solo_conflict when the
        first answer carries a test_result with the triggering scores.
        """
        tr = _TestResult(
            teamwork_score=_TEAMWORK_HIGH,
            adaptability_score=0,
        )
        ans = _make_answer(q_id=1, trait="teamwork", trait_value=5, test_result=tr)
        result = detect_contradictions([ans], [ans.question])
        descriptions = [c["description"] for c in result]
        assert any("teamwork" in d.lower() for d in descriptions), (
            f"Expected teamwork_solo_conflict via detect_contradictions; got {result}"
        )


# ===========================================================================
# 2. Leadership vs. following contradictions
#    (via detect_psychological_pattern_violations)
# ===========================================================================

class TestLeadershipFollowingConflict:
    """Tests for the leadership ↔ following psychological pattern."""

    def test_high_leadership_low_teamwork_flags_contradiction(self):
        """
        Very high leadership combined with very low teamwork should trigger
        the leadership_following_conflict.
        """
        tr = _TestResult(
            leadership_score=_LEADERSHIP_HIGH,
            teamwork_score=_LEADERSHIP_LOW_TEAMWORK - 1,  # just below cut-off
        )
        violations = detect_psychological_pattern_violations(tr)
        descriptions = [v["description"] for v in violations]
        assert any("leadership" in d.lower() for d in descriptions), (
            f"Expected leadership_following_conflict description; got {descriptions}"
        )

    def test_high_leadership_adequate_teamwork_no_contradiction(self):
        """
        High leadership with adequate teamwork should NOT trigger the conflict.
        """
        tr = _TestResult(
            leadership_score=_LEADERSHIP_HIGH,
            teamwork_score=_LEADERSHIP_LOW_TEAMWORK + 20,
        )
        violations = detect_psychological_pattern_violations(tr)
        leadership_violations = [
            v for v in violations
            if "leadership" in v.get("description", "").lower()
        ]
        assert leadership_violations == [], (
            f"Unexpected leadership violations: {leadership_violations}"
        )

    def test_low_leadership_low_teamwork_no_contradiction(self):
        """
        Low leadership score should never trigger leadership_following_conflict.
        """
        tr = _TestResult(
            leadership_score=_LEADERSHIP_HIGH - 1,
            teamwork_score=0,
        )
        violations = detect_psychological_pattern_violations(tr)
        leadership_violations = [
            v for v in violations
            if "leadership" in v.get("description", "").lower()
        ]
        assert leadership_violations == [], (
            "Low leadership should not trigger conflict; "
            f"got {leadership_violations}"
        )

    def test_exactly_at_leadership_threshold(self):
        """
        Leadership score exactly at the high threshold with very low teamwork
        SHOULD be flagged (boundary is inclusive — code uses >=).
        """
        tr = _TestResult(
            leadership_score=_LEADERSHIP_HIGH,   # exactly at threshold
            teamwork_score=0,
        )
        violations = detect_psychological_pattern_violations(tr)
        descriptions = [v["description"] for v in violations]
        assert any("leadership" in d.lower() for d in descriptions), (
            f"Leadership score at threshold should be flagged; got {descriptions}"
        )

    def test_via_detect_contradictions_with_leadership_trigger(self):
        """
        detect_contradictions() must surface leadership_following_conflict when
        the first answer carries a test_result with the triggering scores.
        """
        tr = _TestResult(
            leadership_score=_LEADERSHIP_HIGH,
            teamwork_score=0,
        )
        ans = _make_answer(q_id=2, trait="assertiveness", trait_value=5, test_result=tr)
        result = detect_contradictions([ans], [ans.question])
        descriptions = [c["description"] for c in result]
        assert any("leadership" in d.lower() for d in descriptions), (
            f"Expected leadership_following_conflict via detect_contradictions; got {result}"
        )


# ===========================================================================
# 3. Personality trait consistency (extraversion)
#    (via trait-based rules — opposite and similar checks)
# ===========================================================================

class TestPersonalityTraitConsistency:
    """Tests for personality trait contradiction detection."""

    # --- Extraversion / introversion (opposite rule) -----------------------

    def test_extraversion_introversion_both_high_detected(self):
        """
        An answer indicating high extraversion alongside an answer indicating
        high introversion should be flagged as a contradiction.
        """
        tr = _TestResult()
        high = _EXTRAV_THRESH  # exactly at threshold (inclusive)
        a_extrav = _make_answer(q_id=101, trait="extraversion", trait_value=high, test_result=tr)
        a_introv = _make_answer(q_id=102, trait="introversion", trait_value=high, test_result=tr)
        result = detect_contradictions([a_extrav, a_introv], [a_extrav.question, a_introv.question])
        detected = _detected_pairs(result)
        assert frozenset({101, 102}) in detected, (
            f"Expected extraversion/introversion contradiction at threshold; "
            f"detected pairs: {detected}, full result: {result}"
        )

    def test_extraversion_introversion_one_below_threshold_not_detected(self):
        """
        If either extraversion or introversion value is below the threshold,
        no opposite-trait contradiction should be reported.
        """
        tr = _TestResult()
        below = _EXTRAV_THRESH - 1
        a_extrav = _make_answer(q_id=103, trait="extraversion", trait_value=below, test_result=tr)
        a_introv = _make_answer(q_id=104, trait="introversion", trait_value=_EXTRAV_THRESH, test_result=tr)
        result = detect_contradictions([a_extrav, a_introv], [a_extrav.question, a_introv.question])
        detected = _detected_pairs(result)
        assert frozenset({103, 104}) not in detected, (
            f"Pair with one value below threshold should not be detected; "
            f"detected: {detected}"
        )

    def test_extraversion_introversion_both_below_threshold_not_detected(self):
        """
        Both values below the threshold — no contradiction expected.
        """
        tr = _TestResult()
        below = _EXTRAV_THRESH - 1
        a_extrav = _make_answer(q_id=105, trait="extraversion", trait_value=below, test_result=tr)
        a_introv = _make_answer(q_id=106, trait="introversion", trait_value=below, test_result=tr)
        result = detect_contradictions([a_extrav, a_introv], [a_extrav.question, a_introv.question])
        detected = _detected_pairs(result)
        assert frozenset({105, 106}) not in detected, (
            f"Both below threshold — should not be detected; detected: {detected}"
        )

    def test_extraversion_introversion_clearly_above_threshold_detected(self):
        """
        Both values well above the threshold should definitely be detected.
        """
        tr = _TestResult()
        high = _EXTRAV_THRESH + 2
        a_extrav = _make_answer(q_id=107, trait="extraversion", trait_value=high, test_result=tr)
        a_introv = _make_answer(q_id=108, trait="introversion", trait_value=high, test_result=tr)
        result = detect_contradictions([a_extrav, a_introv], [a_extrav.question, a_introv.question])
        assert len(result) >= 1, (
            f"Clear above-threshold opposite pair should be detected; got {result}"
        )

    # --- Extraversion consistency (two extraversion questions, similar rule) --

    def test_two_extraversion_questions_large_inconsistency_detected(self):
        """
        Two questions both measuring extraversion that give very different
        scores should be flagged for inconsistency.
        """
        tr = _TestResult()
        low = 0
        high = _CONSCIENT_THRESH + 2  # use same similar-threshold value; rules apply per-trait

        # Find the similar threshold specifically for 'extraversion'
        extrav_similar_thresh = next(
            (thresh for t1, t2, rel, thresh in TRAIT_RELATIONSHIP_RULES["personality"]
             if rel == "similar" and t1 == "extraversion" and t2 == "extraversion"),
            None
        )
        # If no extraversion similar rule exists, skip the sub-test
        if extrav_similar_thresh is None:
            pytest.skip("No extraversion similar-consistency rule defined; skipping")

        high_extrav = extrav_similar_thresh + 2
        a1 = _make_answer(q_id=201, trait="extraversion", trait_value=low, test_result=tr)
        a2 = _make_answer(q_id=202, trait="extraversion", trait_value=high_extrav, test_result=tr)
        result = detect_contradictions([a1, a2], [a1.question, a2.question])
        detected = _detected_pairs(result)
        assert frozenset({201, 202}) in detected, (
            f"Two extraversion questions with large inconsistency should be detected; "
            f"detected: {detected}, full result: {result}"
        )

    def test_two_extraversion_questions_small_difference_not_detected(self):
        """
        Two extraversion answers with a small, acceptable difference should
        NOT be flagged.
        """
        tr = _TestResult()
        extrav_similar_thresh = next(
            (thresh for t1, t2, rel, thresh in TRAIT_RELATIONSHIP_RULES["personality"]
             if rel == "similar" and t1 == "extraversion" and t2 == "extraversion"),
            None
        )
        if extrav_similar_thresh is None:
            pytest.skip("No extraversion similar-consistency rule defined; skipping")

        val1 = 5
        val2 = val1 + extrav_similar_thresh  # difference == threshold (NOT strictly greater)
        a1 = _make_answer(q_id=203, trait="extraversion", trait_value=val1, test_result=tr)
        a2 = _make_answer(q_id=204, trait="extraversion", trait_value=val2, test_result=tr)
        result = detect_contradictions([a1, a2], [a1.question, a2.question])
        detected = _detected_pairs(result)
        assert frozenset({203, 204}) not in detected, (
            f"Small extraversion difference should not be flagged; detected: {detected}"
        )

    # --- Conscientiousness consistency (two conscientiousness questions) ----

    def test_two_conscientiousness_questions_large_inconsistency_detected(self):
        """
        Two conscientiousness answers differing by more than the threshold
        should be detected as inconsistent.
        """
        tr = _TestResult()
        low = 0
        high = _CONSCIENT_THRESH + 2  # strictly greater than threshold
        a1 = _make_answer(q_id=301, trait="conscientiousness", trait_value=low, test_result=tr)
        a2 = _make_answer(q_id=302, trait="conscientiousness", trait_value=high, test_result=tr)
        result = detect_contradictions([a1, a2], [a1.question, a2.question])
        detected = _detected_pairs(result)
        assert frozenset({301, 302}) in detected, (
            f"Conscientiousness inconsistency should be detected; "
            f"low={low}, high={high}, threshold={_CONSCIENT_THRESH}, "
            f"detected: {detected}"
        )

    def test_two_conscientiousness_questions_within_threshold_not_detected(self):
        """
        Two conscientiousness answers within the acceptable threshold should
        NOT be flagged.
        """
        tr = _TestResult()
        val1 = 5
        val2 = val1 + _CONSCIENT_THRESH  # difference == threshold → not strictly greater
        a1 = _make_answer(q_id=303, trait="conscientiousness", trait_value=val1, test_result=tr)
        a2 = _make_answer(q_id=304, trait="conscientiousness", trait_value=val2, test_result=tr)
        result = detect_contradictions([a1, a2], [a1.question, a2.question])
        detected = _detected_pairs(result)
        assert frozenset({303, 304}) not in detected, (
            f"Conscientiousness difference at threshold boundary should not be flagged; "
            f"val1={val1}, val2={val2}, threshold={_CONSCIENT_THRESH}, "
            f"detected: {detected}"
        )

    def test_three_conscientiousness_questions_two_contradictions_detected(self):
        """
        Three conscientiousness answers where the first and third differ by
        more than the threshold should produce at least that contradiction.
        """
        tr = _TestResult()
        low = 0
        mid = _CONSCIENT_THRESH  # at threshold (no contradiction with low)
        high = _CONSCIENT_THRESH + 2  # strictly above threshold compared to low

        a1 = _make_answer(q_id=401, trait="conscientiousness", trait_value=low, test_result=tr)
        a2 = _make_answer(q_id=402, trait="conscientiousness", trait_value=mid, test_result=tr)
        a3 = _make_answer(q_id=403, trait="conscientiousness", trait_value=high, test_result=tr)
        questions = [a1.question, a2.question, a3.question]
        result = detect_contradictions([a1, a2, a3], questions)
        detected = _detected_pairs(result)

        # low vs high is a clear contradiction
        assert frozenset({401, 403}) in detected, (
            f"Pair (401, 403) with large difference should be detected; "
            f"detected: {detected}, full result: {result}"
        )


# ===========================================================================
# 4. Combined scenario: multiple contradiction types in one call
# ===========================================================================

class TestCombinedContradictions:
    """Test that multiple contradiction types are all surfaced in one call."""

    def test_teamwork_and_personality_contradictions_both_detected(self):
        """
        When both a psychological-pattern violation and a trait-based
        contradiction exist in the same answer set, both should appear.
        """
        # Build test_result that triggers teamwork_solo_conflict
        tr = _TestResult(
            teamwork_score=_TEAMWORK_HIGH,
            adaptability_score=0,
        )
        # Also plant an extraversion/introversion opposite-trait contradiction
        high_e = _EXTRAV_THRESH
        a_extrav = _make_answer(q_id=501, trait="extraversion", trait_value=high_e, test_result=tr)
        a_introv = _make_answer(q_id=502, trait="introversion", trait_value=high_e, test_result=tr)

        result = detect_contradictions([a_extrav, a_introv], [a_extrav.question, a_introv.question])

        # Trait-based opposite contradiction must be present
        detected = _detected_pairs(result)
        assert frozenset({501, 502}) in detected, (
            f"Extraversion/introversion contradiction not found; detected: {detected}"
        )

        # Psychological pattern violation must also be present
        descriptions = [c["description"] for c in result]
        assert any("teamwork" in d.lower() for d in descriptions), (
            f"Teamwork violation not found in combined result; descriptions: {descriptions}"
        )

    def test_no_answers_returns_empty_list(self):
        """Edge case: empty input should always produce an empty result."""
        result = detect_contradictions([], [])
        assert result == []

    def test_single_answer_no_contradiction(self):
        """A single answer cannot form any pair, so no contradiction is expected."""
        tr = _TestResult()
        ans = _make_answer(q_id=601, trait="extraversion", trait_value=10, test_result=tr)
        result = detect_contradictions([ans], [ans.question])
        # Only psychological violations from test_result scores could appear;
        # with neutral scores (50/50/50) no violation should be triggered.
        assert result == [], f"Single neutral answer should yield no contradictions; got {result}"
