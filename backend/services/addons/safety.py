"""
Safety Assessment Add-on

Modular add-on that evaluates safety risks for delivery personnel and customers.

compute_safety(context: dict) -> dict
- Uses: geospatial_checks, city_intelligence, routing, here_results
- Returns a structured dict with safety score, breakdown, issues, and recommendations
"""
from typing import Dict, Any, Optional, List

# Base safety score (starts high, penalties reduce it)
BASE_SAFETY_SCORE = 90.0

# Safety risk penalties
PENALTY_HIGH_DENSITY = 8.0
PENALTY_MIXED_TRAFFIC = 6.0
PENALTY_PEDESTRIAN_ZONES = 10.0
PENALTY_CYCLISTS = 4.0
PENALTY_AUTO_RICKSHAWS = 5.0
PENALTY_PEDESTRIAN_CROSSINGS = 3.0
PENALTY_CONSTRUCTION = 12.0
PENALTY_POOR_LIGHTING = 7.0
PENALTY_HIGH_CRIME_AREA = 15.0
PENALTY_ISOLATED_LOCATION = 9.0

# Safety bonuses
BONUS_SECURITY_CAMERAS = 5.0
BONUS_POLICE_STATION_NEARBY = 6.0
BONUS_WELL_LIT_AREA = 4.0
BONUS_RESIDENTIAL_AREA = 3.0
BONALTY_COMMERCIAL_AREA = 2.0

# Time-based modifiers
PENALTY_NIGHT_TIME = 8.0  # Additional penalty for night deliveries
PENALTY_EVENING_TIME = 4.0  # Additional penalty for evening deliveries

# Route-based safety penalties
PENALTY_NARROW_ROUTE = 6.0
PENALTY_CONSTRUCTION_ROUTE = 10.0
PENALTY_HIGH_TRAFFIC_ROUTE = 7.0
PENALTY_UNLIT_ROUTE = 8.0

# Places-based safety bonuses
BONUS_NEAR_POLICE = 8.0
BONUS_SECURITY_CAMERAS_NEARBY = 6.0
BONUS_WELL_LIT_NEARBY = 5.0
BONUS_HOSPITAL_NEARBY = 4.0


def _assess_traffic_safety(traffic_concerns: List[str]) -> float:
    """Calculate safety penalty based on traffic concerns."""
    penalty = 0.0
    for concern in traffic_concerns:
        if "high_density" in concern.lower():
            penalty += PENALTY_HIGH_DENSITY
        elif "mixed_traffic" in concern.lower():
            penalty += PENALTY_MIXED_TRAFFIC
        elif "pedestrian" in concern.lower():
            if "zone" in concern.lower():
                penalty += PENALTY_PEDESTRIAN_ZONES
            elif "crossing" in concern.lower():
                penalty += PENALTY_PEDESTRIAN_CROSSINGS
        elif "cyclist" in concern.lower():
            penalty += PENALTY_CYCLISTS
        elif "auto_rickshaw" in concern.lower():
            penalty += PENALTY_AUTO_RICKSHAWS
    return penalty


def _assess_location_safety(city_intel: Dict[str, Any]) -> Dict[str, float]:
    """Assess safety based on location characteristics."""
    penalties = 0.0
    bonuses = 0.0
    
    # Crime and safety indicators
    crime_rate = city_intel.get("crime_rate", "medium")
    if crime_rate == "high":
        penalties += PENALTY_HIGH_CRIME_AREA
    elif crime_rate == "low":
        bonuses += BONUS_SECURITY_CAMERAS
    
    # Infrastructure safety
    if city_intel.get("poor_lighting", False):
        penalties += PENALTY_POOR_LIGHTING
    else:
        bonuses += BONUS_WELL_LIT_AREA
    
    # Area type
    area_type = city_intel.get("area_type", "mixed")
    if area_type == "residential":
        bonuses += BONUS_RESIDENTIAL_AREA
    elif area_type == "commercial":
        bonuses += BONALTY_COMMERCIAL_AREA
    
    # Isolation factors
    if city_intel.get("isolated_location", False):
        penalties += PENALTY_ISOLATED_LOCATION
    
    # Security features
    if city_intel.get("security_cameras", False):
        bonuses += BONUS_SECURITY_CAMERAS
    if city_intel.get("police_station_nearby", False):
        bonuses += BONUS_POLICE_STATION_NEARBY
    
    return {"penalties": penalties, "bonuses": bonuses}


def _assess_route_safety(routing: Dict[str, Any]) -> float:
    """Assess safety concerns along the route."""
    penalty = 0.0
    
    if routing.get("construction_zones", False):
        penalty += PENALTY_CONSTRUCTION
    
    if routing.get("poor_lighting_route", False):
        penalty += PENALTY_POOR_LIGHTING
    
    # Route isolation
    if routing.get("isolated_route_segments", False):
        penalty += PENALTY_ISOLATED_LOCATION * 0.5  # Reduced for route
    
    return penalty


def _assess_route_safety_enhanced(routing: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced route safety assessment with detailed conditions."""
    penalty = 0.0
    conditions = []
    
    if routing.get("narrow_road", False):
        penalty += PENALTY_NARROW_ROUTE
        conditions.append("narrow_road")
    
    if routing.get("construction_zone", False):
        penalty += PENALTY_CONSTRUCTION_ROUTE
        conditions.append("construction")
    
    if routing.get("high_traffic", False):
        penalty += PENALTY_HIGH_TRAFFIC_ROUTE
        conditions.append("high_traffic")
    
    if routing.get("poor_lighting_route", False):
        penalty += PENALTY_UNLIT_ROUTE
        conditions.append("poor_lighting")
    
    # Route isolation
    if routing.get("isolated_route_segments", False):
        penalty += PENALTY_ISOLATED_LOCATION * 0.5
        conditions.append("isolated_segments")
    
    return {
        "penalty": penalty,
        "conditions": conditions,
        "route_length_km": routing.get("distance_km", 0),
        "estimated_time_min": routing.get("duration_min", 0)
    }


def _assess_places_safety_features(places_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Assess safety features from nearby places."""
    bonuses = 0.0
    features = []
    
    if not places_data:
        return {"bonuses": 0.0, "features": [], "nearest_police_m": None}
    
    nearest_police = None
    has_security_cameras = False
    has_hospital = False
    
    for place in places_data:
        category = place.get("category", "").lower()
        distance = place.get("distance", float('inf'))
        
        if "police" in category or "station" in category:
            if nearest_police is None or distance < nearest_police:
                nearest_police = distance
        elif "security" in category or "camera" in category:
            has_security_cameras = True
        elif "hospital" in category or "medical" in category:
            has_hospital = True
    
    # Calculate bonuses based on proximity
    if nearest_police is not None:
        if nearest_police < 500:  # Within 500m
            bonuses += BONUS_NEAR_POLICE
            features.append("police_nearby")
        elif nearest_police < 1000:  # Within 1km
            bonuses += BONUS_NEAR_POLICE * 0.5
            features.append("police_accessible")
    
    if has_security_cameras:
        bonuses += BONUS_SECURITY_CAMERAS_NEARBY
        features.append("security_cameras")
    
    if has_hospital:
        bonuses += BONUS_HOSPITAL_NEARBY
        features.append("hospital_nearby")
    
    return {
        "bonuses": bonuses,
        "features": features,
        "nearest_police_m": nearest_police
    }


def _apply_time_modifier(hour: Optional[int]) -> float:
    """Apply time-based safety modifier."""
    if hour is None:
        return 0.0
    
    if 22 <= hour or hour <= 5:  # Night time (10 PM - 5 AM)
        return -PENALTY_NIGHT_TIME
    elif 18 <= hour <= 21:  # Evening (6 PM - 9 PM)
        return -PENALTY_EVENING_TIME
    
    return 0.0  # Day time is neutral


def compute_safety(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute a safety score (0–100) for delivery operations.

    Inputs:
    - geospatial_checks: { city_intelligence: { safety_concerns, crime_rate, etc. } }
    - routing: { construction_zones, lighting, isolation factors, narrow_road, etc. }
    - places_data: { nearby places with categories and distances }
    - here_results: { primary_result: { address components } }
    - delivery_time_hour: optional hour of delivery (0-23)

    Output:
    {
      "safety_score": float(0–1),
      "breakdown": {
         "traffic_safety_penalty": float,
         "location_safety_penalty": float,
         "route_safety_penalty": float,
         "places_safety_bonuses": float,
         "time_modifier": float,
         "bonuses": float
      },
      "issues": [ ... ],
      "recommendations": [ ... ]
    }
    """
    geo_checks = context.get("geospatial_checks") or {}
    city_intel = geo_checks.get("city_intelligence") or {}
    routing = context.get("routing") or {}
    places_data = context.get("places_data", [])
    
    # Extract safety concerns
    safety_concerns = city_intel.get("safety_concerns", [])
    
    # Calculate different safety components
    traffic_penalty = _assess_traffic_safety(safety_concerns)
    location_assessment = _assess_location_safety(city_intel)
    route_assessment = _assess_route_safety_enhanced(routing)
    places_assessment = _assess_places_safety_features(places_data)
    
    # Time-based modifier
    delivery_hour = context.get("delivery_time_hour")
    time_modifier = _apply_time_modifier(delivery_hour)
    
    # Total penalties and bonuses
    total_penalties = traffic_penalty + location_assessment["penalties"] + route_assessment["penalty"]
    total_bonuses = location_assessment["bonuses"] + places_assessment["bonuses"]
    
    # Calculate final score
    raw_score = BASE_SAFETY_SCORE + total_bonuses + time_modifier - total_penalties
    safety_score = max(0.0, min(100.0, raw_score))
    
    # Generate issues and recommendations
    issues = []
    recommendations = []
    
    # Traffic safety issues
    if traffic_penalty > 0:
        severity = "critical" if traffic_penalty > 15 else "warning" if traffic_penalty > 8 else "info"
        issues.append({
            "tag": "traffic_safety_concerns",
            "severity": severity,
            "explanation": f"Traffic safety concerns detected: {', '.join(safety_concerns)}"
        })
        recommendations.append("Consider delivery during off-peak hours to reduce traffic risks.")
    
    # Location safety issues
    if location_assessment["penalties"] > 0:
        if city_intel.get("crime_rate") == "high":
            issues.append({
                "tag": "high_crime_area",
                "severity": "critical",
                "explanation": "Delivery location is in a high-crime area."
            })
            recommendations.append("Implement additional security measures for high-risk deliveries.")
        
        if city_intel.get("poor_lighting", False):
            issues.append({
                "tag": "poor_lighting",
                "severity": "warning",
                "explanation": "Area has poor lighting which may affect safety."
            })
            recommendations.append("Schedule deliveries during daylight hours when possible.")
    
    # Route safety issues
    if route_assessment["penalty"] > 0:
        route_conditions = route_assessment["conditions"]
        if "construction" in route_conditions:
            issues.append({
                "tag": "construction_zones",
                "severity": "warning",
                "explanation": "Route passes through construction zones."
            })
            recommendations.append("Monitor construction updates and plan alternative routes if needed.")
        
        if "narrow_road" in route_conditions:
            issues.append({
                "tag": "narrow_roads",
                "severity": "warning",
                "explanation": "Route includes narrow roads that may be difficult to navigate."
            })
            recommendations.append("Consider vehicle size and driver experience for narrow road sections.")
        
        if "poor_lighting" in route_conditions:
            issues.append({
                "tag": "poor_route_lighting",
                "severity": "warning",
                "explanation": "Route has sections with poor lighting."
            })
            recommendations.append("Schedule deliveries during daylight hours to avoid poorly lit route sections.")
    
    # Time-based recommendations
    if time_modifier < 0:
        issues.append({
            "tag": "night_time_delivery",
            "severity": "warning",
            "explanation": "Delivery scheduled during night/evening hours increases safety risks."
        })
        recommendations.append("Consider rescheduling to daylight hours for better safety.")
    
    # Places safety features
    if places_assessment["bonuses"] > 0:
        places_features = places_assessment["features"]
        if "police_nearby" in places_features:
            recommendations.append("Police station nearby provides additional security.")
        if "security_cameras" in places_features:
            recommendations.append("Security cameras in the area enhance safety monitoring.")
        if "hospital_nearby" in places_features:
            recommendations.append("Medical facilities nearby provide emergency response capability.")
    
    return {
        "safety_score": safety_score / 100.0,  # Return as 0-1 for consistency
        "breakdown": {
            "traffic_safety_penalty": round(traffic_penalty, 2),
            "location_safety_penalties": round(location_assessment["penalties"], 2),
            "location_safety_bonuses": round(location_assessment["bonuses"], 2),
            "route_safety_penalty": round(route_assessment["penalty"], 2),
            "places_safety_bonuses": round(places_assessment["bonuses"], 2),
            "time_modifier": round(time_modifier, 2),
            "total_penalties": round(total_penalties, 2),
            "total_bonuses": round(total_bonuses, 2),
            "base_score": BASE_SAFETY_SCORE,
            "final_score": round(safety_score, 1),
        },
        "issues": issues,
        "recommendations": recommendations,
        "safety_factors": {
            "traffic_concerns": safety_concerns,
            "crime_rate": city_intel.get("crime_rate", "unknown"),
            "lighting_conditions": "poor" if city_intel.get("poor_lighting") else "good",
            "area_type": city_intel.get("area_type", "mixed"),
            "route_conditions": route_assessment["conditions"],
            "route_details": {
                "length_km": route_assessment["route_length_km"],
                "estimated_time_min": route_assessment["estimated_time_min"]
            },
            "security_features": {
                "cameras": city_intel.get("security_cameras", False),
                "police_station_nearby": city_intel.get("police_station_nearby", False),
                "nearest_police_m": places_assessment["nearest_police_m"],
                "places_features": places_assessment["features"]
            }
        }
    }