"""
Parking & Drop-off Feasibility

Modular add-on that estimates if safe, legal parking or drop-off is available near the address.

compute_parking(context: dict) -> dict
- Uses: here_results, routing, places (optionally integrity, geospatial_checks)
- Returns a structured dict with final score (0–100), breakdown, issues, and suggestions
"""
from typing import Dict, Any, Optional

# Weights (tunable)
W_PARKING_POI = 0.5
W_ROUTING = 0.3
W_ACCESS = 0.2

# Penalties
PENALTY_NO_PARKING = 40.0
PENALTY_FAR_PARKING = 20.0
PENALTY_UNREACHABLE = 30.0

# Bonuses
BONUS_NEAR_PARKING = 10.0
BONUS_DROP_ZONE = 10.0


def compute_parking(context: Dict[str, Any]) -> Dict[str, Any]:
    here = (context.get("here_results") or {}).get("primary_result") or {}
    routing = context.get("routing") or {}
    places = context.get("places") or []
    
    # Base signals
    parking_poi = [p for p in places if p.get("category") == "parking"]
    nearest_parking_m = routing.get("nearest_parking_m", None)
    drop_zone = routing.get("drop_zone", False)
    reachable = routing.get("reachable", True)
    access_type = here.get("result_type", "")
    
    # Weighted base
    base = (
        W_PARKING_POI * (100.0 if parking_poi else 40.0) +
        W_ROUTING * (100.0 if nearest_parking_m is not None and nearest_parking_m <= 100 else 60.0 if nearest_parking_m and nearest_parking_m <= 500 else 30.0) +
        W_ACCESS * (100.0 if access_type in ["houseNumber", "street"] else 60.0)
    )
    
    # Penalties
    penalties = 0.0
    issues = []
    suggestions = []
    if not parking_poi:
        penalties += PENALTY_NO_PARKING
        issues.append({"tag": "no_parking_poi", "severity": "critical", "explanation": "No parking or drop-off POI found nearby."})
        suggestions.append("Advise recipient to expect delivery at curb or nearest accessible point.")
    if nearest_parking_m is not None and nearest_parking_m > 100:
        penalties += PENALTY_FAR_PARKING
        issues.append({"tag": "far_parking", "severity": "warning", "explanation": f"Nearest parking is {nearest_parking_m}m away."})
        suggestions.append(f"Suggest delivery at parking {nearest_parking_m}m away.")
    if not reachable:
        penalties += PENALTY_UNREACHABLE
        issues.append({"tag": "unreachable", "severity": "critical", "explanation": "No direct route for vehicles to parking/drop-off."})
        suggestions.append("Try alternate entrance or nearest accessible road.")
    
    # Bonuses
    bonuses = 0.0
    if parking_poi:
        bonuses += BONUS_NEAR_PARKING
    if drop_zone:
        bonuses += BONUS_DROP_ZONE
        suggestions.append("Dedicated drop-off zone available.")
    
    # Aggregate
    raw = base + bonuses - penalties
    final = int(max(0, min(100, round(raw))))
    
    return {
        "parking_score": final,
        "breakdown": {
            "parking_poi": bool(parking_poi),
            "nearest_parking_m": nearest_parking_m,
            "drop_zone": drop_zone,
            "reachable": reachable,
            "access_type": access_type,
            "base": round(base, 1),
            "bonuses": bonuses,
            "penalties": penalties,
        },
        "issues": issues,
        "suggestions": suggestions,
    }
