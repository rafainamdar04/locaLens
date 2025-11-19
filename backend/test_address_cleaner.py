"""Test script for address_cleaner service."""
import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.address_cleaner import clean_address


async def test_address_cleaner():
    """Test the address cleaner with various inputs."""
    
    print("=" * 70)
    print("Testing Address Cleaner")
    print("=" * 70)
    
    test_cases = [
        # Test 1: Simple address with extra whitespace
        {
            "name": "Extra Whitespace",
            "input": "  123   Main   St,    Mumbai,    Maharashtra   400001  ",
            "strict": False
        },
        # Test 2: Multi-line address
        {
            "name": "Multi-line Address",
            "input": "Flat 301, Tower B\nGreen Valley Apartments\nBangalore, Karnataka\n560001",
            "strict": False
        },
        # Test 3: Address with abbreviations
        {
            "name": "Abbreviations",
            "input": "45 MG Rd, Apt 12B, Blvd Area, DL 110001",
            "strict": False
        },
        # Test 4: Messy punctuation
        {
            "name": "Messy Punctuation",
            "input": "Plot#456,,,Sector-22,,,Gurgaon!!!Haryana---122001",
            "strict": False
        },
        # Test 5: Simple address (strict mode)
        {
            "name": "Strict Mode",
            "input": "12 Brigade Road, Bangalore 560001",
            "strict": True
        },
        # Test 6: Empty string
        {
            "name": "Empty String",
            "input": "   ",
            "strict": False
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*70}")
        print(f"Input (strict={test['strict']}):")
        print(f"  '{test['input']}'")
        
        result = await clean_address(test['input'], strict=test['strict'])
        
        print(f"\nCleaned Text:")
        print(f"  '{result['cleaned_text']}'")
        print(f"\nConfidence: {result['confidence']:.3f}")
        print(f"\nComponents:")
        for key, value in result['components'].items():
            if value:
                print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)


async def test_openai_if_available():
    """Test OpenAI integration if API key is configured."""
    from config import settings
    
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "":
        print("\nℹ️  OpenAI API key not configured - skipping OpenAI test")
        print("   (Tests above used deterministic fallback)")
        return
    
    print("\n" + "=" * 70)
    print("Testing OpenAI Integration")
    print("=" * 70)
    
    test_input = "flat no 12b, tower-c, phoenix   heights\nbangalore karnataka\n560078"
    print(f"\nInput:")
    print(f"  '{test_input}'")
    
    result = await clean_address(test_input)
    
    print(f"\nCleaned (via OpenAI):")
    print(f"  '{result['cleaned_text']}'")
    print(f"\nConfidence: {result['confidence']:.3f}")
    print(f"\nComponents:")
    for key, value in result['components'].items():
        if value:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(test_address_cleaner())
    asyncio.run(test_openai_if_available())
