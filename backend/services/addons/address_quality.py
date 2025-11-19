"""
Address Quality add-on for LocaLens

A pure, modular scoring module that synthesizes core pipeline signals
into a single 0–100 score suitable for cross-industry use.

compute_address_quality(context: dict) -> dict
- Reads from the shared, read-only context built by main.py
- Uses: integrity, fused_confidence, geospatial_checks, HERE field_scores, metrics, anomaly flags
- Returns a structured dict under the key "address_quality" with a breakdown and final score
- No side effects; does not mutate the input context

Scoring overview (0–100):
- Integrity component (0–100)           weight 0.35
- Fused confidence (0–1 → 0–100)        weight 0.35
- HERE field-scores (avg → 0–100)       weight 0.15
- Penalties (subtract):
  * ML↔HERE mismatch (km): up to -20 (2 pts per km up to 10km)
  * City boundary violation: -15
  * Anomaly detected: -10

Weights and thresholds are easy to tune and can be made configurable later.
"""
from typing import Dict, Any, Optional


# Tunable weights (kept simple and local for now)
W_INTEGRITY = 0.35
W_CONFIDENCE = 0.35
W_FIELDS = 0.15
# Remaining weight (0.15) is implicitly reserved for penalties

PENALTY_PER_KM = 2.0    # points per km (capped)
PENALTY_MAX_KM = 10.0    # km cap
PENALTY_BOUNDARY = 15.0  # points
PENALTY_ANOMALY = 10.0   # points


def _to_float(x: Optional[float], default: float = 0.0) -> float:
    try:
        return float(x) if x is not None else default
    except Exception:
        return default


def _avg_field_score(field_scores: Dict[str, Any]) -> float:
    if not isinstance(field_scores, dict) or not field_scores:
        return 0.0
    vals = []
    for v in field_scores.values():
        try:
            vals.append(float(v))
        except Exception:
            continue
    if not vals:
        return 0.0
    # HERE field scores typically 0–1; clamp and average then scale to 0–100
    avg01 = sum(max(0.0, min(1.0, v)) for v in vals) / len(vals)
    return avg01 * 100.0


def compute_address_quality(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute a 0–100 Address Quality score using core signals.

    Expected context keys:
    - integrity: { score: int 0–100 }
    - fused_confidence: float 0–1
    - geospatial_checks: { distance_match: float|None, details: { city_violation?: bool } }
    - here_results.primary_result.field_scores: dict of per-field 0–1 scores (optional)
    - anomaly_detected: bool
    - metrics: { ml_similarity, here_confidence, ... } (optional; not required)

    Returns:
    {
      "address_quality": {
        "score": float(0–100),
        "components": { ... raw inputs used ... },
        "contributions": { integrity, confidence, field_scores, penalties: { mismatch, boundary, anomaly } },
        "weights": { integrity, confidence, field_scores },
        "notes": [ ... ]
      }
    }
    """
    integ_score = float((context.get("integrity") or {}).get("score", 0))  # 0–100
    fused = _to_float(context.get("fused_confidence"), 0.0)                  # 0–1

    geo = context.get("geospatial_checks") or {}
    mismatch_km = _to_float(geo.get("distance_match"), None)
    details = geo.get("details") or {}
    city_violation = bool(details.get("city_violation") or (not geo.get("boundary_check", True)))

    here_primary = (context.get("here_results") or {}).get("primary_result") or {}
    field_scores = here_primary.get("field_scores") or {}
    fields_component = _avg_field_score(field_scores)  # 0–100

    anomaly = bool(context.get("anomaly_detected", False))

    # Positive contributions
    contrib_integrity = W_INTEGRITY * integ_score
    contrib_confidence = W_CONFIDENCE * (fused * 100.0)
    contrib_fields = W_FIELDS * fields_component

    # Penalties
    pen_mismatch = 0.0
    if mismatch_km is not None:
        pen_mismatch = min(PENALTY_MAX_KM, max(0.0, mismatch_km)) * PENALTY_PER_KM

    pen_boundary = PENALTY_BOUNDARY if city_violation else 0.0
    pen_anomaly = PENALTY_ANOMALY if anomaly else 0.0

    # Final score
    raw_score = contrib_integrity + contrib_confidence + contrib_fields
    final_score = raw_score - (pen_mismatch + pen_boundary + pen_anomaly)
    final_score = max(0.0, min(100.0, final_score))

    result = {
        "address_quality": {
            "score": round(final_score, 1),
            "weights": {
                "integrity": W_INTEGRITY,
                "confidence": W_CONFIDENCE,
                "field_scores": W_FIELDS,
            },
            "components": {
                "integrity": integ_score,
                "fused_confidence": round(fused, 4),
                "fields_avg": round(fields_component, 1),
                "mismatch_km": mismatch_km,
                "boundary_violation": city_violation,
                "anomaly_detected": anomaly,
            },
            "contributions": {
                "integrity": round(contrib_integrity, 2),
                "confidence": round(contrib_confidence, 2),
                "field_scores": round(contrib_fields, 2),
                "penalties": {
                    "mismatch": round(pen_mismatch, 2),
                    "boundary": round(pen_boundary, 2),
                    "anomaly": round(pen_anomaly, 2),
                },
            },
            "notes": [
                "Confidence normalized 0–1; converted to 0–100 for weighting.",
                "Mismatch penalty capped at 10km × 2 points/km = 20.",
                "Weights are tunable and can be externalized later.",
            ],
        }
    }
    return result
