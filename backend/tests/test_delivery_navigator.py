"""Tests for Delivery & Navigation service."""

import os
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Ensure repo root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.delivery_navigator import calculate_route, extract_route_insights, get_delivery_navigation


class TestDeliveryNavigator:
    """Test suite for delivery navigation functionality."""

    @patch('services.delivery_navigator._geocode_with_retry')
    def test_calculate_route_success(self, mock_retry):
        """Test successful route calculation."""
        mock_response = {
            "routes": [{
                "sections": [{
                    "summary": {
                        "length": 10000,  # 10 km
                        "duration": 900,  # 15 min
                        "baseDuration": 720  # 12 min without traffic
                    },
                    "polyline": "encoded_polyline",
                    "actions": [
                        {"instruction": "Turn left onto Main St"},
                        {"instruction": "Continue straight"}
                    ]
                }]
            }]
        }
        mock_retry.return_value = mock_response

        origin = {"lat": 12.9716, "lon": 77.5946}  # Bangalore
        dest = {"lat": 13.0827, "lon": 80.2707}  # Chennai approx

        result = calculate_route(origin, dest, "car")

        assert "routes" in result
        assert result["routes"][0]["sections"][0]["summary"]["length"] == 10000

    @patch('services.delivery_navigator._geocode_with_retry')
    def test_calculate_route_error(self, mock_retry):
        """Test route calculation with API error."""
        mock_retry.return_value = {"error": "Rate limit exceeded"}

        origin = {"lat": 12.9716, "lon": 77.5946}
        dest = {"lat": 13.0827, "lon": 80.2707}

        result = calculate_route(origin, dest)

        assert "error" in result
        assert result["error"] == "Rate limit exceeded"

    def test_extract_route_insights(self):
        """Test extraction of insights from route data."""
        route_data = {
            "routes": [{
                "sections": [{
                    "summary": {
                        "length": 5000,  # 5 km
                        "duration": 600,  # 10 min
                        "baseDuration": 480  # 8 min
                    },
                    "actions": [
                        {"instruction": "Start on Main St"},
                        {"instruction": "Turn right"}
                    ]
                }]
            }]
        }

        insights = extract_route_insights(route_data)

        assert "routes" in insights
        assert "scores" in insights
        assert "recommendation" in insights
        assert insights["scores"]["delivery_efficiency"]["score"] >= 0
        assert insights["scores"]["delivery_efficiency"]["score"] <= 100

    @patch('services.delivery_navigator.calculate_route')
    def test_get_delivery_navigation(self, mock_calc):
        """Test main navigation function."""
        mock_calc.return_value = {
            "routes": [{
                "sections": [{
                    "summary": {"length": 10000, "duration": 900, "baseDuration": 720},
                    "actions": [{"instruction": "Drive north"}]
                }]
            }]
        }

        origin = {"lat": 12.9716, "lon": 77.5946}
        dest = {"lat": 13.0827, "lon": 80.2707}

        result = get_delivery_navigation(origin, dest)

        assert "routes" in result
        assert "scores" in result
        assert "recommendation" in result


if __name__ == "__main__":
    # Quick demo
    print("Testing Delivery Navigator...")

    # Mock a simple test
    route_data = {
        "routes": [{
            "sections": [{
                "summary": {"length": 15000, "duration": 1200, "baseDuration": 900},
                "actions": [
                    {"instruction": "Head north on Highway"},
                    {"instruction": "Turn left at exit"},
                    {"instruction": "Arrive at destination"}
                ]
            }]
        }]
    }

    insights = extract_route_insights(route_data)
    print("Sample Insights:")
    print(f"Routes: {len(insights['routes'])}")
    print(f"Efficiency Score: {insights['scores']['delivery_efficiency']['score']}/100")
    print(f"Explanation: {insights['scores']['delivery_efficiency']['explanation']}")
    print(f"Recommendation: {insights['recommendation']}")