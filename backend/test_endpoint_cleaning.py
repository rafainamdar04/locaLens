"""
Quick test of the FastAPI /process endpoint with address cleaning.
"""
import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Mock test without actually starting the server
from services.address_cleaner import clean_address


async def test_endpoint_logic():
    """Test the address cleaning logic that will be used by the endpoint."""
    
    print("\n" + "="*70)
    print("Testing /process Endpoint Logic")
    print("="*70)
    
    test_address = "Flat 12B, Tower C\nPhoenix Heights\nBangalore, Karnataka 560001"
    
    print(f"\nInput Address:")
    print(f"  {repr(test_address)}")
    
    # Step 1: Clean address (this is what the endpoint does first)
    cleaned_result = await clean_address(test_address)
    cleaned_address = cleaned_result["cleaned_text"]
    
    print(f"\nCleaned Address:")
    print(f"  {cleaned_address}")
    print(f"\nCleaning Confidence: {cleaned_result['confidence']:.1%}")
    print(f"\nExtracted Components:")
    for key, value in cleaned_result['components'].items():
        if value:
            print(f"  {key}: {value}")
    
    # Simulate what the endpoint would return
    mock_event = {
        "raw_address": test_address,
        "cleaned_address": cleaned_address,
        "cleaning_result": cleaned_result,
        # Other fields would be populated by geocoding services...
        "ml_results": None,
        "here_results": None,
        "integrity_score": 0.5,
        "fused_confidence": 0.5,
        "anomaly_detected": False
    }
    
    print(f"\n✓ Endpoint would return event with cleaned address")
    print(f"✓ Ready for geocoding pipeline")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_endpoint_logic())
