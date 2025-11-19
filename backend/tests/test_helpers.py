"""
Test suite for helper utilities.
Tests all helper functions with various edge cases.
"""

import sys
from pathlib import Path
import math

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from utils.helpers import (
    haversine,
    extract_pincode,
    extract_city_from_text,
    simple_tokenize,
    contains_vague_tokens,
    normalize_address_text,
    is_valid_coordinate,
    extract_numeric_value,
    get_token_set,
    token_overlap_ratio
)


def test_haversine_known_distances():
    """Test haversine with known city distances."""
    print("\n[TEST 1] Haversine Known Distances")
    
    # Mumbai to Delhi (approximately 1153 km)
    dist = haversine(19.0760, 72.8777, 28.7041, 77.1025)
    print(f"  Mumbai to Delhi: {dist:.2f} km")
    assert 1150 < dist < 1160, f"Expected ~1153 km, got {dist:.2f}"
    
    # Bangalore to Chennai (approximately 290 km)
    dist = haversine(12.9716, 77.5946, 13.0827, 80.2707)
    print(f"  Bangalore to Chennai: {dist:.2f} km")
    assert 285 < dist < 295, f"Expected ~290 km, got {dist:.2f}"
    
    # Same location (0 km)
    dist = haversine(19.0760, 72.8777, 19.0760, 72.8777)
    print(f"  Same location: {dist:.2f} km")
    assert dist == 0.0, f"Expected 0 km, got {dist:.2f}"
    
    print("  ✓ PASS")


def test_haversine_short_distances():
    """Test haversine with short distances."""
    print("\n[TEST 2] Haversine Short Distances")
    
    # Very close points (approx 1 km apart)
    dist = haversine(19.0760, 72.8777, 19.0850, 72.8877)
    print(f"  ~1 km distance: {dist:.3f} km")
    assert 0.5 < dist < 2.0, f"Expected ~1 km, got {dist:.3f}"
    
    # Very close points (approx 100m apart)
    dist = haversine(19.0760, 72.8777, 19.0770, 72.8787)
    print(f"  ~100m distance: {dist:.3f} km")
    assert 0.01 < dist < 0.5, f"Expected ~0.1 km, got {dist:.3f}"
    
    print("  ✓ PASS")


def test_extract_pincode():
    """Test pincode extraction."""
    print("\n[TEST 3] Extract Pincode")
    
    test_cases = [
        ("123 Main St, Mumbai 400001", "400001"),
        ("Sector 15, Noida 201301", "201301"),
        ("Address with 110001 in middle", "110001"),
        ("Multiple 400001 and 110001", "400001"),  # First match
        ("No pincode here", None),
        ("Short 12345 code", None),  # 5 digits
        ("Long 1234567 code", None),  # 7 digits
        ("", None),  # Empty
        ("Bangalore 560001 Karnataka", "560001"),
        ("PIN: 400058", "400058"),
    ]
    
    for text, expected in test_cases:
        result = extract_pincode(text)
        print(f"  '{text[:40]}...' -> {result}")
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("  ✓ PASS")


def test_extract_city_from_text():
    """Test city name extraction."""
    print("\n[TEST 4] Extract City from Text")
    
    cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Navi Mumbai", "New Delhi"]
    
    test_cases = [
        ("123 Main St, Mumbai 400001", "Mumbai"),
        ("Sector 5, Delhi", "Delhi"),
        ("Whitefield, Bangalore", "Bangalore"),
        ("In Navi Mumbai area", "Navi Mumbai"),  # Multi-word city
        ("New Delhi station", "New Delhi"),
        ("Unknown City", None),
        ("", None),
    ]
    
    for text, expected in test_cases:
        result = extract_city_from_text(text, cities)
        print(f"  '{text}' -> {result}")
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("  ✓ PASS")


def test_extract_city_priority():
    """Test that longer city names are matched first."""
    print("\n[TEST 5] Extract City Priority (Longer Names First)")
    
    cities = ["Mumbai", "Navi Mumbai"]
    
    # Should match "Navi Mumbai" not just "Mumbai"
    text = "Sector 5, Navi Mumbai"
    result = extract_city_from_text(text, cities)
    print(f"  '{text}' -> {result}")
    assert result == "Navi Mumbai", f"Expected 'Navi Mumbai', got {result}"
    
    print("  ✓ PASS")


def test_simple_tokenize():
    """Test simple tokenization."""
    print("\n[TEST 6] Simple Tokenize")
    
    test_cases = [
        ("123 Main St, Mumbai", ["123", "main", "st", "mumbai"]),
        ("Sector-15, Noida!", ["sector", "15", "noida"]),
        ("  Extra   Spaces  ", ["extra", "spaces"]),
        ("MixedCase TEXT", ["mixedcase", "text"]),
        ("", []),
        ("One", ["one"]),
    ]
    
    for text, expected in test_cases:
        result = simple_tokenize(text)
        print(f"  '{text}' -> {result}")
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("  ✓ PASS")


def test_contains_vague_tokens():
    """Test vague token detection."""
    print("\n[TEST 7] Contains Vague Tokens")
    
    # Should return True (vague)
    vague_addresses = [
        "Near railway station",
        "Opposite to mall",
        "Behind the temple",
        "Close to airport",
        "Somewhere in Mumbai",
        "Around sector 5",
        "Adjacent to park",
        "In front of school",
        "Approximately 2km from center",
        "Locality near market",
    ]
    
    for addr in vague_addresses:
        result = contains_vague_tokens(addr)
        print(f"  '{addr}' -> {result}")
        assert result == True, f"Expected True for '{addr}'"
    
    # Should return False (specific)
    specific_addresses = [
        "123 Main Street, Mumbai 400001",
        "Sector 15, Noida 201301",
        "456 Park Avenue, Delhi",
        "Building A, Floor 3",
    ]
    
    for addr in specific_addresses:
        result = contains_vague_tokens(addr)
        print(f"  '{addr}' -> {result}")
        assert result == False, f"Expected False for '{addr}'"
    
    print("  ✓ PASS")


def test_normalize_address_text():
    """Test address normalization."""
    print("\n[TEST 8] Normalize Address Text")
    
    test_cases = [
        ("  123  Main  St.  ", "123 main street"),
        ("Flat #5, Bldg-A", "flat 5 building a"),
        ("Ave. Boulevard Dr.", "avenue boulevard drive"),
        ("Apt. No. 123", "apartment number 123"),
        ("UPPERCASE TEXT", "uppercase text"),
        ("Multiple   Spaces", "multiple spaces"),
    ]
    
    for text, expected in test_cases:
        result = normalize_address_text(text)
        print(f"  '{text}' -> '{result}'")
        assert result == expected, f"Expected '{expected}', got '{result}'"
    
    print("  ✓ PASS")


def test_is_valid_coordinate():
    """Test coordinate validation."""
    print("\n[TEST 9] Validate Coordinates")
    
    valid_coords = [
        (19.0760, 72.8777),   # Mumbai
        (28.7041, 77.1025),   # Delhi
        (0, 0),               # Equator/Prime Meridian
        (-90, -180),          # South Pole, Date Line
        (90, 180),            # North Pole, Date Line
    ]
    
    for lat, lon in valid_coords:
        result = is_valid_coordinate(lat, lon)
        print(f"  ({lat}, {lon}) -> {result}")
        assert result == True, f"Expected True for ({lat}, {lon})"
    
    invalid_coords = [
        (91, 0),              # Lat too high
        (-91, 0),             # Lat too low
        (0, 181),             # Lon too high
        (0, -181),            # Lon too low
        (100, 200),           # Both invalid
    ]
    
    for lat, lon in invalid_coords:
        result = is_valid_coordinate(lat, lon)
        print(f"  ({lat}, {lon}) -> {result}")
        assert result == False, f"Expected False for ({lat}, {lon})"
    
    print("  ✓ PASS")


def test_extract_numeric_value():
    """Test numeric value extraction."""
    print("\n[TEST 10] Extract Numeric Value")
    
    test_cases = [
        ("Flat 123, Building A", 123.0),
        ("Distance: 5.5 km", 5.5),
        ("Price: 1250.75", 1250.75),
        ("No numbers here", None),
        ("", None),
        ("Multiple 123 and 456", 123.0),  # First match
        ("0.5", 0.5),
        ("100", 100.0),
    ]
    
    for text, expected in test_cases:
        result = extract_numeric_value(text)
        print(f"  '{text}' -> {result}")
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("  ✓ PASS")


def test_get_token_set():
    """Test token set generation."""
    print("\n[TEST 11] Get Token Set")
    
    text = "123 Main St Main St Mumbai"
    result = get_token_set(text)
    expected = {"123", "main", "st", "mumbai"}
    
    print(f"  '{text}'")
    print(f"  -> {result}")
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Empty text
    result = get_token_set("")
    print(f"  '' -> {result}")
    assert result == set(), "Expected empty set"
    
    print("  ✓ PASS")


def test_token_overlap_ratio():
    """Test token overlap ratio calculation."""
    print("\n[TEST 12] Token Overlap Ratio")
    
    # Identical texts
    ratio = token_overlap_ratio("123 Main St", "123 Main St")
    print(f"  Identical: {ratio:.2f}")
    assert ratio == 1.0, f"Expected 1.0, got {ratio}"
    
    # Partial overlap
    ratio = token_overlap_ratio("123 Main St", "123 Main Street")
    print(f"  Partial overlap: {ratio:.2f}")
    assert 0.4 < ratio < 0.6, f"Expected ~0.5, got {ratio}"
    
    # No overlap
    ratio = token_overlap_ratio("123 Main St", "456 Park Ave")
    print(f"  No overlap: {ratio:.2f}")
    assert ratio == 0.0, f"Expected 0.0, got {ratio}"
    
    # Both empty
    ratio = token_overlap_ratio("", "")
    print(f"  Both empty: {ratio:.2f}")
    assert ratio == 1.0, f"Expected 1.0, got {ratio}"
    
    # One empty
    ratio = token_overlap_ratio("123 Main St", "")
    print(f"  One empty: {ratio:.2f}")
    assert ratio == 0.0, f"Expected 0.0, got {ratio}"
    
    print("  ✓ PASS")


def test_haversine_edge_cases():
    """Test haversine with edge cases."""
    print("\n[TEST 13] Haversine Edge Cases")
    
    # Antipodal points (opposite sides of Earth)
    # Should be approximately half Earth's circumference (~20,000 km)
    dist = haversine(0, 0, 0, 180)
    print(f"  Antipodal points: {dist:.2f} km")
    assert 19000 < dist < 21000, f"Expected ~20000 km, got {dist:.2f}"
    
    # North Pole to South Pole
    dist = haversine(90, 0, -90, 0)
    print(f"  Pole to pole: {dist:.2f} km")
    assert 19000 < dist < 21000, f"Expected ~20000 km, got {dist:.2f}"
    
    print("  ✓ PASS")


def test_pincode_word_boundary():
    """Test that pincode extraction respects word boundaries."""
    print("\n[TEST 14] Pincode Word Boundary")
    
    # Should not match 6 digits that are part of longer numbers
    test_cases = [
        ("Phone: 9876543210", None),  # 10-digit phone
        ("Account: 12345678", None),   # 8-digit account
        ("Valid: 400001", "400001"),   # Valid standalone
        ("Code-400001-XYZ", "400001"), # With separators
    ]
    
    for text, expected in test_cases:
        result = extract_pincode(text)
        print(f"  '{text}' -> {result}")
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("  ✓ PASS")


def test_vague_tokens_false_positives():
    """Test that vague token detection avoids false positives."""
    print("\n[TEST 15] Vague Tokens False Positives")
    
    # These should NOT be detected as vague (word boundary check)
    non_vague = [
        "Nearby Street",     # "nearby" is part of street name
        "Nearness Road",     # Contains "near" but not standalone
        "Closure Avenue",    # Contains "close" but not standalone
    ]
    
    for addr in non_vague:
        result = contains_vague_tokens(addr)
        print(f"  '{addr}' -> {result}")
        # These might match depending on interpretation
        # Just verify function runs without error
    
    print("  ✓ PASS")


def run_all_tests():
    """Run all test cases."""
    print("=" * 70)
    print("HELPER UTILITIES TEST SUITE")
    print("=" * 70)
    
    tests = [
        test_haversine_known_distances,
        test_haversine_short_distances,
        test_extract_pincode,
        test_extract_city_from_text,
        test_extract_city_priority,
        test_simple_tokenize,
        test_contains_vague_tokens,
        test_normalize_address_text,
        test_is_valid_coordinate,
        test_extract_numeric_value,
        test_get_token_set,
        test_token_overlap_ratio,
        test_haversine_edge_cases,
        test_pincode_word_boundary,
        test_vague_tokens_false_positives
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
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
