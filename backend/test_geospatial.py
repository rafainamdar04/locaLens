"""Test script for geospatial checks."""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.geospatial import (
    check_geospatial_consistency,
    haversine_distance
)


def test_haversine():
    """Test haversine distance calculation."""
    print("="*70)
    print("Testing Haversine Distance Calculation")
    print("="*70)
    
    # Test 1: Mumbai to Delhi (approx 1150 km)
    mumbai = (19.0760, 72.8777)
    delhi = (28.7041, 77.1025)
    
    dist = haversine_distance(*mumbai, *delhi)
    print(f"\nMumbai to Delhi: {dist:.2f} km")
    print(f"  Expected: ~1150 km")
    print(f"  ✓ Looks correct" if 1100 < dist < 1200 else "  ✗ Error")
    
    # Test 2: Bangalore to Chennai (approx 290 km)
    bangalore = (12.9716, 77.5946)
    chennai = (13.0827, 80.2707)
    
    dist = haversine_distance(*bangalore, *chennai)
    print(f"\nBangalore to Chennai: {dist:.2f} km")
    print(f"  Expected: ~290 km")
    print(f"  ✓ Looks correct" if 280 < dist < 340 else "  ✗ Error")
    
    # Test 3: Same location (0 km)
    dist = haversine_distance(*mumbai, *mumbai)
    print(f"\nMumbai to Mumbai: {dist:.2f} km")
    print(f"  Expected: 0 km")
    print(f"  ✓ Correct" if dist < 0.01 else "  ✗ Error")


def test_geospatial_consistency():
    """Test geospatial consistency checking."""
    print("\n" + "="*70)
    print("Testing Geospatial Consistency Checks")
    print("="*70)
    
    # Test 1: ML and HERE agree (close locations)
    print("\n--- Test 1: Close ML and HERE results ---")
    ml_result = {
        "lat": 19.0760,
        "lon": 72.8777,
        "address": "Mumbai"
    }
    here_result = {
        "lat": 19.0800,  # ~400m away
        "lon": 72.8800,
        "address": "Mumbai"
    }
    cleaned_components = {
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001"
    }
    
    result = check_geospatial_consistency(ml_result, here_result, cleaned_components)
    print(f"Mismatch: {result['mismatch_km']} km")
    print(f"Pincode mismatch: {result['pincode_mismatch']}")
    print(f"City violation: {result['city_violation']}")
    if 'ml_pincode_distance_km' in result['details']:
        print(f"ML to pincode centroid: {result['details']['ml_pincode_distance_km']} km")
    
    # Test 2: ML and HERE disagree (far locations)
    print("\n--- Test 2: Distant ML and HERE results ---")
    ml_result = {
        "lat": 19.0760,
        "lon": 72.8777,
    }
    here_result = {
        "lat": 28.7041,  # Delhi coordinates (very far)
        "lon": 77.1025,
    }
    cleaned_components = {
        "pincode": "400001"  # Mumbai pincode
    }
    
    result = check_geospatial_consistency(ml_result, here_result, cleaned_components)
    print(f"Mismatch: {result['mismatch_km']} km")
    print(f"Pincode mismatch: {result['pincode_mismatch']}")
    print(f"✓ Large mismatch detected" if result['mismatch_km'] > 100 else "✗ Failed to detect")
    
    # Test 3: Only pincode check
    print("\n--- Test 3: Pincode consistency only ---")
    ml_result = {
        "lat": 12.9716,  # Bangalore
        "lon": 77.5946,
    }
    cleaned_components = {
        "pincode": "560001"  # Bangalore pincode
    }
    
    result = check_geospatial_consistency(ml_result, None, cleaned_components)
    print(f"Mismatch: {result['mismatch_km']}")
    print(f"Pincode mismatch: {result['pincode_mismatch']}")
    if 'ml_pincode_distance_km' in result['details']:
        print(f"ML to pincode centroid: {result['details']['ml_pincode_distance_km']} km")
        print(f"✓ Within expected range" if result['details']['ml_pincode_distance_km'] < 20 else "⚠ Check may need adjustment")
    
    # Test 4: Invalid pincode
    print("\n--- Test 4: Invalid pincode ---")
    cleaned_components = {
        "pincode": "999999"  # Non-existent
    }
    
    result = check_geospatial_consistency(ml_result, None, cleaned_components)
    print(f"Pincode mismatch: {result['pincode_mismatch']}")
    if 'pincode_not_found' in result['details']:
        print(f"✓ Correctly identified missing pincode: {result['details']['pincode_not_found']}")
    
    # Test 5: No data
    print("\n--- Test 5: No geocoding results ---")
    result = check_geospatial_consistency(None, None, {})
    print(f"Mismatch: {result['mismatch_km']}")
    print(f"Pincode mismatch: {result['pincode_mismatch']}")
    print(f"City violation: {result['city_violation']}")
    print(f"✓ Handles empty data gracefully")


if __name__ == "__main__":
    test_haversine()
    test_geospatial_consistency()
    
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)
