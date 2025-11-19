"""
Anomaly Detection Service

Detects anomalies in geocoding results based on multiple quality metrics.
Returns whether an anomaly is detected and the list of specific reasons.
"""

from typing import Tuple, List


def detect_anomaly(
    metrics: dict,
    integrity_score: int,
    fused_conf: float,
    geospatial_checks: dict
) -> Tuple[bool, List[str]]:
    """
    Detect anomalies in geocoding results based on multiple quality metrics.
    
    Args:
        metrics: Dictionary containing ML and HERE results with confidence scores
                 Expected keys: ml_result, here_result, ml_here_mismatch_km, latency_ms
        integrity_score: Data integrity score (0-100)
        fused_conf: Fused confidence score (0.0-1.0)
        geospatial_checks: Dictionary with validation results
                          Expected keys: pincode_mismatch, within_city_bounds, distance_km
    
    Returns:
        Tuple of (is_anomaly: bool, reasons: List[str])
        - is_anomaly: True if any anomaly detected
        - reasons: List of anomaly reason codes
    
    Anomaly Rules:
        - fused_conf < 0.5 -> "low_fused_conf"
        - integrity_score < 40 -> "low_integrity"
        - ml_here_mismatch_km > 3 -> "ml_here_mismatch"
        - here_confidence < 0.4 -> "low_here_conf"
        - pincode_mismatch True -> "pincode_mismatch"
        - latency_ms > 1500 -> "high_latency"
    
    Example:
        >>> metrics = {
        ...     "ml_result": {"confidence": 0.85},
        ...     "here_result": {"confidence": 0.35},
        ...     "ml_here_mismatch_km": 5.2,
        ...     "latency_ms": 1200
        ... }
        >>> geospatial = {"pincode_mismatch": False}
        >>> is_anomaly, reasons = detect_anomaly(metrics, 75, 0.45, geospatial)
        >>> print(is_anomaly, reasons)
        True ['low_fused_conf', 'ml_here_mismatch', 'low_here_conf']
    """
    reasons = []
    
    # Rule 1: Low fused confidence
    if fused_conf < 0.5:
        reasons.append("low_fused_conf")
    
    # Rule 2: Low integrity score
    if integrity_score < 40:
        reasons.append("low_integrity")
    
    # Rule 3: ML-HERE mismatch distance
    ml_here_mismatch_km = metrics.get("ml_here_mismatch_km", 0)
    if ml_here_mismatch_km is not None and ml_here_mismatch_km > 3:
        reasons.append("ml_here_mismatch")
    
    # Rule 4: Low HERE confidence
    here_result = metrics.get("here_result", {})
    here_confidence = here_result.get("confidence", 1.0)
    if here_confidence < 0.4:
        reasons.append("low_here_conf")
    
    # Rule 5: Pincode mismatch
    pincode_mismatch = geospatial_checks.get("pincode_mismatch", False)
    if pincode_mismatch:
        reasons.append("pincode_mismatch")
    
    # Rule 6: High latency
    latency_ms = metrics.get("latency_ms", 0)
    if latency_ms > 1500:
        reasons.append("high_latency")
    
    # Determine if any anomaly detected
    is_anomaly = len(reasons) > 0
    
    return is_anomaly, reasons


def get_anomaly_severity(reasons: List[str]) -> str:
    """
    Classify anomaly severity based on detected reasons.
    
    Args:
        reasons: List of anomaly reason codes
    
    Returns:
        Severity level: "critical", "high", "medium", "low", or "none"
    """
    if not reasons:
        return "none"
    
    # Critical anomalies (data quality issues)
    critical = {"low_integrity", "pincode_mismatch"}
    if any(r in critical for r in reasons):
        return "critical"
    
    # High severity (low confidence)
    high = {"low_fused_conf", "low_here_conf"}
    if any(r in high for r in reasons):
        return "high"
    
    # Medium severity (mismatch)
    medium = {"ml_here_mismatch"}
    if any(r in medium for r in reasons):
        return "medium"
    
    # Low severity (performance)
    return "low"


def format_anomaly_report(
    is_anomaly: bool,
    reasons: List[str],
    metrics: dict = None
) -> dict:
    """
    Format anomaly detection results into a structured report.
    
    Args:
        is_anomaly: Whether anomaly was detected
        reasons: List of anomaly reason codes
        metrics: Optional metrics dictionary for additional context
    
    Returns:
        Dictionary with formatted anomaly report
    """
    report = {
        "is_anomaly": is_anomaly,
        "reason_count": len(reasons),
        "reasons": reasons,
        "severity": get_anomaly_severity(reasons)
    }
    
    # Add human-readable descriptions
    descriptions = {
        "low_fused_conf": "Fused confidence score below 0.5",
        "low_integrity": "Integrity score below 40",
        "ml_here_mismatch": "ML and HERE results differ by >3km",
        "low_here_conf": "HERE confidence below 0.4",
        "pincode_mismatch": "Pincode validation failed",
        "high_latency": "Processing latency exceeded 1500ms"
    }
    
    report["descriptions"] = [descriptions.get(r, r) for r in reasons]
    
    # Add specific values if metrics provided
    if metrics:
        report["values"] = {}
        if "ml_here_mismatch_km" in metrics:
            report["values"]["mismatch_km"] = metrics["ml_here_mismatch_km"]
        if "latency_ms" in metrics:
            report["values"]["latency_ms"] = metrics["latency_ms"]
        if "here_result" in metrics:
            report["values"]["here_confidence"] = metrics["here_result"].get("confidence")
    
    return report


# New architecture-compatible entry
def compute_anomaly(context: dict) -> dict:
    metrics = {
        "ml_result": context.get("ml_results") or {},
        "here_result": context.get("here_results") or {},
        "ml_here_mismatch_km": (context.get("geospatial_checks") or {}).get("distance_match"),
        **({"latency_ms": context["latency_ms"]} if "latency_ms" in context else {}),
    }
    is_anom, reasons = detect_anomaly(
        metrics=metrics,
        integrity_score=(context.get("integrity") or {}).get("score", 0),
        fused_conf=context.get("fused_confidence", 0.0),
        geospatial_checks=context.get("geospatial_checks") or {},
    )
    return {
        "anomaly_detected": is_anom,
        "anomaly_reasons": reasons,
        "anomaly_details": format_anomaly_report(is_anom, reasons, metrics),
    }
