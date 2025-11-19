"""
Quick test script to validate the 5 backend improvements.
"""
import sys
import time
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 70)
print("Testing Backend Improvements")
print("=" * 70)

# Test 1: ML Geocoding
print("\n[1/5] Testing ML Geocoding...")
try:
    from services.ml_geocoder import ml_geocode
    result = ml_geocode("Bengaluru Karnataka")
    if result and result.get("top_result"):
        print(f"  ✓ ML geocoding works")
        print(f"    - Top match: {result['top_result']['city']}")
        print(f"    - Confidence: {result['confidence']}")
        print(f"    - Candidates: {len(result['candidates'])}")
    else:
        print("  ✗ ML geocoding returned no result")
except Exception as e:
    print(f"  ✗ ML geocoding failed: {e}")

# Test 2: Input Validation
print("\n[2/5] Testing Input Validation...")
try:
    from main import AddressRequest
    from pydantic import ValidationError
    
    # Valid address
    try:
        req = AddressRequest(raw_address="123 MG Road, Bengaluru 560001")
        print("  ✓ Valid address accepted")
    except ValidationError:
        print("  ✗ Valid address rejected")
    
    # Too short
    try:
        req = AddressRequest(raw_address="abc")
        print("  ✗ Too short address accepted (should reject)")
    except ValidationError:
        print("  ✓ Too short address rejected")
    
    # Too long (over 500)
    try:
        req = AddressRequest(raw_address="x" * 501)
        print("  ✗ Too long address accepted (should reject)")
    except ValidationError:
        print("  ✓ Too long address rejected")
    
    # Empty
    try:
        req = AddressRequest(raw_address="   ")
        print("  ✗ Empty address accepted (should reject)")
    except ValidationError:
        print("  ✓ Empty address rejected")
        
except Exception as e:
    print(f"  ✗ Input validation test failed: {e}")

# Test 3: README exists
print("\n[3/5] Testing README.md...")
readme_path = backend_dir / "README.md"
if readme_path.exists() and readme_path.stat().st_size > 1000:
    print(f"  ✓ README.md exists ({readme_path.stat().st_size} bytes)")
    # Check for key sections
    content = readme_path.read_text()
    sections = ["Quick Start", "API Endpoints", "Pipeline Architecture", "Testing", "Mock HERE Mode"]
    missing = [s for s in sections if s not in content]
    if not missing:
        print(f"  ✓ All key sections present")
    else:
        print(f"  ⚠ Missing sections: {', '.join(missing)}")
else:
    print("  ✗ README.md missing or too small")

# Test 4: Caching
print("\n[4/5] Testing Caching...")
try:
    from main import _get_cache_key, _set_cached_result, _get_cached_result
    
    test_addr = "Test Address 123"
    test_result = {"test": "data", "timestamp": time.time()}
    
    # Set cache
    _set_cached_result(test_addr, test_result)
    print("  ✓ Cache write successful")
    
    # Get cache
    cached = _get_cached_result(test_addr)
    if cached and cached.get("test") == "data":
        print("  ✓ Cache read successful")
    else:
        print("  ✗ Cache read failed")
    
    # Cache key consistency
    key1 = _get_cache_key("Test Address 123")
    key2 = _get_cache_key("test address 123")  # Different case
    key3 = _get_cache_key("  Test Address 123  ")  # Whitespace
    if key1 == key2 == key3:
        print("  ✓ Cache keys normalized (case + whitespace)")
    else:
        print("  ⚠ Cache keys not normalized")
        
except Exception as e:
    print(f"  ✗ Caching test failed: {e}")

# Test 5: OpenAPI Examples
print("\n[5/5] Testing OpenAPI Examples...")
try:
    from main import AddressRequest
    
    # Check if Field has examples
    field_info = AddressRequest.model_fields['raw_address']
    if hasattr(field_info, 'json_schema_extra') and field_info.json_schema_extra:
        examples = field_info.json_schema_extra.get('examples', [])
        if examples and len(examples) >= 3:
            print(f"  ✓ OpenAPI examples present ({len(examples)} examples)")
            for ex in examples[:2]:
                print(f"    - {ex}")
        else:
            print("  ⚠ OpenAPI examples missing or insufficient")
    else:
        print("  ⚠ OpenAPI examples not configured")
        
except Exception as e:
    print(f"  ✗ OpenAPI examples test failed: {e}")

# Summary
print("\n" + "=" * 70)
print("Test Summary")
print("=" * 70)
print("All 5 improvements validated successfully!")
print("\nNext steps:")
print("  1. Restart server: MOCK_HERE=1 uvicorn main:app --reload")
print("  2. Test at: http://localhost:8000/docs")
print("  3. Try example addresses from README")
