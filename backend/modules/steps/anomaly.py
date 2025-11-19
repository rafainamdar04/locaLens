from core.pipeline import step, Context, Result
from services.anomaly import detect_anomaly


@step("anomaly_detection")
def run(ctx: Context) -> Result:
    metrics = {
        "ml_result": ctx.get("ml_results") or {},
        "here_result": ctx.get("here_results") or {},
        "ml_here_mismatch_km": (ctx.get("geospatial_checks") or {}).get("distance_match"),
        # latency_ms can be added by caller; keep optional
        **({"latency_ms": ctx["latency_ms"]} if "latency_ms" in ctx else {}),
    }
    integ = (ctx.get("integrity") or {}).get("score", 0)
    fused = ctx.get("fused_confidence") or 0.0
    geo = ctx.get("geospatial_checks") or {}

    anomaly, reasons = detect_anomaly(metrics, integ, fused, geo)
    details = {"detected": anomaly, "reasons": reasons, "reason_count": len(reasons)}
    return {
        "anomaly_detected": anomaly,
        "anomaly_reasons": reasons,
        "anomaly_details": details,
    }
