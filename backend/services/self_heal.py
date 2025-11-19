"""
Self-Healing Service

Attempts to recover from anomalous geocoding results using multiple strategies.
Implements intelligent fallback mechanisms based on detected anomaly types.
"""

from typing import Dict, Any, Optional, List, Tuple
import re


async def self_heal(
    raw: str,
    cleaned: str,
    ml_candidates: Optional[Dict[str, Any]],
    here_resp: Optional[Dict[str, Any]],
    reasons: List[str]
) -> Dict[str, Any]:
    """
    Attempt to self-heal anomalous geocoding results using targeted strategies.
    
    Healing Strategies:
    1. Low Integrity: Re-clean with strict mode and retry ML geocoding
    2. ML-HERE Mismatch: Reverse geocode ML coordinates and compare
    3. Pincode Mismatch: Build structured query with pincode, city, state
    4. Final summary: Human-readable report of all actions taken
    
    Args:
        raw: Original raw address string
        cleaned: Cleaned address string
        ml_candidates: ML geocoding results (contains top_result, candidates, confidence)
        here_resp: HERE geocoding results (contains primary_result, confidence)
        reasons: List of anomaly reason codes
        
    Returns:
        Dictionary containing:
        - healed: Boolean indicating if healing was successful
        - actions: List of action dictionaries with details of each healing step
        - final_result: Best result after healing attempts
        - confidence: Final confidence score after healing
        - summary: Human-readable summary of healing process
    """
    actions = []
    healed = False
    final_result = None
    final_confidence = 0.0
    
    # Strategy 1: Handle low integrity by strict re-cleaning
    if "low_integrity" in reasons:
        action = await _heal_low_integrity(raw, cleaned, ml_candidates)
        actions.append(action)
        
        if action.get("success") and action.get("improved"):
            healed = True
            final_result = action.get("new_ml_result")
            final_confidence = action.get("new_confidence", 0.0)
    
    # Strategy 2: Handle ML-HERE mismatch with reverse geocoding
    if "ml_here_mismatch" in reasons and ml_candidates:
        action = await _heal_ml_here_mismatch(ml_candidates, here_resp)
        actions.append(action)
        
        if action.get("success") and action.get("reverse_match"):
            healed = True
            final_result = action.get("reconciled_result")
            final_confidence = action.get("confidence", 0.0)
    
    # Strategy 3: Handle pincode mismatch with structured query
    if "pincode_mismatch" in reasons:
        action = await _heal_pincode_mismatch(cleaned, ml_candidates, here_resp)
        actions.append(action)
        
        if action.get("success") and action.get("pincode_validated"):
            healed = True
            final_result = action.get("fallback_result")
            final_confidence = action.get("confidence", 0.0)
    
    # Generate human-readable summary
    summary = _generate_summary(reasons, actions, healed)
    
    return {
        "healed": healed,
        "actions": actions,
        "final_result": final_result,
        "confidence": final_confidence,
        "summary": summary,
        "strategies_attempted": len(actions),
        "original_reasons": reasons
    }


async def _heal_low_integrity(
    raw: str,
    cleaned: str,
    ml_candidates: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Strategy 1: Re-clean address with strict mode and retry ML geocoding.
    
    Args:
        raw: Original raw address
        cleaned: Previously cleaned address
        ml_candidates: Previous ML geocoding results
        
    Returns:
        Action dictionary with healing results
    """
    from services.address_cleaner import clean_address
    from services.ml_geocoder import ml_geocode
    
    action = {
        "strategy": "strict_recleaning",
        "reason": "low_integrity",
        "success": False,
        "improved": False
    }
    
    try:
        # Re-clean with strict mode
        strict_result = await clean_address(raw, strict=True)
        new_cleaned = strict_result.get("cleaned_text", "")
        
        action["original_cleaned"] = cleaned
        action["strict_cleaned"] = new_cleaned
        action["cleaning_confidence"] = strict_result.get("confidence", 0.0)
        
        # Check if cleaning improved
        if new_cleaned and new_cleaned != cleaned:
            # Retry ML geocoding with strictly cleaned address
            new_ml_result = ml_geocode(new_cleaned)
            
            action["new_ml_result"] = new_ml_result
            action["new_confidence"] = new_ml_result.get("confidence", 0.0) if new_ml_result else 0.0
            
            # Compare with previous results
            old_confidence = ml_candidates.get("confidence", 0.0) if ml_candidates else 0.0
            new_confidence = action["new_confidence"]
            
            if new_confidence > old_confidence:
                action["success"] = True
                action["improved"] = True
                action["confidence_gain"] = new_confidence - old_confidence
            else:
                action["success"] = True
                action["improved"] = False
                action["note"] = "Strict cleaning applied but confidence did not improve"
        else:
            action["note"] = "Strict cleaning produced identical result"
            action["success"] = True
            
    except Exception as e:
        action["error"] = str(e)
        action["error_type"] = type(e).__name__
    
    return action


async def _heal_ml_here_mismatch(
    ml_candidates: Dict[str, Any],
    here_resp: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Strategy 2: Reverse geocode ML coordinates and compare with HERE results.
    
    Args:
        ml_candidates: ML geocoding results with coordinates
        here_resp: HERE geocoding results
        
    Returns:
        Action dictionary with reconciliation results
    """
    action = {
        "strategy": "reverse_geocode_reconciliation",
        "reason": "ml_here_mismatch",
        "success": False,
        "reverse_match": False
    }
    
    try:
        # Extract ML top result coordinates
        ml_top = ml_candidates.get("top_result")
        if not ml_top:
            action["note"] = "No ML top result available for reverse geocoding"
            return action
        
        ml_coords = ml_top.get("coordinates") or ml_top.get("coords")
        if not ml_coords:
            action["note"] = "ML result missing coordinates"
            return action
        
        # Simulate reverse geocoding (placeholder - would call HERE Reverse Geocode API)
        reverse_result = await _here_reverse_geocode(ml_coords)
        
        action["ml_coordinates"] = ml_coords
        action["reverse_geocode_result"] = reverse_result
        action["success"] = True
        
        # Compare reverse geocoded address with HERE primary result
        if here_resp and reverse_result:
            here_primary = here_resp.get("primary_result")
            if here_primary:
                similarity = _compare_addresses(reverse_result, here_primary)
                action["address_similarity"] = similarity
                
                if similarity > 0.7:  # 70% threshold
                    action["reverse_match"] = True
                    action["reconciled_result"] = reverse_result
                    action["confidence"] = similarity
                    action["note"] = "Reverse geocoding validates ML coordinates"
                else:
                    action["note"] = f"Reverse geocode similarity low ({similarity:.2f})"
            else:
                action["note"] = "HERE primary result not available for comparison"
        else:
            action["note"] = "Insufficient data for reverse geocode comparison"
            
    except Exception as e:
        action["error"] = str(e)
        action["error_type"] = type(e).__name__
    
    return action


async def _heal_pincode_mismatch(
    cleaned: str,
    ml_candidates: Optional[Dict[str, Any]],
    here_resp: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Strategy 3: Build structured query with pincode, city, state for fallback geocoding.
    
    Args:
        cleaned: Cleaned address string
        ml_candidates: ML geocoding results
        here_resp: HERE geocoding results
        
    Returns:
        Action dictionary with pincode-based healing results
    """
    from services.here_geocoder import here_geocode
    
    action = {
        "strategy": "pincode_fallback_query",
        "reason": "pincode_mismatch",
        "success": False,
        "pincode_validated": False
    }
    
    try:
        # Extract pincode from cleaned address
        pincode = _extract_pincode(cleaned)
        
        if not pincode:
            action["note"] = "No pincode found in cleaned address"
            return action
        
        action["extracted_pincode"] = pincode
        
        # Extract city and state from ML or HERE results
        city, state = _extract_city_state(ml_candidates, here_resp)
        
        action["extracted_city"] = city
        action["extracted_state"] = state
        
        # Build structured fallback query
        if city and state:
            fallback_query = f"{pincode}, {city}, {state}"
        elif city:
            fallback_query = f"{pincode}, {city}"
        else:
            fallback_query = pincode
        
        action["fallback_query"] = fallback_query
        action["success"] = True
        
        # Geocode using structured query
        fallback_result = here_geocode(fallback_query)
        
        action["fallback_result"] = fallback_result
        action["fallback_confidence"] = fallback_result.get("confidence", 0.0) if fallback_result else 0.0
        
        # Validate that result matches expected pincode
        if fallback_result and fallback_result.get("primary_result"):
            result_pincode = _extract_pincode_from_result(fallback_result["primary_result"])
            
            if result_pincode == pincode:
                action["pincode_validated"] = True
                action["confidence"] = action["fallback_confidence"]
                action["note"] = "Pincode validated with structured query"
            else:
                action["note"] = f"Result pincode {result_pincode} != expected {pincode}"
        else:
            action["note"] = "Fallback geocoding did not return results"
            
    except Exception as e:
        action["error"] = str(e)
        action["error_type"] = type(e).__name__
    
    return action


# Helper functions

async def _here_reverse_geocode(coords: Dict[str, float]) -> Optional[Dict[str, Any]]:
    """
    Reverse geocode coordinates using HERE RevGeocode v1 with retry logic.
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

    url = "https://revgeocode.search.hereapi.com/v1/revgeocode"
    params = {"at": f"{lat},{lon}", "apiKey": api_key, "lang": "en-US", "limit": 1}
    
    # Retry with exponential backoff
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.ok:
                data = resp.json()
                items = data.get("items") or []
                if not items:
                    return None
                item = items[0]
                addr = item.get("address") or {}
                pos = item.get("position") or {"lat": lat, "lng": lon}
                scoring = item.get("scoring") or {}
                query_score = scoring.get("queryScore", 0.0) if isinstance(scoring, dict) else 0.0
                # Normalize confidence to 0-1
                confidence = float(query_score) if query_score > 0 else 0.75
                return {
                    "address": addr.get("label") or item.get("title"),
                    "coordinates": {"lat": pos.get("lat"), "lon": pos.get("lng")},
                    "confidence": round(min(max(confidence, 0.0), 1.0), 4),
                    "components": {
                        "street": addr.get("street"),
                        "city": addr.get("city"),
                        "state": addr.get("state"),
                        "pincode": addr.get("postalCode"),
                        "country": addr.get("countryName"),
                    },
                }
            # Rate limit or transient error: retry
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep((2 ** attempt) * 0.5)
                continue
            return None
        except requests.RequestException:
            if attempt < 2:
                time.sleep((2 ** attempt) * 0.5)
                continue
            return None
    return None


def _compare_addresses(addr1: Dict[str, Any], addr2: Dict[str, Any]) -> float:
    """
    Compare two address results and return similarity score.
    
    Args:
        addr1: First address result dictionary
        addr2: Second address result dictionary
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    from rapidfuzz import fuzz
    
    # Extract address strings
    addr1_str = addr1.get("address", "") if isinstance(addr1, dict) else str(addr1)
    addr2_str = addr2.get("address", "") if isinstance(addr2, dict) else str(addr2)
    
    if not addr1_str or not addr2_str:
        return 0.0
    
    # Calculate fuzzy string similarity
    similarity = fuzz.ratio(addr1_str.lower(), addr2_str.lower()) / 100.0
    
    return similarity


def _extract_pincode(text: str) -> Optional[str]:
    """
    Extract Indian pincode from text.
    
    Args:
        text: Address text to search
        
    Returns:
        6-digit pincode or None
    """
    # Indian pincodes are 6 digits
    match = re.search(r'\b\d{6}\b', text)
    return match.group(0) if match else None


def _extract_city_state(
    ml_candidates: Optional[Dict[str, Any]],
    here_resp: Optional[Dict[str, Any]]
) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract city and state from geocoding results.
    
    Args:
        ml_candidates: ML geocoding results
        here_resp: HERE geocoding results
        
    Returns:
        Tuple of (city, state) or (None, None)
    """
    city = None
    state = None
    
    # Try ML results first
    if ml_candidates and ml_candidates.get("top_result"):
        top = ml_candidates["top_result"]
        city = top.get("city") or top.get("City")
        state = top.get("state") or top.get("State")
    
    # Fallback to HERE results
    if (not city or not state) and here_resp and here_resp.get("primary_result"):
        primary = here_resp["primary_result"]
        components = primary.get("components", {})
        city = city or components.get("city")
        state = state or components.get("state")
    
    return city, state


def _extract_pincode_from_result(result: Dict[str, Any]) -> Optional[str]:
    """
    Extract pincode from geocoding result.
    
    Args:
        result: Geocoding result dictionary
        
    Returns:
        Pincode string or None
    """
    # Try common keys
    if isinstance(result, dict):
        # Check address components
        components = result.get("components", {})
        pincode = components.get("pincode") or components.get("postalCode") or components.get("Pincode")
        
        if pincode:
            return str(pincode)
        
        # Try extracting from full address
        address = result.get("address", "")
        if address:
            return _extract_pincode(address)
    
    return None


def _generate_summary(
    reasons: List[str],
    actions: List[Dict[str, Any]],
    healed: bool
) -> str:
    """
    Generate human-readable summary of healing process.
    
    Args:
        reasons: List of original anomaly reasons
        actions: List of healing actions taken
        healed: Whether healing was successful
        
    Returns:
        Human-readable summary string
    """
    summary_parts = []
    
    # Header
    summary_parts.append(f"Self-Healing Report: {len(reasons)} anomalies detected")
    summary_parts.append(f"Anomalies: {', '.join(reasons)}")
    summary_parts.append(f"Strategies attempted: {len(actions)}")
    
    # Action details
    for i, action in enumerate(actions, 1):
        strategy = action.get("strategy", "unknown")
        success = action.get("success", False)
        reason = action.get("reason", "")
        
        summary_parts.append(f"\nAction {i}: {strategy} (for {reason})")
        summary_parts.append(f"  Status: {'SUCCESS' if success else 'FAILED'}")
        
        if action.get("note"):
            summary_parts.append(f"  Note: {action['note']}")
        
        if action.get("improved"):
            summary_parts.append(f"  Improvement: Confidence increased by {action.get('confidence_gain', 0):.3f}")
        
        if action.get("reverse_match"):
            summary_parts.append(f"  Reverse geocoding validated ML coordinates")
        
        if action.get("pincode_validated"):
            summary_parts.append(f"  Pincode validation succeeded with fallback query")
        
        if action.get("error"):
            summary_parts.append(f"  Error: {action['error']}")
    
    # Final status
    summary_parts.append(f"\nFinal Status: {'HEALED' if healed else 'NOT HEALED'}")
    
    if healed:
        summary_parts.append("The system successfully recovered from detected anomalies.")
    else:
        summary_parts.append("Manual review recommended - automated healing was unsuccessful.")
    
    return "\n".join(summary_parts)

