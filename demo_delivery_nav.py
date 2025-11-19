#!/usr/bin/env python3
"""Demo script for Delivery & Navigation feature."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.delivery_navigator import get_delivery_navigation

def main():
    print("🚚 Delivery & Navigation Demo")
    print("=" * 50)

    # Example: From Bangalore central to a delivery address
    origin = {"lat": 12.9716, "lon": 77.5946}  # Bangalore
    destination = {"lat": 12.9352, "lon": 77.6245}  # Nearby area

    print(f"Origin: {origin}")
    print(f"Destination: {destination}")
    print("Transport: Car")
    print()

    # Note: This will fail without HERE API key, but shows structure
    try:
        result = get_delivery_navigation(origin, destination, "car")

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            print("Note: Requires valid HERE API key in .env")
        else:
            print("✅ Route calculated successfully!")
            print(f"Routes: {len(result['routes'])}")
            print(f"ETA: {result['routes'][0]['duration_min']:.1f} minutes")
            print(f"Distance: {result['routes'][0]['distance_km']:.1f} km")
            print()

            scores = result['scores']
            print("📊 Scores & Insights:")
            print(f"• Delivery Efficiency: {scores['delivery_efficiency']['score']}/100")
            print(f"  {scores['delivery_efficiency']['explanation']}")
            print(f"• Navigation Ease: {scores['navigation_ease']['score']}/100")
            print(f"  {scores['navigation_ease']['explanation']}")
            print(f"• Traffic Safety: {scores['traffic_safety']['score']}/100")
            print(f"  {scores['traffic_safety']['explanation']}")
            print()

            print("💡 Recommendation:")
            print(result['recommendation'])
            print()

            print("🗺️  Sample Instructions:")
            for i, instr in enumerate(result['routes'][0]['instructions'][:5], 1):
                print(f"{i}. {instr}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()