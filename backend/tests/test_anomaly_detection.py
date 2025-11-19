"""
Test suite for anomaly detection service.
Tests all 6 anomaly rules and edge cases.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.anomaly import detect_anomaly, get_anomaly_severity, format_anomaly_report


def test_no_anomalies():
    """Test case with all good metrics - no anomalies expected."""
    print("\n[TEST 1] No Anomalies (All Good Metrics)")
    metrics = {
        "ml_result": {"confidence": 0.85},
        "here_result": {"confidence": 0.75},
        "ml_here_mismatch_km": 1.2,
        "latency_ms": 800
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 85, 0.82, geospatial)
    
    print(f"  is_anomaly: {is_anomaly}")
    print(f"  reasons: {reasons}")
    assert not is_anomaly, "Expected no anomaly"
    assert len(reasons) == 0, "Expected no reasons"
    print("  ✓ PASS")


def test_low_fused_confidence():
    """Test Rule 1: fused_conf < 0.5"""
    print("\n[TEST 2] Low Fused Confidence")
    metrics = {
        "ml_result": {"confidence": 0.85},
        "here_result": {"confidence": 0.75},
        "ml_here_mismatch_km": 1.0,
        "latency_ms": 500
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 85, 0.45, geospatial)
    
    print(f"  is_anomaly: {is_anomaly}")
    print(f"  reasons: {reasons}")
    assert is_anomaly, "Expected anomaly detected"
    assert "low_fused_conf" in reasons, "Expected low_fused_conf reason"
    print("  ✓ PASS")


def test_low_integrity():
    """Test Rule 2: integrity_score < 40"""
    print("\n[TEST 3] Low Integrity Score")
    metrics = {
        "ml_result": {"confidence": 0.85},
        "here_result": {"confidence": 0.75},
        "ml_here_mismatch_km": 1.0,
        "latency_ms": 500
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 35, 0.65, geospatial)
    
    print(f"  is_anomaly: {is_anomaly}")
    print(f"  reasons: {reasons}")
    assert is_anomaly, "Expected anomaly detected"
    assert "low_integrity" in reasons, "Expected low_integrity reason"
    print("  ✓ PASS")


def test_ml_here_mismatch():
    """Test Rule 3: ml_here_mismatch_km > 3"""
    print("\n[TEST 4] ML-HERE Mismatch")
    metrics = {
        "ml_result": {"confidence": 0.85},
        "here_result": {"confidence": 0.75},
        "ml_here_mismatch_km": 5.8,
        "latency_ms": 500
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 85, 0.65, geospatial)
    
    print(f"  is_anomaly: {is_anomaly}")
    print(f"  reasons: {reasons}")
    assert is_anomaly, "Expected anomaly detected"
    assert "ml_here_mismatch" in reasons, "Expected ml_here_mismatch reason"
    print("  ✓ PASS")


def test_low_here_confidence():
    """Test Rule 4: here_confidence < 0.4"""
    print("\n[TEST 5] Low HERE Confidence")
    metrics = {
        "ml_result": {"confidence": 0.85},
        "here_result": {"confidence": 0.35},
        "ml_here_mismatch_km": 1.0,
        "latency_ms": 500
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 85, 0.65, geospatial)
    
    print(f"  is_anomaly: {is_anomaly}")
    print(f"  reasons: {reasons}")
    assert is_anomaly, "Expected anomaly detected"
    assert "low_here_conf" in reasons, "Expected low_here_conf reason"
    print("  ✓ PASS")


def test_pincode_mismatch():
    """Test Rule 5: pincode_mismatch True"""
    print("\n[TEST 6] Pincode Mismatch")
    metrics = {
        "ml_result": {"confidence": 0.85},
        "here_result": {"confidence": 0.75},
        "ml_here_mismatch_km": 1.0,
        "latency_ms": 500
    }
    geospatial = {"pincode_mismatch": True}
    
    is_anomaly, reasons = detect_anomaly(metrics, 85, 0.65, geospatial)
    
    print(f"  is_anomaly: {is_anomaly}")
    print(f"  reasons: {reasons}")
    assert is_anomaly, "Expected anomaly detected"
    assert "pincode_mismatch" in reasons, "Expected pincode_mismatch reason"
    print("  ✓ PASS")


def test_high_latency():
    """Test Rule 6: latency_ms > 1500"""
    print("\n[TEST 7] High Latency")
    metrics = {
        "ml_result": {"confidence": 0.85},
        "here_result": {"confidence": 0.75},
        "ml_here_mismatch_km": 1.0,
        "latency_ms": 2500
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 85, 0.65, geospatial)
    
    print(f"  is_anomaly: {is_anomaly}")
    print(f"  reasons: {reasons}")
    assert is_anomaly, "Expected anomaly detected"
    assert "high_latency" in reasons, "Expected high_latency reason"
    print("  ✓ PASS")


def test_multiple_anomalies():
    """Test case with multiple anomalies triggered simultaneously."""
    print("\n[TEST 8] Multiple Anomalies")
    metrics = {
        "ml_result": {"confidence": 0.85},
        "here_result": {"confidence": 0.25},  # Triggers low_here_conf
        "ml_here_mismatch_km": 8.5,  # Triggers ml_here_mismatch
        "latency_ms": 3000  # Triggers high_latency
    }
    geospatial = {"pincode_mismatch": True}  # Triggers pincode_mismatch
    
    is_anomaly, reasons = detect_anomaly(metrics, 25, 0.35, geospatial)  # Triggers low_integrity, low_fused_conf
    
    print(f"  is_anomaly: {is_anomaly}")
    print(f"  reasons: {reasons}")
    print(f"  reason_count: {len(reasons)}")
    assert is_anomaly, "Expected anomaly detected"
    assert len(reasons) == 6, f"Expected all 6 anomalies, got {len(reasons)}"
    assert "low_fused_conf" in reasons
    assert "low_integrity" in reasons
    assert "ml_here_mismatch" in reasons
    assert "low_here_conf" in reasons
    assert "pincode_mismatch" in reasons
    assert "high_latency" in reasons
    print("  ✓ PASS - All 6 rules triggered")


def test_edge_cases():
    """Test edge cases at threshold boundaries."""
    print("\n[TEST 9] Edge Cases at Thresholds")
    
    # Exactly at threshold - should NOT trigger
    metrics = {
        "ml_result": {"confidence": 0.85},
        "here_result": {"confidence": 0.4},  # Exactly 0.4
        "ml_here_mismatch_km": 3.0,  # Exactly 3.0
        "latency_ms": 1500  # Exactly 1500
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 40, 0.5, geospatial)  # Exactly 40 and 0.5
    
    print(f"  At thresholds - is_anomaly: {is_anomaly}, reasons: {reasons}")
    assert not is_anomaly, "Should not trigger at exact thresholds"
    
    # Just below threshold - should trigger all 5 rules
    # (low_fused_conf, low_integrity, ml_here_mismatch, low_here_conf, high_latency)
    metrics["here_result"]["confidence"] = 0.39
    metrics["ml_here_mismatch_km"] = 3.01
    metrics["latency_ms"] = 1501
    
    is_anomaly, reasons = detect_anomaly(metrics, 39, 0.49, geospatial)
    
    print(f"  Below thresholds - is_anomaly: {is_anomaly}, reasons: {reasons}")
    assert is_anomaly, "Should trigger just below thresholds"
    assert len(reasons) == 5, f"Expected 5 anomalies, got {len(reasons)}"
    print("  ✓ PASS")


def test_severity_classification():
    """Test anomaly severity classification."""
    print("\n[TEST 10] Severity Classification")
    
    # Critical severity
    severity = get_anomaly_severity(["low_integrity", "pincode_mismatch"])
    print(f"  Critical: {severity}")
    assert severity == "critical", "Expected critical severity"
    
    # High severity
    severity = get_anomaly_severity(["low_fused_conf", "low_here_conf"])
    print(f"  High: {severity}")
    assert severity == "high", "Expected high severity"
    
    # Medium severity
    severity = get_anomaly_severity(["ml_here_mismatch"])
    print(f"  Medium: {severity}")
    assert severity == "medium", "Expected medium severity"
    
    # Low severity
    severity = get_anomaly_severity(["high_latency"])
    print(f"  Low: {severity}")
    assert severity == "low", "Expected low severity"
    
    # None
    severity = get_anomaly_severity([])
    print(f"  None: {severity}")
    assert severity == "none", "Expected none severity"
    
    print("  ✓ PASS")


def test_formatted_report():
    """Test formatted anomaly report generation."""
    print("\n[TEST 11] Formatted Report")
    
    metrics = {
        "ml_result": {"confidence": 0.85},
        "here_result": {"confidence": 0.35},
        "ml_here_mismatch_km": 5.2,
        "latency_ms": 1800
    }
    
    is_anomaly, reasons = detect_anomaly(metrics, 30, 0.45, {"pincode_mismatch": False})
    report = format_anomaly_report(is_anomaly, reasons, metrics)
    
    print(f"  is_anomaly: {report['is_anomaly']}")
    print(f"  reason_count: {report['reason_count']}")
    print(f"  reasons: {report['reasons']}")
    print(f"  severity: {report['severity']}")
    print(f"  descriptions: {report['descriptions']}")
    print(f"  values: {report['values']}")
    
    assert report["is_anomaly"] == is_anomaly
    assert report["reason_count"] == len(reasons)
    assert report["severity"] in ["critical", "high", "medium", "low", "none"]
    assert len(report["descriptions"]) == len(reasons)
    print("  ✓ PASS")


def run_all_tests():
    """Run all test cases."""
    print("=" * 60)
    print("ANOMALY DETECTION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_no_anomalies,
        test_low_fused_confidence,
        test_low_integrity,
        test_ml_here_mismatch,
        test_low_here_confidence,
        test_pincode_mismatch,
        test_high_latency,
        test_multiple_anomalies,
        test_edge_cases,
        test_severity_classification,
        test_formatted_report
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
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
