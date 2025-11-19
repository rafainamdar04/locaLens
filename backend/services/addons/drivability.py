"""
Drivability Score (Vehicle/Autonomous Access)

Modular add-on that estimates how suitable an address is for vehicle access.

compute_drivability(context: dict) -> dict
- Uses: here_results, routing (optionally integrity, geospatial_checks)
- Returns a structured dict with final score (0–100), breakdown, issues, and suggestions
"""
from typing import Dict, Any, Optional

# Weights (tunable)
W_HERE_CONF = 0.4
W_ACCESS = 0.3
W_ROAD_QUALITY = 0.2
W_ROUTING = 0.1

# Penalties
PENALTY_RESTRICTED = 30.0
PENALTY_POOR_ROAD = 20.0
PENALTY_COMPLEX_TURN = 10.0
PENALTY_UNREACHABLE = 40.0

# Bonuses
BONUS_CLEAR_ACCESS = 10.0
BONUS_GOOD_ROAD = 10.0
BONUS_SIMPLE_ROUTE = 5.0


def compute_drivability(context: Dict[str, Any]) -> Dict[str, Any]:
    here = (context.get("here_results") or {}).get("primary_result") or {}
    routing = context.get("routing") or {}
    
    # Base signals
    here_conf = float((context.get("here_results") or {}).get("confidence", 0.0))
    access_type = here.get("result_type", "")
    road_quality = routing.get("road_quality", "good")
    reachable = routing.get("reachable", True)
    complex_turns = routing.get("complex_turns", False)
    
    # Weighted base
    base = (
        W_HERE_CONF * (here_conf * 100.0) +
        W_ACCESS * (100.0 if access_type in ["houseNumber", "street"] else 60.0) +
        W_ROAD_QUALITY * (100.0 if road_quality == "good" else 60.0 if road_quality == "fair" else 30.0) +
        W_ROUTING * (100.0 if reachable else 0.0)
    )
    
    # Penalties
    penalties = 0.0
    issues = []
    suggestions = []
    if access_type in ["pedestrian", "privateRoad"]:
        penalties += PENALTY_RESTRICTED
        issues.append({"tag": "restricted_access", "severity": "critical", "explanation": "Address is on a restricted or private road."})
        suggestions.append("Check for alternate public access or permissions.")
    if road_quality == "poor":
        penalties += PENALTY_POOR_ROAD
        issues.append({"tag": "poor_road_quality", "severity": "warning", "explanation": "Road quality is poor (unpaved, narrow, or damaged)."})
        suggestions.append("Delivery may require special vehicle or be delayed.")
    if complex_turns:
        penalties += PENALTY_COMPLEX_TURN
        issues.append({"tag": "complex_turns", "severity": "info", "explanation": "Route includes complex turns or ambiguous entries."})
        suggestions.append("Provide clear instructions for driver.")
    if not reachable:
        penalties += PENALTY_UNREACHABLE
        issues.append({"tag": "unreachable", "severity": "critical", "explanation": "No direct route for vehicles."})
        suggestions.append("Try alternate entrance or nearest accessible road.")
    
    # Bonuses
    bonuses = 0.0
    if access_type in ["houseNumber", "street"]:
        bonuses += BONUS_CLEAR_ACCESS
    if road_quality == "good":
        bonuses += BONUS_GOOD_ROAD
    if not complex_turns:
        bonuses += BONUS_SIMPLE_ROUTE
    
    # Aggregate
    raw = base + bonuses - penalties
    final = int(max(0, min(100, round(raw))))
    
    return {
        "drivability_score": final,
        "breakdown": {
            "here_conf": round(here_conf, 3),
            "access_type": access_type,
            "road_quality": road_quality,
            "reachable": reachable,
            "complex_turns": complex_turns,
            "base": round(base, 1),
            "bonuses": bonuses,
            "penalties": penalties,
        },
        "issues": issues,
        "suggestions": suggestions,
    }
