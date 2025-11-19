"""
Test suite for integrity scoring service.
Tests all scoring rules and edge cases.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.integrity import compute_integrity


def test_complete_address():
    """Test integrity scoring for a complete address."""
    print("\n[TEST 1] Complete Address with All Components")
    
    raw = "123 MG Road, Bangalore, Karnataka 560001"
    cleaned = "123 MG Road, Bangalore, Karnataka 560001"
    
    result = compute_integrity(raw, cleaned)
    
    print(f"  Raw: {raw}")
    print(f"  Cleaned: {cleaned}")
    print(f"  Score: {result['score']}")
    print(f"  Issues: {result['issues']}")
    print(f"  Components: {result['components']}")
    
    # Base(50) + pincode(+15) + city(+10) = 75
    assert result['score'] >= 70, f"Expected score ~75, got {result['score']}"
    assert result['components']['pincode'] == '560001'
    assert result['components']['city'] is not None
    assert len(result['issues']) == 0
    
    print("  ✓ PASS")


def test_missing_pincode():
    """Test penalty for missing pincode."""
    print("\n[TEST 2] Address Without Pincode")
    
    raw = "MG Road, Bangalore"
    cleaned = "MG Road, Bangalore"
    
    result = compute_integrity(raw, cleaned)
    
    print(f"  Raw: {raw}")
    print(f"  Score: {result['score']}")
    print(f"  Issues: {result['issues']}")
    print(f"  Components: {result['components']}")
    
    # Base(50) + city(+10) - no_pincode(0) = 60
    assert result['components']['pincode'] is None
    assert 'missing_pincode' in result['issues']
    assert result['score'] == 60  # 50 base + 10 city
    
    print("  ✓ PASS")


def test_missing_city():
    """Test penalty for missing city."""
    print("\n[TEST 3] Address Without City")
    
    raw = "123 Unknown Street 560001"
    cleaned = "123 Unknown Street 560001"
    
    result = compute_integrity(raw, cleaned)
    
    print(f"  Raw: {raw}")
    print(f"  Score: {result['score']}")
    print(f"  Issues: {result['issues']}")
    print(f"  Components: {result['components']}")
    
    # Base(50) + pincode(+15) - no_city(-20) = 45
    assert result['components']['city'] is None
    assert 'no_city_found' in result['issues']
    assert result['score'] == 45
    
    print("  ✓ PASS")


def test_vague_tokens():
    """Test penalty for vague location tokens."""
    print("\n[TEST 4] Address with Vague Tokens")
    
    raw = "Near railway station, Bangalore 560001"
    cleaned = "Near railway station, Bangalore 560001"
    
    result = compute_integrity(raw, cleaned)
    
    print(f"  Raw: {raw}")
    print(f"  Score: {result['score']}")
    print(f"  Issues: {result['issues']}")
    
    # Base(50) + pincode(+15) + city(+10) - vague(-10) = 65
    assert 'contains_vague_tokens' in result['issues']
    assert result['score'] == 65
    
    print("  ✓ PASS")


def test_too_short():
    """Test penalty for very short addresses."""
    print("\n[TEST 5] Address Too Short (< 15 chars)")
    
    raw = "Mumbai 400001"
    cleaned = "Mumbai 400001"
    
    result = compute_integrity(raw, cleaned)
    
    print(f"  Raw: {raw}")
    print(f"  Cleaned: '{cleaned}' (length: {len(cleaned)})")
    print(f"  Score: {result['score']}")
    print(f"  Issues: {result['issues']}")
    
    # Base(50) + pincode(+15) + city(+10) - short(-15) = 60
    assert len(cleaned) < 15
    assert 'too_short' in result['issues']
    assert result['score'] == 60
    
    print("  ✓ PASS")


def test_multiple_issues():
    """Test address with multiple quality issues."""
    print("\n[TEST 6] Address with Multiple Issues")
    
    raw = "Near xyz"
    cleaned = "Near xyz"
    
    result = compute_integrity(raw, cleaned)
    
    print(f"  Raw: {raw}")
    print(f"  Score: {result['score']}")
    print(f"  Issues: {result['issues']}")
    print(f"  Components: {result['components']}")
    
    # Base(50) - no_city(-20) - vague(-10) - short(-15) = 5
    # (no pincode bonus since missing)
    assert result['score'] <= 10
    assert len(result['issues']) >= 3
    assert 'contains_vague_tokens' in result['issues']
    assert 'too_short' in result['issues']
    
    print("  ✓ PASS")


def test_perfect_score():
    """Test address that achieves maximum score."""
    print("\n[TEST 7] Perfect Score Address")
    
    raw = "123 Brigade Road, Bangalore, Karnataka 560001"
    cleaned = "123 Brigade Road, Bangalore, Karnataka 560001"
    
    result = compute_integrity(raw, cleaned)
    
    print(f"  Raw: {raw}")
    print(f"  Score: {result['score']}")
    print(f"  Issues: {result['issues']}")
    
    # Base(50) + pincode(+15) + city(+10) = 75 (max possible)
    assert result['score'] == 75
    assert len(result['issues']) == 0
    
    print("  ✓ PASS")


def test_worst_case():
    """Test address that gets lowest possible score."""
    print("\n[TEST 8] Worst Case Score")
    
    raw = "Near"
    cleaned = "Near"
    
    result = compute_integrity(raw, cleaned)
    
    print(f"  Raw: {raw}")
    print(f"  Score: {result['score']}")
    print(f"  Issues: {result['issues']}")
    
    # Base(50) - no_city(-20) - vague(-10) - short(-15) = 5
    # Score clamped at 0 minimum
    assert result['score'] >= 0
    assert result['score'] <= 10
    assert len(result['issues']) >= 3
    
    print("  ✓ PASS")


def test_known_vs_unknown_city():
    """Test major cities are properly detected."""
    print("\n[TEST 9] Major City Detection")
    
    # Test major Indian cities
    major_cities = [
        ("MG Road, Mumbai 400001", "mumbai"),
        ("Brigade Road, Bangalore 560001", "bangalore"),
        ("CP, Delhi 110001", "delhi"),
        ("Marina Beach, Chennai 600001", "chennai"),
        ("123 Bund Garden, Pune 411001", "pune"),
    ]
    
    all_passed = True
    for addr, expected_city in major_cities:
        result = compute_integrity(addr, addr)
        city = result['components']['city']
        score = result['score']
        
        print(f"  '{addr}' -> City: {city}, Score: {score}")
        
        # Check if expected city is found and score is high
        if city and expected_city in city.lower():
            assert score >= 70, f"Expected high score for {expected_city}"
        else:
            print(f"    Warning: Expected {expected_city}, got {city}")
            all_passed = False
    
    assert all_passed, "Not all major cities were detected"
    print("  ✓ PASS")


def test_vague_token_examples():
    """Test various vague token examples."""
    print("\n[TEST 10] Various Vague Token Examples")
    
    vague_examples = [
        "Opposite police station, Delhi 110001",
        "Behind temple, Chennai 600001",
        "Close to airport, Mumbai 400001",
        "Around market area, Pune 411001"
    ]
    
    for addr in vague_examples:
        result = compute_integrity(addr, addr)
        print(f"  '{addr}' -> Score: {result['score']}, Vague: {'contains_vague_tokens' in result['issues']}")
        assert 'contains_vague_tokens' in result['issues']
    
    print("  ✓ PASS")


def test_score_bounds():
    """Test that score is always clamped to 0-100 range."""
    print("\n[TEST 11] Score Bounds (0-100)")
    
    test_cases = [
        ("", ""),  # Empty
        ("X", "X"),  # Minimal
        ("123 MG Road, Bangalore, Karnataka 560001", "123 MG Road, Bangalore, Karnataka 560001"),  # Complete
    ]
    
    for raw, cleaned in test_cases:
        result = compute_integrity(raw, cleaned)
        print(f"  Score: {result['score']} (valid: {0 <= result['score'] <= 100})")
        assert 0 <= result['score'] <= 100, f"Score {result['score']} out of bounds"
    
    print("  ✓ PASS")


def test_pincode_extraction():
    """Test pincode extraction in various formats."""
    print("\n[TEST 12] Pincode Extraction")
    
    test_cases = [
        ("Address 560001", "560001"),
        ("PIN: 400001", "400001"),
        ("Mumbai-400001", "400001"),
        ("No pincode here", None),
    ]
    
    for addr, expected_pincode in test_cases:
        result = compute_integrity(addr, addr)
        actual = result['components']['pincode']
        print(f"  '{addr}' -> {actual} (expected: {expected_pincode})")
        assert actual == expected_pincode
    
    print("  ✓ PASS")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("INTEGRITY SCORING TEST SUITE")
    print("="*60)
    
    tests = [
        test_complete_address,
        test_missing_pincode,
        test_missing_city,
        test_vague_tokens,
        test_too_short,
        test_multiple_issues,
        test_perfect_score,
        test_worst_case,
        test_known_vs_unknown_city,
        test_vague_token_examples,
        test_score_bounds,
        test_pincode_extraction,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed > 0:
        sys.exit(1)
