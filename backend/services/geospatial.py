"""Geospatial validation and checks."""
import json
import math
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import pandas as pd
import numpy as np
import asyncio
import difflib


# Cache for pincode centroids
_PINCODE_CENTROIDS: Optional[Dict[str, Tuple[float, float]]] = None
_CITY_BOUNDARIES: Optional[Dict[str, Any]] = None


def _load_pincode_centroids() -> Dict[str, Tuple[float, float]]:
    """
    Load pincode centroids from the India postal codes dataset.
    Computes mean lat/lon for each pincode.
    
    Returns:
        Dictionary mapping pincode to (lat, lon) tuple
    """
    global _PINCODE_CENTROIDS
    
    if _PINCODE_CENTROIDS is not None:
        return _PINCODE_CENTROIDS
    
    try:
        # Load the dataset
        data_path = Path(__file__).parent.parent / "data" / "IndiaPostalCodes.csv"
        if not data_path.exists():
            print("[GEOSPATIAL] IndiaPostalCodes.csv not found, pincode validation disabled")
            _PINCODE_CENTROIDS = {}
            return _PINCODE_CENTROIDS
        df = pd.read_csv(data_path)
        
        # Group by PIN and compute mean lat/lon
        # Filter out invalid coordinates
        df_clean = df[
            (df['Lat'].notna()) & 
            (df['Lng'].notna()) &
            (df['Lat'] > 0) & 
            (df['Lat'] < 40) &  # Valid latitude range for India
            (df['Lng'] > 60) & 
            (df['Lng'] < 100)   # Valid longitude range for India
        ]
        
        pincode_centroids = (
            df_clean.groupby('PIN')
            .agg({'Lat': 'mean', 'Lng': 'mean'})
            .to_dict('index')
        )
        
        # Convert to simple dict
        _PINCODE_CENTROIDS = {
            str(pin): (data['Lat'], data['Lng'])
            for pin, data in pincode_centroids.items()
        }
        
        print(f"Loaded {len(_PINCODE_CENTROIDS)} pincode centroids")
        
    except Exception as e:
        print(f"Warning: Failed to load pincode centroids: {e}")
        _PINCODE_CENTROIDS = {}
    
    return _PINCODE_CENTROIDS


def _load_city_boundaries() -> Optional[Dict[str, Any]]:
    """
    Load city boundaries from city_boundaries.json if it exists.
    
    Returns:
        Dictionary of city boundaries or None
    """
    global _CITY_BOUNDARIES
    
    if _CITY_BOUNDARIES is not None:
        return _CITY_BOUNDARIES
    
    try:
        boundaries_path = Path(__file__).parent.parent / "data" / "city_boundaries.json"
        if boundaries_path.exists():
            with open(boundaries_path, 'r') as f:
                _CITY_BOUNDARIES = json.load(f)
            print(f"Loaded city boundaries for {len(_CITY_BOUNDARIES)} cities")
        else:
            _CITY_BOUNDARIES = None
    except Exception as e:
        print(f"Warning: Failed to load city boundaries: {e}")
        _CITY_BOUNDARIES = None
    
    return _CITY_BOUNDARIES


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1: Latitude of point 1 (degrees)
        lon1: Longitude of point 1 (degrees)
        lat2: Latitude of point 2 (degrees)
        lon2: Longitude of point 2 (degrees)
        
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


async def _here_reverse_geocode(coords: Dict[str, float]) -> Optional[Dict[str, Any]]:
    """
    Reverse geocode coordinates using HERE RevGeocode v1 with caching.
    """
    from config import settings
    import requests
    import time

    lat = coords.get("lat") or coords.get("latitude")
    lon = coords.get("lon") or coords.get("longitude")
    if lat is None or lon is None:
        return None

    api_key = settings.HERE_API_KEY
    if not api_key:
        return None
    
    # Check cache first
    from services.here_geocoder import _get_coord_cache_key, _get_cached_result, _set_cached_result, _HERE_COORD_CACHE
    cache_key = _get_coord_cache_key(lat, lon)
    cached_result = _get_cached_result(_HERE_COORD_CACHE, cache_key)
    if cached_result:
        return cached_result

    url = "https://revgeocode.search.hereapi.com/v1/revgeocode"
    params = {"at": f"{lat},{lon}", "apiKey": api_key, "lang": "en-US", "limit": 1}

    # Simple retry logic
    for attempt in range(2):
        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.ok:
                data = resp.json()
                items = data.get("items", [])
                if not items:
                    return None
                item = items[0]
                addr = item.get("address", {})
                pos = item.get("position", {"lat": lat, "lng": lon})
                result = {
                    "address": addr.get("label", ""),
                    "coordinates": {"lat": pos.get("lat"), "lon": pos.get("lng")},
                    "components": {
                        "street": addr.get("street", ""),
                        "city": addr.get("city", ""),
                        "state": addr.get("state", ""),
                        "pincode": addr.get("postalCode", ""),
                        "country": addr.get("countryName", ""),
                    }
                }
                # Cache the result
                _set_cached_result(_HERE_COORD_CACHE, cache_key, result)
                return result
        except Exception:
            if attempt < 1:
                time.sleep(0.5)
    return None


def _compare_addresses(addr1: str, addr2: str) -> float:
    """
    Compare two addresses using sequence matching.
    Returns similarity score 0-1.
    """
    if not addr1 or not addr2:
        return 0.0

    # Normalize addresses
    addr1_norm = addr1.lower().strip()
    addr2_norm = addr2.lower().strip()

    # Exact match
    if addr1_norm == addr2_norm:
        return 1.0

    # Sequence matcher for fuzzy matching
    return difflib.SequenceMatcher(None, addr1_norm, addr2_norm).ratio()


def validate_address_components(ml_result: Optional[Dict], here_result: Optional[Dict], cleaned_components: Dict) -> Dict[str, Any]:
    """
    Validate consistency of address components across ML, HERE, and cleaned results.
    """
    issues = []
    component_matches = {}

    # Extract components
    ml_components = ml_result.get("components", {}) if ml_result else {}
    here_components = here_result.get("components", {}) if here_result else {}

    # Check each component
    for component in ["city", "state", "pincode"]:
        ml_val = (ml_components.get(component, "") or "").strip().lower()
        here_val = (here_components.get(component, "") or "").strip().lower()
        expected_val = (cleaned_components.get(component, "") or "").strip().lower()

        matches = {
            "ml_here_match": ml_val == here_val if ml_val and here_val else None,
            "ml_expected_match": ml_val == expected_val if ml_val and expected_val else None,
            "here_expected_match": here_val == expected_val if here_val and expected_val else None,
        }

        component_matches[component] = matches

        # Flag issues
        if matches["ml_here_match"] is False:
            issues.append(f"{component}_mismatch_ml_here")
        if matches["ml_expected_match"] is False:
            issues.append(f"{component}_mismatch_ml_expected")
        if matches["here_expected_match"] is False:
            issues.append(f"{component}_mismatch_here_expected")

    return {
        "component_issues": issues,
        "component_matches": component_matches,
        "consistency_score": 1.0 - (len(issues) * 0.1)  # Penalty per issue
    }


async def validate_reverse_geocoding(ml_coords: Optional[Dict], here_coords: Optional[Dict], cleaned_address: str) -> Dict[str, Any]:
    """
    Cross-validate coordinates by reverse geocoding both ML and HERE results.
    """
    result = {
        "ml_reverse_match": None,
        "here_reverse_match": None,
        "cross_consistency": None,
        "reverse_geocode_details": {}
    }

    try:
        # Reverse geocode ML coordinates
        if ml_coords:
            ml_reverse = await _here_reverse_geocode(ml_coords)
            if ml_reverse:
                ml_similarity = _compare_addresses(ml_reverse["address"], cleaned_address)
                result["ml_reverse_match"] = ml_similarity > 0.8
                result["reverse_geocode_details"]["ml_reverse"] = {
                    "address": ml_reverse["address"],
                    "similarity": ml_similarity,
                    "components": ml_reverse["components"]
                }

        # Reverse geocode HERE coordinates
        if here_coords:
            here_reverse = await _here_reverse_geocode(here_coords)
            if here_reverse:
                here_similarity = _compare_addresses(here_reverse["address"], cleaned_address)
                result["here_reverse_match"] = here_similarity > 0.8
                result["reverse_geocode_details"]["here_reverse"] = {
                    "address": here_reverse["address"],
                    "similarity": here_similarity,
                    "components": here_reverse["components"]
                }

        # Cross-consistency check
        if ml_reverse and here_reverse:
            cross_similarity = _compare_addresses(ml_reverse["address"], here_reverse["address"])
            result["cross_consistency"] = cross_similarity > 0.9
            result["reverse_geocode_details"]["cross_similarity"] = cross_similarity

    except Exception as e:
        result["error"] = str(e)

    return result


async def analyze_poi_proximity(location: Dict[str, float], address_type: str = "", radius: int = 500) -> Dict[str, Any]:
    """
    Analyze proximity to relevant points of interest for address validation.
    
    Args:
        location: Dict with 'lat' and 'lon' keys
        address_type: Type of address (residential, commercial, etc.)
        radius: Search radius in meters
        
    Returns:
        Analysis of POI proximity and validation insights
    """
    from services.here_geocoder import here_places_search
    
    try:
        # Get nearby places
        places = await here_places_search(location, radius=radius)
        
        # Categorize places
        commercial_places = [p for p in places if any(cat in (p.get("categories", []) + [p.get("category", "")]) for cat in ["restaurant", "shop", "office", "commercial"])]
        residential_places = [p for p in places if any(cat in (p.get("categories", []) + [p.get("category", "")]) for cat in ["residential", "apartment", "house"])]
        infrastructure_places = [p for p in places if any(cat in (p.get("categories", []) + [p.get("category", "")]) for cat in ["hospital", "school", "government", "transport"])]
        
        # Analyze based on address type
        analysis = {
            "total_places": len(places),
            "commercial_nearby": len(commercial_places),
            "residential_nearby": len(residential_places),
            "infrastructure_nearby": len(infrastructure_places),
            "nearest_place_distance": min([p.get("distance", 1000) for p in places]) if places else None,
            "validation_insights": []
        }
        
        # Address type validation
        if "commercial" in address_type.lower() and len(commercial_places) == 0:
            analysis["validation_insights"].append({
                "type": "poi_mismatch",
                "severity": "warning",
                "message": "Commercial address but no commercial POIs nearby"
            })
        
        if "residential" in address_type.lower() and len(residential_places) == 0:
            analysis["validation_insights"].append({
                "type": "poi_mismatch", 
                "severity": "warning",
                "message": "Residential address but no residential POIs nearby"
            })
        
        # Infrastructure accessibility
        if len(infrastructure_places) == 0:
            analysis["validation_insights"].append({
                "type": "infrastructure_access",
                "severity": "info",
                "message": "Limited infrastructure access in vicinity"
            })
        
        # Isolation check
        if len(places) < 3:
            analysis["validation_insights"].append({
                "type": "location_isolation",
                "severity": "info", 
                "message": "Location appears isolated with few nearby POIs"
            })
        
        return analysis
        
    except Exception as e:
        return {
            "error": str(e),
            "total_places": 0,
            "validation_insights": []
        }


def cluster_addresses_by_proximity(addresses_with_coords: List[Dict[str, Any]], max_distance_km: float = 5.0) -> List[List[Dict[str, Any]]]:
    """
    Cluster addresses by spatial proximity for batch processing optimization.
    
    Args:
        addresses_with_coords: List of dicts with 'address', 'lat', 'lon' keys
        max_distance_km: Maximum distance for clustering
        
    Returns:
        List of clusters, where each cluster is a list of nearby addresses
    """
    if not addresses_with_coords:
        return []
    
    # Extract coordinates
    coords = []
    for addr in addresses_with_coords:
        if addr.get('lat') is not None and addr.get('lon') is not None:
            coords.append((addr['lat'], addr['lon']))
        else:
            coords.append((0, 0))  # Placeholder for missing coords
    
    # Simple distance-based clustering
    clusters = []
    used_indices = set()
    
    for i, addr1 in enumerate(addresses_with_coords):
        if i in used_indices:
            continue
            
        cluster = [addr1]
        used_indices.add(i)
        
        for j, addr2 in enumerate(addresses_with_coords):
            if j in used_indices or j == i:
                continue
                
            if addr1.get('lat') and addr1.get('lon') and addr2.get('lat') and addr2.get('lon'):
                distance = haversine_distance(
                    addr1['lat'], addr1['lon'], 
                    addr2['lat'], addr2['lon']
                )
                
                if distance <= max_distance_km:
                    cluster.append(addr2)
                    used_indices.add(j)
        
        clusters.append(cluster)
    

    return clusters


async def process_address_batch(addresses: List[str]) -> List[Dict[str, Any]]:
    """
    Process multiple addresses with spatial clustering and batch geocoding optimization.
    
    Args:
        addresses: List of address strings to process
        
    Returns:
        List of processing results in same order as input
    """
    from services.address_cleaner import clean_address
    from services.ml_geocoder import ml_geocode
    from services.here_geocoder import here_batch_geocode
    
    if not addresses:
        return []
    
    results = []
    
    # Step 1: Clean all addresses
    cleaned_addresses = []
    for addr in addresses:
        try:
            cleaned_result = await clean_address(addr)
            cleaned_addresses.append({
                'original': addr,
                'cleaned': cleaned_result.get('cleaned_text', ''),
                'components': cleaned_result.get('components', {})
            })
        except Exception as e:
            cleaned_addresses.append({
                'original': addr,
                'cleaned': addr,
                'components': {},
                'error': str(e)
            })
    
    # Step 2: ML geocoding for all
    ml_results = []
    for cleaned in cleaned_addresses:
        try:
            ml_result = ml_geocode(cleaned['cleaned'])
            ml_results.append(ml_result)
        except Exception as e:
            ml_results.append({'error': str(e)})
    
    # Step 3: Batch HERE geocoding
    here_addresses = [cleaned['cleaned'] for cleaned in cleaned_addresses]
    here_results = await here_batch_geocode(here_addresses)
    
    # Step 4: Extract coordinates for clustering
    addresses_with_coords = []
    for i, (cleaned, ml_res, here_res) in enumerate(zip(cleaned_addresses, ml_results, here_results)):
        ml_coords = None
        here_coords = None
        
        if ml_res and ml_res.get('top_result'):
            ml_top = ml_res['top_result']
            if ml_top.get('lat') and ml_top.get('lon'):
                ml_coords = {'lat': ml_top['lat'], 'lon': ml_top['lon']}
        
        if here_res and here_res.get('primary_result'):
            here_primary = here_res['primary_result']
            if here_primary.get('lat') and here_primary.get('lon'):
                here_coords = {'lat': here_primary['lat'], 'lon': here_primary['lon']}
        
        addresses_with_coords.append({
            'index': i,
            'address': cleaned['original'],
            'cleaned': cleaned['cleaned'],
            'ml_coords': ml_coords,
            'here_coords': here_coords,
            'ml_result': ml_res,
            'here_result': here_res
        })
    
    # Step 5: Process each address with full pipeline
    for addr_data in addresses_with_coords:
        try:
            # Geospatial validation
            geo_checks = geospatial_checks(
                ml_top=addr_data['ml_result'].get('top_result') if addr_data['ml_result'] else None,
                here_primary=addr_data['here_result'].get('primary_result') if addr_data['here_result'] else None,
                cleaned=addr_data['cleaned']
            )
            
            # Reverse geocoding validation
            reverse_validation = await validate_reverse_geocoding(
                ml_coords=addr_data['ml_coords'],
                here_coords=addr_data['here_coords'],
                cleaned_address=addr_data['cleaned']
            )
            
            # POI analysis
            poi_analysis = None
            if addr_data['here_coords']:
                poi_analysis = await analyze_poi_proximity(
                    location=addr_data['here_coords'],
                    address_type="",
                    radius=500
                )
            
            result = {
                'success': True,
                'address': addr_data['address'],
                'cleaned_address': addr_data['cleaned'],
                'ml_results': addr_data['ml_result'],
                'here_results': addr_data['here_result'],
                'geospatial_checks': geo_checks,
                'reverse_geocoding_validation': reverse_validation,
                'poi_proximity_analysis': poi_analysis
            }
            
        except Exception as e:
            result = {
                'success': False,
                'address': addr_data['address'],
                'error': str(e)
            }
        
        results.append(result)
    
    return results


def check_geospatial_consistency(
    ml_top: Optional[Dict[str, Any]],
    here_primary: Optional[Dict[str, Any]],
    cleaned_components: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Check geospatial consistency between ML and HERE results.
    
    Args:
        ml_top: Top result from ML geocoding with 'lat', 'lon' keys
        here_primary: Primary result from HERE geocoding with 'lat', 'lon' keys
        cleaned_components: Cleaned address components with 'pincode', 'city' keys
        
    Returns:
        Dictionary containing:
        - mismatch_km: Distance between ML and HERE results in km (None if can't compute)
        - pincode_mismatch: Boolean indicating pincode location mismatch
        - city_violation: Boolean indicating city boundary violation
        - details: Additional diagnostic information
    """
    result = {
        "mismatch_km": None,
        "pincode_mismatch": False,
        "city_violation": False,
        "details": {}
    }
    
    # Check 1: Compute ML-HERE mismatch distance
    if ml_top and here_primary:
        ml_lat = ml_top.get('lat')
        ml_lon = ml_top.get('lon')
        here_lat = here_primary.get('lat')
        here_lon = here_primary.get('lon')
        
        if all(v is not None for v in [ml_lat, ml_lon, here_lat, here_lon]):
            try:
                mismatch_km = haversine_distance(ml_lat, ml_lon, here_lat, here_lon)
                result["mismatch_km"] = round(mismatch_km, 2)
                result["details"]["ml_coords"] = (ml_lat, ml_lon)
                result["details"]["here_coords"] = (here_lat, here_lon)
            except Exception as e:
                result["details"]["mismatch_error"] = str(e)
    
    # Check 2: Pincode consistency
    pincode = cleaned_components.get('pincode')
    if pincode:
        pincode_centroids = _load_pincode_centroids()
        pincode_str = str(pincode).strip()
        
        if pincode_str in pincode_centroids:
            pincode_lat, pincode_lon = pincode_centroids[pincode_str]
            result["details"]["pincode_centroid"] = (pincode_lat, pincode_lon)
            
            # Check distance from ML result to pincode centroid
            if ml_top:
                ml_lat = ml_top.get('lat')
                ml_lon = ml_top.get('lon')
                if ml_lat is not None and ml_lon is not None:
                    try:
                        ml_pincode_dist = haversine_distance(
                            ml_lat, ml_lon, pincode_lat, pincode_lon
                        )
                        result["details"]["ml_pincode_distance_km"] = round(ml_pincode_dist, 2)
                        
                        # Flag mismatch if distance > 50km (reasonable threshold for PIN code areas)
                        if ml_pincode_dist > 50:
                            result["pincode_mismatch"] = True
                    except Exception as e:
                        result["details"]["ml_pincode_error"] = str(e)
            
            # Check distance from HERE result to pincode centroid
            if here_primary:
                here_lat = here_primary.get('lat')
                here_lon = here_primary.get('lon')
                if here_lat is not None and here_lon is not None:
                    try:
                        here_pincode_dist = haversine_distance(
                            here_lat, here_lon, pincode_lat, pincode_lon
                        )
                        result["details"]["here_pincode_distance_km"] = round(here_pincode_dist, 2)
                        
                        # Flag mismatch if distance > 50km
                        if here_pincode_dist > 50:
                            result["pincode_mismatch"] = True
                    except Exception as e:
                        result["details"]["here_pincode_error"] = str(e)
        else:
            result["details"]["pincode_not_found"] = pincode_str
    
    # Check 3: City boundaries (optional)
    city = cleaned_components.get('city')
    if city:
        city_boundaries = _load_city_boundaries()
        if city_boundaries and city in city_boundaries:
            boundary = city_boundaries[city]
            
            # Check if ML result is within city boundary
            if ml_top:
                ml_lat = ml_top.get('lat')
                ml_lon = ml_top.get('lon')
                if ml_lat is not None and ml_lon is not None:
                    if not _point_in_boundary(ml_lat, ml_lon, boundary):
                        result["city_violation"] = True
                        result["details"]["ml_outside_city"] = True
            
            # Check if HERE result is within city boundary
            if here_primary:
                here_lat = here_primary.get('lat')
                here_lon = here_primary.get('lon')
                if here_lat is not None and here_lon is not None:
                    if not _point_in_boundary(here_lat, here_lon, boundary):
                        result["city_violation"] = True
                        result["details"]["here_outside_city"] = True
    
    # Check 4: Address component consistency
    component_validation = validate_address_components(ml_top, here_primary, cleaned_components)
    result["component_issues"] = component_validation["component_issues"]
    result["component_matches"] = component_validation["component_matches"]
    result["component_consistency_score"] = component_validation["consistency_score"]
    
    return result


def _point_in_boundary(lat: float, lon: float, boundary: Dict[str, Any]) -> bool:
    """
    Check if a point is within a city boundary.
    
    Args:
        lat: Latitude
        lon: Longitude
        boundary: Boundary definition (can be bounding box or polygon)
        
    Returns:
        True if point is within boundary
    """
    # Simple bounding box check
    if 'bbox' in boundary:
        bbox = boundary['bbox']
        min_lat, min_lon, max_lat, max_lon = bbox
        return (min_lat <= lat <= max_lat) and (min_lon <= lon <= max_lon)
    
    # Polygon check using ray casting algorithm
    if 'polygon' in boundary:
        polygon = boundary['polygon']  # List of (lat, lon) tuples
        return _point_in_polygon(lat, lon, polygon)
    
    return True  # If no boundary defined, assume within


def _point_in_polygon(lat: float, lon: float, polygon: list) -> bool:
    """
    Ray casting algorithm to check if point is inside polygon.
    
    Args:
        lat: Point latitude
        lon: Point longitude
        polygon: List of (lat, lon) coordinate tuples defining polygon
        
    Returns:
        True if point is inside polygon
    """
    n = len(polygon)
    inside = False
    
    p1_lat, p1_lon = polygon[0]
    for i in range(1, n + 1):
        p2_lat, p2_lon = polygon[i % n]
        
        if lon > min(p1_lon, p2_lon):
            if lon <= max(p1_lon, p2_lon):
                if lat <= max(p1_lat, p2_lat):
                    if p1_lon != p2_lon:
                        x_intersection = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                    if p1_lat == p2_lat or lat <= x_intersection:
                        inside = not inside
        
        p1_lat, p1_lon = p2_lat, p2_lon
    
    return inside


def geospatial_checks(
    ml_top: Optional[Dict[str, Any]],
    here_primary: Optional[Dict[str, Any]],
    cleaned: str
) -> Dict[str, Any]:
    """
    Legacy wrapper for backwards compatibility with main.py.
    
    Args:
        ml_top: Top result from ML geocoding
        here_primary: Primary result from HERE geocoding
        cleaned: Cleaned address string (not used in new implementation)
        
    Returns:
        Dictionary containing score and validation results
    """
    # For legacy support, extract components from cleaned string if needed
    # In practice, main.py should pass cleaned_components from clean_address result
    cleaned_components = {}
    
    # Run consistency checks
    consistency = check_geospatial_consistency(ml_top, here_primary, cleaned_components)
    
    # Compute overall score based on checks
    score = 1.0
    
    if consistency["mismatch_km"] is not None:
        # Penalty based on mismatch distance
        if consistency["mismatch_km"] > 100:
            score -= 0.4
        elif consistency["mismatch_km"] > 50:
            score -= 0.3
        elif consistency["mismatch_km"] > 20:
            score -= 0.2
        elif consistency["mismatch_km"] > 5:
            score -= 0.1
    
    if consistency["pincode_mismatch"]:
        score -= 0.3
    
    if consistency["city_violation"]:
        score -= 0.2
    
    score = max(0.0, score)
    
    return {
        "score": score,
        "distance_match": consistency["mismatch_km"],
        "boundary_check": not consistency["city_violation"],
        "consistency": score,
        "details": consistency
    }


# New architecture-compatible entry
def compute_checks(context: Dict[str, Any]) -> Dict[str, Any]:
    ml_top = context.get("ml_top")
    here_primary = context.get("here_primary")
    cleaned_components = context.get("cleaned_components") or {}
    if cleaned_components:
        checks = check_geospatial_consistency(ml_top, here_primary, cleaned_components)
        # Standardize top-level booleans for consumers
        pincode_mismatch = bool(checks.get("pincode_mismatch", False))
        city_violation = bool(checks.get("city_violation", False))
        res = {
            "score": 1.0,
            "distance_match": checks.get("mismatch_km"),
            "boundary_check": not city_violation,
            "pincode_mismatch": pincode_mismatch,
            "city_violation": city_violation,
            "consistency": 1.0,
            "details": checks,
        }
    else:
        res = geospatial_checks(ml_top=ml_top, here_primary=here_primary, cleaned=context.get("cleaned_address") or "")
    return {"geospatial_checks": res}
