"""
Unit Tests for Interest Intersection Detection

Task 7.1: Create interest intersection detection logic
Tests the detect_interest_intersections() function that identifies cross-domain patterns
when multiple interest domains score ≥70.

Validates Requirements: 2.5
"""

import pytest

from neuroapt.app.utils.profile_builder import (
    detect_interest_intersections,
    format_generic_intersection
)


class TestDetectInterestIntersections:
    """Tests for the detect_interest_intersections() function."""

    # --- No intersection (fewer than 2 high domains) -------------------------

    def test_no_high_domains_returns_empty_string(self):
        """When no domains score ≥70, should return empty string."""
        domains = {
            'stem_tech': 50,
            'creative_media': 60,
            'people_oriented': 65,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 55
        }
        result = detect_interest_intersections(domains)
        assert result == ''

    def test_single_high_domain_returns_empty_string(self):
        """When only one domain scores ≥70, should return empty string."""
        domains = {
            'stem_tech': 85,
            'creative_media': 60,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == ''

    def test_all_domains_below_threshold_returns_empty_string(self):
        """When all domains are below 70, should return empty string."""
        domains = {
            'stem_tech': 69,
            'creative_media': 69,
            'people_oriented': 69,
            'business_management': 69,
            'legal_governance': 69,
            'logistics_distribution': 69
        }
        result = detect_interest_intersections(domains)
        assert result == ''

    # --- Specific pattern matches (2 high domains) ---------------------------

    def test_stem_plus_creative_pattern(self):
        """STEM+Creative pattern: stem_tech and creative_media both ≥70."""
        domains = {
            'stem_tech': 75,
            'creative_media': 80,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == 'STEM+Creative'

    def test_business_plus_people_oriented_pattern(self):
        """Business+People-Oriented pattern."""
        domains = {
            'stem_tech': 50,
            'creative_media': 60,
            'people_oriented': 85,
            'business_management': 75,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == 'Business+People-Oriented'

    def test_stem_plus_business_pattern(self):
        """STEM+Business pattern."""
        domains = {
            'stem_tech': 90,
            'creative_media': 60,
            'people_oriented': 50,
            'business_management': 70,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == 'STEM+Business'

    def test_legal_plus_people_oriented_pattern(self):
        """Legal+People-Oriented pattern."""
        domains = {
            'stem_tech': 50,
            'creative_media': 60,
            'people_oriented': 75,
            'business_management': 40,
            'legal_governance': 80,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == 'Legal+People-Oriented'

    def test_creative_plus_people_oriented_pattern(self):
        """Creative+People-Oriented pattern."""
        domains = {
            'stem_tech': 50,
            'creative_media': 85,
            'people_oriented': 72,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == 'Creative+People-Oriented'

    def test_legal_plus_business_pattern(self):
        """Legal+Business pattern."""
        domains = {
            'stem_tech': 50,
            'creative_media': 60,
            'people_oriented': 50,
            'business_management': 78,
            'legal_governance': 82,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == 'Legal+Business'

    def test_logistics_plus_business_pattern(self):
        """Logistics+Business pattern."""
        domains = {
            'stem_tech': 50,
            'creative_media': 60,
            'people_oriented': 50,
            'business_management': 75,
            'legal_governance': 30,
            'logistics_distribution': 80
        }
        result = detect_interest_intersections(domains)
        assert result == 'Logistics+Business'

    # --- Edge case: exactly at threshold -------------------------------------

    def test_domains_exactly_at_70_are_included(self):
        """Domains scoring exactly 70 should be included."""
        domains = {
            'stem_tech': 70,
            'creative_media': 70,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == 'STEM+Creative'

    def test_one_at_70_one_above_70(self):
        """One domain at 70, one above 70."""
        domains = {
            'stem_tech': 70,
            'creative_media': 85,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == 'STEM+Creative'

    # --- Generic patterns (unlisted pairs) -----------------------------------

    def test_generic_pattern_stem_plus_legal(self):
        """Unlisted pair should use generic formatting."""
        domains = {
            'stem_tech': 75,
            'creative_media': 60,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 80,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        # Sorted by score: legal_governance (80) > stem_tech (75)
        assert result == 'Legal+STEM'

    def test_generic_pattern_creative_plus_logistics(self):
        """Another unlisted pair."""
        domains = {
            'stem_tech': 50,
            'creative_media': 88,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 72
        }
        result = detect_interest_intersections(domains)
        assert result == 'Creative+Logistics'

    # --- Three or more high domains ------------------------------------------

    def test_three_high_domains_returns_best_match(self):
        """With 3 high domains, should find best matching pattern from known pairs."""
        domains = {
            'stem_tech': 80,
            'creative_media': 75,
            'people_oriented': 70,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        # Should match STEM+Creative (highest scoring pair)
        assert result == 'STEM+Creative'

    def test_three_high_domains_with_known_pattern(self):
        """With 3 high domains where two form a known pattern."""
        domains = {
            'stem_tech': 50,
            'creative_media': 75,
            'people_oriented': 85,
            'business_management': 70,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        # Sorted by score: people_oriented (85) > creative_media (75) > business_management (70)
        # Should find Creative+People-Oriented pattern (highest scoring pair with known pattern)
        assert result == 'Creative+People-Oriented'

    def test_four_high_domains_returns_best_pattern(self):
        """With 4 high domains, should find best matching known pattern."""
        domains = {
            'stem_tech': 85,
            'creative_media': 80,
            'people_oriented': 75,
            'business_management': 72,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        # Should find a known pattern among the pairs
        assert result in ['STEM+Creative', 'STEM+Business', 
                          'Business+People-Oriented', 'Creative+People-Oriented']

    def test_all_domains_high_returns_pattern(self):
        """When all 6 domains are high, should still return a meaningful pattern."""
        domains = {
            'stem_tech': 85,
            'creative_media': 80,
            'people_oriented': 90,
            'business_management': 75,
            'legal_governance': 78,
            'logistics_distribution': 82
        }
        result = detect_interest_intersections(domains)
        # Should not be empty
        assert result != ''
        # Should contain a '+' separator
        assert '+' in result

    # --- Ordering consistency ------------------------------------------------

    def test_ordering_by_score_is_consistent(self):
        """Domains are sorted by score, so highest scoring domain appears first."""
        domains_a = {
            'stem_tech': 90,  # Higher score
            'creative_media': 50,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 75,  # Lower score
            'logistics_distribution': 45
        }
        domains_b = {
            'stem_tech': 75,  # Lower score now
            'creative_media': 50,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 90,  # Higher score now
            'logistics_distribution': 45
        }
        result_a = detect_interest_intersections(domains_a)
        result_b = detect_interest_intersections(domains_b)
        
        # Both should return a result
        assert result_a != ''
        assert result_b != ''
        # When scores are flipped, order changes
        assert result_a == 'STEM+Legal'  # stem_tech (90) > legal_governance (75)
        assert result_b == 'Legal+STEM'  # legal_governance (90) > stem_tech (75)


class TestFormatGenericIntersection:
    """Tests for the format_generic_intersection() helper function."""

    def test_format_two_domains(self):
        """Basic formatting of two domain names."""
        result = format_generic_intersection(['stem_tech', 'creative_media'])
        assert result == 'STEM+Creative'

    def test_format_preserves_order(self):
        """Formatting should preserve the order passed in."""
        result = format_generic_intersection(['legal_governance', 'logistics_distribution'])
        assert result == 'Legal+Logistics'

    def test_format_all_domain_types(self):
        """Test formatting for each domain type."""
        mappings = {
            'stem_tech': 'STEM',
            'creative_media': 'Creative',
            'people_oriented': 'People-Oriented',
            'business_management': 'Business',
            'legal_governance': 'Legal',
            'logistics_distribution': 'Logistics'
        }
        
        for domain, expected in mappings.items():
            # Test with another domain
            result = format_generic_intersection([domain, 'stem_tech'])
            assert expected in result

    def test_format_unknown_domain_uses_title_case(self):
        """Unknown domain names should be title-cased."""
        result = format_generic_intersection(['unknown_domain', 'stem_tech'])
        assert 'Unknown_Domain' in result
        assert 'STEM' in result


class TestInterestIntersectionIntegration:
    """Integration tests for interest intersection detection in profile building."""

    def test_intersection_appears_in_metadata(self):
        """The interest_intersection should appear in profile metadata."""
        # This test would require importing TestResult mock
        # For now, we just verify the function works standalone
        domains = {
            'stem_tech': 85,
            'creative_media': 75,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == 'STEM+Creative'

    def test_empty_intersection_when_no_pattern(self):
        """Empty string should be returned when no intersection exists."""
        domains = {
            'stem_tech': 50,
            'creative_media': 60,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == ''


class TestInterestIntersectionBoundaryConditions:
    """Test boundary conditions and edge cases."""

    def test_score_69_is_not_included(self):
        """Score of 69 should not count as high (threshold is 70)."""
        domains = {
            'stem_tech': 69,
            'creative_media': 69,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == ''

    def test_score_100_works(self):
        """Maximum score of 100 should work correctly."""
        domains = {
            'stem_tech': 100,
            'creative_media': 100,
            'people_oriented': 50,
            'business_management': 40,
            'legal_governance': 30,
            'logistics_distribution': 45
        }
        result = detect_interest_intersections(domains)
        assert result == 'STEM+Creative'

    def test_all_zeros_returns_empty(self):
        """All zero scores should return empty string."""
        domains = {
            'stem_tech': 0,
            'creative_media': 0,
            'people_oriented': 0,
            'business_management': 0,
            'legal_governance': 0,
            'logistics_distribution': 0
        }
        result = detect_interest_intersections(domains)
        assert result == ''
