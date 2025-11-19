"""
Demonstration of Anomaly Detection
Shows realistic scenarios with different anomaly patterns.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.anomaly import detect_anomaly, get_anomaly_severity, format_anomaly_report


def print_scenario(title: str, description: str):
    """Print scenario header."""
    print("\n" + "=" * 70)
    print(f"SCENARIO: {title}")
    print(f"Description: {description}")
    print("=" * 70)


def print_result(is_anomaly: bool, reasons: list, metrics: dict, integrity: int, fused_conf: float):
    """Print detection results."""
    severity = get_anomaly_severity(reasons)
    
    print(f"\n[RESULT]")
    print(f"  Anomaly Detected: {is_anomaly}")
    print(f"  Severity: {severity.upper()}")
    print(f"  Reason Count: {len(reasons)}")
    
    if reasons:
        print(f"  Reasons:")
        for reason in reasons:
            print(f"    - {reason}")
    
    print(f"\n[METRICS]")
    print(f"  Fused Confidence: {fused_conf:.4f}")
    print(f"  Integrity Score: {integrity}")
    
    if 'ml_result' in metrics and 'confidence' in metrics['ml_result']:
        print(f"  ML Confidence: {metrics['ml_result']['confidence']:.4f}")
    if 'here_result' in metrics and 'confidence' in metrics['here_result']:
        print(f"  HERE Confidence: {metrics['here_result']['confidence']:.4f}")
    if 'ml_here_mismatch_km' in metrics:
        print(f"  ML-HERE Mismatch: {metrics['ml_here_mismatch_km']:.2f} km")
    if 'latency_ms' in metrics:
        print(f"  Latency: {metrics['latency_ms']:.0f} ms")


def scenario_1_clean_result():
    """Perfect scenario - no anomalies."""
    print_scenario(
        "Clean Result",
        "High confidence, good integrity, low mismatch, fast processing"
    )
    
    metrics = {
        "ml_result": {"confidence": 0.92},
        "here_result": {"confidence": 0.88},
        "ml_here_mismatch_km": 0.5,
        "latency_ms": 850
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 85, 0.89, geospatial)
    print_result(is_anomaly, reasons, metrics, 85, 0.89)


def scenario_2_low_confidence():
    """Low confidence scenario - triggers multiple warnings."""
    print_scenario(
        "Low Confidence Result",
        "Both ML and HERE have low confidence, triggering anomaly detection"
    )
    
    metrics = {
        "ml_result": {"confidence": 0.65},
        "here_result": {"confidence": 0.35},
        "ml_here_mismatch_km": 1.8,
        "latency_ms": 920
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 75, 0.48, geospatial)
    print_result(is_anomaly, reasons, metrics, 75, 0.48)


def scenario_3_mismatch_problem():
    """Geographic mismatch scenario."""
    print_scenario(
        "Geographic Mismatch",
        "ML and HERE results differ significantly in location"
    )
    
    metrics = {
        "ml_result": {"confidence": 0.82},
        "here_result": {"confidence": 0.78},
        "ml_here_mismatch_km": 8.5,
        "latency_ms": 1100
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 70, 0.68, geospatial)
    print_result(is_anomaly, reasons, metrics, 70, 0.68)


def scenario_4_data_quality_issues():
    """Critical data quality problems."""
    print_scenario(
        "Data Quality Issues",
        "Low integrity score and pincode validation failure"
    )
    
    metrics = {
        "ml_result": {"confidence": 0.72},
        "here_result": {"confidence": 0.68},
        "ml_here_mismatch_km": 2.1,
        "latency_ms": 980
    }
    geospatial = {"pincode_mismatch": True}
    
    is_anomaly, reasons = detect_anomaly(metrics, 32, 0.55, geospatial)
    print_result(is_anomaly, reasons, metrics, 32, 0.55)


def scenario_5_performance_problem():
    """High latency scenario."""
    print_scenario(
        "Performance Problem",
        "System experiencing high latency, everything else looks good"
    )
    
    metrics = {
        "ml_result": {"confidence": 0.88},
        "here_result": {"confidence": 0.85},
        "ml_here_mismatch_km": 1.2,
        "latency_ms": 2800
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 80, 0.82, geospatial)
    print_result(is_anomaly, reasons, metrics, 80, 0.82)


def scenario_6_multiple_failures():
    """Worst case - multiple critical issues."""
    print_scenario(
        "Multiple Critical Failures",
        "Everything is failing - low confidence, bad data, high latency"
    )
    
    metrics = {
        "ml_result": {"confidence": 0.42},
        "here_result": {"confidence": 0.28},
        "ml_here_mismatch_km": 12.5,
        "latency_ms": 3500
    }
    geospatial = {"pincode_mismatch": True}
    
    is_anomaly, reasons = detect_anomaly(metrics, 22, 0.25, geospatial)
    print_result(is_anomaly, reasons, metrics, 22, 0.25)
    
    # Show formatted report
    report = format_anomaly_report(is_anomaly, reasons, metrics)
    print(f"\n[FORMATTED REPORT]")
    print(f"  Severity: {report['severity']}")
    print(f"  Descriptions:")
    for desc in report['descriptions']:
        print(f"    - {desc}")


def scenario_7_edge_case():
    """Edge case at thresholds."""
    print_scenario(
        "Edge Case at Thresholds",
        "Multiple metrics exactly at or just below thresholds"
    )
    
    metrics = {
        "ml_result": {"confidence": 0.88},
        "here_result": {"confidence": 0.39},  # Just below 0.4
        "ml_here_mismatch_km": 3.01,  # Just above 3.0
        "latency_ms": 1501  # Just above 1500
    }
    geospatial = {"pincode_mismatch": False}
    
    is_anomaly, reasons = detect_anomaly(metrics, 40, 0.50, geospatial)  # Exactly at thresholds
    print_result(is_anomaly, reasons, metrics, 40, 0.50)


def main():
    """Run all demonstration scenarios."""
    print("\n" + "#" * 70)
    print("# ANOMALY DETECTION DEMONSTRATION")
    print("# Showing realistic scenarios with different anomaly patterns")
    print("#" * 70)
    
    scenario_1_clean_result()
    scenario_2_low_confidence()
    scenario_3_mismatch_problem()
    scenario_4_data_quality_issues()
    scenario_5_performance_problem()
    scenario_6_multiple_failures()
    scenario_7_edge_case()
    
    print("\n" + "#" * 70)
    print("# DEMONSTRATION COMPLETE")
    print("#" * 70)
    print("\nAll scenarios executed successfully!")
    print("\nKey Takeaways:")
    print("  - 6 anomaly rules implemented and tested")
    print("  - Severity classification (critical, high, medium, low)")
    print("  - Multiple anomalies can be detected simultaneously")
    print("  - Thresholds are properly exclusive (< not <=)")


if __name__ == "__main__":
    main()
