"""
Documentation for the clean_address function.

USAGE EXAMPLES:
===============

1. Basic Usage (Deterministic Fallback):
```python
from services.address_cleaner import clean_address

result = await clean_address("123  main  st\nmumbai 400001")

# Returns:
{
    "cleaned_text": "123 Main Street Mumbai 400001",
    "components": {
        "street": None,
        "city": "Mumbai",
        "state": None,
        "pincode": "400001",
        "country": "India"
    },
    "confidence": 0.91
}
```

2. With LLM (if OPENROUTER_API_KEY or OPENAI_API_KEY is set in .env):
```python
result = await clean_address("flat 12b tower-c\nphoenix heights bangalore")

# LLM will normalize the address more intelligently:
{
    "cleaned_text": "Flat 12B, Tower C, Phoenix Heights, Bangalore",
    "components": {...},
    "confidence": 0.95
}
```

3. Strict Mode:
```python
result = await clean_address("messy address", strict=True)
# Applies stricter validation and lower confidence scores
```

FEATURES:
=========

Deterministic Fallback (when no OpenAI key):
- Strips extra whitespace
- Removes newlines and converts to single line
- Collapses multiple spaces
- Cleans up excessive punctuation
- Standardizes common abbreviations (Rd→Road, St→Street, etc.)
- Title cases for readability
- Extracts PIN codes (6-digit Indian postal codes)
- Identifies Indian states
- Computes confidence based on multiple heuristics

LLM Integration (when OpenRouter or OpenAI API key configured):
- Uses GPT-3.5-turbo for intelligent normalization
- Fixes typos and spelling errors
- Properly formats addresses
- Better handling of complex address structures
- Falls back to deterministic if API call fails

Confidence Scoring:
- Based on address length, presence of numbers, alphabetic content
- Uses rapidfuzz similarity if available
- Checks for common address indicators (road, street, city, pin, etc.)
- Strict mode applies 0.9x penalty

CONFIGURATION:
==============

To enable LLM-based cleaning, add to .env:
```
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here
```
or
```
OPENAI_API_KEY=sk-your-openai-key-here
```

To use deterministic only (no API calls):
```
OPENROUTER_API_KEY=
OPENAI_API_KEY=
```

RETURN FORMAT:
==============

{
    "cleaned_text": str,      # Single-line normalized address
    "components": {            # Extracted address components
        "street": str | None,
        "city": str | None,
        "state": str | None,
        "pincode": str | None,
        "country": str          # Always "India"
    },
    "confidence": float        # 0.0 to 1.0
}
"""

# This file serves as documentation only
pass
