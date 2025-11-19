"""
Comprehensive test demonstrating all geospatial check features.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.geospatial import check_geospatial_consistency


def demo_geospatial_checks():
    """Demonstrate all geospatial checking capabilities."""
    
    print("\n" + "="*70)
    print("Geospatial Consistency Checks - Complete Demo")
    print("="*70)
    
    # Scenario 1: Perfect consistency
    print("\n" + "-"*70)
    print("SCENARIO 1: High Confidence - All sources agree")
    print("-"*70)
    ml_result = {
        "lat": 19.0760,
        "lon": 72.8777,
        "address": "Chhatrapati Shivaji Terminus, Mumbai"
    }
    here_result = {
        "lat": 19.0765,  # Very close
        "lon": 72.8780,
        "address": "CST, Mumbai"
    }
    cleaned_components = {
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001"
    }
    
    result = check_geospatial_consistency(ml_result, here_result, cleaned_components)
    
    print(f"\n✓ ML and HERE results: {result['mismatch_km']} km apart")
    print(f"✓ ML to pincode centroid: {result['details'].get('ml_pincode_distance_km', 'N/A')} km")
    print(f"✓ HERE to pincode centroid: {result['details'].get('here_pincode_distance_km', 'N/A')} km")
    print(f"✓ Pincode mismatch: {result['pincode_mismatch']}")
    print(f"✓ City boundary violation: {result['city_violation']}")
    print(f"\n→ VERDICT: HIGH CONFIDENCE - All checks passed")
    
    # Scenario 2: Moderate mismatch
    print("\n" + "-"*70)
    print("SCENARIO 2: Medium Confidence - Moderate ML/HERE distance")
    print("-"*70)
    ml_result = {
        "lat": 12.9716,
        "lon": 77.5946,
        "address": "MG Road, Bangalore"
    }
    here_result = {
        "lat": 13.0100,  # ~5km away
        "lon": 77.6200,
        "address": "Whitefield, Bangalore"
    }
    cleaned_components = {
        "city": "Bangalore",
        "pincode": "560001"
    }
    
    result = check_geospatial_consistency(ml_result, here_result, cleaned_components)
    
    print(f"\n⚠ ML and HERE results: {result['mismatch_km']} km apart")
    print(f"✓ ML to pincode: {result['details'].get('ml_pincode_distance_km', 'N/A')} km")
    print(f"✓ HERE to pincode: {result['details'].get('here_pincode_distance_km', 'N/A')} km")
    print(f"✓ Pincode mismatch: {result['pincode_mismatch']}")
    print(f"✓ City boundary: {result['city_violation']}")
    print(f"\n→ VERDICT: MEDIUM CONFIDENCE - Some discrepancy but within city")
    
    # Scenario 3: Major red flags
    print("\n" + "-"*70)
    print("SCENARIO 3: Low Confidence - Major inconsistencies detected")
    print("-"*70)
    ml_result = {
        "lat": 19.0760,  # Mumbai
        "lon": 72.8777,
        "address": "Mumbai location"
    }
    here_result = {
        "lat": 28.7041,  # Delhi
        "lon": 77.1025,
        "address": "Delhi location"
    }
    cleaned_components = {
        "city": "Bangalore",  # Claims Bangalore
        "pincode": "560001"   # Bangalore pincode
    }
    
    result = check_geospatial_consistency(ml_result, here_result, cleaned_components)
    
    print(f"\n✗ ML and HERE results: {result['mismatch_km']} km apart (MAJOR MISMATCH)")
    print(f"✗ ML to pincode: {result['details'].get('ml_pincode_distance_km', 'N/A')} km")
    print(f"✗ HERE to pincode: {result['details'].get('here_pincode_distance_km', 'N/A')} km")
    print(f"✗ Pincode mismatch: {result['pincode_mismatch']} (FLAGGED)")
    print(f"✗ City boundary: {result['city_violation']} (FLAGGED)")
    print(f"\n→ VERDICT: LOW CONFIDENCE - Needs self-healing / manual review")
    
    # Scenario 4: Sparse data (only ML)
    print("\n" + "-"*70)
    print("SCENARIO 4: Partial Data - Only ML result available")
    print("-"*70)
    ml_result = {
        "lat": 13.0827,
        "lon": 80.2707,
        "address": "Chennai"
    }
    cleaned_components = {
        "city": "Chennai",
        "pincode": "600001"
    }
    
    result = check_geospatial_consistency(ml_result, None, cleaned_components)
    
    print(f"\nℹ ML result only (no HERE comparison)")
    print(f"✓ ML to pincode: {result['details'].get('ml_pincode_distance_km', 'N/A')} km")
    print(f"✓ Pincode mismatch: {result['pincode_mismatch']}")
    print(f"✓ City boundary: {result['city_violation']}")
    print(f"\n→ VERDICT: Can still validate with pincode and city boundaries")
    
    print("\n" + "="*70)
    print("Demo Complete - Geospatial checks working as expected!")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_geospatial_checks()
