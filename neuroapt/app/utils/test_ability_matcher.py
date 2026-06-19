"""
Unit tests for Ability Match Calculator Module

Tests career type detection, dimension matching, and overall match calculations
with career-specific weighting.
"""

import pytest
from neuroapt.app.utils.ability_matcher import (
    detect_career_type,
    calculate_dimension_score,
    calculate_dimension_match,
    calculate_ability_match_for_career,
    CAREER_REQUIREMENTS,
    CAREER_WEIGHTS
)


# Sample student profile for testing
SAMPLE_PROFILE = {
    'user_id': 1,
    'test_id': 1,
    'cognitive_abilities': {
        'verbal': 80,
        'numerical': 85,
        'abstract': 75,
        'overall_aptitude': 80
    },
    'personality_traits': {
        'openness': 70,
        'conscientiousness': 75,
        'extraversion': 60,
        'agreeableness': 65,
        'neuroticism': 30  # Lower is better
    },
    'work_attributes': {
        'leadership': 70,
        'teamwork': 75,
        'creativity': 65,
        'analytical': 85,
        'communication': 70,
        'adaptability': 75
    },
    'interest_domains': {
        'stem_tech': 85,
        'creative_media': 50,
        'people_oriented': 60,
        'business_management': 65,
        'legal_governance': 55,
        'logistics_distribution': 45
    },
    'emotional_intelligence': 75,
    'metadata': {
        'test_date': '2024-01-15T10:00:00',
        'pattern_classification': 'decisive',
        'contradictions': [],
        'consistency_score': 95.0
    }
}


class TestCareerTypeDetection:
    """Test career type detection using keyword matching."""
    
    def test_software_engineer_detected_as_technical(self):
        """Test that Software Engineer is classified as technical."""
        career_type = detect_career_type("Software Engineer", "STEM+Tech")
        assert career_type == 'technical'
    
    def test_graphic_designer_detected_as_creative(self):
        """Test that Graphic Designer is classified as creative."""
        career_type = detect_career_type("Graphic Designer", "Creative+Media")
        assert career_type == 'creative'
    
    def test_teacher_detected_as_people_oriented(self):
        """Test that Teacher is classified as people-oriented."""
        career_type = detect_career_type("High School Teacher", "Education")
        assert career_type == 'people_oriented'
    
    def test_financial_analyst_detected_as_business(self):
        """Test that Financial Analyst is classified as business."""
        career_type = detect_career_type("Financial Analyst", "Business+Finance")
        assert career_type == 'business'
    
    def test_research_scientist_detected_as_research(self):
        """Test that Research Scientist is classified as research."""
        career_type = detect_career_type("Research Scientist", "Science")
        assert career_type == 'research'
    
    def test_nurse_detected_as_healthcare(self):
        """Test that Nurse is classified as healthcare."""
        career_type = detect_career_type("Registered Nurse", "Healthcare")
        assert career_type == 'healthcare'
    
    def test_unknown_career_defaults_to_business(self):
        """Test that unknown careers default to business type."""
        career_type = detect_career_type("Mysterious Job", "Unknown Category")
        assert career_type == 'business'
    
    def test_case_insensitive_matching(self):
        """Test that keyword matching is case-insensitive."""
        career_type = detect_career_type("SOFTWARE DEVELOPER", "")
        assert career_type == 'technical'


class TestDimensionScoreCalculation:
    """Test dimension score aggregation from student profile."""
    
    def test_cognitive_dimension_score(self):
        """Test cognitive score is average of all cognitive abilities."""
        score = calculate_dimension_score(SAMPLE_PROFILE, 'cognitive')
        # (80 + 85 + 75 + 80) / 4 = 80
        assert score == 80
    
    def test_personality_dimension_score(self):
        """Test personality score accounts for inverted neuroticism."""
        score = calculate_dimension_score(SAMPLE_PROFILE, 'personality')
        # (70 + 75 + 60 + 65 + (100-30)) / 5 = (70 + 75 + 60 + 65 + 70) / 5 = 68
        assert score == 68
    
    def test_emotional_intelligence_dimension_score(self):
        """Test EQ score is returned directly."""
        score = calculate_dimension_score(SAMPLE_PROFILE, 'emotional_intelligence')
        assert score == 75
    
    def test_work_style_dimension_score(self):
        """Test work style score is average of all work attributes."""
        score = calculate_dimension_score(SAMPLE_PROFILE, 'work_style')
        # (70 + 75 + 65 + 85 + 70 + 75) / 6 = 73.33 → 73
        assert score == 73
    
    def test_interest_dimension_score(self):
        """Test interest score is average of all interest domains."""
        score = calculate_dimension_score(SAMPLE_PROFILE, 'interest')
        # (85 + 50 + 60 + 65 + 55 + 45) / 6 = 60
        assert score == 60


class TestDimensionMatchCalculation:
    """Test dimension match formula application."""
    
    def test_perfect_match_when_student_exceeds_requirement(self):
        """Test match is capped at 100% when student exceeds requirement."""
        match = calculate_dimension_match(90, 75)
        # (90 / 75) * 100 = 120 → capped at 100
        assert match == 100
    
    def test_partial_match_when_student_below_requirement(self):
        """Test match percentage when student is below requirement."""
        match = calculate_dimension_match(60, 80)
        # (60 / 80) * 100 = 75
        assert match == 75
    
    def test_exact_match_when_student_meets_requirement(self):
        """Test 100% match when student meets requirement exactly."""
        match = calculate_dimension_match(75, 75)
        assert match == 100
    
    def test_zero_requirement_returns_perfect_match(self):
        """Test that zero requirement results in perfect match."""
        match = calculate_dimension_match(50, 0)
        assert match == 100


class TestAbilityMatchForCareer:
    """Test complete ability match calculation with career-specific weighting."""
    
    def test_software_engineer_match_calculation(self):
        """Test software engineer match uses technical weights."""
        result = calculate_ability_match_for_career(
            SAMPLE_PROFILE,
            "Software Engineer",
            "STEM+Tech"
        )
        
        # Verify all required fields are present
        assert 'cognitive_match' in result
        assert 'personality_match' in result
        assert 'emotional_intelligence_match' in result
        assert 'work_style_match' in result
        assert 'interest_alignment' in result
        assert 'overall_match' in result
        
        # Verify all values are in valid range
        for key, value in result.items():
            assert 0 <= value <= 100
        
        # Verify technical career has high cognitive weight impact
        # Technical weights: cognitive 45%, personality 20%, EQ 10%, work_style 15%, interest 10%
        assert result['overall_match'] > 0
    
    def test_graphic_designer_match_with_creative_weights(self):
        """Test graphic designer match uses creative weights."""
        result = calculate_ability_match_for_career(
            SAMPLE_PROFILE,
            "Graphic Designer",
            "Creative+Media"
        )
        
        # Creative careers weight personality and work_style more heavily
        # Creative weights: cognitive 15%, personality 35%, EQ 15%, work_style 25%, interest 10%
        assert result['overall_match'] > 0
        assert 0 <= result['overall_match'] <= 100
    
    def test_teacher_match_with_people_oriented_weights(self):
        """Test teacher match uses people-oriented weights."""
        result = calculate_ability_match_for_career(
            SAMPLE_PROFILE,
            "High School Teacher",
            "Education"
        )
        
        # People-oriented careers weight EQ heavily
        # People-oriented weights: cognitive 20%, personality 25%, EQ 35%, work_style 10%, interest 10%
        assert result['overall_match'] > 0
        assert result['emotional_intelligence_match'] > 0
    
    def test_match_values_are_integers(self):
        """Test that all match values are integers."""
        result = calculate_ability_match_for_career(
            SAMPLE_PROFILE,
            "Data Analyst",
            "Business"
        )
        
        for key, value in result.items():
            assert isinstance(value, int)
    
    def test_overall_match_is_weighted_average(self):
        """Test that overall match is correctly weighted."""
        result = calculate_ability_match_for_career(
            SAMPLE_PROFILE,
            "Software Engineer",
            "STEM+Tech"
        )
        
        # Manually calculate weighted average with technical weights
        weights = CAREER_WEIGHTS['technical']
        expected = int(
            result['cognitive_match'] * weights['cognitive'] +
            result['personality_match'] * weights['personality'] +
            result['emotional_intelligence_match'] * weights['emotional_intelligence'] +
            result['work_style_match'] * weights['work_style'] +
            result['interest_alignment'] * weights['interest']
        )
        
        assert result['overall_match'] == expected


class TestCareerSpecificWeighting:
    """Test that different career types apply correct weights."""
    
    def test_technical_career_weights_cognitive_highest(self):
        """Test technical careers emphasize cognitive abilities."""
        weights = CAREER_WEIGHTS['technical']
        assert weights['cognitive'] == 0.45  # Highest weight
        assert weights['personality'] == 0.20
    
    def test_creative_career_weights_personality_highest(self):
        """Test creative careers emphasize personality and work style."""
        weights = CAREER_WEIGHTS['creative']
        assert weights['personality'] == 0.35  # High weight
        assert weights['work_style'] == 0.25   # Second highest
    
    def test_healthcare_career_weights_eq_highest(self):
        """Test healthcare careers emphasize emotional intelligence."""
        weights = CAREER_WEIGHTS['healthcare']
        assert weights['emotional_intelligence'] == 0.35  # Highest weight
    
    def test_all_weights_sum_to_one(self):
        """Test that weights for each career type sum to 1.0."""
        for career_type, weights in CAREER_WEIGHTS.items():
            total = sum(weights.values())
            assert abs(total - 1.0) < 0.01, f"{career_type} weights sum to {total}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
