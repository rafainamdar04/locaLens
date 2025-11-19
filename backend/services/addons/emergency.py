"""
Emergency Access

Modular add-on that estimates how easily emergency vehicles (ambulance, fire truck, police) can reach the address.

compute_emergency_access(context: dict) -> dict
- Uses: here_results, routing, places (optionally integrity, geospatial_checks)
- Returns a structured dict with score (0–100), breakdown, issues, and suggestions
"""
from typing import Dict, Any, Optional

# Weights (tunable)
W_ACCESS = 0.4
W_ROUTING = 0.3
W_POI = 0.2
W_ROAD_QUALITY = 0.1

# Penalties
PENALTY_RESTRICTED = 30.0
PENALTY_UNREACHABLE = 40.0
PENALTY_POOR_ROAD = 20.0
PENALTY_FAR_EMERGENCY = 20.0

# Bonuses
BONUS_NEAR_EMERGENCY = 10.0
BONUS_CLEAR_ROUTE = 10.0


def compute_emergency_access(context: Dict[str, Any]) -> Dict[str, Any]:
    here = (context.get("here_results") or {}).get("primary_result") or {}
    routing = context.get("routing") or {}
    places = context.get("places") or []
    
    # Base signals
    access_type = here.get("result_type", "")
    road_quality = routing.get("road_quality", "good")
    reachable = routing.get("reachable", True)
    emergency_poi = [p for p in places if p.get("category") in ["hospital", "fire_station", "police_station"]]
    nearest_emergency_m = routing.get("nearest_emergency_m", None)
    
    # Weighted base
    base = (
        W_ACCESS * (100.0 if access_type in ["houseNumber", "street"] else 60.0) +
        W_ROUTING * (100.0 if reachable else 0.0) +
        W_POI * (100.0 if emergency_poi else 40.0) +
        W_ROAD_QUALITY * (100.0 if road_quality == "good" else 60.0 if road_quality == "fair" else 30.0)
    )
    
    # Penalties
    penalties = 0.0
    issues = []
    suggestions = []
    if access_type in ["pedestrian", "privateRoad"]:
        penalties += PENALTY_RESTRICTED
        issues.append({"tag": "restricted_access", "severity": "critical", "explanation": "Address is on a restricted or private road."})
        suggestions.append("Check for alternate public access or permissions for emergency vehicles.")
    if not reachable:
        penalties += PENALTY_UNREACHABLE
        issues.append({"tag": "unreachable", "severity": "critical", "explanation": "No direct route for emergency vehicles."})
        suggestions.append("Try alternate entrance or nearest accessible road.")
    if road_quality == "poor":
        penalties += PENALTY_POOR_ROAD
        issues.append({"tag": "poor_road_quality", "severity": "warning", "explanation": "Road quality is poor (unpaved, narrow, or damaged)."})
        suggestions.append("Emergency access may be delayed or require special vehicle.")
    if nearest_emergency_m is not None and nearest_emergency_m > 1000:
        penalties += PENALTY_FAR_EMERGENCY
        issues.append({"tag": "far_emergency_service", "severity": "warning", "explanation": f"Nearest emergency service is {nearest_emergency_m}m away."})
        suggestions.append(f"Advise residents about emergency service distance: {nearest_emergency_m}m.")
    
    # Bonuses
    bonuses = 0.0
    if emergency_poi:
        bonuses += BONUS_NEAR_EMERGENCY
        suggestions.append("Emergency services are nearby.")
    if reachable:
        bonuses += BONUS_CLEAR_ROUTE
        suggestions.append("Clear route for emergency vehicles.")
    
    # Aggregate
    raw = base + bonuses - penalties
    final = int(max(0, min(100, round(raw))))
    
    return {
        "emergency_access_score": final,
        "breakdown": {
            "access_type": access_type,
            "road_quality": road_quality,
            "reachable": reachable,
            "emergency_poi": bool(emergency_poi),
            "nearest_emergency_m": nearest_emergency_m,
            "base": round(base, 1),
            "bonuses": bonuses,
            "penalties": penalties,
        },
        "issues": issues,
        "suggestions": suggestions,
    }
