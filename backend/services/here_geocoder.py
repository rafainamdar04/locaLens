"""HERE Maps geocoding service (real API)."""
from typing import Dict, Any, Optional, List
from config import settings
import requests
import time
import hashlib


# HERE API result caches
_HERE_ADDRESS_CACHE: Dict[str, Dict[str, Any]] = {}
_HERE_COORD_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_MAX_SIZE = 500  # Limit cache size


class HERERateLimiter:
    """Rate limiter for HERE API calls."""
    
    def __init__(self):
        self.requests_this_second = 0
        self.requests_today = 0
        self.second_reset = time.time() + 1
        self.day_start = time.time()
        
    def wait_if_needed(self):
        """Wait if rate limit exceeded."""
        now = time.time()
        
        # Reset per-second counter
        if now >= self.second_reset:
            self.requests_this_second = 0
            self.second_reset = now + 1
            
        # Reset daily counter (approximate)
        if now - self.day_start >= 86400:  # 24 hours
            self.requests_today = 0
            self.day_start = now
            
        # Check limits
        if self.requests_this_second >= 10:  # 10 requests/second
            wait_time = self.second_reset - now
            if wait_time > 0:
                time.sleep(wait_time)
                self.requests_this_second = 0
                self.second_reset = time.time() + 1
                
        if self.requests_today >= 10000:  # 10k requests/day
            print("[HERE GEOCODER] Daily quota exceeded, blocking request")
            return False
            
        self.requests_this_second += 1
        self.requests_today += 1
        return True


# Global rate limiter instance
_rate_limiter = HERERateLimiter()


def _get_cache_key(text: str) -> str:
    """Generate cache key for address text."""
    return hashlib.md5(text.lower().strip().encode()).hexdigest()


def _get_coord_cache_key(lat: float, lon: float) -> str:
    """Generate cache key for coordinates (rounded to 4 decimal places)."""
    return f"{round(lat, 4)}_{round(lon, 4)}"


def _manage_cache_size(cache_dict: Dict[str, Any]):
    """Keep cache size under limit using LRU eviction."""
    if len(cache_dict) >= _CACHE_MAX_SIZE:
        # Remove oldest 10% of entries
        items_to_remove = int(_CACHE_MAX_SIZE * 0.1)
        keys_to_remove = list(cache_dict.keys())[:items_to_remove]
        for key in keys_to_remove:
            del cache_dict[key]


def _get_cached_result(cache_dict: Dict[str, Any], key: str) -> Optional[Dict[str, Any]]:
    """Retrieve cached result if it exists and is fresh (< 1 hour)."""
    if key in cache_dict:
        cached = cache_dict[key]
        age_seconds = time.time() - cached['cached_at']
        if age_seconds < 3600:  # 1 hour TTL
            return cached['result']
        else:
            # Expired, remove it
            del cache_dict[key]
    return None


def _set_cached_result(cache_dict: Dict[str, Any], key: str, result: Dict[str, Any]):
    """Store result in cache with timestamp."""
    _manage_cache_size(cache_dict)
    cache_dict[key] = {
        'result': result,
        'cached_at': time.time()
    }


def _extract_primary(item: Dict[str, Any]) -> Dict[str, Any]:
    """Extract primary result with field scores and normalized confidence."""
    pos = item.get("position") or {}
    addr = item.get("address") or {}
    scoring = item.get("scoring") or {}
    field_score = scoring.get("fieldScore") or {}
    
    return {
        "address": addr.get("label") or item.get("title"),
        "lat": pos.get("lat"),
        "lon": pos.get("lng"),
        "city": addr.get("city"),
        "pincode": addr.get("postalCode"),
        "components": {
            "city": addr.get("city"),
            "state": addr.get("state"),
            "district": addr.get("county"),
            "pincode": addr.get("postalCode"),
            "country": addr.get("countryName"),
        },
        "field_scores": field_score,  # city, postalCode, placeName, etc.
        "result_type": item.get("resultType"),
    }


def _geocode_with_retry(url: str, params: Dict[str, Any], retries: int) -> Dict[str, Any]:
    """Execute HERE API call with rate limiting and exponential backoff retry logic."""
    timeout_s = float(settings.HERE_HTTP_TIMEOUT_S)
    
    # Check rate limit first
    if not _rate_limiter.wait_if_needed():
        return {"error": "Rate limit exceeded", "status": "rate_limit"}
    
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=timeout_s)
            if resp.ok:
                return resp.json()
            # Rate limit or server error: retry with backoff
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                backoff = (2 ** attempt) * 0.5  # 0.5s, 1s
                time.sleep(backoff)
                continue
            return {"error": resp.text, "status": resp.status_code}
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep((2 ** attempt) * 0.5)
                continue
            return {"error": str(e), "status": "exception"}
    return {"error": "Max retries exceeded", "status": "retry_limit"}


def here_geocode(cleaned_address: str) -> Optional[Dict[str, Any]]:
    """
    Perform geocoding using HERE Geocoding & Search v7 with retry logic and caching.

    Args:
        cleaned_address: Cleaned address string

    Returns:
        Dictionary with primary_result, confidence (0-1), alternatives, raw_response
    """
    if not cleaned_address or not cleaned_address.strip():
        return {"primary_result": None, "confidence": 0.0, "alternatives": [], "raw_response": None}

    api_key = settings.HERE_API_KEY
    if not api_key:
        print("[HERE GEOCODER] No HERE_API_KEY configured - skipping HERE geocoding")
        return {"primary_result": None, "confidence": 0.0, "alternatives": [], "raw_response": None}
    
    # Check cache first
    cache_key = _get_cache_key(cleaned_address)
    cached_result = _get_cached_result(_HERE_ADDRESS_CACHE, cache_key)
    if cached_result:
        cached_result['cached'] = True
        return cached_result
    
    print(f"[HERE GEOCODER] Using HERE Maps API (key configured: {bool(api_key)})")
    url = "https://geocode.search.hereapi.com/v1/geocode"
    params = {"q": cleaned_address, "apiKey": api_key, "limit": 5, "lang": "en-US"}

    data = _geocode_with_retry(url, params, retries=settings.HERE_HTTP_RETRIES)
    items: List[Dict[str, Any]] = data.get("items", []) if isinstance(data, dict) else []

    primary = _extract_primary(items[0]) if items else None

    # Normalize confidence to 0.0-1.0 scale (consistent with ML geocoder)
    score = 0.0
    if items:
        scoring = items[0].get("scoring") or {}
        query_score = scoring.get("queryScore", 0.0) if isinstance(scoring, dict) else 0.0
        if query_score > 0:
            # HERE queryScore is already 0-1
            score = float(query_score)
        else:
            # Heuristic fallback based on resultType
            rt = items[0].get("resultType") or ""
            score = 0.9 if rt == "houseNumber" else 0.8 if rt == "street" else 0.7

    alternatives = [
        _extract_primary(it) for it in items[1:]
    ] if len(items) > 1 else []

    result = {
        "primary_result": primary,
        "confidence": round(min(max(score, 0.0), 1.0), 4),  # Clamp to [0, 1]
        "alternatives": alternatives,
        "raw_response": data,
    }
    
    # Cache the result
    _set_cached_result(_HERE_ADDRESS_CACHE, cache_key, result)
    
    return result


async def here_batch_geocode(addresses: List[str]) -> List[Optional[Dict[str, Any]]]:
    """
    Geocode multiple addresses in batches to optimize API usage.
    
    Args:
        addresses: List of address strings to geocode
        
    Returns:
        List of geocoding results in same order as input
    """
    if not addresses:
        return []
    
    api_key = settings.HERE_API_KEY
    if not api_key:
        return [{"primary_result": None, "confidence": 0.0, "alternatives": [], "raw_response": None} for _ in addresses]
    
    results = []
    
    # Process in batches of 10 to avoid URL length limits
    batch_size = 10
    for i in range(0, len(addresses), batch_size):
        batch = addresses[i:i + batch_size]
        
        # Check cache for each address in batch
        batch_results = []
        uncached_addresses = []
        uncached_indices = []
        
        for idx, addr in enumerate(batch):
            if addr and addr.strip():
                cache_key = _get_cache_key(addr)
                cached = _get_cached_result(_HERE_ADDRESS_CACHE, cache_key)
                if cached:
                    batch_results.append((idx, cached))
                else:
                    uncached_addresses.append(addr)
                    uncached_indices.append(idx)
            else:
                batch_results.append((idx, {"primary_result": None, "confidence": 0.0, "alternatives": [], "raw_response": None}))
        
        # Geocode uncached addresses individually (for now)
        # TODO: Implement true HERE batch geocoding API when available
        for addr, orig_idx in zip(uncached_addresses, uncached_indices):
            result = here_geocode(addr)
            batch_results.append((orig_idx, result))
        
        # Sort by original index and extract results
        batch_results.sort(key=lambda x: x[0])
        results.extend([result for _, result in batch_results])
    
    return results


async def here_routing(origin: Dict[str, float], destination: Dict[str, float], transport_mode: str = "car") -> Optional[Dict[str, Any]]:
    """
    Get routing information using HERE Routing v8 API.
    
    Args:
        origin: Dict with 'lat' and 'lon' keys
        destination: Dict with 'lat' and 'lon' keys  
        transport_mode: 'car', 'truck', 'pedestrian', etc.
        
    Returns:
        Routing result with distance, duration, and route details
    """
    api_key = settings.HERE_API_KEY
    if not api_key:
        return None
    
    # Check rate limit
    if not _rate_limiter.wait_if_needed():
        return {"error": "Rate limit exceeded"}
    
    url = "https://router.hereapi.com/v8/routes"
    params = {
        "transportMode": transport_mode,
        "origin": f"{origin['lat']},{origin['lon']}",
        "destination": f"{destination['lat']},{destination['lon']}",
        "return": "summary,polyline",
        "apiKey": api_key
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.ok:
            data = resp.json()
            routes = data.get("routes", [])
            if routes:
                route = routes[0]
                summary = route.get("sections", [{}])[0].get("summary", {})
                
                return {
                    "distance_m": summary.get("length", 0),
                    "duration_s": summary.get("duration", 0),
                    "distance_km": round(summary.get("length", 0) / 1000, 2),
                    "duration_min": round(summary.get("duration", 0) / 60, 1),
                    "polyline": route.get("polyline"),
                    "transport_mode": transport_mode
                }
    except Exception as e:
        print(f"[HERE ROUTING] Error: {e}")
    
    return None


async def here_routing(origin: Dict[str, float], destination: Dict[str, float], transport_mode: str = "car") -> Optional[Dict[str, Any]]:
    """
    Get routing information using HERE Routing v8 API.
    
    Args:
        origin: Dict with 'lat' and 'lon' keys
        destination: Dict with 'lat' and 'lon' keys  
        transport_mode: 'car', 'truck', 'pedestrian', etc.
        
    Returns:
        Routing result with distance, duration, and route details
    """
    api_key = settings.HERE_API_KEY
    if not api_key:
        return None
    
    # Check rate limit
    if not _rate_limiter.wait_if_needed():
        return {"error": "Rate limit exceeded"}
    
    url = "https://router.hereapi.com/v8/routes"
    params = {
        "transportMode": transport_mode,
        "origin": f"{origin['lat']},{origin['lon']}",
        "destination": f"{destination['lat']},{destination['lon']}",
        "return": "summary,polyline",
        "apiKey": api_key
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.ok:
            data = resp.json()
            routes = data.get("routes", [])
            if routes:
                route = routes[0]
                summary = route.get("sections", [{}])[0].get("summary", {})
                
                return {
                    "distance_m": summary.get("length", 0),
                    "duration_s": summary.get("duration", 0),
                    "distance_km": round(summary.get("length", 0) / 1000, 2),
                    "duration_min": round(summary.get("duration", 0) / 60, 1),
                    "polyline": route.get("polyline"),
                    "transport_mode": transport_mode
                }
    except Exception as e:
        print(f"[HERE ROUTING] Error: {e}")
    
    return None


async def here_places_search(location: Dict[str, float], radius: int = 500, categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Search for places near a location using HERE Places API.
    
    Args:
        location: Dict with 'lat' and 'lon' keys
        radius: Search radius in meters (default 500m)
        categories: List of place categories to filter by
        
    Returns:
        List of nearby places with details
    """
    api_key = settings.HERE_API_KEY
    if not api_key:
        return []
    
    # Check rate limit
    if not _rate_limiter.wait_if_needed():
        return []
    
    url = "https://places.ls.hereapi.com/places/v1/discover/explore"
    params = {
        "at": f"{location['lat']},{location['lon']}",
        "radius": radius,
        "apiKey": api_key
    }
    
    if categories:
        params["cat"] = ",".join(categories)
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.ok:
            data = resp.json()
            results = data.get("results", {}).get("items", [])
            
            places = []
            for item in results:
                place = {
                    "name": item.get("title", ""),
                    "category": item.get("category", {}).get("id", ""),
                    "categories": [cat.get("id", "") for cat in item.get("category", {}).get("id", [])] if isinstance(item.get("category"), list) else [item.get("category", {}).get("id", "")],
                    "position": item.get("position", []),
                    "distance": item.get("distance", 0),
                    "vicinity": item.get("vicinity", ""),
                    "href": item.get("href", "")
                }
                places.append(place)
            
            return places
    except Exception as e:
        print(f"[HERE PLACES] Error: {e}")
    
    return []


# New architecture-compatible entry
def compute_here(context: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = context.get("cleaned_address") or ""
    res = here_geocode(cleaned)
    primary = (res or {}).get("primary_result")
    return {
        "here_results": res,
        "here_primary": primary,
        "here_confidence": (res or {}).get("confidence", 0.0),
    }
def compute_here(context: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = context.get("cleaned_address") or ""
    res = here_geocode(cleaned)
    primary = (res or {}).get("primary_result")
    return {
        "here_results": res,
        "here_primary": primary,
        "here_confidence": (res or {}).get("confidence", 0.0),
    }
