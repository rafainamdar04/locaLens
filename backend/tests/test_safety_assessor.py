"""Tests for Safety Assessor service."""

import pytest
from unittest.mock import patch
from services.safety_assessor import calculate_safety_scores, assess_residential_safety


class TestSafetyAssessor:
    """Test suite for safety assessment functionality."""

    @patch('services.safety_assessor.search_nearby_places')
    @patch('services.safety_assessor.get_traffic_incidents')
    def test_calculate_safety_scores_success(self, mock_traffic, mock_places):
        """Test successful safety score calculation."""
        # Mock emergency places
        mock_places.return_value = {
            "items": [
                {"categories": [{"id": "hospital"}]},
                {"categories": [{"id": "police"}]},
                {"categories": [{"id": "fire-station"}]},
                {"categories": [{"id": "school"}]},
                {"categories": [{"id": "park"}]}
            ]
        }
        # Mock traffic
        mock_traffic.return_value = {"incidents": [{"severity": 1}, {"severity": 2}]}

        result = calculate_safety_scores(12.9716, 77.5946)

        assert "scores" in result
        assert "overall_safety" in result["scores"]
        assert result["scores"]["overall_safety"]["score"] >= 0
        assert result["scores"]["overall_safety"]["score"] <= 100
        assert "detailed_insights" in result

    @patch('services.safety_assessor.search_nearby_places')
    def test_calculate_safety_scores_error(self, mock_places):
        """Test safety calculation with API error."""
        mock_places.return_value = {"error": "API limit exceeded"}

        result = calculate_safety_scores(12.9716, 77.5946)

        assert "scores" in result
        # Should still return scores with neutral values
        assert result["scores"]["emergency_response"]["score"] == 50

    def test_assess_residential_safety(self):
        """Test main assessment function."""
        # This will use real API if key is set, or mock if patched
        result = assess_residential_safety(12.9716, 77.5946)

        assert "scores" in result
        assert "detailed_insights" in result


if __name__ == "__main__":
    # Quick demo
    print("🏠 Residential Safety Assessment Demo")
    print("=" * 50)

    # Example location: Bangalore residential area
    lat, lon = 12.9352, 77.6245

    print(f"Assessing safety for location: {lat}, {lon}")
    print()

    result = assess_residential_safety(lat, lon)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        print("Note: Requires valid HERE API key in .env")
    else:
        print("✅ Safety assessment completed!")
        print()

        scores = result['scores']
        print("📊 Safety Scores:")
        print(f"• Overall Safety: {scores['overall_safety']['score']}/100")
        print(f"  {scores['overall_safety']['explanation']}")
        print()

        print(f"• Emergency Response: {scores['emergency_response']['score']}/100")
        print(f"  {scores['emergency_response']['explanation']}")
        print()

        print(f"• Accessibility: {scores['accessibility']['score']}/100")
        print(f"  {scores['accessibility']['explanation']}")
        print()

        print(f"• Traffic Impact: {scores['traffic_impact']['score']}/100")
        print(f"  {scores['traffic_impact']['explanation']}")
        print()

        insights = result['detailed_insights']
        print("🔍 Detailed Insights:")
        print(f"• Emergency Services: {insights['emergency_services']['hospitals']} hospitals, {insights['emergency_services']['police_stations']} police stations")
        print(f"• Accessibility: {insights['accessibility']['schools']} schools, {insights['accessibility']['parks']} parks, {insights['accessibility']['public_transport']} transport stops")
        print(f"• Traffic: {insights['traffic']['incident_count']} incidents nearby")