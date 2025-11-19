"""
Helper Utilities Module

Provides common utility functions for address processing, geocoding,
and geospatial calculations.
"""

import re
import math
from typing import Optional, List, Set


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Uses the Haversine formula to compute the distance between two geographic
    coordinates. Returns the distance in kilometers.
    
    Args:
        lat1: Latitude of first point (decimal degrees)
        lon1: Longitude of first point (decimal degrees)
        lat2: Latitude of second point (decimal degrees)
        lon2: Longitude of second point (decimal degrees)
        
    Returns:
        Distance in kilometers (float)
        
    Formula:
        a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
        c = 2 * atan2(√a, √(1−a))
        d = R * c
        where R = Earth's radius (6371 km)
    
    Example:
        >>> # Mumbai to Delhi
        >>> haversine(19.0760, 72.8777, 28.7041, 77.1025)
        1153.46
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    
    return distance


def extract_pincode(text: str) -> Optional[str]:
    """
    Extract Indian pincode from text using regex.
    
    Indian pincodes are exactly 6 digits. This function searches for
    the first occurrence of a 6-digit number in the text.
    
    Args:
        text: Text to search for pincode
        
    Returns:
        6-digit pincode string or None if not found
        
    Examples:
        >>> extract_pincode("123 Main St, Mumbai 400001")
        '400001'
        >>> extract_pincode("Sector 15, Noida 201301")
        '201301'
        >>> extract_pincode("No pincode here")
        None
    """
    if not text:
        return None
    
    # Regex pattern for 6-digit Indian pincode
    # \b ensures word boundary (not part of longer number)
    pattern = r'\b\d{6}\b'
    
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_city_from_text(text: str, known_cities_list: List[str]) -> Optional[str]:
    """
    Extract city name from text using a known cities list.
    
    Searches for city names from the known_cities_list in the input text.
    Performs case-insensitive matching and returns the first match found.
    Prefers longer city names over shorter ones to avoid false matches.
    
    Args:
        text: Text to search for city name
        known_cities_list: List of known city names to search for
        
    Returns:
        Matched city name (original case from list) or None if not found
        
    Examples:
        >>> cities = ["Mumbai", "Delhi", "Bangalore", "Navi Mumbai"]
        >>> extract_city_from_text("123 Main St, Navi Mumbai 400001", cities)
        'Navi Mumbai'
        >>> extract_city_from_text("Sector 5, Delhi", cities)
        'Delhi'
        >>> extract_city_from_text("Unknown location", cities)
        None
    """
    if not text or not known_cities_list:
        return None
    
    text_lower = text.lower()
    
    # Sort cities by length (longest first) to match multi-word cities first
    # This prevents "Mumbai" from matching before "Navi Mumbai"
    sorted_cities = sorted(known_cities_list, key=len, reverse=True)
    
    for city in sorted_cities:
        city_lower = city.lower()
        
        # Check if city name appears in text
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(city_lower) + r'\b'
        if re.search(pattern, text_lower):
            return city
    
    return None


def simple_tokenize(text: str) -> List[str]:
    """
    Perform simple tokenization of text.
    
    Splits text into tokens by whitespace and punctuation.
    Converts to lowercase and removes empty tokens.
    
    Args:
        text: Text to tokenize
        
    Returns:
        List of lowercase tokens
        
    Examples:
        >>> simple_tokenize("123 Main St, Mumbai")
        ['123', 'main', 'st', 'mumbai']
        >>> simple_tokenize("Sector-15, Noida!")
        ['sector', '15', 'noida']
    """
    if not text:
        return []
    
    # Replace common punctuation with spaces
    text = re.sub(r'[,;.!?:()\-\[\]{}]', ' ', text)
    
    # Split by whitespace and convert to lowercase
    tokens = text.lower().split()
    
    # Remove empty tokens
    tokens = [token for token in tokens if token]
    
    return tokens


def contains_vague_tokens(text: str) -> bool:
    """
    Check if text contains vague or non-specific location tokens.
    
    Identifies addresses that are too vague for reliable geocoding.
    Checks for common vague terms like "near", "opposite", "behind", etc.
    
    Args:
        text: Text to check for vague tokens
        
    Returns:
        True if text contains vague tokens, False otherwise
        
    Vague tokens include:
        - Directional vague: near, nearby, close to, next to, beside, opposite
        - Relational vague: behind, front of, adjacent, around
        - Uncertain: somewhere, approximately, about, roughly
        - Non-specific: area, locality, region, zone, vicinity
        
    Examples:
        >>> contains_vague_tokens("Near railway station")
        True
        >>> contains_vague_tokens("Opposite mall, Mumbai")
        True
        >>> contains_vague_tokens("123 Main Street, Delhi")
        False
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Define vague token patterns
    vague_tokens = {
        # Directional/proximity vague terms
        'near', 'nearby', 'close to', 'next to', 'beside', 'besides',
        'opposite', 'opp', 'adj', 'adjacent',
        
        # Relational vague terms
        'behind', 'in front of', 'front of', 'back of', 'around',
        'towards', 'heading to', 'on the way to',
        
        # Uncertain terms
        'somewhere', 'approximately', 'approx', 'about', 'roughly',
        'around', 'circa',
        
        # Non-specific location terms
        'area', 'locality', 'region', 'zone', 'vicinity', 'neighborhood',
        'somewhere in', 'somewhere near',
        
        # Common incomplete patterns
        'near by', 'close by', 'not far from',
    }
    
    # Check for presence of vague tokens
    for token in vague_tokens:
        # Use word boundary matching to avoid false positives
        # e.g., "nearby" in "nearbystreet" shouldn't match
        pattern = r'\b' + re.escape(token) + r'\b'
        if re.search(pattern, text_lower):
            return True
    
    return False


def normalize_address_text(text: str) -> str:
    """
    Normalize address text for better matching.
    
    Performs common normalization operations:
    - Remove extra whitespace
    - Convert to lowercase
    - Expand common abbreviations
    - Remove special characters (keep alphanumeric and basic punctuation)
    
    Args:
        text: Address text to normalize
        
    Returns:
        Normalized address text
        
    Examples:
        >>> normalize_address_text("  123  Main  St.  ")
        '123 main street'
        >>> normalize_address_text("Flat #5, Bldg-A")
        'flat 5 building a'
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Common abbreviation expansions
    abbreviations = {
        r'\bst\.?\b': 'street',
        r'\brd\.?\b': 'road',
        r'\bave\.?\b': 'avenue',
        r'\bblvd\.?\b': 'boulevard',
        r'\bdr\.?\b': 'drive',
        r'\bln\.?\b': 'lane',
        r'\bpk\.?\b': 'park',
        r'\bsq\.?\b': 'square',
        r'\bct\.?\b': 'court',
        r'\bpl\.?\b': 'place',
        r'\bter\.?\b': 'terrace',
        r'\bapt\.?\b': 'apartment',
        r'\bflat\.?\b': 'flat',
        r'\bbldg\.?\b': 'building',
        r'\bno\.?\b': 'number',
    }
    
    for abbrev, expanded in abbreviations.items():
        text = re.sub(abbrev, expanded, text)
    
    # Remove special characters (keep only alphanumeric and spaces)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Normalize whitespace (replace multiple spaces with single space)
    text = re.sub(r'\s+', ' ', text)
    
    # Trim leading/trailing whitespace
    text = text.strip()
    
    return text


def is_valid_coordinate(lat: float, lon: float) -> bool:
    """
    Check if latitude and longitude are valid coordinates.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        
    Returns:
        True if valid, False otherwise
        
    Valid ranges:
        Latitude: -90 to +90
        Longitude: -180 to +180
        
    Examples:
        >>> is_valid_coordinate(19.0760, 72.8777)  # Mumbai
        True
        >>> is_valid_coordinate(91.0, 72.8777)  # Invalid lat
        False
        >>> is_valid_coordinate(19.0760, 181.0)  # Invalid lon
        False
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180


def extract_numeric_value(text: str) -> Optional[float]:
    """
    Extract first numeric value from text.
    
    Args:
        text: Text to search for numeric value
        
    Returns:
        First numeric value as float or None if not found
        
    Examples:
        >>> extract_numeric_value("Flat 123, Building A")
        123.0
        >>> extract_numeric_value("Distance: 5.5 km")
        5.5
        >>> extract_numeric_value("No numbers here")
        None
    """
    if not text:
        return None
    
    # Pattern for integers or decimals
    pattern = r'\d+\.?\d*'
    
    match = re.search(pattern, text)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    
    return None


def get_token_set(text: str) -> Set[str]:
    """
    Get set of unique tokens from text.
    
    Useful for fast token-based comparisons and matching.
    
    Args:
        text: Text to tokenize
        
    Returns:
        Set of unique lowercase tokens
        
    Examples:
        >>> get_token_set("123 Main St Main St")
        {'123', 'main', 'st'}
    """
    tokens = simple_tokenize(text)
    return set(tokens)


def token_overlap_ratio(text1: str, text2: str) -> float:
    """
    Calculate token overlap ratio between two texts.
    
    Computes Jaccard similarity: |A ∩ B| / |A ∪ B|
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Overlap ratio between 0.0 and 1.0
        
    Examples:
        >>> token_overlap_ratio("123 Main St", "123 Main Street")
        0.5  # 2 common tokens out of 4 total unique tokens
    """
    tokens1 = get_token_set(text1)
    tokens2 = get_token_set(text2)
    
    if not tokens1 and not tokens2:
        return 1.0  # Both empty
    
    if not tokens1 or not tokens2:
        return 0.0  # One empty
    
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    
    return intersection / union if union > 0 else 0.0
