"""Delivery & Navigation service using HERE API for e-commerce logistics.

Provides route planning, ETA with traffic, and user-friendly insights like scores and explanations.
"""

from typing import Dict, Any, Optional, List
from config import settings
import requests
import time
import hashlib
from datetime import datetime, timedelta

# Reuse rate limiter from here_geocoder
from services.here_geocoder import _rate_limiter, _geocode_with_retry
from services.warehouses import find_nearest_warehouse

# Cache for routes (key: origin_dest_mode)
_ROUTE_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_MAX_SIZE = 200


def _get_route_cache_key(origin: Dict[str, float], dest: Dict[str, float], mode: str) -> str:
    """Generate cache key for route."""
    return hashlib.md5(f"{origin['lat']}_{origin['lon']}_{dest['lat']}_{dest['lon']}_{mode}".encode()).hexdigest()


def _manage_route_cache():
    """Keep cache size under limit."""
    if len(_ROUTE_CACHE) >= _CACHE_MAX_SIZE:
        items_to_remove = int(_CACHE_MAX_SIZE * 0.1)
        keys_to_remove = list(_ROUTE_CACHE.keys())[:items_to_remove]
        for key in keys_to_remove:
            del _ROUTE_CACHE[key]


def _get_cached_route(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve cached route if fresh (< 30 mins)."""
    if key in _ROUTE_CACHE:
        cached = _ROUTE_CACHE[key]
        age_seconds = time.time() - cached['cached_at']
        if age_seconds < 1800:  # 30 mins
            return cached['result']
        else:
            del _ROUTE_CACHE[key]
    return None


def _set_cached_route(key: str, result: Dict[str, Any]):
    """Store route in cache."""
    _manage_route_cache()
    _ROUTE_CACHE[key] = {
        'result': result,
        'cached_at': time.time()
    }


def calculate_route(origin: Dict[str, float], destination: Dict[str, float], transport_mode: str = "car",
                   alternatives: int = 1, include_traffic: bool = True) -> Dict[str, Any]:
    """Calculate route from origin to destination using HERE Routing API.

    Args:
        origin: {'lat': float, 'lon': float}
        destination: {'lat': float, 'lon': float}
        transport_mode: 'car', 'truck', 'pedestrian', 'bicycle'
        alternatives: Number of route alternatives (1-3)
        include_traffic: Include real-time traffic in ETA

    Returns:
        Route data or error dict
    """
    if not settings.HERE_API_KEY:
        return {"error": "HERE API key not configured"}

    cache_key = _get_route_cache_key(origin, destination, transport_mode)
    cached = _get_cached_route(cache_key)
    if cached:
        return cached

    url = "https://router.hereapi.com/v8/routes"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "origin": f"{origin['lat']},{origin['lon']}",
        "destination": f"{destination['lat']},{destination['lon']}",
        "transportMode": transport_mode,
        "return": "summary,polyline,actions,instructions",
        "alternatives": min(alternatives, 3),
    }

    if include_traffic:
        # Use current time + 5 mins for departure to get traffic
        departure = datetime.utcnow() + timedelta(minutes=5)
        params["departureTime"] = departure.isoformat() + "Z"

    result = _geocode_with_retry(url, params, settings.HERE_HTTP_RETRIES)
    if "error" in result:
        return result

    _set_cached_route(cache_key, result)
    return result


def extract_route_insights(route_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract user-friendly insights from route data.

    Returns:
        {
            "routes": [list of route summaries],
            "scores": {
                "delivery_efficiency": {"score": int, "explanation": str},
                "navigation_ease": {"score": int, "explanation": str},
                "traffic_safety": {"score": int, "explanation": str}
            },
            "recommendation": str
        }
    """
    if "routes" not in route_data:
        return {"error": "No routes found"}

    routes = []
    scores_list = []

    for route in route_data["routes"]:
        summary = route.get("sections", [{}])[0].get("summary", {})
        distance_m = summary.get("length", 0)  # meters
        duration_s = summary.get("duration", 0)  # seconds
        base_duration_s = summary.get("baseDuration", duration_s)  # without traffic

        # Convert to user-friendly units
        distance_km = distance_m / 1000
        duration_min = duration_s / 60
        base_duration_min = base_duration_s / 60
        traffic_delay_min = duration_min - base_duration_min

        instructions = []
        for section in route.get("sections", []):
            for action in section.get("actions", []):
                instr = action.get("instruction", "")
                if instr:
                    instructions.append(instr)

        routes.append({
            "distance_km": round(distance_km, 2),
            "duration_min": round(duration_min, 1),
            "traffic_delay_min": round(traffic_delay_min, 1),
            "instructions": instructions[:10],  # Limit to first 10
            "polyline": route.get("sections", [{}])[0].get("polyline")
        })

        # Calculate scores (0-100)
        # Delivery Efficiency: Lower duration/distance = higher score
        efficiency_score = max(0, min(100, 100 - (duration_min / 60) * 20 - (distance_km / 50) * 10))
        efficiency_exp = f"Efficient delivery with {duration_min:.1f} min ETA and {distance_km:.1f} km distance."

        # Navigation Ease: Fewer instructions = higher score
        ease_score = max(0, min(100, 100 - len(instructions) * 2))
        ease_exp = f"Navigation is {'easy' if ease_score > 70 else 'moderate' if ease_score > 40 else 'complex'} with {len(instructions)} maneuvers."

        # Traffic Safety: Lower delay = higher score (proxy for safety)
        safety_score = max(0, min(100, 100 - traffic_delay_min * 2))
        safety_exp = f"Traffic impact is {'low' if safety_score > 70 else 'moderate' if safety_score > 40 else 'high'} with {traffic_delay_min:.1f} min delay."

        scores_list.append({
            "delivery_efficiency": {"score": int(efficiency_score), "explanation": efficiency_exp},
            "navigation_ease": {"score": int(ease_score), "explanation": ease_exp},
            "traffic_safety": {"score": int(safety_score), "explanation": safety_exp}
        })

    # Overall recommendation
    best_route_idx = 0  # Could be based on combined score
    recommendation = f"Recommended route: {routes[best_route_idx]['duration_min']} min, {routes[best_route_idx]['distance_km']} km. {scores_list[best_route_idx]['delivery_efficiency']['explanation']}"

    return {
        "routes": routes,
        "scores": scores_list[0],  # Return scores for the first/best route
        "recommendation": recommendation
    }


def get_delivery_navigation(destination: Dict[str, float], transport_mode: str = "car",
                          service_type: str = "standard") -> Dict[str, Any]:
    """Main function: Get delivery navigation insights from nearest warehouse.

    Args:
        destination: Delivery address {'lat': float, 'lon': float}
        transport_mode: 'car', 'truck', 'pedestrian', 'bicycle'
        service_type: 'express', 'standard', or 'bulk'

    Returns:
        Full insights dict including warehouse info
    """
    # Find nearest warehouse
    warehouse = find_nearest_warehouse(destination['lat'], destination['lon'], service_type)

    if not warehouse:
        return {
            "error": f"No warehouse found supporting {service_type} service",
            "available_services": ["express", "standard", "bulk"]
        }

    origin = {"lat": warehouse["lat"], "lon": warehouse["lon"]}

    # Calculate route from warehouse to destination
    route_data = calculate_route(origin, destination, transport_mode)

    if "error" in route_data:
        return {
            "error": route_data["error"],
            "warehouse": warehouse
        }

    insights = extract_route_insights(route_data)

    # Add warehouse information to response
    result = {
        "warehouse": warehouse,
        "destination": destination,
        "transport_mode": transport_mode,
        "service_type": service_type,
        **insights
    }

    return result