"""
HERE geocoder tests.

These tests are skipped as they require live HERE API calls.
For integration testing, use the main test suite with a valid API key.
"""
import os
import sys
from pathlib import Path
import pytest

# Skip entire module: these were mock-specific tests, now obsolete
pytest.skip("Mock mode removed: skipping legacy mock tests", allow_module_level=True)

# Ensure repo root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_mock_here_pincode():
    """Ensure mock HERE returns centroid for a pincode."""
    print("\n[TEST 1] Mock HERE - Pincode lookup")
    addr = "123 MG Road, Bangalore 560001"
    res = here_geocode(addr)
    print(f"  Response: {res}")
    assert isinstance(res, dict)
    # In mock mode, response must include mock flag
    assert res['raw_response'] and res['raw_response'].get('mock') is True
    primary = res['primary_result']
    assert primary is not None
    assert primary['pincode'] == '560001'
    assert 'lat' in primary and 'lon' in primary
    assert res['confidence'] >= 0.8
    print("  ✓ PASS")


def test_mock_here_city_fallback():
    """Ensure mock HERE returns city mapping when pincode missing."""
    print("\n[TEST 2] Mock HERE - City fallback")
    addr = "Near MG Road, Bangalore"
    res = here_geocode(addr)
    primary = res['primary_result']
    assert primary is not None
    assert primary['city'] is not None
    assert 'lat' in primary and 'lon' in primary
    print("  ✓ PASS")


if __name__ == '__main__':
    # Run tests (expects MOCK_HERE to be set in env before launching)
    print("Starting mock-HERE tests. MOCK_HERE =", os.getenv('MOCK_HERE'))
    
    tests = [
        test_mock_here_pincode,
        test_mock_here_city_fallback
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1

    print(f"\nRESULTS: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
    sys.exit(0)
