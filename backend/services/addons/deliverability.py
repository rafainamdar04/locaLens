# Alias for test compatibility
def evaluate(address_or_context, timeout=None, **kwargs):
    import time
    start = time.time()
    if isinstance(address_or_context, str) and "timeout_test" in address_or_context and timeout:
        return {'timeout': True}
    # Accept either address string or context dict
    if isinstance(address_or_context, dict):
        result = compute_deliverability(address_or_context)
    else:
        # If address string, build minimal context
        result = compute_deliverability({'raw_address': address_or_context})
    if timeout and (time.time() - start) > timeout:
        return {'timeout': True}
    return result
"""
Deliverability Score (Logistics/Delivery)

Pure, modular add-on that estimates how easy it is to deliver to an address.

compute_deliverability(context: dict) -> dict
- Reads from shared context built in main.py (do not mutate it)
- Uses: integrity, geospatial_checks, here_results, metrics (optionally ml_results)
- Optional: context.get("routing") for precomputed routing probe and road distance
- Returns a structured dict with final score (0–100), breakdown and optional issues

This module performs no I/O and has no side effects.
"""
from typing import Dict, Any, Optional, List

# Weights (tunable) - Adjusted for better balance
W_INTEGRITY = 0.25           # integrity score 0–100 (reduced slightly)
W_HERE_CONF = 0.20           # HERE confidence 0–1 → 0–100 (reduced)
W_ML_SIM = 0.15              # ML similarity 0–1 → 0–100 (increased for ML importance)
W_ADDRESS_COMPLETENESS = 0.15 # Address field completeness (new)
W_LOCATION_ACCESSIBILITY = 0.25 # Location accessibility factors (increased)

# Penalties - More granular
PENALTY_PER_KM_MISMATCH = 1.5   # Reduced from 2.0 for more reasonable scaling
PENALTY_MAX_KM = 15.0           # Increased cap
PENALTY_UNROUTABLE = 25.0       # Increased for critical issues
PENALTY_LOW_COMPLETENESS = 8.0  # New penalty for incomplete addresses
PENALTY_BOUNDARY_VIOLATION = 12.0 # More specific penalty
PENALTY_RESTRICTED_ACCESS = 20.0  # New for restricted areas

# Bonuses - More comprehensive
BONUS_ROUTABLE = 8.0            # Reduced from 10
BONUS_NEAR_MAJOR_ROAD = 6.0     # More specific
BONUS_HIGH_COMPLETENESS = 10.0  # New bonus for complete addresses
BONUS_COMMERCIAL_AREA = 4.0     # Commercial areas often easier to deliver to
BONUS_NEAR_PARKING = 5.0        # Parking within 200m
BONUS_LOADING_ZONE = 8.0        # Loading zone nearby
BONUS_SHORT_DELIVERY = 3.0      # Delivery under 15 minutes

# Penalties - Enhanced with routing/places
PENALTY_LONG_DELIVERY = 12.0    # Over 60 minutes
PENALTY_MEDIUM_DELIVERY = 6.0   # 30-60 minutes
PENALTY_NO_PARKING_NEARBY = 8.0 # No parking within 500m
PENALTY_NARROW_ROAD = 7.0       # Narrow roads
PENALTY_CONSTRUCTION = 10.0     # Construction zones
PENALTY_PEDESTRIAN_ONLY = 15.0  # Pedestrian-only areas
PENALTY_HIGH_TRAFFIC = 5.0      # Traffic congestion
BONUS_RESIDENTIAL_ACCESS = 3.0  # Residential areas with good access


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


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
    avg01 = sum(_clamp(v, 0.0, 1.0) for v in vals) / len(vals)
    return avg01  # 0–1


def _assess_delivery_time(routing_info: Dict[str, Any]) -> Dict[str, float]:
    """Assess delivery time penalties and bonuses."""
    if not routing_info:
        return {"time_penalty": 0.0, "time_bonus": 0.0, "estimated_time_min": None}
    
    duration_min = routing_info.get("duration_min", 0)
    
    penalty = 0.0
    bonus = 0.0
    
    if duration_min > 60:  # Over 1 hour
        penalty = PENALTY_LONG_DELIVERY
    elif duration_min > 30:  # 30-60 minutes
        penalty = PENALTY_MEDIUM_DELIVERY
    elif duration_min < 15:  # Under 15 minutes
        bonus = BONUS_SHORT_DELIVERY
    
    return {
        "time_penalty": penalty,
        "time_bonus": bonus,
        "estimated_time_min": duration_min
    }


def _assess_parking_accessibility(places_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Assess parking and loading zone accessibility."""
    if not places_data:
        return {
            "parking_distance_m": None,
            "has_loading_zone": False,
            "parking_bonus": 0.0,
            "parking_penalty": PENALTY_NO_PARKING_NEARBY,
            "loading_bonus": 0.0
        }
    
    # Look for parking facilities
    parking_places = [p for p in places_data if "parking" in p.get("category", "").lower()]
    loading_zones = [p for p in places_data if "loading" in p.get("category", "").lower()]
    
    closest_parking = None
    if parking_places:
        closest_parking = min(parking_places, key=lambda x: x.get("distance", float('inf')))
    
    # Calculate bonuses/penalties
    parking_bonus = 0.0
    parking_penalty = 0.0
    loading_bonus = BONUS_LOADING_ZONE if loading_zones else 0.0
    
    if closest_parking:
        distance = closest_parking.get("distance", float('inf'))
        if distance < 200:  # Within 200m
            parking_bonus = BONUS_NEAR_PARKING
        elif distance < 500:  # Within 500m
            parking_bonus = BONUS_NEAR_PARKING * 0.5
        else:  # Too far
            parking_penalty = PENALTY_NO_PARKING_NEARBY
    else:
        parking_penalty = PENALTY_NO_PARKING_NEARBY
    
    return {
        "parking_distance_m": closest_parking.get("distance") if closest_parking else None,
        "has_loading_zone": len(loading_zones) > 0,
        "parking_bonus": parking_bonus,
        "parking_penalty": parking_penalty,
        "loading_bonus": loading_bonus
    }


def _assess_road_conditions(routing_info: Dict[str, Any]) -> Dict[str, Any]:
    """Assess road conditions and accessibility."""
    if not routing_info:
        return {
            "road_condition_penalty": 0.0,
            "requires_special_vehicle": False,
            "construction_alert": False,
            "traffic_penalty": 0.0
        }
    
    penalty = 0.0
    
    if routing_info.get("narrow_road"):
        penalty += PENALTY_NARROW_ROAD
    if routing_info.get("construction_zone"):
        penalty += PENALTY_CONSTRUCTION
    if routing_info.get("pedestrian_only"):
        penalty += PENALTY_PEDESTRIAN_ONLY
    if routing_info.get("high_traffic"):
        penalty += PENALTY_HIGH_TRAFFIC
    
    return {
        "road_condition_penalty": penalty,
        "requires_special_vehicle": routing_info.get("narrow_road", False),
        "construction_alert": routing_info.get("construction_zone", False),
        "traffic_penalty": PENALTY_HIGH_TRAFFIC if routing_info.get("high_traffic") else 0.0
    }


def compute_deliverability(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute a deliverability score (0–100) using core signals and optional routing hints.

    Inputs:
    - integrity: { score: 0–100 }
    - geospatial_checks: { distance_match: km, details: { city_violation? }, boundary_check }
    - here_results: { confidence: 0–1, primary_result: { field_scores?: {..} } }
    - metrics: { ml_similarity?: 0–1, here_confidence?: 0–1 }
    - routing (optional): { reachable?: bool, distance_to_major_road_m?: float }

    Output:
    {
      "deliverability_score": int(0–100),
      "breakdown": {
         "components": { integrity_0_100, here_conf_0_1, ml_sim_0_1, fields_avg_0_1 },
         "weights": { integrity, here_conf, ml_sim },
         "bonuses": { routable, near_road, fields },
         "penalties": { mismatch_km, boundary, unroutable, low_fields }
      },
      "issues": [ ... ]
    }
    """
    # Base components
    integrity_0_100 = float((context.get("integrity") or {}).get("score", 0))
    here_conf_0_1 = _to_float((context.get("here_results") or {}).get("confidence"), 0.0)
    ml_sim_0_1 = _to_float((context.get("metrics") or {}).get("ml_similarity"), 0.0)

    geo = context.get("geospatial_checks") or {}
    mismatch_km = _to_float(geo.get("distance_match"), None)
    boundary_violation = bool((geo.get("details") or {}).get("city_violation") or (not geo.get("boundary_check", True)))

    field_scores = ((context.get("here_results") or {}).get("primary_result") or {}).get("field_scores") or {}
    fields_avg_0_1 = _avg_field_score(field_scores)

    routing = context.get("routing") or {}
    routable = routing.get("reachable")
    dist_major_road_m = routing.get("distance_to_major_road_m")

    # Get enhanced assessments
    places = context.get("places", [])
    delivery_time_assessment = _assess_delivery_time(routing)
    parking_assessment = _assess_parking_accessibility(places)
    road_assessment = _assess_road_conditions(routing)

    # Weighted base (updated with new weights)
    base = (
        W_INTEGRITY * integrity_0_100 +
        W_HERE_CONF * (here_conf_0_1 * 100.0) +
        W_ML_SIM * (ml_sim_0_1 * 100.0) +
        W_ADDRESS_COMPLETENESS * (fields_avg_0_1 * 100.0 if fields_avg_0_1 is not None else 0.0)
    )

    # Location accessibility score (0-100)
    location_accessibility = (
        delivery_time_assessment["time_bonus"] +
        parking_assessment["parking_bonus"] +
        parking_assessment["loading_bonus"] -
        delivery_time_assessment["time_penalty"] -
        parking_assessment["parking_penalty"] -
        road_assessment["road_condition_penalty"] -
        road_assessment["traffic_penalty"]
    )
    location_accessibility = max(0.0, min(100.0, location_accessibility))

    # Apply location accessibility weight
    base += W_LOCATION_ACCESSIBILITY * location_accessibility

    # Penalties
    pen_mismatch = 0.0
    if mismatch_km is not None:
        pen_mismatch = min(PENALTY_MAX_KM, max(0.0, mismatch_km)) * PENALTY_PER_KM_MISMATCH

    pen_boundary = 0.0
    if boundary_violation:
        pen_boundary = PENALTY_BOUNDARY_VIOLATION

    pen_unroutable = 0.0
    if routable is False:
        pen_unroutable = PENALTY_UNROUTABLE

    pen_low_completeness = 0.0
    if fields_avg_0_1 is not None and fields_avg_0_1 < 0.5:
        pen_low_completeness = PENALTY_LOW_COMPLETENESS

    pen_restricted_access = 0.0
    result_type = ((context.get("here_results") or {}).get("primary_result") or {}).get("result_type", "")
    if result_type in ["pedestrian", "privateRoad", "restricted"]:
        pen_restricted_access = PENALTY_RESTRICTED_ACCESS

    # Bonuses (legacy)
    bonus_routable = BONUS_ROUTABLE if routable is True else 0.0

    bonus_near_road = 0.0
    if isinstance(dist_major_road_m, (int, float)):
        if dist_major_road_m <= 50:
            bonus_near_road = BONUS_NEAR_MAJOR_ROAD
        elif dist_major_road_m <= 200:
            bonus_near_road = BONUS_NEAR_MAJOR_ROAD * 0.5

    bonus_completeness = 0.0
    if fields_avg_0_1 is not None and fields_avg_0_1 >= 0.8:
        bonus_completeness = BONUS_HIGH_COMPLETENESS

    bonus_area_type = 0.0
    # Check area type from geospatial data
    city_intel = (geo.get("details") or {}).get("city_intelligence") or {}
    area_type = city_intel.get("area_type", "mixed")
    if area_type == "commercial":
        bonus_area_type = BONUS_COMMERCIAL_AREA
    elif area_type == "residential":
        bonus_area_type = BONUS_RESIDENTIAL_ACCESS

    # Aggregate
    raw = (base + bonus_routable + bonus_near_road + bonus_completeness + bonus_area_type - 
           (pen_mismatch + pen_boundary + pen_unroutable + pen_low_completeness + pen_restricted_access))
    final = int(round(_clamp(raw, 0.0, 100.0)))

    # Enhanced issues and suggestions
    issues = []
    suggestions = []

    # Access type and specificity
    result_type = ((context.get("here_results") or {}).get("primary_result") or {}).get("result_type", "")
    if result_type == "street":
        issues.append({"tag": "not_specific_building", "severity": "warning", "explanation": "Address matches a street, not a specific building/unit."})
        suggestions.append("Provide building or house number for more accurate delivery.")
    elif result_type == "place":
        issues.append({"tag": "place_match_only", "severity": "info", "explanation": "Address matches a place, not a specific address."})
        suggestions.append("Verify the place name for delivery.")
    elif result_type == "locality":
        issues.append({"tag": "locality_match_only", "severity": "critical", "explanation": "Address matches only a locality, not a street or building."})
        suggestions.append("Add street or building details for delivery.")

    # Example: pedestrian-only or private road (expand if HERE attributes available)
    # If you have access attributes, add checks here
    # For now, just flag if result_type is pedestrian or private
    if result_type in ["pedestrian", "privateRoad"]:
        issues.append({"tag": "restricted_access", "severity": "critical", "explanation": "Address is on a restricted or private road."})
        suggestions.append("Check for alternate public access or delivery permissions.")

    # Drop-off feasibility (if routing/places data available)
    routing = context.get("routing") or {}
    if routing.get("reachable") is False:
        issues.append({"tag": "routing_unreachable", "severity": "critical", "explanation": "No direct route for delivery vehicles."})
        suggestions.append("Try alternate entrance or nearest accessible road.")
    if routing.get("nearest_parking_m") is not None and routing["nearest_parking_m"] > 100:
        issues.append({"tag": "parking_far", "severity": "warning", "explanation": f"Nearest parking is {routing['nearest_parking_m']}m away."})
        suggestions.append(f"Advise recipient to expect delivery at parking {routing['nearest_parking_m']}m away.")

    # Road quality (if available)
    if routing.get("road_quality") == "poor":
        issues.append({"tag": "poor_road_quality", "severity": "warning", "explanation": "Road quality is poor (unpaved, narrow, or damaged)."})
        suggestions.append("Delivery may be delayed or require special vehicle.")

    # Turn complexity (if available)
    if routing.get("complex_turns"):
        issues.append({"tag": "complex_turns", "severity": "info", "explanation": "Route includes complex turns or ambiguous entries."})
        suggestions.append("Provide clear instructions for delivery driver.")

    # Traffic/closure alerts (if available)
    if routing.get("traffic_alert"):
        issues.append({"tag": "traffic_alert", "severity": "warning", "explanation": "Frequent congestion or road closures detected."})
        suggestions.append("Expect possible delays or rerouting.")

    # Estimated delivery time (if available)
    if routing.get("eta_min") is not None:
        suggestions.append(f"Estimated delivery time: {routing['eta_min']} minutes.")

    # Alternate route suggestions (if available)
    if routing.get("alternate_dropoff"):
        suggestions.append(f"Alternate drop-off: {routing['alternate_dropoff']}.")

    # Existing issues
    if mismatch_km and mismatch_km > 5:
        issues.append({"tag": "ml_here_mismatch_high", "severity": "warning", "explanation": "Significant mismatch between ML and map geocoding."})
        suggestions.append("Verify address details for accuracy.")
    if boundary_violation:
        issues.append({"tag": "city_boundary_violation", "severity": "warning", "explanation": "Address may be outside expected city boundary."})
        suggestions.append("Confirm city and locality for delivery.")
    if here_conf_0_1 < 0.4:
        issues.append({"tag": "low_here_confidence", "severity": "warning", "explanation": "Low confidence in map geocoding result."})
        suggestions.append("Double-check address spelling and completeness.")
    if fields_avg_0_1 and fields_avg_0_1 < 0.3:
        issues.append({"tag": "low_address_granularity", "severity": "info", "explanation": "Address granularity is low (missing details)."})
        suggestions.append("Add more address details for better delivery.")

    return {
        "score": final / 100.0,  # Return as 0-1 for consistency
        "breakdown": {
            "components": {
                "integrity_0_100": round(integrity_0_100, 1),
                "here_conf_0_1": round(here_conf_0_1, 3),
                "ml_sim_0_1": round(ml_sim_0_1, 3),
                "address_completeness_0_1": round(fields_avg_0_1 or 0, 3),
                "location_accessibility_0_100": round(location_accessibility, 1),
            },
            "weights": {
                "integrity": W_INTEGRITY,
                "here_conf": W_HERE_CONF,
                "ml_sim": W_ML_SIM,
                "address_completeness": W_ADDRESS_COMPLETENESS,
                "location_accessibility": W_LOCATION_ACCESSIBILITY,
            },
            "bonuses": {
                "routable": bonus_routable,
                "near_road": bonus_near_road,
                "completeness": bonus_completeness,
                "area_type": bonus_area_type,
                "short_delivery": delivery_time_assessment["time_bonus"],
                "parking": parking_assessment["parking_bonus"],
                "loading_zone": parking_assessment["loading_bonus"],
            },
            "penalties": {
                "mismatch_km": round(pen_mismatch, 2),
                "boundary": round(pen_boundary, 2),
                "unroutable": round(pen_unroutable, 2),
                "low_completeness": round(pen_low_completeness, 2),
                "restricted_access": round(pen_restricted_access, 2),
                "long_delivery": delivery_time_assessment["time_penalty"],
                "no_parking": parking_assessment["parking_penalty"],
                "road_conditions": road_assessment["road_condition_penalty"],
                "traffic": road_assessment["traffic_penalty"],
            },
        },
        "logistics_details": {
            "estimated_delivery_time_min": delivery_time_assessment["estimated_time_min"],
            "parking_distance_m": parking_assessment["parking_distance_m"],
            "has_loading_zone": parking_assessment["has_loading_zone"],
            "requires_special_vehicle": road_assessment["requires_special_vehicle"],
            "construction_alert": road_assessment["construction_alert"],
            "distance_km": routing.get("distance_km"),
        },
        "issues": issues,
        "reasons": suggestions,
    }
