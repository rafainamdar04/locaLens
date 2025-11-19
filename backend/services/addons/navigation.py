"""
Turn-by-Turn Navigation Insights

Modular add-on that analyzes route complexity and navigation challenges for delivery/vehicle access.

compute_navigation(context: dict) -> dict
- Uses: routing (optionally here_results, integrity, geospatial_checks)
- Returns a structured dict with insights, issues, and suggestions
"""
from typing import Dict, Any, Optional

# Scoring weights and thresholds
BASE_SCORE = 85.0  # Start with a good base score

# Route complexity penalties
PENALTY_COMPLEX_TURN = 8.0
PENALTY_AMBIGUOUS_ENTRY = 12.0
PENALTY_ROUNDABOUT = 4.0
PENALTY_NARROW_ROAD = 6.0
PENALTY_TRAFFIC_LIGHTS = 2.0  # Per traffic light
PENALTY_CONSTRUCTION = 10.0
PENALTY_ONE_WAY_STREET = 5.0

# Bonuses for good conditions
BONUS_CLEAR_ENTRY = 5.0
BONUS_SIMPLE_ROUTE = 8.0
BONUS_MAJOR_ROAD_ACCESS = 6.0
BONUS_GOOD_SIGNAGE = 3.0

# Distance-based penalties
PENALTY_PER_KM_COMPLEX = 1.0  # Additional penalty per km for complex routes
MAX_DISTANCE_PENALTY = 15.0


def _calculate_route_complexity(routing: Dict[str, Any]) -> float:
    """Calculate route complexity score based on various factors."""
    complexity = 0.0
    
    # Count complex turns
    turns = routing.get("turns", [])
    complex_turn_count = sum(1 for turn in turns if turn.get("complexity", "simple") in ["complex", "difficult"])
    complexity += complex_turn_count * PENALTY_COMPLEX_TURN
    
    # Roundabouts
    roundabout_count = routing.get("roundabout_count", 0)
    complexity += roundabout_count * PENALTY_ROUNDABOUT
    
    # Traffic lights
    traffic_light_count = routing.get("traffic_light_count", 0)
    complexity += traffic_light_count * PENALTY_TRAFFIC_LIGHTS
    
    # Road conditions
    if routing.get("narrow_road", False):
        complexity += PENALTY_NARROW_ROAD
    if routing.get("construction_zone", False):
        complexity += PENALTY_CONSTRUCTION
    if routing.get("one_way_street", False):
        complexity += PENALTY_ONE_WAY_STREET
    
    # Distance-based complexity
    route_length_km = routing.get("route_length_km", 0)
    if route_length_km > 1:  # Only penalize longer routes
        distance_penalty = min(route_length_km * PENALTY_PER_KM_COMPLEX, MAX_DISTANCE_PENALTY)
        complexity += distance_penalty
    
    return complexity


def compute_navigation(context: Dict[str, Any]) -> Dict[str, Any]:
    routing = context.get("routing") or {}
    
    # Calculate route complexity
    route_complexity_penalty = _calculate_route_complexity(routing)
    
    # Entry/access issues
    ambiguous_entry = routing.get("ambiguous_entry", False)
    clear_entry = routing.get("clear_entry", True)
    major_road_access = routing.get("major_road_access", True)
    good_signage = routing.get("good_signage", False)
    
    # Calculate bonuses
    bonuses = 0.0
    penalties = route_complexity_penalty
    
    issues = []
    suggestions = []
    
    # Process entry/access issues
    if ambiguous_entry:
        penalties += PENALTY_AMBIGUOUS_ENTRY
        issues.append({"tag": "ambiguous_entry", "severity": "critical", "explanation": "Entry point is ambiguous or hard to find."})
        suggestions.append("Share entry photos or detailed directions.")
    elif clear_entry:
        bonuses += BONUS_CLEAR_ENTRY
        suggestions.append("Entry point is clear and easy to find.")
    
    if major_road_access:
        bonuses += BONUS_MAJOR_ROAD_ACCESS
        suggestions.append("Good access from major roads.")
    
    if good_signage:
        bonuses += BONUS_GOOD_SIGNAGE
        suggestions.append("Area has good signage for navigation.")
    
    # Route complexity issues
    turns = routing.get("turns", [])
    complex_turns = any(turn.get("complexity") in ["complex", "difficult"] for turn in turns)
    if complex_turns:
        issues.append({"tag": "complex_turns", "severity": "warning", "explanation": "Route includes complex turns."})
        suggestions.append("Provide clear turn-by-turn instructions for driver.")
    
    roundabout_count = routing.get("roundabout_count", 0)
    if roundabout_count > 0:
        issues.append({"tag": "roundabouts", "severity": "info", "explanation": f"Route includes {roundabout_count} roundabout(s)."})
        suggestions.append("Warn driver about roundabout navigation.")
    
    # Road condition issues
    if routing.get("narrow_road", False):
        issues.append({"tag": "narrow_road", "severity": "warning", "explanation": "Route includes narrow roads."})
        suggestions.append("Ensure vehicle can navigate narrow roads safely.")
    
    if routing.get("construction_zone", False):
        issues.append({"tag": "construction", "severity": "critical", "explanation": "Route passes through construction zones."})
        suggestions.append("Check for road closures or delays.")
    
    if routing.get("one_way_street", False):
        issues.append({"tag": "one_way_street", "severity": "info", "explanation": "Route includes one-way streets."})
        suggestions.append("Ensure proper direction compliance.")
    
    # Traffic considerations
    traffic_light_count = routing.get("traffic_light_count", 0)
    if traffic_light_count > 3:
        issues.append({"tag": "heavy_traffic_lights", "severity": "info", "explanation": f"Route has {traffic_light_count} traffic lights."})
        suggestions.append("Expect potential delays at traffic lights.")
    
    # Calculate final score
    raw_score = BASE_SCORE + bonuses - penalties
    navigation_score = int(max(0, min(100, raw_score)))
    
    return {
        "navigation_score": navigation_score / 100.0,  # Return as 0-1 for consistency
        "breakdown": {
            "route_complexity_penalty": round(route_complexity_penalty, 2),
            "entry_access_penalty": PENALTY_AMBIGUOUS_ENTRY if ambiguous_entry else 0,
            "bonuses": round(bonuses, 2),
            "penalties": round(penalties, 2),
            "base_score": BASE_SCORE,
            "final_score": navigation_score,
        },
        "issues": issues,
        "suggestions": suggestions,
        "route_details": {
            "complex_turns_count": len([t for t in turns if t.get("complexity") in ["complex", "difficult"]]),
            "roundabout_count": roundabout_count,
            "traffic_light_count": traffic_light_count,
            "route_length_km": routing.get("route_length_km", 0),
            "estimated_time_min": routing.get("estimated_time_min", 0),
        }
    }
