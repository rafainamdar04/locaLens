"""Address cleaning service with LLM (OpenRouter/OpenAI) and fallback methods."""
import re
import asyncio
from typing import Dict, Any, Optional
try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

from config import settings


async def clean_address(raw_text: str, strict: bool = False) -> Dict[str, Any]:
    """
    Clean and normalize raw address string using LLM (OpenRouter/OpenAI) or deterministic fallback.
    
    Args:
        raw_text: Raw address input from user
        strict: If True, applies stricter validation and confidence thresholds
        
    Returns:
        Dictionary with:
        - cleaned_text: Normalized single-line address string
        - components: Extracted address components (dict)
        - confidence: Confidence score (0.0-1.0)
    """
    if not raw_text or not raw_text.strip():
        return {
            "cleaned_text": "",
            "components": {},
            "confidence": 0.0
        }
    
    # Try LLM if API key is configured
    if settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY:
        try:
            result = await _clean_with_openai(raw_text, strict)
            return result
        except Exception as e:
            print(f"LLM cleaning failed, falling back to deterministic: {e}")
            # Fall through to deterministic method
    
    # Deterministic fallback
    return _clean_deterministic(raw_text, strict)


async def _clean_with_openai(raw_text: str, strict: bool) -> Dict[str, Any]:
    """
    Clean address using LLM (OpenRouter or OpenAI) ChatCompletion API.
    
    Args:
        raw_text: Raw address text
        strict: Whether to apply strict validation
        
    Returns:
        Cleaned address dictionary
    """
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")
    
    # Determine API key and base URL
    api_key = settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY
    if not api_key:
        raise ValueError("No API key configured for LLM cleaning")
    
    # Detect OpenRouter keys and set proper base URL
    if api_key.startswith("sk-or-"):
        print(f"[ADDRESS CLEANER] Using OpenRouter API for cleaning")
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    else:
        print(f"[ADDRESS CLEANER] Using OpenAI API for cleaning")
        client = openai.AsyncOpenAI(api_key=api_key)
    
    # Construct concise prompt
    system_prompt = (
        "You are an address normalizer. Convert the given address into a clean, "
        "single-line format suitable for geocoding. Remove extra whitespace, "
        "fix typos, standardize abbreviations, and format it properly. "
        "Respond ONLY with the cleaned address, nothing else."
    )
    
    user_prompt = f"Normalize this Indian address: {raw_text}"
    
    # Call OpenAI API
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,  # Deterministic output
        max_tokens=150
    )
    
    cleaned_text = response.choices[0].message.content.strip()
    
    # Compute confidence based on similarity to original
    confidence = 0.85  # Default high confidence for OpenAI
    if RAPIDFUZZ_AVAILABLE:
        similarity = fuzz.ratio(raw_text.lower(), cleaned_text.lower()) / 100.0
        # High similarity suggests minimal changes needed (good)
        # But very high similarity might mean no cleaning happened
        if similarity > 0.95:
            confidence = 0.9
        elif similarity > 0.7:
            confidence = 0.95
        else:
            confidence = 0.8
    
    # Extract basic components (simplified)
    components = _extract_components(cleaned_text)
    
    return {
        "cleaned_text": cleaned_text,
        "components": components,
        "confidence": confidence
    }


# New architecture-compatible entry: pure function taking context dict
async def compute_clean(context: Dict[str, Any]) -> Dict[str, Any]:
    raw = context.get("raw_address") or context.get("raw") or ""
    result = await clean_address(raw)
    return {
        "cleaning_result": result,
        "cleaned_address": result.get("cleaned_text", ""),
        "cleaned_components": result.get("components", {}),
        "clean_confidence": result.get("confidence", 0.0),
    }


def _clean_deterministic(raw_text: str, strict: bool) -> Dict[str, Any]:
    """
    Deterministic address cleaning fallback.
    
    Args:
        raw_text: Raw address text
        strict: Whether to apply strict validation
        
    Returns:
        Cleaned address dictionary
    """
    # Step 1: Basic normalization
    text = raw_text.strip()
    
    # Step 2: Remove extra newlines and collapse to single line
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\r+', ' ', text)
    
    # Step 3: Collapse multiple whitespace into single space
    text = re.sub(r'\s+', ' ', text)
    
    # Step 4: Basic punctuation cleanup
    # Remove excessive punctuation but keep commas, periods, hyphens
    text = re.sub(r'[^\w\s,.\-/()&]', '', text)
    
    # Remove multiple commas
    text = re.sub(r',+', ',', text)
    
    # Remove leading/trailing commas and spaces
    text = re.sub(r'^\s*,\s*|\s*,\s*$', '', text)
    
    # Step 5: Standardize common abbreviations (Indian context)
    abbreviations = {
        r'\bRd\b': 'Road',
        r'\bSt\b': 'Street',
        r'\bAve\b': 'Avenue',
        r'\bBlvd\b': 'Boulevard',
        r'\bDr\b': 'Drive',
        r'\bLn\b': 'Lane',
        r'\bPl\b': 'Place',
        r'\bApt\b': 'Apartment',
        r'\bBldg\b': 'Building',
        r'\bFlr\b': 'Floor',
        r'\bMH\b': 'Maharashtra',
        r'\bKA\b': 'Karnataka',
        r'\bTN\b': 'Tamil Nadu',
        r'\bDL\b': 'Delhi',
    }
    
    for abbr, full in abbreviations.items():
        text = re.sub(abbr, full, text, flags=re.IGNORECASE)
    
    # Step 6: Title case for better readability
    # But preserve all-caps state codes
    words = text.split()
    cleaned_words = []
    for word in words:
        if len(word) <= 3 and word.isupper():
            cleaned_words.append(word)  # Keep short uppercase (state codes)
        else:
            cleaned_words.append(word.title())
    
    cleaned_text = ' '.join(cleaned_words)
    
    # Step 7: Final cleanup
    cleaned_text = cleaned_text.strip()
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Step 8: Compute confidence heuristic
    confidence = _compute_confidence(raw_text, cleaned_text, strict)
    
    # Step 9: Extract components
    components = _extract_components(cleaned_text)
    
    return {
        "cleaned_text": cleaned_text,
        "components": components,
        "confidence": confidence
    }


def _compute_confidence(raw: str, cleaned: str, strict: bool) -> float:
    """
    Compute confidence score for deterministic cleaning.
    
    Args:
        raw: Original raw text
        cleaned: Cleaned text
        strict: Whether strict mode is enabled
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    confidence = 0.5  # Base confidence
    
    # Factor 1: Length check (too short or too long is suspicious)
    length = len(cleaned)
    if 10 <= length <= 200:
        confidence += 0.15
    elif 5 <= length <= 300:
        confidence += 0.05
    
    # Factor 2: Has numbers (addresses usually have numbers)
    if re.search(r'\d', cleaned):
        confidence += 0.1
    
    # Factor 3: Has alphabetic content
    if re.search(r'[a-zA-Z]', cleaned):
        confidence += 0.1
    
    # Factor 4: Use rapidfuzz if available for similarity
    if RAPIDFUZZ_AVAILABLE:
        similarity = fuzz.ratio(raw.lower(), cleaned.lower()) / 100.0
        # Higher similarity = less aggressive cleaning = good
        if similarity > 0.8:
            confidence += 0.15
        elif similarity > 0.6:
            confidence += 0.1
    
    # Factor 5: Check for common address indicators
    address_indicators = [
        r'\b(road|street|avenue|lane|nagar|colony|sector|block|floor|apartment|building|house|plot)\b',
        r'\b(city|town|village|district|state|pin|pincode)\b',
        r'\b\d{6}\b',  # PIN code
    ]
    
    for pattern in address_indicators:
        if re.search(pattern, cleaned, re.IGNORECASE):
            confidence += 0.03
    
    # Apply strict mode penalty
    if strict:
        confidence *= 0.9
    
    # Clamp confidence to [0.0, 1.0]
    confidence = max(0.0, min(1.0, confidence))
    
    return round(confidence, 3)


def _extract_components(address: str) -> Dict[str, Optional[str]]:
    """
    Extract basic address components from cleaned text.
    
    Args:
        address: Cleaned address string
        
    Returns:
        Dictionary of extracted components
    """
    components = {
        "street": None,
        "city": None,
        "state": None,
        "pincode": None,
        "country": "India"  # Assume India by default
    }
    
    # Extract PIN code (6 digits)
    pincode_match = re.search(r'\b(\d{6})\b', address)
    if pincode_match:
        components["pincode"] = pincode_match.group(1)
    
    # Extract common Indian states
    indian_states = [
        'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Kerala', 'Gujarat',
        'Rajasthan', 'Uttar Pradesh', 'Madhya Pradesh', 'West Bengal',
        'Delhi', 'Telangana', 'Andhra Pradesh', 'Bihar', 'Haryana',
        'Punjab', 'Assam', 'Odisha', 'Jharkhand', 'Chattisgarh'
    ]
    
    for state in indian_states:
        if re.search(r'\b' + re.escape(state) + r'\b', address, re.IGNORECASE):
            components["state"] = state
            break
    
    # Simple city extraction (word before state or before PIN)
    # This is a basic heuristic
    if components["state"]:
        city_match = re.search(
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,?\s*' + re.escape(components["state"]),
            address
        )
        if city_match:
            components["city"] = city_match.group(1).strip()
    elif components["pincode"]:
        city_match = re.search(
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,?\s*\d{6}',
            address
        )
        if city_match:
            components["city"] = city_match.group(1).strip()
    
    return components
