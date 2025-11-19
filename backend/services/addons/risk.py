from typing import Dict, Any

# Example optional add-on: property risk proxy

def compute_risk(context: Dict[str, Any]) -> Dict[str, Any]:
    # Penalize large ML-HERE mismatch and low integrity
    mismatch = (context.get("geospatial_checks") or {}).get("distance_match") or 0.0
    integrity = (context.get("integrity") or {}).get("score", 0)
    risk = min(max(50 + (mismatch * 5) - (integrity * 0.3), 0), 100)
    return {
        "risk": {
            "score": round(risk, 1),
            "mismatch_km": mismatch,
        }
    }
