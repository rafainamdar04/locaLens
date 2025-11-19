#!/usr/bin/env python3
"""Demo script for Residential Safety Assessment feature."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.safety_assessor import assess_residential_safety

def main():
    print("🏠 Residential Safety Assessment Demo")
    print("=" * 50)

    # Example: Residential area in Bangalore
    lat, lon = 12.9352, 77.6245  # Koramangala area

    print(f"Assessing safety for residential location: {lat}, {lon}")
    print("(Example: Koramangala, Bangalore)")
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
        print("🔍 Detailed Insights for Real Estate:")
        print(f"• Emergency Services: {insights['emergency_services']['hospitals']} hospitals, {insights['emergency_services']['police_stations']} police stations, {insights['emergency_services']['fire_stations']} fire stations within 3km")
        print(f"• Daily Amenities: {insights['accessibility']['schools']} schools, {insights['accessibility']['parks']} parks, {insights['accessibility']['shopping']} shopping areas within 1.5km")
        print(f"• Public Transport: {insights['accessibility']['public_transport']} stops nearby")
        print(f"• Traffic Concerns: {insights['traffic']['incident_count']} incidents within 2km")
        print()

        print("💡 Real Estate Recommendations:")
        if scores['overall_safety']['score'] > 80:
            print("• Excellent choice for families - safe, accessible, and well-serviced.")
        elif scores['overall_safety']['score'] > 60:
            print("• Good residential option with solid safety features.")
        else:
            print("• Consider additional security measures or nearby alternatives.")

if __name__ == "__main__":
    main()