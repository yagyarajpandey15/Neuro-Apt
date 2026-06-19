"""
Property-Based Test for Contradiction Detection Accuracy

**Property 2: Contradiction Detection Accuracy**
**Validates: Requirements 1.2**

For any set of user answers with planted contradictions, the contradiction
detector should identify all actual contradictions without false positives.

Strategy overview
-----------------
``detect_contradictions()`` works exclusively through trait-based rules
(``detect_trait_based_contradictions``) and psychological-pattern violations
(``detect_psychological_pattern_violations``).  The latter requires a
``test_result`` attribute on the first answer, so we supply one.

We therefore define two distinct planted-contradiction scenarios that the
function is *guaranteed* to detect according to the rules encoded in
``TRAIT_RELATIONSHIP_RULES``:

1. **Opposite-trait contradiction** – two answers where both have
   ``trait_value >= threshold`` for the two opposite traits
   (e.g., ``extraversion`` and ``introversion``, threshold = 7).

2. **Same-trait inconsistency** – two answers for the *same* trait where the
   absolute difference between ``trait_value`` scores exceeds the similarity
   threshold (e.g., both tagged ``conscientiousness``, threshold = 5,
   values differ by >5).

For each scenario we:
   a) Generate a *clean* answer set (no planted contradictions).
   b) Plant exactly N known contradictions.
   c) Call ``detect_contradictions()`` with the combined set.
   d) Assert that **every planted contradiction is reported** (no false
      negatives) and that the **clean answers produce zero detections**
      (no false positives).

Why not test *all* rules?
The dependency, tension, and cross-category rules require very specific
multi-answer configurations that are hard to generate reliably with Hypothesis
without essentially re-implementing the rule engine. The two rule types above
are the primary contradiction mechanisms described in Requirements 1.2 and the
design document and are sufficient to validate the property.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from neuroapt.app.utils.pattern_analyzer import detect_contradictions, TRAIT_RELATIONSHIP_RULES


# ---------------------------------------------------------------------------
# Stub classes (identical structure to test_pattern_extraction_consistency.py)
# ---------------------------------------------------------------------------

class StubOption:
    """Mimics QuestionOption fields used by detect_contradictions()."""
    def __init__(self, score_value: int, trait_impact: str | None, trait_value: int):
        self.score_value = score_value
        self.trait_impact = trait_impact
        self.trait_value = trait_value


class StubQuestion:
    """Mimics Question fields used by detect_contradictions()."""
    def __init__(self, question_id: int, category: str = 'personality'):
        self.id = question_id
        self.category = category


class StubTestResult:
    """
    Minimal TestResult stub — only the fields that
    detect_psychological_pattern_violations() touches.
    """
    _id_counter = 0

    def __init__(self, **score_kwargs):
        StubTestResult._id_counter += 1
        self.id = StubTestResult._id_counter
        self.teamwork_score = score_kwargs.get('teamwork_score', 50)
        self.adaptability_score = score_kwargs.get('adaptability_score', 50)
        self.leadership_score = score_kwargs.get('leadership_score', 50)


class StubAnswer:
    """Mimics UserAnswer fields used by detect_contradictions()."""
    def __init__(self, answer_id: int, question: StubQuestion,
                 selected_option: StubOption, test_result: StubTestResult):
        self.id = answer_id
        self.question_id = question.id
        self.question = question
        self.selected_option = selected_option
        self.selected_option_id = answer_id
        self.test_result = test_result


# ---------------------------------------------------------------------------
# Helpers: look up real threshold values from TRAIT_RELATIONSHIP_RULES
# ---------------------------------------------------------------------------

def _get_opposite_rule(category: str, trait_1: str, trait_2: str):
    """Return the threshold for an 'opposite' rule, or None if not found."""
    for t1, t2, rel_type, threshold in TRAIT_RELATIONSHIP_RULES.get(category, []):
        if rel_type == 'opposite' and t1 == trait_1 and t2 == trait_2:
            return threshold
    return None


def _get_similar_rule(category: str, trait: str):
    """Return the threshold for a 'similar' rule on the same trait, or None."""
    for t1, t2, rel_type, threshold in TRAIT_RELATIONSHIP_RULES.get(category, []):
        if rel_type == 'similar' and t1 == trait and t2 == trait:
            return threshold
    return None


# Concrete rule instances we rely on for planted contradictions:
#   'opposite' rule: extraversion vs introversion in personality (threshold=7)
#   'similar' rule:  conscientiousness consistency in personality   (threshold=5)
_OPPOSITE_THRESHOLD = _get_opposite_rule('personality', 'extraversion', 'introversion')
_SIMILAR_THRESHOLD = _get_similar_rule('personality', 'conscientiousness')

assert _OPPOSITE_THRESHOLD is not None, "Could not find extraversion/introversion opposite rule"
assert _SIMILAR_THRESHOLD is not None, "Could not find conscientiousness similar rule"


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

NEUTRAL_TRAITS = [
    'stem_tech', 'creative_media', 'people_oriented',
    'business_management', 'verbal', 'numerical', 'abstract',
]

# The unique ID counter for generated answers
_answer_id_counter = 0


def _next_id() -> int:
    global _answer_id_counter
    _answer_id_counter += 1
    return _answer_id_counter


@st.composite
def neutral_answer_strategy(draw, test_result: StubTestResult, question_id_offset: int = 0):
    """
    Build a single answer whose trait combination is guaranteed NOT to trigger
    any planted-contradiction rule:
      - trait_impact is one of NEUTRAL_TRAITS (not involved in opposite/similar rules)
      - OR trait_value is below the contradiction threshold for opposite rules
    """
    question_id = draw(st.integers(min_value=1000, max_value=9000)) + question_id_offset
    trait_impact = draw(st.sampled_from(NEUTRAL_TRAITS))
    score_value = draw(st.integers(min_value=0, max_value=10))
    # trait_value kept safely below opposite threshold so no accidental contradictions
    trait_value = draw(st.integers(min_value=0, max_value=_OPPOSITE_THRESHOLD - 1))
    q = StubQuestion(question_id, category='interest')
    opt = StubOption(score_value, trait_impact, trait_value)
    return StubAnswer(_next_id(), q, opt, test_result)


@st.composite
def clean_answers_strategy(draw, test_result: StubTestResult):
    """Generate 0–20 answers guaranteed to produce no trait-rule contradictions."""
    n = draw(st.integers(min_value=0, max_value=20))
    answers = []
    for i in range(n):
        ans = draw(neutral_answer_strategy(test_result, question_id_offset=i))
        answers.append(ans)
    return answers


# ---------------------------------------------------------------------------
# Opposite-trait planted contradiction builders
# ---------------------------------------------------------------------------

def make_opposite_contradiction_pair(test_result: StubTestResult,
                                     high_value: int,
                                     q1_id: int,
                                     q2_id: int):
    """
    Return a pair of answers that MUST be detected as an opposite-trait
    contradiction:
      answer_1 -> trait 'extraversion', trait_value = high_value
      answer_2 -> trait 'introversion', trait_value = high_value
    Both values >= _OPPOSITE_THRESHOLD => detected by check_opposite_traits().
    """
    q1 = StubQuestion(q1_id, category='personality')
    q2 = StubQuestion(q2_id, category='personality')
    opt1 = StubOption(score_value=high_value, trait_impact='extraversion',
                      trait_value=high_value)
    opt2 = StubOption(score_value=high_value, trait_impact='introversion',
                      trait_value=high_value)
    ans1 = StubAnswer(_next_id(), q1, opt1, test_result)
    ans2 = StubAnswer(_next_id(), q2, opt2, test_result)
    return ans1, ans2


# ---------------------------------------------------------------------------
# Same-trait inconsistency planted contradiction builders
# ---------------------------------------------------------------------------

def make_similar_contradiction_pair(test_result: StubTestResult,
                                    low_value: int,
                                    high_value: int,
                                    q1_id: int,
                                    q2_id: int):
    """
    Return a pair of answers that MUST be detected as a same-trait inconsistency:
      answer_1 -> trait 'conscientiousness', trait_value = low_value
      answer_2 -> trait 'conscientiousness', trait_value = high_value
    Difference > _SIMILAR_THRESHOLD => detected by check_trait_consistency().
    """
    q1 = StubQuestion(q1_id, category='personality')
    q2 = StubQuestion(q2_id, category='personality')
    opt1 = StubOption(score_value=low_value, trait_impact='conscientiousness',
                      trait_value=low_value)
    opt2 = StubOption(score_value=high_value, trait_impact='conscientiousness',
                      trait_value=high_value)
    ans1 = StubAnswer(_next_id(), q1, opt1, test_result)
    ans2 = StubAnswer(_next_id(), q2, opt2, test_result)
    return ans1, ans2


# ---------------------------------------------------------------------------
# Helper: extract all reported (q1_id, q2_id) pairs (order-normalised)
# ---------------------------------------------------------------------------

def detected_pairs(contradictions):
    """Return a set of frozensets of (q1_id, q2_id) from contradiction list."""
    pairs = set()
    for c in contradictions:
        pairs.add(frozenset({c['question_1_id'], c['question_2_id']}))
    return pairs


# ---------------------------------------------------------------------------
# Property 2a: Opposite-trait contradictions are always detected
# ---------------------------------------------------------------------------

@given(
    clean_answers=st.lists(
        st.integers(min_value=0, max_value=10),
        min_size=0, max_size=15
    ),
    num_planted=st.integers(min_value=1, max_value=3),
    high_value=st.integers(min_value=_OPPOSITE_THRESHOLD, max_value=10),
)
@settings(max_examples=100)
def test_opposite_trait_contradictions_detected(clean_answers, num_planted, high_value):
    """
    Property 2: Contradiction Detection Accuracy (opposite-trait case)
    **Validates: Requirements 1.2**

    For any answer set with planted opposite-trait contradictions
    (extraversion + introversion both >= threshold), detect_contradictions()
    must report at least one contradiction referencing each planted pair.
    """
    test_result = StubTestResult()

    # Build clean answers (neutral traits, low trait_values)
    neutral_answers = []
    for i, tv in enumerate(clean_answers):
        safe_tv = min(tv, _OPPOSITE_THRESHOLD - 1)
        q = StubQuestion(1000 + i, category='interest')
        opt = StubOption(score_value=safe_tv, trait_impact='stem_tech',
                         trait_value=safe_tv)
        neutral_answers.append(StubAnswer(_next_id(), q, opt, test_result))

    # Plant N opposite-trait contradiction pairs with unique question IDs
    planted_pairs_ids = []
    planted_answers = []
    for n in range(num_planted):
        q1_id = 2000 + n * 2
        q2_id = 2001 + n * 2
        a1, a2 = make_opposite_contradiction_pair(test_result, high_value, q1_id, q2_id)
        planted_pairs_ids.append(frozenset({q1_id, q2_id}))
        planted_answers.extend([a1, a2])

    all_answers = neutral_answers + planted_answers
    all_questions = [a.question for a in all_answers]

    result = detect_contradictions(all_answers, all_questions)

    # Every planted pair must appear in the detected contradictions
    detected = detected_pairs(result)
    for pair_ids in planted_pairs_ids:
        # At least one detected contradiction must cover both question IDs
        assert any(pair_ids.issubset(det) or det.issubset(pair_ids) or det == pair_ids
                   for det in detected), (
            f"Planted opposite-trait contradiction {pair_ids} not detected. "
            f"Detected pairs: {detected}. "
            f"high_value={high_value}, threshold={_OPPOSITE_THRESHOLD}"
        )


# ---------------------------------------------------------------------------
# Property 2b: Same-trait inconsistency contradictions are always detected
# ---------------------------------------------------------------------------

@given(
    clean_answers=st.lists(
        st.integers(min_value=0, max_value=10),
        min_size=0, max_size=15
    ),
    num_planted=st.integers(min_value=1, max_value=3),
    low_value=st.integers(min_value=0, max_value=4),
    high_value=st.integers(min_value=0, max_value=10),
)
@settings(max_examples=100)
def test_same_trait_inconsistency_detected(clean_answers, num_planted,
                                            low_value, high_value):
    """
    Property 2: Contradiction Detection Accuracy (same-trait inconsistency case)
    **Validates: Requirements 1.2**

    For any answer set with planted same-trait inconsistencies where the
    difference between conscientiousness scores exceeds the threshold,
    detect_contradictions() must detect them.
    """
    # Ensure the planted pair actually exceeds the similarity threshold
    assume(high_value - low_value > _SIMILAR_THRESHOLD)

    test_result = StubTestResult()

    # Build clean neutral answers
    neutral_answers = []
    for i, tv in enumerate(clean_answers):
        safe_tv = min(tv, _OPPOSITE_THRESHOLD - 1)
        q = StubQuestion(3000 + i, category='interest')
        opt = StubOption(score_value=safe_tv, trait_impact='stem_tech',
                         trait_value=safe_tv)
        neutral_answers.append(StubAnswer(_next_id(), q, opt, test_result))

    # Plant N same-trait inconsistency pairs
    planted_pairs_ids = []
    planted_answers = []
    for n in range(num_planted):
        q1_id = 4000 + n * 2
        q2_id = 4001 + n * 2
        a1, a2 = make_similar_contradiction_pair(
            test_result, low_value, high_value, q1_id, q2_id
        )
        planted_pairs_ids.append(frozenset({q1_id, q2_id}))
        planted_answers.extend([a1, a2])

    all_answers = neutral_answers + planted_answers
    all_questions = [a.question for a in all_answers]

    result = detect_contradictions(all_answers, all_questions)

    detected = detected_pairs(result)
    for pair_ids in planted_pairs_ids:
        assert any(pair_ids.issubset(det) or det.issubset(pair_ids) or det == pair_ids
                   for det in detected), (
            f"Planted same-trait inconsistency {pair_ids} not detected. "
            f"Detected pairs: {detected}. "
            f"low_value={low_value}, high_value={high_value}, "
            f"difference={high_value - low_value}, threshold={_SIMILAR_THRESHOLD}"
        )


# ---------------------------------------------------------------------------
# Property 2c: Clean answers (no planted contradictions) produce no false positives
# ---------------------------------------------------------------------------

@given(
    num_answers=st.integers(min_value=0, max_value=30),
)
@settings(max_examples=100)
def test_no_false_positives_on_clean_answers(num_answers):
    """
    Property 2: Contradiction Detection Accuracy (no false positives)
    **Validates: Requirements 1.2**

    When all answers use only neutral traits with low trait_values (below
    every contradiction threshold), detect_contradictions() must return
    an empty list.
    """
    test_result = StubTestResult(
        teamwork_score=50,
        adaptability_score=50,
        leadership_score=50,
    )

    answers = []
    for i in range(num_answers):
        q = StubQuestion(5000 + i, category='interest')
        # safe trait_value: below opposite threshold, difference between
        # any two of these is 0 (all same), so no similar-rule violations either
        opt = StubOption(score_value=3, trait_impact='stem_tech', trait_value=3)
        answers.append(StubAnswer(_next_id(), q, opt, test_result))

    questions = [a.question for a in answers]
    result = detect_contradictions(answers, questions)

    # No contradiction should be reported for truly neutral answers
    assert result == [], (
        f"Expected no contradictions for clean answers, got: {result}"
    )


# ---------------------------------------------------------------------------
# Unit tests for deterministic edge cases
# ---------------------------------------------------------------------------

def test_empty_answers_returns_empty():
    """Unit test: Empty answer list should produce zero contradictions."""
    result = detect_contradictions([], [])
    assert result == [], f"Expected [] for empty inputs, got {result}"


def test_single_answer_no_contradiction():
    """Unit test: A single answer cannot form a contradiction pair."""
    test_result = StubTestResult()
    q = StubQuestion(1, category='personality')
    opt = StubOption(score_value=9, trait_impact='extraversion', trait_value=9)
    answer = StubAnswer(1, q, opt, test_result)
    result = detect_contradictions([answer], [q])
    assert result == [], f"Single answer should not produce contradictions, got {result}"


def test_opposite_pair_above_threshold_detected():
    """
    Unit test: One explicit opposite-trait pair above threshold must be detected.
    """
    test_result = StubTestResult()
    high_val = _OPPOSITE_THRESHOLD + 1  # clearly above threshold

    q1 = StubQuestion(10, category='personality')
    q2 = StubQuestion(11, category='personality')
    opt1 = StubOption(score_value=high_val, trait_impact='extraversion',
                      trait_value=high_val)
    opt2 = StubOption(score_value=high_val, trait_impact='introversion',
                      trait_value=high_val)
    a1 = StubAnswer(10, q1, opt1, test_result)
    a2 = StubAnswer(11, q2, opt2, test_result)

    result = detect_contradictions([a1, a2], [q1, q2])

    assert len(result) >= 1, (
        f"Expected at least one contradiction for opposite-trait pair above threshold, "
        f"got {result}"
    )
    detected = detected_pairs(result)
    assert frozenset({10, 11}) in detected, (
        f"Expected pair (10, 11) in detected contradictions, got {detected}"
    )


def test_opposite_pair_below_threshold_not_detected():
    """
    Unit test: An opposite-trait pair where at least one value is below the
    threshold should NOT be flagged.
    """
    test_result = StubTestResult()
    low_val = _OPPOSITE_THRESHOLD - 1  # just below threshold

    q1 = StubQuestion(20, category='personality')
    q2 = StubQuestion(21, category='personality')
    opt1 = StubOption(score_value=low_val, trait_impact='extraversion',
                      trait_value=low_val)
    opt2 = StubOption(score_value=low_val, trait_impact='introversion',
                      trait_value=low_val)
    a1 = StubAnswer(20, q1, opt1, test_result)
    a2 = StubAnswer(21, q2, opt2, test_result)

    result = detect_contradictions([a1, a2], [q1, q2])
    detected = detected_pairs(result)

    assert frozenset({20, 21}) not in detected, (
        f"Pair below threshold should not be detected, got {result}"
    )


def test_same_trait_large_difference_detected():
    """
    Unit test: Two answers for the same trait with a difference > threshold
    must be reported.
    """
    test_result = StubTestResult()
    low_val = 0
    high_val = _SIMILAR_THRESHOLD + 2  # comfortably above threshold

    q1 = StubQuestion(30, category='personality')
    q2 = StubQuestion(31, category='personality')
    opt1 = StubOption(score_value=low_val, trait_impact='conscientiousness',
                      trait_value=low_val)
    opt2 = StubOption(score_value=high_val, trait_impact='conscientiousness',
                      trait_value=high_val)
    a1 = StubAnswer(30, q1, opt1, test_result)
    a2 = StubAnswer(31, q2, opt2, test_result)

    result = detect_contradictions([a1, a2], [q1, q2])

    assert len(result) >= 1, (
        f"Expected contradiction for large same-trait difference, got {result}"
    )
    detected = detected_pairs(result)
    assert frozenset({30, 31}) in detected, (
        f"Expected pair (30, 31) in detected contradictions, got {detected}"
    )


def test_same_trait_small_difference_not_detected():
    """
    Unit test: Two answers for the same trait with a difference <= threshold
    should NOT be flagged.
    """
    test_result = StubTestResult()
    val1 = 5
    val2 = val1 + _SIMILAR_THRESHOLD  # exactly at threshold — not strictly greater

    q1 = StubQuestion(40, category='personality')
    q2 = StubQuestion(41, category='personality')
    opt1 = StubOption(score_value=val1, trait_impact='conscientiousness',
                      trait_value=val1)
    opt2 = StubOption(score_value=val2, trait_impact='conscientiousness',
                      trait_value=val2)
    a1 = StubAnswer(40, q1, opt1, test_result)
    a2 = StubAnswer(41, q2, opt2, test_result)

    result = detect_contradictions([a1, a2], [q1, q2])
    detected = detected_pairs(result)

    assert frozenset({40, 41}) not in detected, (
        f"Pair at/below threshold should not be detected as contradiction, got {result}"
    )


def test_contradiction_objects_have_required_fields():
    """
    Unit test: Every contradiction object in the output must contain
    question_1_id, question_2_id, description, severity.
    """
    test_result = StubTestResult()
    high_val = _OPPOSITE_THRESHOLD + 1

    q1 = StubQuestion(50, 'personality')
    q2 = StubQuestion(51, 'personality')
    opt1 = StubOption(high_val, 'extraversion', high_val)
    opt2 = StubOption(high_val, 'introversion', high_val)
    a1 = StubAnswer(50, q1, opt1, test_result)
    a2 = StubAnswer(51, q2, opt2, test_result)

    result = detect_contradictions([a1, a2], [q1, q2])

    assert len(result) >= 1
    for item in result:
        assert isinstance(item, dict), f"Expected dict, got {type(item)}"
        for key in ('question_1_id', 'question_2_id', 'description', 'severity'):
            assert key in item, f"Missing key '{key}' in {item}"
        assert item['severity'] in ('low', 'medium', 'high'), (
            f"Invalid severity: {item['severity']!r}"
        )


# ---------------------------------------------------------------------------
# Entry point for direct execution
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("=" * 80)
    print("Property-Based Test: Contradiction Detection Accuracy")
    print("=" * 80)

    print("\nRunning unit tests...")
    test_empty_answers_returns_empty()
    print("  ✓ Empty answers → no contradictions")

    test_single_answer_no_contradiction()
    print("  ✓ Single answer → no contradiction")

    test_opposite_pair_above_threshold_detected()
    print("  ✓ Opposite pair above threshold → detected")

    test_opposite_pair_below_threshold_not_detected()
    print("  ✓ Opposite pair below threshold → not detected")

    test_same_trait_large_difference_detected()
    print("  ✓ Same-trait large difference → detected")

    test_same_trait_small_difference_not_detected()
    print("  ✓ Same-trait small difference → not detected")

    test_contradiction_objects_have_required_fields()
    print("  ✓ Contradiction objects have required fields")

    print("\nRunning property-based tests (100 examples each)...")
    test_opposite_trait_contradictions_detected()
    print("  ✓ Opposite-trait contradictions always detected")

    test_same_trait_inconsistency_detected()
    print("  ✓ Same-trait inconsistencies always detected")

    test_no_false_positives_on_clean_answers()
    print("  ✓ No false positives on clean answers")

    print("\n" + "=" * 80)
    print("✓ All tests passed!")
    print("=" * 80)
