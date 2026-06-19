from hypothesis import given, settings
from hypothesis import strategies as st
from unittest.mock import MagicMock
import pytest
from neuroapt.app.utils.ability_matcher import calculate_ability_match_for_career, detect_career_type

CAREER_TYPES = ["technical", "creative", "business", "research", "healthcare", "people_oriented"]

@given(
    cognitive=st.floats(0, 100),
    personality=st.floats(0, 100),
    eq=st.floats(0, 100),
    work_style=st.floats(0, 100),
    interest=st.floats(0, 100),
    career_type=st.sampled_from(CAREER_TYPES)
)
@settings(max_examples=100)
def test_ability_match_calculation_correctness(cognitive, personality, eq, work_style, interest, career_type):
    profile = {
        "cognitive_score": cognitive,
        "personality_score": personality,
        "eq_score": eq,
        "work_style_score": work_style,
        "interest_score": interest
    }
    result = calculate_ability_match_for_career(profile, career_type + " engineer", career_type)
    assert 0 <= result <= 100

@given(career_type=st.sampled_from(CAREER_TYPES))
@settings(max_examples=100)
def test_career_type_detection_accuracy(career_type):
    keywords = {
        "technical": "software engineer",
        "creative": "graphic designer",
        "business": "business analyst",
        "research": "research scientist",
        "healthcare": "nurse",
        "people_oriented": "teacher"
    }
    title = keywords[career_type]
    detected = detect_career_type(title, career_type)
    assert detected in CAREER_TYPES

def test_software_engineer_technical_weights():
    profile = {
        "cognitive_score": 85,
        "personality_score": 60,
        "eq_score": 60,
        "work_style_score": 70,
        "interest_score": 80
    }
    result = calculate_ability_match_for_career(profile, "Software Engineer", "Technology")
    assert result > 50

def test_graphic_designer_creative_weights():
    profile = {
        "cognitive_score": 60,
        "personality_score": 75,
        "eq_score": 65,
        "work_style_score": 60,
        "interest_score": 85
    }
    result = calculate_ability_match_for_career(profile, "Graphic Designer", "Design")
    assert result > 50

def test_teacher_people_oriented_weights():
    profile = {
        "cognitive_score": 65,
        "personality_score": 80,
        "eq_score": 90,
        "work_style_score": 70,
        "interest_score": 75
    }
    result = calculate_ability_match_for_career(profile, "Teacher", "Education")
    assert result > 50
