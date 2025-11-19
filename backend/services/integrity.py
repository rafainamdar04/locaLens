"""Data integrity computation service."""
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import pandas as pd

from utils.helpers import extract_pincode, extract_city_from_text, contains_vague_tokens


# Cache for known cities list
_KNOWN_CITIES: Optional[Set[str]] = None


def _load_known_cities() -> Set[str]:
    """
    Load known cities from IndiaPostalCodes.csv dataset.
    
    Returns:
        Set of city names (lowercase)
    """
    global _KNOWN_CITIES
    
    if _KNOWN_CITIES is not None:
        return _KNOWN_CITIES
    
    try:
        data_path = Path(__file__).parent.parent / "data" / "IndiaPostalCodes.csv"
        df = pd.read_csv(data_path)
        
        # Extract unique cities (from City and District columns)
        cities = set()
        
        if 'City' in df.columns:
            # Extract city names and clean them
            city_names = df['City'].dropna().astype(str)
            # Add full names
            cities.update(city_names.str.lower().unique())
            # Also extract base city names (e.g., "Bangalore" from "Bangalore G.P.O.")
            for name in city_names:
                # Split on common delimiters and take first part
                base = name.split('(')[0].split('-')[0].strip().lower()
                # Only add if length >= 4 to avoid false positives like "main", "mall"
                if base and len(base) >= 4:
                    cities.add(base)
        
        if 'District' in df.columns:
            districts = df['District'].dropna().astype(str).str.lower().unique()
            # Filter districts by length >= 4
            cities.update([d for d in districts if len(d) >= 4])
        
        # Add common alternate names
        city_aliases = {
            'bengaluru': ['bangalore'],
            'bangalore': ['bengaluru'],
            'mumbai': ['bombay'],
            'bombay': ['mumbai'],
            'kolkata': ['calcutta'],
            'calcutta': ['kolkata'],
            'chennai': ['madras'],
            'madras': ['chennai'],
            'pune': ['poona'],
            'poona': ['pune'],
        }
        
        # Add aliases
        cities_copy = cities.copy()
        for city in cities_copy:
            if city in city_aliases:
                cities.update(city_aliases[city])
        
        _KNOWN_CITIES = cities
        print(f"Loaded {len(_KNOWN_CITIES)} known cities from dataset")
        
    except Exception as e:
        print(f"Warning: Failed to load known cities: {e}")
        _KNOWN_CITIES = set()
    
    return _KNOWN_CITIES


def compute_integrity(raw_address: str, cleaned_address: str) -> Dict[str, Any]:
    """
    Compute data integrity score for the cleaned address.
    
    Scoring Rules:
    - Base score: 50
    - +15 if 6-digit pincode found
    - +10 if city in known list
    - -20 if no city found
    - -10 if contains vague tokens like "near", "opp", "behind"
    - -15 if cleaned length < 15 characters
    
    Args:
        raw_address: Original raw address string
        cleaned_address: Cleaned address string
        
    Returns:
        Dictionary containing:
        - score: Integrity score between 0 and 100
        - issues: List of quality issues detected
        - components: Dictionary with pincode and city
        
    Examples:
        >>> integrity = compute_integrity("Raw addr", "123 Main St, Mumbai 400001")
        >>> print(integrity["score"])
        75
        >>> print(integrity["components"])
        {'pincode': '400001', 'city': 'mumbai'}
    """
    # Start with base score
    score = 50
    issues: List[str] = []
    
    # Extract components
    pincode = extract_pincode(cleaned_address)
    
    # Load known cities
    known_cities = _load_known_cities()
    city = extract_city_from_text(cleaned_address.lower(), list(known_cities))
    
    # Rule 1: +15 if 6-digit pincode found
    if pincode:
        score += 15
    else:
        issues.append("missing_pincode")
    
    # Rule 2: +10 if city in known list
    # Rule 3: -20 if no city found
    if city:
        score += 10
    else:
        score -= 20
        issues.append("no_city_found")
    
    # Rule 4: -10 if contains vague tokens
    if contains_vague_tokens(cleaned_address):
        score -= 10
        issues.append("contains_vague_tokens")
    
    # Rule 5: -15 if cleaned length < 15
    if len(cleaned_address.strip()) < 15:
        score -= 15
        issues.append("too_short")
    
    # Clamp score to 0-100 range
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "issues": issues,
        "components": {
            "pincode": pincode,
            "city": city
        }
    }


# New architecture-compatible entry
def compute_integrity_ctx(context: Dict[str, Any]) -> Dict[str, Any]:
    raw = context.get("raw_address") or ""
    cleaned = context.get("cleaned_address") or ""
    integ = compute_integrity(raw, cleaned)
    # Provide normalized (0-1) for consumers that prefer it
    integ_norm = round(min(max(integ.get("score", 0) / 100.0, 0.0), 1.0), 4)
    return {
        "integrity": integ,
        "integrity_norm": integ_norm,
    }
