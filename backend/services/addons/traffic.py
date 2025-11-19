"""
Traffic & Road Condition Alerts

Modular add-on that analyzes real-time and historical traffic, congestion, and road condition alerts for delivery/vehicle access.

compute_traffic(context: dict) -> dict
- Uses: traffic (optionally routing, here_results)
- Returns a structured dict with alerts, issues, and suggestions
"""
from typing import Dict, Any, Optional

# Penalties
PENALTY_CONGESTION = 15.0
PENALTY_CLOSURE = 30.0
PENALTY_ACCIDENT = 20.0

# Bonuses
BONUS_CLEAR_ROAD = 10.0
BONUS_LOW_TRAFFIC = 5.0


def compute_traffic(context: Dict[str, Any]) -> Dict[str, Any]:
    traffic = context.get("traffic") or {}
    
    # Signals
    congestion = traffic.get("congestion", False)
    closure = traffic.get("closure", False)
    accident = traffic.get("accident", False)
    low_traffic = traffic.get("low_traffic", True)
    clear_road = traffic.get("clear_road", True)
    
    # Penalties/Bonuses
    penalties = 0.0
    bonuses = 0.0
    issues = []
    suggestions = []
    if congestion:
        penalties += PENALTY_CONGESTION
        issues.append({"tag": "congestion", "severity": "warning", "explanation": "Heavy traffic congestion detected."})
        suggestions.append("Expect possible delays or rerouting.")
    if closure:
        penalties += PENALTY_CLOSURE
        issues.append({"tag": "closure", "severity": "critical", "explanation": "Road closure detected on route."})
        suggestions.append("Find alternate route or reschedule delivery.")
    if accident:
        penalties += PENALTY_ACCIDENT
        issues.append({"tag": "accident", "severity": "warning", "explanation": "Accident reported near address."})
        suggestions.append("Expect possible delays or rerouting.")
    if clear_road:
        bonuses += BONUS_CLEAR_ROAD
        suggestions.append("Roads are clear for delivery.")
    if low_traffic:
        bonuses += BONUS_LOW_TRAFFIC
        suggestions.append("Low traffic expected, delivery should be smooth.")
    
    # Aggregate
    alert_score = int(max(0, min(100, 80 + bonuses - penalties)))
    
    return {
        "traffic_score": alert_score,
        "breakdown": {
            "congestion": congestion,
            "closure": closure,
            "accident": accident,
            "low_traffic": low_traffic,
            "clear_road": clear_road,
            "bonuses": bonuses,
            "penalties": penalties,
        },
        "issues": issues,
        "suggestions": suggestions,
    }
