"""Test city boundary checking with the city_boundaries.json file."""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.geospatial import check_geospatial_consistency


def test_city_boundaries():
    """Test city boundary violation detection."""
    print("="*70)
    print("Testing City Boundary Checks")
    print("="*70)
    
    # Test 1: Valid Mumbai location
    print("\n--- Test 1: Valid Mumbai location ---")
    ml_result = {
        "lat": 19.0760,  # Mumbai CST
        "lon": 72.8777,
    }
    cleaned_components = {
        "city": "Mumbai",
        "pincode": "400001"
    }
    
    result = check_geospatial_consistency(ml_result, None, cleaned_components)
    print(f"City violation: {result['city_violation']}")
    print(f"✓ Correctly inside Mumbai" if not result['city_violation'] else "✗ False violation")
    
    # Test 2: Delhi coordinates but Mumbai city claim (violation)
    print("\n--- Test 2: Delhi coords with Mumbai city (should violate) ---")
    ml_result = {
        "lat": 28.7041,  # Delhi
        "lon": 77.1025,
    }
    cleaned_components = {
        "city": "Mumbai"
    }
    
    result = check_geospatial_consistency(ml_result, None, cleaned_components)
    print(f"City violation: {result['city_violation']}")
    print(f"Details: {result['details'].get('ml_outside_city', 'N/A')}")
    print(f"✓ Correctly detected violation" if result['city_violation'] else "✗ Missed violation")
    
    # Test 3: Valid Bangalore location
    print("\n--- Test 3: Valid Bangalore location ---")
    here_result = {
        "lat": 12.9716,  # Bangalore center
        "lon": 77.5946,
    }
    cleaned_components = {
        "city": "Bangalore"
    }
    
    result = check_geospatial_consistency(None, here_result, cleaned_components)
    print(f"City violation: {result['city_violation']}")
    print(f"✓ Correctly inside Bangalore" if not result['city_violation'] else "✗ False violation")
    
    # Test 4: Both ML and HERE outside claimed city
    print("\n--- Test 4: Both sources outside claimed city ---")
    ml_result = {
        "lat": 13.0827,  # Chennai
        "lon": 80.2707,
    }
    here_result = {
        "lat": 22.5726,  # Kolkata
        "lon": 88.3639,
    }
    cleaned_components = {
        "city": "Mumbai"
    }
    
    result = check_geospatial_consistency(ml_result, here_result, cleaned_components)
    print(f"City violation: {result['city_violation']}")
    print(f"ML outside: {result['details'].get('ml_outside_city', False)}")
    print(f"HERE outside: {result['details'].get('here_outside_city', False)}")
    print(f"✓ Both violations detected" if result['city_violation'] else "✗ Missed violations")
    
    # Test 5: City not in boundaries file
    print("\n--- Test 5: Unknown city (not in boundaries file) ---")
    ml_result = {
        "lat": 23.0225,
        "lon": 72.5714,
    }
    cleaned_components = {
        "city": "Ahmedabad"  # Not in our sample boundaries file
    }
    
    result = check_geospatial_consistency(ml_result, None, cleaned_components)
    print(f"City violation: {result['city_violation']}")
    print(f"✓ No false violation for unknown city" if not result['city_violation'] else "✗ False violation")


if __name__ == "__main__":
    test_city_boundaries()
    
    print("\n" + "="*70)
    print("City boundary tests completed!")
    print("="*70)
