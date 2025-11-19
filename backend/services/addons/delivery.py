from typing import Dict, Any

# Example optional add-on: delivery scoring/ETA heuristic
# Pure function: reads context, returns structured dict

def compute_delivery(context: Dict[str, Any]) -> Dict[str, Any]:
    fused = float(context.get("fused_confidence") or 0.0)
    integrity = (context.get("integrity") or {}).get("score", 0)
    # Simple illustrative score: weighted of integrity (0-100) and fused (0-1)
    score_0_100 = min(max(0.6 * integrity + 40 * fused, 0), 100)
    return {
        "delivery": {
            "score": round(score_0_100, 1),
            "eta_reliability": round(fused, 2),
        }
    }
