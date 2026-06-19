"""
Property-Based Test for Pattern Extraction Consistency

**Property 1: Pattern Extraction Consistency**
**Validates: Requirements 1.1, 1.2, 1.3**

For any completed test result, extracting response patterns should produce a valid
pattern analysis with classification, consistency score, and contradiction list.

This test uses Hypothesis to generate TestResult-like objects with various answer
patterns and verifies that analyze_answer_patterns() always produces the required
output structure with valid values.
"""

from hypothesis import given, strategies as st, settings
from neuroapt.app.utils.pattern_analyzer import analyze_answer_patterns

# ---------------------------------------------------------------------------
# Lightweight plain-object stubs — no database, no Flask application context
# needed. We replicate only the attribute access paths that
# analyze_answer_patterns() (and its helpers) actually uses.
# ---------------------------------------------------------------------------

VALID_TRAIT_IMPACTS = [
    'extraversion', 'introversion', 'thinking', 'feeling',
    'conscientiousness', 'openness', 'agreeableness', 'neuroticism',
    'stem_tech', 'creative_media', 'people_oriented',
    'business_management', 'verbal', 'numerical', 'abstract',
    'assertiveness', 'perceiving', 'logical_reasoning', 'basic_logic',
]

VALID_CATEGORIES = [
    'personality', 'interest', 'aptitude', 'work_style', 'orientation', 'eq',
]


class StubOption:
    """Mimics QuestionOption fields used by the analyzer."""
    def __init__(self, score_value, trait_impact, trait_value):
        self.score_value = score_value
        self.trait_impact = trait_impact
        self.trait_value = trait_value


class StubQuestion:
    """Mimics Question fields used by the analyzer."""
    def __init__(self, question_id, category):
        self.id = question_id
        self.category = category


class StubAnswer:
    """Mimics UserAnswer fields used by the analyzer."""
    def __init__(self, answer_id, question, selected_option, test_result_ref):
        self.id = answer_id
        self.question_id = question.id
        self.question = question
        self.selected_option = selected_option
        self.selected_option_id = answer_id  # arbitrary
        self.test_result = test_result_ref


class StubTestResult:
    """
    Mimics the TestResult attributes consumed by analyze_answer_patterns()
    and its helpers (calculate_consistency_score, analyze_cross_section_alignment,
    detect_psychological_pattern_violations).

    All score fields default to 0; answers are injected after construction so
    that StubAnswer.test_result can back-reference this object.
    """
    _id_counter = 0

    def __init__(self, answers=None, **score_kwargs):
        StubTestResult._id_counter += 1
        self.id = StubTestResult._id_counter

        # Score fields accessed by the cross-section alignment helper
        self.analytical_score = score_kwargs.get('analytical_score', 0)
        self.stem_tech_score = score_kwargs.get('stem_tech_score', 0)
        self.creativity_score = score_kwargs.get('creativity_score', 0)
        self.creative_media_score = score_kwargs.get('creative_media_score', 0)
        self.communication_score = score_kwargs.get('communication_score', 0)
        self.teamwork_score = score_kwargs.get('teamwork_score', 0)
        self.people_oriented_score = score_kwargs.get('people_oriented_score', 0)

        # Score fields accessed by detect_psychological_pattern_violations
        self.leadership_score = score_kwargs.get('leadership_score', 0)
        self.adaptability_score = score_kwargs.get('adaptability_score', 0)

        self.answers = answers or []


# ---------------------------------------------------------------------------
# Hypothesis composite strategy: build a StubTestResult with N answers
# ---------------------------------------------------------------------------

@st.composite
def answer_strategy(draw, test_result_ref, answer_id):
    """Build a single StubAnswer with generated question/option attributes."""
    question_id = draw(st.integers(min_value=1, max_value=500))
    category = draw(st.sampled_from(VALID_CATEGORIES))
    trait_impact = draw(st.one_of(
        st.sampled_from(VALID_TRAIT_IMPACTS),
        st.none(),            # some answers have no trait impact
    ))
    score_value = draw(st.integers(min_value=0, max_value=10))
    trait_value = draw(st.integers(min_value=0, max_value=10))

    question = StubQuestion(question_id, category)
    option = StubOption(score_value, trait_impact, trait_value)
    return StubAnswer(answer_id, question, option, test_result_ref)


@st.composite
def build_test_result(draw):
    """
    Generate a StubTestResult with a variable number of answers (0-50)
    and randomly populated score fields.

    Score fields are integers in [0, 100] to reflect normalised scores.
    """
    score_fields = {
        'analytical_score': draw(st.integers(0, 100)),
        'stem_tech_score': draw(st.integers(0, 100)),
        'creativity_score': draw(st.integers(0, 100)),
        'creative_media_score': draw(st.integers(0, 100)),
        'communication_score': draw(st.integers(0, 100)),
        'teamwork_score': draw(st.integers(0, 100)),
        'people_oriented_score': draw(st.integers(0, 100)),
        'leadership_score': draw(st.integers(0, 100)),
        'adaptability_score': draw(st.integers(0, 100)),
    }

    stub = StubTestResult(**score_fields)

    num_answers = draw(st.integers(min_value=0, max_value=50))
    answers = []
    for i in range(num_answers):
        ans = draw(answer_strategy(stub, answer_id=i + 1))
        answers.append(ans)
    stub.answers = answers

    return stub


# ---------------------------------------------------------------------------
# Property test
# ---------------------------------------------------------------------------

@given(test_result=build_test_result())
@settings(max_examples=100)
def test_pattern_extraction_consistency(test_result):
    """
    Property 1: Pattern Extraction Consistency
    **Validates: Requirements 1.1, 1.2, 1.3**

    For any TestResult-like object with arbitrary answer patterns, calling
    analyze_answer_patterns() must:

    1. Return a dict (never raise, never return None)
    2. Contain the key 'pattern_classification' with one of the three
       valid string values: 'decisive', 'ambivalent', 'random'
    3. Contain the key 'consistency_score' as a float in [0, 100]
    4. Contain the key 'contradictions' as a list (may be empty)
    5. Contain the key 'cross_section_alignment' as a dict
    """
    result = analyze_answer_patterns(test_result)

    # 1. Result must be a non-None dict
    assert result is not None, "analyze_answer_patterns() returned None"
    assert isinstance(result, dict), (
        f"Expected dict, got {type(result)}"
    )

    # 2. Valid pattern classification
    assert 'pattern_classification' in result, (
        "Result missing 'pattern_classification'"
    )
    assert result['pattern_classification'] in ('decisive', 'ambivalent', 'random'), (
        f"Invalid pattern_classification: {result['pattern_classification']!r}"
    )

    # 3. Consistency score is a number in [0, 100]
    assert 'consistency_score' in result, (
        "Result missing 'consistency_score'"
    )
    score = result['consistency_score']
    assert isinstance(score, (int, float)), (
        f"consistency_score must be numeric, got {type(score)}"
    )
    assert 0.0 <= score <= 100.0, (
        f"consistency_score {score} is outside [0, 100]"
    )

    # 4. Contradictions is a list
    assert 'contradictions' in result, "Result missing 'contradictions'"
    assert isinstance(result['contradictions'], list), (
        f"'contradictions' must be a list, got {type(result['contradictions'])}"
    )

    # 5. Each contradiction object has required keys
    for contradiction in result['contradictions']:
        assert isinstance(contradiction, dict), (
            f"Each contradiction must be a dict, got {type(contradiction)}"
        )
        for key in ('question_1_id', 'question_2_id', 'description', 'severity'):
            assert key in contradiction, (
                f"Contradiction missing key '{key}': {contradiction}"
            )
        assert contradiction['severity'] in ('low', 'medium', 'high'), (
            f"Invalid contradiction severity: {contradiction['severity']!r}"
        )

    # 6. Cross-section alignment is a dict
    assert 'cross_section_alignment' in result, (
        "Result missing 'cross_section_alignment'"
    )
    assert isinstance(result['cross_section_alignment'], dict), (
        f"'cross_section_alignment' must be a dict, "
        f"got {type(result['cross_section_alignment'])}"
    )


# ---------------------------------------------------------------------------
# Quick unit smoke-tests for deterministic edge cases
# ---------------------------------------------------------------------------

def test_empty_answers_returns_defaults():
    """
    Unit test: An empty-answer TestResult should return the documented
    default values (ambivalent, 50.0, empty contradictions).
    """
    stub = StubTestResult()
    stub.answers = []

    result = analyze_answer_patterns(stub)

    assert result['pattern_classification'] == 'ambivalent', (
        f"Expected 'ambivalent' for empty answers, got {result['pattern_classification']!r}"
    )
    assert result['consistency_score'] == 50.0, (
        f"Expected 50.0 for empty answers, got {result['consistency_score']}"
    )
    assert result['contradictions'] == [], (
        f"Expected no contradictions for empty answers, got {result['contradictions']}"
    )


def test_all_same_scores_high_consistency():
    """
    Unit test: When all answers in the same category have identical scores,
    consistency should be 100 (no variance), leading to 'decisive' or 'ambivalent'.
    """
    stub = StubTestResult()
    answers = []
    for i in range(5):
        q = StubQuestion(i + 1, 'personality')
        opt = StubOption(score_value=8, trait_impact='conscientiousness', trait_value=8)
        answers.append(StubAnswer(i + 1, q, opt, stub))
    stub.answers = answers

    result = analyze_answer_patterns(stub)

    # With uniform scores, variance = 0, so consistency_score = 100
    assert result['consistency_score'] == 100.0, (
        f"Expected 100.0 consistency with uniform scores, got {result['consistency_score']}"
    )


def test_output_keys_present_with_single_answer():
    """
    Unit test: Even with a single answer, all four output keys must be present.
    """
    stub = StubTestResult()
    q = StubQuestion(1, 'aptitude')
    opt = StubOption(score_value=5, trait_impact='numerical', trait_value=5)
    stub.answers = [StubAnswer(1, q, opt, stub)]

    result = analyze_answer_patterns(stub)

    for key in ('pattern_classification', 'consistency_score', 'contradictions',
                'cross_section_alignment'):
        assert key in result, f"Missing key '{key}' in result"


if __name__ == '__main__':
    print("=" * 80)
    print("Property-Based Test: Pattern Extraction Consistency")
    print("=" * 80)

    # Unit tests first
    print("\nRunning unit tests...")
    test_empty_answers_returns_defaults()
    print("  ✓ Empty answers returns defaults")

    test_all_same_scores_high_consistency()
    print("  ✓ Uniform scores yield 100% consistency")

    test_output_keys_present_with_single_answer()
    print("  ✓ Single answer still produces all output keys")

    # Property test
    print("\nRunning property-based test (100 examples)...")
    test_pattern_extraction_consistency()
    print("  ✓ Pattern extraction consistency property verified")

    print("\n" + "=" * 80)
    print("✓ All tests passed!")
    print("=" * 80)
