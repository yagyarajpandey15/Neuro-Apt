"""
Simple test script for pattern_analyzer module
"""

from neuroapt.app.utils import pattern_analyzer

def test_trait_rules():
    """Test that trait relationship rules are properly defined"""
    print("Testing trait relationship rules...")
    
    rules = pattern_analyzer.get_trait_relationship_rules()
    
    # Check that all categories have rules
    assert 'personality' in rules, "Missing personality rules"
    assert 'interest' in rules, "Missing interest rules"
    assert 'aptitude' in rules, "Missing aptitude rules"
    assert 'work_style' in rules, "Missing work_style rules"
    
    # Check personality rules
    personality_rules = rules['personality']
    assert len(personality_rules) > 0, "No personality rules defined"
    
    # Check structure of rules
    for rule in personality_rules:
        assert len(rule) == 4, f"Invalid rule structure: {rule}"
        trait_1, trait_2, rel_type, threshold = rule
        assert isinstance(trait_1, str), "Trait 1 must be string"
        assert isinstance(trait_2, str), "Trait 2 must be string"
        assert rel_type in ['opposite', 'similar', 'dependency', 'tension', 'independent'], \
            f"Invalid relationship type: {rel_type}"
        assert isinstance(threshold, int), "Threshold must be integer"
    
    print(f"✓ Trait relationship rules validated")
    print(f"  - Personality: {len(rules['personality'])} rules")
    print(f"  - Interest: {len(rules['interest'])} rules")
    print(f"  - Aptitude: {len(rules['aptitude'])} rules")
    print(f"  - Work Style: {len(rules['work_style'])} rules")


def test_classify_pattern():
    """Test pattern classification logic"""
    print("\nTesting pattern classification...")
    
    # Test decisive pattern
    result = pattern_analyzer.classify_pattern(consistency_score=85, contradiction_rate=0.05)
    assert result == 'decisive', f"Expected 'decisive', got '{result}'"
    print("✓ Decisive pattern classified correctly")
    
    # Test ambivalent pattern
    result = pattern_analyzer.classify_pattern(consistency_score=65, contradiction_rate=0.12)
    assert result == 'ambivalent', f"Expected 'ambivalent', got '{result}'"
    print("✓ Ambivalent pattern classified correctly")
    
    # Test random pattern (low consistency)
    result = pattern_analyzer.classify_pattern(consistency_score=45, contradiction_rate=0.08)
    assert result == 'random', f"Expected 'random', got '{result}'"
    print("✓ Random pattern (low consistency) classified correctly")
    
    # Test random pattern (high contradictions)
    result = pattern_analyzer.classify_pattern(consistency_score=70, contradiction_rate=0.25)
    assert result == 'random', f"Expected 'random', got '{result}'"
    print("✓ Random pattern (high contradictions) classified correctly")


def test_add_trait_rule():
    """Test adding a custom trait rule"""
    print("\nTesting custom trait rule addition...")
    
    pattern_analyzer.add_trait_relationship_rule(
        category='personality',
        trait_1='test_trait_1',
        trait_2='test_trait_2',
        relationship_type='opposite',
        threshold=5
    )
    
    rules = pattern_analyzer.get_trait_relationship_rules()
    found = False
    for rule in rules['personality']:
        if rule[0] == 'test_trait_1' and rule[1] == 'test_trait_2':
            found = True
            break
    
    assert found, "Custom trait rule was not added"
    print("✓ Custom trait rule added successfully")


def test_psychological_patterns():
    """Test that psychological pattern violations are defined"""
    print("\nTesting psychological patterns...")
    
    patterns = pattern_analyzer.PSYCHOLOGICAL_PATTERNS
    
    assert 'teamwork_solo_conflict' in patterns, "Missing teamwork_solo_conflict pattern"
    assert 'leadership_following_conflict' in patterns, "Missing leadership_following_conflict pattern"
    
    # Check structure
    for pattern_name, pattern_def in patterns.items():
        assert 'description' in pattern_def, f"Pattern {pattern_name} missing description"
        print(f"✓ Pattern '{pattern_name}': {pattern_def['description']}")


if __name__ == '__main__':
    print("=" * 70)
    print("Pattern Analyzer Module Tests")
    print("=" * 70)
    
    try:
        test_trait_rules()
        test_classify_pattern()
        test_add_trait_rule()
        test_psychological_patterns()
        
        print("\n" + "=" * 70)
        print("✓ All tests passed!")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
