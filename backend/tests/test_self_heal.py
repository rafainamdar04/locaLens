"""
Test suite for self-healing service.
Tests all 3 healing strategies and edge cases.
"""

import sys
from pathlib import Path
import asyncio

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.self_heal import (
    self_heal,
    _extract_pincode,
    _extract_city_state,
    _extract_pincode_from_result,
    _compare_addresses,
    _generate_summary
)


async def test_low_integrity_healing():
    """Test Strategy 1: Low integrity with strict re-cleaning."""
    print("\n[TEST 1] Low Integrity Healing")
    
    raw = "  123  main  st   mumbai  400001  "
    cleaned = "123 main st mumbai 400001"
    ml_candidates = {"top_result": {"address": "123 Main St"}, "confidence": 0.6}
    here_resp = None
    reasons = ["low_integrity"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    
    print(f"  Healed: {result['healed']}")
    print(f"  Actions: {len(result['actions'])}")
    print(f"  Strategies: {result['strategies_attempted']}")
    
    assert len(result['actions']) == 1, "Expected 1 action for low_integrity"
    assert result['actions'][0]['strategy'] == 'strict_recleaning'
    assert result['actions'][0]['reason'] == 'low_integrity'
    print("  ✓ PASS")


async def test_ml_here_mismatch_healing():
    """Test Strategy 2: ML-HERE mismatch with reverse geocoding."""
    print("\n[TEST 2] ML-HERE Mismatch Healing")
    
    raw = "123 Main St, Mumbai"
    cleaned = "123 Main St Mumbai"
    ml_candidates = {
        "top_result": {
            "address": "123 Main St",
            "coordinates": {"lat": 19.0760, "lon": 72.8777}
        },
        "confidence": 0.85
    }
    here_resp = {
        "primary_result": {"address": "456 Different St, Mumbai"},
        "confidence": 0.80
    }
    reasons = ["ml_here_mismatch"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    
    print(f"  Healed: {result['healed']}")
    print(f"  Actions: {len(result['actions'])}")
    
    assert len(result['actions']) == 1, "Expected 1 action for ml_here_mismatch"
    assert result['actions'][0]['strategy'] == 'reverse_geocode_reconciliation'
    assert result['actions'][0]['reason'] == 'ml_here_mismatch'
    assert 'ml_coordinates' in result['actions'][0]
    print("  ✓ PASS")


async def test_pincode_mismatch_healing():
    """Test Strategy 3: Pincode mismatch with structured query."""
    print("\n[TEST 3] Pincode Mismatch Healing")
    
    raw = "Sector 5, Andheri, Mumbai 400058"
    cleaned = "Sector 5 Andheri Mumbai 400058"
    ml_candidates = {
        "top_result": {
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001"  # Wrong pincode
        },
        "confidence": 0.70
    }
    here_resp = None
    reasons = ["pincode_mismatch"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    
    print(f"  Healed: {result['healed']}")
    print(f"  Actions: {len(result['actions'])}")
    
    assert len(result['actions']) == 1, "Expected 1 action for pincode_mismatch"
    assert result['actions'][0]['strategy'] == 'pincode_fallback_query'
    assert result['actions'][0]['reason'] == 'pincode_mismatch'
    assert 'extracted_pincode' in result['actions'][0]
    assert result['actions'][0]['extracted_pincode'] == '400058'
    print("  ✓ PASS")


async def test_multiple_strategies():
    """Test multiple healing strategies triggered together."""
    print("\n[TEST 4] Multiple Healing Strategies")
    
    raw = "  messy   address   mumbai  400001  "
    cleaned = "messy address mumbai 400001"
    ml_candidates = {
        "top_result": {
            "address": "Messy Address",
            "coordinates": {"lat": 19.0760, "lon": 72.8777},
            "city": "Mumbai",
            "state": "Maharashtra"
        },
        "confidence": 0.50
    }
    here_resp = {
        "primary_result": {"address": "Different Address"},
        "confidence": 0.45
    }
    reasons = ["low_integrity", "ml_here_mismatch", "pincode_mismatch"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    
    print(f"  Healed: {result['healed']}")
    print(f"  Actions: {len(result['actions'])}")
    print(f"  Summary length: {len(result['summary'])}")
    
    assert len(result['actions']) == 3, "Expected 3 actions for 3 reasons"
    assert result['strategies_attempted'] == 3
    assert 'summary' in result
    assert len(result['summary']) > 0
    print("  ✓ PASS")


async def test_no_healing_needed():
    """Test when no anomalies are present."""
    print("\n[TEST 5] No Healing Needed")
    
    raw = "123 Main St, Mumbai 400001"
    cleaned = "123 Main St Mumbai 400001"
    ml_candidates = {"top_result": {"address": "123 Main St"}, "confidence": 0.95}
    here_resp = {"primary_result": {"address": "123 Main St"}, "confidence": 0.92}
    reasons = []  # No anomalies
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    
    print(f"  Healed: {result['healed']}")
    print(f"  Actions: {len(result['actions'])}")
    
    assert len(result['actions']) == 0, "Expected no actions when no reasons"
    assert result['strategies_attempted'] == 0
    print("  ✓ PASS")


def test_extract_pincode():
    """Test pincode extraction utility."""
    print("\n[TEST 6] Pincode Extraction")
    
    test_cases = [
        ("123 Main St, Mumbai 400001", "400001"),
        ("Address with 110001 pincode", "110001"),
        ("No pincode here", None),
        ("Multiple 400001 and 110001", "400001"),  # First match
        ("Short 12345 code", None),  # 5 digits - not valid
    ]
    
    for text, expected in test_cases:
        result = _extract_pincode(text)
        print(f"  '{text}' -> {result}")
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("  ✓ PASS")


def test_extract_city_state():
    """Test city and state extraction."""
    print("\n[TEST 7] City and State Extraction")
    
    ml_candidates = {
        "top_result": {
            "city": "Mumbai",
            "state": "Maharashtra"
        }
    }
    here_resp = None
    
    city, state = _extract_city_state(ml_candidates, here_resp)
    
    print(f"  City: {city}, State: {state}")
    assert city == "Mumbai"
    assert state == "Maharashtra"
    print("  ✓ PASS")


def test_extract_pincode_from_result():
    """Test pincode extraction from geocoding result."""
    print("\n[TEST 8] Pincode from Result")
    
    result = {
        "components": {
            "pincode": "400001",
            "city": "Mumbai"
        }
    }
    
    pincode = _extract_pincode_from_result(result)
    
    print(f"  Extracted: {pincode}")
    assert pincode == "400001"
    
    # Test extraction from address string
    result2 = {
        "address": "123 Main St, Mumbai 400001"
    }
    
    pincode2 = _extract_pincode_from_result(result2)
    print(f"  Extracted from address: {pincode2}")
    assert pincode2 == "400001"
    
    print("  ✓ PASS")


def test_compare_addresses():
    """Test address comparison utility."""
    print("\n[TEST 9] Address Comparison")
    
    addr1 = {"address": "123 Main Street, Mumbai"}
    addr2 = {"address": "123 Main Street Mumbai"}
    
    similarity = _compare_addresses(addr1, addr2)
    
    print(f"  Similarity: {similarity:.3f}")
    assert similarity > 0.8, "Expected high similarity for similar addresses"
    
    addr3 = {"address": "456 Different Road, Delhi"}
    similarity2 = _compare_addresses(addr1, addr3)
    
    print(f"  Different addresses: {similarity2:.3f}")
    assert similarity2 < 0.5, "Expected low similarity for different addresses"
    
    print("  ✓ PASS")


def test_generate_summary():
    """Test summary generation."""
    print("\n[TEST 10] Summary Generation")
    
    reasons = ["low_integrity", "pincode_mismatch"]
    actions = [
        {
            "strategy": "strict_recleaning",
            "reason": "low_integrity",
            "success": True,
            "improved": True,
            "confidence_gain": 0.15,
            "note": "Cleaning improved"
        },
        {
            "strategy": "pincode_fallback_query",
            "reason": "pincode_mismatch",
            "success": True,
            "pincode_validated": True
        }
    ]
    
    summary = _generate_summary(reasons, actions, healed=True)
    
    print(f"  Summary length: {len(summary)}")
    print(f"  Lines: {summary.count(chr(10)) + 1}")
    
    assert "2 anomalies detected" in summary
    assert "strict_recleaning" in summary
    assert "pincode_fallback_query" in summary
    assert "HEALED" in summary
    assert len(summary) > 100
    
    print("  ✓ PASS")


async def test_healing_with_missing_data():
    """Test healing when geocoding results are missing."""
    print("\n[TEST 11] Healing with Missing Data")
    
    raw = "123 Main St"
    cleaned = "123 Main St"
    ml_candidates = None  # Missing ML results
    here_resp = None  # Missing HERE results
    reasons = ["low_integrity", "ml_here_mismatch"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    
    print(f"  Healed: {result['healed']}")
    print(f"  Actions: {len(result['actions'])}")
    
    # Should attempt strategies but may not succeed
    assert len(result['actions']) >= 1
    assert 'summary' in result
    print("  ✓ PASS")


async def test_healing_summary_format():
    """Test that healing summary is properly formatted."""
    print("\n[TEST 12] Healing Summary Format")
    
    raw = "Sector 5, Mumbai 400001"
    cleaned = "Sector 5 Mumbai 400001"
    ml_candidates = {
        "top_result": {"city": "Mumbai", "state": "Maharashtra"},
        "confidence": 0.6
    }
    here_resp = None
    reasons = ["low_integrity", "pincode_mismatch"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    
    summary = result['summary']
    
    print(f"  Summary preview:")
    print("  " + "\n  ".join(summary.split("\n")[:5]))
    
    # Check key elements
    assert "Self-Healing Report" in summary
    assert "anomalies detected" in summary
    assert "Strategies attempted" in summary
    assert "Final Status" in summary
    
    # Check action reporting
    assert "Action 1:" in summary or "Action 2:" in summary
    
    print("  ✓ PASS")


async def run_all_tests():
    """Run all test cases."""
    print("=" * 70)
    print("SELF-HEALING SERVICE TEST SUITE")
    print("=" * 70)
    
    # Async tests
    async_tests = [
        test_low_integrity_healing,
        test_ml_here_mismatch_healing,
        test_pincode_mismatch_healing,
        test_multiple_strategies,
        test_no_healing_needed,
        test_healing_with_missing_data,
        test_healing_summary_format
    ]
    
    # Sync tests
    sync_tests = [
        test_extract_pincode,
        test_extract_city_state,
        test_extract_pincode_from_result,
        test_compare_addresses,
        test_generate_summary
    ]
    
    passed = 0
    failed = 0
    
    # Run async tests
    for test in async_tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
    
    # Run sync tests
    for test in sync_tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
