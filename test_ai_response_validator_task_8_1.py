"""
Test suite for AI Response Validator - Task 8.1 verification

This test suite validates that the ai_response_validator module meets all
requirements specified in task 8.1 of the AI-Enhanced Career Matching spec.

Requirements validated: 2.3, 6.2, 6.6, 8.4, 8.5, 12.4
"""

import pytest
from neuroapt.app.utils.ai_response_validator import (
    validate_and_format_ai_response,
    format_career_matches,
    validate_roadmap,
    validate_reality_check,
    validate_career_match,
    validate_numeric_range,
    validate_array_count
)


class TestValidateAndFormatAIResponse:
    """Test the main validation function for AI responses"""
    
    def test_validates_required_top_level_keys(self):
        """REQUIREMENT: Validate required top-level keys exist"""
        # Missing top_careers
        response = {
            'alternate_careers': [],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }
        assert validate_and_format_ai_response(response) is None
        
        # Missing alternate_careers
        response = {
            'top_careers': [],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }
        assert validate_and_format_ai_response(response) is None
        
        # Missing confidence_analysis
        response = {
            'top_careers': [],
            'alternate_careers': [],
            'personality_summary': 'test'
        }
        assert validate_and_format_ai_response(response) is None
        
        # Missing personality_summary
        response = {
            'top_careers': [],
            'alternate_careers': [],
            'confidence_analysis': {}
        }
        assert validate_and_format_ai_response(response) is None
    
    def test_validates_top_careers_count_3_to_5(self):
        """REQUIREMENT: Check array element counts - top_careers (3-5)"""
        # Too few top careers (< 3)
        response = {
            'top_careers': [self._create_valid_career(), self._create_valid_career()],
            'alternate_careers': [self._create_valid_career(), self._create_valid_career()],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }
        assert validate_and_format_ai_response(response) is None
        
        # Too many top careers (> 5)
        response = {
            'top_careers': [self._create_valid_career() for _ in range(6)],
            'alternate_careers': [self._create_valid_career(), self._create_valid_career()],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }
        assert validate_and_format_ai_response(response) is None
        
        # Valid count (3)
        response = {
            'top_careers': [self._create_valid_career() for _ in range(3)],
            'alternate_careers': [self._create_valid_career(), self._create_valid_career()],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert len(result['top_careers']) == 3
        
        # Valid count (5)
        response = {
            'top_careers': [self._create_valid_career() for _ in range(5)],
            'alternate_careers': [self._create_valid_career(), self._create_valid_career()],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert len(result['top_careers']) == 5
    
    def test_validates_alternate_careers_count_2_to_4(self):
        """REQUIREMENT: Check array element counts - alternate_careers (2-4)"""
        # Too few alternate careers (< 2)
        response = {
            'top_careers': [self._create_valid_career() for _ in range(3)],
            'alternate_careers': [self._create_valid_career()],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }
        assert validate_and_format_ai_response(response) is None
        
        # Too many alternate careers (> 4)
        response = {
            'top_careers': [self._create_valid_career() for _ in range(3)],
            'alternate_careers': [self._create_valid_career() for _ in range(5)],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }
        assert validate_and_format_ai_response(response) is None
        
        # Valid count (2)
        response = {
            'top_careers': [self._create_valid_career() for _ in range(3)],
            'alternate_careers': [self._create_valid_career(), self._create_valid_career()],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert len(result['alternate_careers']) == 2
        
        # Valid count (4)
        response = {
            'top_careers': [self._create_valid_career() for _ in range(3)],
            'alternate_careers': [self._create_valid_career() for _ in range(4)],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert len(result['alternate_careers']) == 4
    
    def test_validates_career_match_required_fields(self):
        """REQUIREMENT: Validate career match required fields"""
        # Missing title
        career = self._create_valid_career()
        del career['title']
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        assert validate_and_format_ai_response(response) is None
        
        # Missing match_percentage
        career = self._create_valid_career()
        del career['match_percentage']
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        assert validate_and_format_ai_response(response) is None
        
        # Missing why_this_fits
        career = self._create_valid_career()
        del career['why_this_fits']
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        assert validate_and_format_ai_response(response) is None
        
        # Missing roadmap
        career = self._create_valid_career()
        del career['roadmap']
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        assert validate_and_format_ai_response(response) is None
        
        # Missing reality_check
        career = self._create_valid_career()
        del career['reality_check']
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        assert validate_and_format_ai_response(response) is None
    
    def test_validates_match_percentage_range_0_to_100(self):
        """REQUIREMENT: Validate numeric ranges - match_percentage (0-100)"""
        # Below range
        career = self._create_valid_career()
        career['match_percentage'] = -1
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        assert validate_and_format_ai_response(response) is None
        
        # Above range
        career = self._create_valid_career()
        career['match_percentage'] = 101
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        assert validate_and_format_ai_response(response) is None
        
        # Valid (0)
        career = self._create_valid_career()
        career['match_percentage'] = 0
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert result['top_careers'][0]['match_percentage'] == 0
        
        # Valid (100)
        career = self._create_valid_career()
        career['match_percentage'] = 100
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert result['top_careers'][0]['match_percentage'] == 100
        
        # Valid (50)
        career = self._create_valid_career()
        career['match_percentage'] = 50
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert result['top_careers'][0]['match_percentage'] == 50
    
    def test_validates_roadmap_timeframes(self):
        """REQUIREMENT: Validate roadmap timeframes"""
        # Missing immediate_1_month
        career = self._create_valid_career()
        del career['roadmap']['immediate_1_month']
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        assert validate_and_format_ai_response(response) is None
        
        # Missing short_term_3_6_months
        career = self._create_valid_career()
        del career['roadmap']['short_term_3_6_months']
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        assert validate_and_format_ai_response(response) is None
        
        # Missing medium_term_6_12_months
        career = self._create_valid_career()
        del career['roadmap']['medium_term_6_12_months']
        response = self._create_valid_response_with_careers([career, self._create_valid_career(), self._create_valid_career()])
        assert validate_and_format_ai_response(response) is None
        
        # All timeframes present
        response = self._create_valid_response_with_careers([self._create_valid_career() for _ in range(3)])
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert 'immediate_1_month' in result['top_careers'][0]['roadmap']
        assert 'short_term_3_6_months' in result['top_careers'][0]['roadmap']
        assert 'medium_term_6_12_months' in result['top_careers'][0]['roadmap']
    
    def test_valid_complete_response(self):
        """Test that a fully valid response passes all validations"""
        response = {
            'top_careers': [self._create_valid_career() for _ in range(3)],
            'alternate_careers': [self._create_valid_career() for _ in range(2)],
            'confidence_analysis': {'score': 85, 'level': 'HIGH'},
            'personality_summary': 'Analytical and creative individual',
            'unique_strengths': ['Problem solving', 'Creativity'],
            'growth_areas': ['Teamwork', 'Communication'],
            'emotional_readiness': {'stress_tolerance': 'High'},
            'contradiction_analysis': 'No significant contradictions',
            'parent_report': {'summary': 'Strong potential'}
        }
        
        result = validate_and_format_ai_response(response)
        assert result is not None
        assert len(result['top_careers']) == 3
        assert len(result['alternate_careers']) == 2
        assert result['confidence_analysis'] == {'score': 85, 'level': 'HIGH'}
        assert result['personality_summary'] == 'Analytical and creative individual'
    
    # Helper methods
    def _create_valid_career(self):
        """Create a valid career match object for testing"""
        return {
            'title': 'Software Engineer',
            'match_percentage': 85,
            'category': 'STEM+Tech',
            'why_this_fits': 'Strong analytical skills and problem-solving ability',
            'challenges': 'May need to improve teamwork skills',
            'ability_breakdown': {
                'cognitive_match': 90,
                'personality_match': 80,
                'emotional_intelligence_match': 75,
                'work_style_match': 85,
                'interest_alignment': 88
            },
            'matching_traits': ['Analytical', 'Detail-oriented', 'Problem solver'],
            'reality_check': {
                'daily_life': 'Writing code, debugging, attending meetings',
                'work_environment': 'Office or remote, collaborative team',
                'common_challenges': 'Tight deadlines, complex problems',
                'stress_factors': 'Project deadlines, on-call rotations',
                'work_life_balance': 'Generally good with flexible hours'
            },
            'roadmap': {
                'immediate_1_month': ['Learn Python basics', 'Set up development environment'],
                'short_term_3_6_months': ['Build portfolio projects', 'Complete online course'],
                'medium_term_6_12_months': ['Apply for internships', 'Contribute to open source'],
                'skill_development': ['Data structures', 'Algorithms', 'System design'],
                'resources': ['Codecademy', 'LeetCode', 'GitHub']
            },
            'confidence_score': 85
        }
    
    def _create_valid_response_with_careers(self, top_careers):
        """Create a valid response with specific top careers"""
        return {
            'top_careers': top_careers,
            'alternate_careers': [self._create_valid_career() for _ in range(2)],
            'confidence_analysis': {},
            'personality_summary': 'test'
        }


class TestFormatCareerMatches:
    """Test the format_career_matches function"""
    
    def test_formats_career_list_with_defaults(self):
        """Test that format_career_matches fills in missing optional fields"""
        careers = [
            {
                'title': 'Software Engineer',
                'match_percentage': 85,
                'why_this_fits': 'Good fit',
                'challenges': 'Some challenges',
                'roadmap': {
                    'immediate_1_month': ['Step 1'],
                    'short_term_3_6_months': ['Step 2'],
                    'medium_term_6_12_months': ['Step 3']
                },
                'reality_check': {
                    'daily_life': 'Coding'
                }
            }
        ]
        
        formatted = format_career_matches(careers)
        assert len(formatted) == 1
        assert 'ability_breakdown' in formatted[0]
        assert 'matching_traits' in formatted[0]
        assert formatted[0]['title'] == 'Software Engineer'
        assert formatted[0]['match_percentage'] == 85
    
    def test_handles_empty_list(self):
        """Test that empty list returns empty list"""
        result = format_career_matches([])
        assert result == []
    
    def test_handles_invalid_input(self):
        """Test that invalid input returns empty list"""
        result = format_career_matches(None)
        assert result == []
        
        result = format_career_matches("not a list")
        assert result == []


class TestValidateRoadmap:
    """Test the validate_roadmap function"""
    
    def test_requires_all_three_timeframes(self):
        """REQUIREMENT: Validate roadmap timeframes"""
        # All three present
        roadmap = {
            'immediate_1_month': ['Step 1'],
            'short_term_3_6_months': ['Step 2'],
            'medium_term_6_12_months': ['Step 3']
        }
        assert validate_roadmap(roadmap) is True
        
        # Missing immediate_1_month
        roadmap = {
            'short_term_3_6_months': ['Step 2'],
            'medium_term_6_12_months': ['Step 3']
        }
        assert validate_roadmap(roadmap) is False
        
        # Missing short_term_3_6_months
        roadmap = {
            'immediate_1_month': ['Step 1'],
            'medium_term_6_12_months': ['Step 3']
        }
        assert validate_roadmap(roadmap) is False
        
        # Missing medium_term_6_12_months
        roadmap = {
            'immediate_1_month': ['Step 1'],
            'short_term_3_6_months': ['Step 2']
        }
        assert validate_roadmap(roadmap) is False
    
    def test_requires_non_empty_arrays(self):
        """Test that each timeframe must have at least one action"""
        # Empty immediate_1_month
        roadmap = {
            'immediate_1_month': [],
            'short_term_3_6_months': ['Step 2'],
            'medium_term_6_12_months': ['Step 3']
        }
        assert validate_roadmap(roadmap) is False
    
    def test_rejects_invalid_input(self):
        """Test that invalid input is rejected"""
        assert validate_roadmap(None) is False
        assert validate_roadmap("not a dict") is False
        assert validate_roadmap({}) is False


class TestValidateNumericRange:
    """Test the validate_numeric_range helper function"""
    
    def test_validates_numeric_ranges(self):
        """REQUIREMENT: Validate numeric ranges"""
        # Valid values
        assert validate_numeric_range(0, 0, 100) is True
        assert validate_numeric_range(50, 0, 100) is True
        assert validate_numeric_range(100, 0, 100) is True
        
        # Out of range
        assert validate_numeric_range(-1, 0, 100) is False
        assert validate_numeric_range(101, 0, 100) is False
        
        # Non-numeric
        assert validate_numeric_range("50", 0, 100) is False
        assert validate_numeric_range(None, 0, 100) is False


class TestValidateArrayCount:
    """Test the validate_array_count helper function"""
    
    def test_validates_array_counts(self):
        """REQUIREMENT: Check array element counts"""
        # Valid counts
        assert validate_array_count([1, 2, 3], 3, 5) is True
        assert validate_array_count([1, 2, 3, 4], 3, 5) is True
        assert validate_array_count([1, 2, 3, 4, 5], 3, 5) is True
        
        # Too few
        assert validate_array_count([1, 2], 3, 5) is False
        
        # Too many
        assert validate_array_count([1, 2, 3, 4, 5, 6], 3, 5) is False
        
        # Non-array
        assert validate_array_count("not an array", 3, 5) is False
        assert validate_array_count(None, 3, 5) is False


class TestIntegration:
    """Integration tests for the complete validation flow"""
    
    def test_complete_validation_flow(self):
        """Test complete validation with realistic AI response"""
        response = {
            'top_careers': [
                {
                    'title': 'Software Engineer',
                    'match_percentage': 87,
                    'category': 'STEM+Tech',
                    'why_this_fits': 'Your high analytical score of 85 and strong problem-solving skills align perfectly with software engineering',
                    'challenges': 'Teamwork score of 65 suggests you may need to improve collaboration skills',
                    'ability_breakdown': {
                        'cognitive_match': 90,
                        'personality_match': 82,
                        'emotional_intelligence_match': 78,
                        'work_style_match': 85,
                        'interest_alignment': 88
                    },
                    'matching_traits': ['Analytical', 'Detail-oriented', 'Problem solver', 'Logical thinker'],
                    'reality_check': {
                        'daily_life': 'Writing code, debugging issues, attending team meetings, code reviews',
                        'work_environment': 'Office or remote, collaborative team environment',
                        'common_challenges': 'Tight deadlines, complex technical problems, rapid technology changes',
                        'stress_factors': 'Project deadlines, on-call rotations, production incidents',
                        'work_life_balance': 'Generally good with flexible hours, occasional crunch times'
                    },
                    'roadmap': {
                        'immediate_1_month': [
                            'Choose a programming language (Python or JavaScript)',
                            'Complete an online coding tutorial',
                            'Set up your development environment'
                        ],
                        'short_term_3_6_months': [
                            'Build 2-3 small projects for portfolio',
                            'Learn data structures and algorithms',
                            'Complete a comprehensive programming course'
                        ],
                        'medium_term_6_12_months': [
                            'Apply for internships or junior positions',
                            'Contribute to open source projects',
                            'Build a substantial capstone project'
                        ],
                        'skill_development': ['Python', 'Git', 'Web development', 'Database fundamentals'],
                        'resources': ['Codecademy', 'freeCodeCamp', 'LeetCode', 'GitHub']
                    },
                    'confidence_score': 87
                },
                {
                    'title': 'Data Analyst',
                    'match_percentage': 83,
                    'category': 'STEM+Tech',
                    'why_this_fits': 'Strong numerical reasoning (82) and analytical skills make you well-suited for data analysis',
                    'challenges': 'Communication score of 68 suggests presenting findings might require development',
                    'ability_breakdown': {
                        'cognitive_match': 88,
                        'personality_match': 80,
                        'emotional_intelligence_match': 72,
                        'work_style_match': 83,
                        'interest_alignment': 85
                    },
                    'matching_traits': ['Numerical', 'Analytical', 'Detail-focused', 'Pattern recognition'],
                    'reality_check': {
                        'daily_life': 'Analyzing datasets, creating visualizations, writing reports, presenting insights',
                        'work_environment': 'Office setting, mix of independent and collaborative work',
                        'common_challenges': 'Data quality issues, unclear requirements, stakeholder management',
                        'stress_factors': 'Reporting deadlines, handling large datasets, presenting to executives',
                        'work_life_balance': 'Typically good, predictable hours with occasional busy periods'
                    },
                    'roadmap': {
                        'immediate_1_month': [
                            'Learn Excel fundamentals',
                            'Understand basic statistics',
                            'Explore data visualization concepts'
                        ],
                        'short_term_3_6_months': [
                            'Complete SQL course',
                            'Learn Python for data analysis (pandas, numpy)',
                            'Practice with real datasets on Kaggle'
                        ],
                        'medium_term_6_12_months': [
                            'Build data analysis portfolio',
                            'Learn Power BI or Tableau',
                            'Apply for entry-level analyst positions'
                        ],
                        'skill_development': ['SQL', 'Python', 'Statistics', 'Data visualization'],
                        'resources': ['DataCamp', 'Kaggle', 'Tableau Public', 'Mode Analytics']
                    },
                    'confidence_score': 83
                },
                {
                    'title': 'Systems Analyst',
                    'match_percentage': 79,
                    'category': 'STEM+Tech',
                    'why_this_fits': 'Your analytical skills (85) combined with moderate communication (68) suit systems analysis',
                    'challenges': 'Lower creativity score (62) may limit innovation in solution design',
                    'ability_breakdown': {
                        'cognitive_match': 85,
                        'personality_match': 78,
                        'emotional_intelligence_match': 75,
                        'work_style_match': 80,
                        'interest_alignment': 81
                    },
                    'matching_traits': ['Analytical', 'Systematic', 'Problem solver', 'Process-oriented'],
                    'reality_check': {
                        'daily_life': 'Gathering requirements, documenting processes, analyzing workflows, testing systems',
                        'work_environment': 'Corporate setting, regular stakeholder interaction',
                        'common_challenges': 'Conflicting requirements, resistance to change, technical constraints',
                        'stress_factors': 'Project deadlines, managing expectations, system failures',
                        'work_life_balance': 'Good with standard business hours'
                    },
                    'roadmap': {
                        'immediate_1_month': [
                            'Research systems analysis role',
                            'Learn basic business process modeling',
                            'Understand software development lifecycle'
                        ],
                        'short_term_3_6_months': [
                            'Study requirements gathering techniques',
                            'Learn UML and process modeling tools',
                            'Take business analysis fundamentals course'
                        ],
                        'medium_term_6_12_months': [
                            'Pursue entry-level BA or systems analyst role',
                            'Consider CBAP certification preparation',
                            'Build case studies of system analysis work'
                        ],
                        'skill_development': ['Requirements analysis', 'Process modeling', 'Stakeholder management'],
                        'resources': ['IIBA resources', 'LinkedIn Learning', 'Coursera Business Analysis']
                    },
                    'confidence_score': 79
                }
            ],
            'alternate_careers': [
                {
                    'title': 'Technical Writer',
                    'match_percentage': 72,
                    'category': 'Creative+Tech',
                    'why_this_fits': 'Combination of technical knowledge and ability to explain complex concepts',
                    'challenges': 'Moderate communication skills may need enhancement',
                    'roadmap': {
                        'immediate_1_month': ['Study technical writing basics'],
                        'short_term_3_6_months': ['Build writing portfolio'],
                        'medium_term_6_12_months': ['Apply for technical writing roles']
                    },
                    'reality_check': {
                        'daily_life': 'Writing documentation, collaborating with developers',
                        'work_environment': 'Office or remote',
                        'common_challenges': 'Keeping documentation updated'
                    },
                    'confidence_score': 72
                },
                {
                    'title': 'Quality Assurance Tester',
                    'match_percentage': 70,
                    'category': 'STEM+Tech',
                    'why_this_fits': 'Detail-oriented nature and systematic thinking suit QA work',
                    'challenges': 'Repetitive tasks may become monotonous',
                    'roadmap': {
                        'immediate_1_month': ['Learn QA fundamentals'],
                        'short_term_3_6_months': ['Practice test case writing'],
                        'medium_term_6_12_months': ['Learn automation testing']
                    },
                    'reality_check': {
                        'daily_life': 'Testing software, documenting bugs, regression testing',
                        'work_environment': 'Team environment with developers',
                        'common_challenges': 'Finding elusive bugs'
                    },
                    'confidence_score': 70
                }
            ],
            'confidence_analysis': {
                'score': 85,
                'level': 'HIGH',
                'explanation': 'Strong consistency across responses with minimal contradictions'
            },
            'personality_summary': 'You demonstrate strong analytical and logical thinking patterns with a preference for structured problem-solving. Your scores suggest you excel in independent work while maintaining adequate collaboration skills.',
            'unique_strengths': [
                'Analytical thinking and problem-solving',
                'Strong numerical reasoning',
                'Detail-oriented approach',
                'Logical and systematic thinking'
            ],
            'growth_areas': [
                'Teamwork and collaboration skills',
                'Communication and presentation',
                'Creative thinking and innovation',
                'Emotional expression and empathy'
            ],
            'emotional_readiness': {
                'summary': 'Moderate emotional intelligence with room for growth',
                'stress_tolerance': 'Medium',
                'leadership_potential': 'Medium',
                'teamwork_fit': 'Independent-leaning'
            },
            'contradiction_analysis': 'Your responses showed good consistency. Minor contradiction detected between preference for independent work (high) and leadership interest (medium), which is common and not concerning.',
            'parent_report': {
                'summary': 'Your child shows strong analytical abilities suited for technical careers, with opportunities to develop interpersonal skills.',
                'what_child_is_good_at': [
                    'Problem-solving and logical thinking',
                    'Working with numbers and data',
                    'Independent work and focus',
                    'Attention to detail'
                ],
                'recommended_support': [
                    'Encourage team projects to build collaboration skills',
                    'Provide opportunities for public speaking or presentations',
                    'Support exploration of coding or data analysis',
                    'Consider summer tech camps or workshops'
                ],
                'careers_to_discuss': [
                    'Software Engineering',
                    'Data Analysis',
                    'Systems Analysis'
                ]
            }
        }
        
        # Validate the response
        result = validate_and_format_ai_response(response)
        
        # Assert the response is valid
        assert result is not None
        
        # Verify structure
        assert len(result['top_careers']) == 3
        assert len(result['alternate_careers']) == 2
        
        # Verify top-level keys
        assert 'confidence_analysis' in result
        assert 'personality_summary' in result
        assert 'unique_strengths' in result
        assert 'growth_areas' in result
        
        # Verify career match structure
        for career in result['top_careers']:
            assert 'title' in career
            assert 'match_percentage' in career
            assert 0 <= career['match_percentage'] <= 100
            assert 'why_this_fits' in career
            assert 'roadmap' in career
            assert 'reality_check' in career
            
            # Verify roadmap timeframes
            assert 'immediate_1_month' in career['roadmap']
            assert 'short_term_3_6_months' in career['roadmap']
            assert 'medium_term_6_12_months' in career['roadmap']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
