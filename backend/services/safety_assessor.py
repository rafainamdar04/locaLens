"""Safety Assessor service for residential real estate using HERE API.

Evaluates location safety and livability with detailed insights for property buyers/renters.
"""

from typing import Dict, Any, Optional, List
from config import settings
import requests
import time
import hashlib
from datetime import datetime, timedelta

# Reuse rate limiter
from services.here_geocoder import _rate_limiter, _geocode_with_retry

# Cache for safety data
_SAFETY_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_MAX_SIZE = 200


def _get_safety_cache_key(lat: float, lon: float) -> str:
    """Generate cache key for location."""
    return hashlib.md5(f"{round(lat, 4)}_{round(lon, 4)}".encode()).hexdigest()


def _manage_safety_cache():
    """Keep cache size under limit."""
    if len(_SAFETY_CACHE) >= _CACHE_MAX_SIZE:
        items_to_remove = int(_CACHE_MAX_SIZE * 0.1)
        keys_to_remove = list(_SAFETY_CACHE.keys())[:items_to_remove]
        for key in keys_to_remove:
            del _SAFETY_CACHE[key]


def _get_cached_safety(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve cached safety data if fresh (< 1 hour)."""
    if key in _SAFETY_CACHE:
        cached = _SAFETY_CACHE[key]
        age_seconds = time.time() - cached['cached_at']
        if age_seconds < 3600:  # 1 hour
            return cached['result']
        else:
            del _SAFETY_CACHE[key]
    return None


def _set_cached_safety(key: str, result: Dict[str, Any]):
    """Store safety data in cache."""
    _manage_safety_cache()
    _SAFETY_CACHE[key] = {
        'result': result,
        'cached_at': time.time()
    }


def search_nearby_places(lat: float, lon: float, categories: List[str], radius: int = 2000) -> Dict[str, Any]:
    """Search for nearby places using HERE Places API.

    Args:
        lat, lon: Location coordinates
        categories: List of HERE category IDs (e.g., ['hospital', 'police'])
        radius: Search radius in meters

    Returns:
        Places data or error dict
    """
    if not settings.HERE_API_KEY:
        return {"error": "HERE API key not configured"}

    cache_key = _get_safety_cache_key(lat, lon)
    cached = _get_cached_safety(cache_key)
    if cached:
        return cached

    # Use browse endpoint for category search
    url = "https://browse.search.hereapi.com/v1/browse"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "at": f"{lat},{lon}",
        "categories": ",".join(categories),
        "limit": 20,
        "radius": radius
    }

    result = _geocode_with_retry(url, params, settings.HERE_HTTP_RETRIES)
    if "error" in result:
        return result

    _set_cached_safety(cache_key, result)
    return result


def get_pedestrian_accessibility(lat: float, lon: float, destinations: List[Dict[str, float]]) -> Dict[str, Any]:
    """Calculate pedestrian routes to key destinations.

    Args:
        lat, lon: Origin
        destinations: List of {'lat': float, 'lon': float}

    Returns:
        Route data or error
    """
    if not destinations:
        return {"error": "No destinations provided"}

    # For simplicity, calculate to first destination (can extend to matrix)
    dest = destinations[0]
    url = "https://router.hereapi.com/v8/routes"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "origin": f"{lat},{lon}",
        "destination": f"{dest['lat']},{dest['lon']}",
        "transportMode": "pedestrian",
        "return": "summary"
    }

    result = _geocode_with_retry(url, params, settings.HERE_HTTP_RETRIES)
    return result


def get_traffic_incidents(lat: float, lon: float, radius: int = 1000) -> Dict[str, Any]:
    """Get traffic incidents near location using HERE Traffic API.

    Args:
        lat, lon: Location
        radius: Search radius in meters

    Returns:
        Incidents data or error
    """
    if not settings.HERE_API_KEY:
        return {"error": "HERE API key not configured"}

    url = "https://data.traffic.hereapi.com/v7/incidents"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "location": f"{lat},{lon}",
        "radius": radius
    }

    result = _geocode_with_retry(url, params, settings.HERE_HTTP_RETRIES)
    return result


def calculate_safety_scores(lat: float, lon: float) -> Dict[str, Any]:
    """Calculate detailed safety scores for residential real estate.

    Returns:
        {
            "overall_safety": {"score": int, "explanation": str},
            "accessibility": {"score": int, "explanation": str},
            "emergency_response": {"score": int, "explanation": str},
            "traffic_impact": {"score": int, "explanation": str},
            "detailed_insights": {...}
        }
    """
    scores = {}
    detailed_insights = {}

    # 1. Emergency Response: Hospitals, Police, Fire stations
    emergency_categories = ["600-6000-0061", "600-6100-0062", "600-6200-0063"]  # hospital, police, fire
    emergency_places = search_nearby_places(lat, lon, emergency_categories, radius=3000)
    hospital_count = police_count = fire_count = 0
    if "error" in emergency_places:
        emergency_score = 50  # Neutral if error
        emergency_exp = "Unable to assess emergency services proximity."
    else:
        items = emergency_places.get("items", [])
        hospital_count = sum(1 for item in items if any(cat.get("id") == "600-6000-0061" for cat in item.get("categories", [])))
        police_count = sum(1 for item in items if any(cat.get("id") == "600-6100-0062" for cat in item.get("categories", [])))
        fire_count = sum(1 for item in items if any(cat.get("id") == "600-6200-0063" for cat in item.get("categories", [])))

        # Score based on counts and distances
        emergency_score = min(100, 20 + hospital_count * 15 + police_count * 15 + fire_count * 10)
        emergency_exp = f"Found {hospital_count} hospitals, {police_count} police stations, {fire_count} fire stations within 3km. "
        if emergency_score > 80:
            emergency_exp += "Excellent emergency access."
        elif emergency_score > 60:
            emergency_exp += "Good emergency coverage."
        else:
            emergency_exp += "Limited emergency services nearby."

    scores["emergency_response"] = {"score": emergency_score, "explanation": emergency_exp}
    detailed_insights["emergency_services"] = {
        "hospitals": hospital_count,
        "police_stations": police_count,
        "fire_stations": fire_count,
        "nearest_hospital_distance": "N/A"  # Could calculate min distance
    }

    # 2. Accessibility: Schools, Parks, Shopping, Public transport
    accessibility_categories = ["600-6300-0064", "600-6400-0065", "600-6500-0066", "600-6600-0067"]  # school, park, shopping, transport
    accessibility_places = search_nearby_places(lat, lon, accessibility_categories, radius=1500)
    school_count = park_count = shopping_count = transport_count = 0
    if "error" in accessibility_places:
        accessibility_score = 50
        accessibility_exp = "Unable to assess accessibility."
    else:
        items = accessibility_places.get("items", [])
        school_count = sum(1 for item in items if any(cat.get("id") == "600-6300-0064" for cat in item.get("categories", [])))
        park_count = sum(1 for item in items if any(cat.get("id") == "600-6400-0065" for cat in item.get("categories", [])))
        shopping_count = sum(1 for item in items if any(cat.get("id") == "600-6500-0066" for cat in item.get("categories", [])))
        transport_count = sum(1 for item in items if any(cat.get("id") == "600-6600-0067" for cat in item.get("categories", [])))

        accessibility_score = min(100, 30 + school_count * 10 + park_count * 10 + shopping_count * 5 + transport_count * 15)
        accessibility_exp = f"Found {school_count} schools, {park_count} parks, {shopping_count} shopping areas, {transport_count} transport stops within 1.5km. "
        if accessibility_score > 75:
            accessibility_exp += "Highly walkable and convenient."
        elif accessibility_score > 50:
            accessibility_exp += "Moderately accessible."
        else:
            accessibility_exp += "Limited amenities within walking distance."

    scores["accessibility"] = {"score": accessibility_score, "explanation": accessibility_exp}
    detailed_insights["accessibility"] = {
        "schools": school_count,
        "parks": park_count,
        "shopping": shopping_count,
        "public_transport": transport_count
    }

    # 3. Traffic Impact: Incidents and congestion
    traffic_incidents = get_traffic_incidents(lat, lon, radius=2000)
    incident_count = 0
    incidents = []
    if "error" in traffic_incidents:
        traffic_score = 70  # Assume moderate if error
        traffic_exp = "Unable to assess traffic conditions."
    else:
        incidents = traffic_incidents.get("incidents", [])
        incident_count = len(incidents)
        # Score inversely: fewer incidents = higher score
        traffic_score = max(0, 100 - incident_count * 5)
        traffic_exp = f"Found {incident_count} traffic incidents within 2km. "
        if traffic_score > 80:
            traffic_exp += "Low traffic disruption."
        elif traffic_score > 60:
            traffic_exp += "Moderate traffic activity."
        else:
            traffic_exp += "High traffic congestion and incidents."

    scores["traffic_impact"] = {"score": traffic_score, "explanation": traffic_exp}
    detailed_insights["traffic"] = {
        "incident_count": incident_count,
        "severity_levels": [inc.get("severity", 0) for inc in incidents[:5]]  # Top 5
    }

    # 4. Overall Safety: Weighted average
    weights = {"emergency_response": 0.4, "accessibility": 0.3, "traffic_impact": 0.3}
    overall_score = int(sum(scores[k]["score"] * weights[k] for k in weights))
    overall_exp = f"Overall safety score of {overall_score}/100 based on emergency access ({scores['emergency_response']['score']}), accessibility ({scores['accessibility']['score']}), and traffic impact ({scores['traffic_impact']['score']}). "
    if overall_score > 80:
        overall_exp += "This location appears very safe and livable."
    elif overall_score > 60:
        overall_exp += "This location has good safety features with some areas for improvement."
    else:
        overall_exp += "This location may have safety concerns; consider alternatives."

    scores["overall_safety"] = {"score": overall_score, "explanation": overall_exp}

    return {
        "scores": scores,
        "detailed_insights": detailed_insights,
        "location": {"lat": lat, "lon": lon}
    }


def assess_residential_safety(lat: float, lon: float) -> Dict[str, Any]:
    """Main function: Assess safety for residential real estate.

    Args:
        lat, lon: Property location

    Returns:
        Full safety assessment
    """
    return calculate_safety_scores(lat, lon)