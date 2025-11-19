"""
Demonstration of address cleaning capabilities.
Shows both deterministic and OpenAI-based cleaning.
"""
import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.address_cleaner import clean_address


async def demo():
    """Demonstrate address cleaning."""
    
    print("\n" + "="*70)
    print("Address Cleaner Demo")
    print("="*70)
    
    # Example addresses with various issues
    examples = [
        "flat  301    tower-b\ngreen valley\nmumbai MH\n400001",
        "Plot#45, Sector 22, Gurgaon, Haryana - 122001",
        "12 brigade rd bangalore 560001",
        "H.No. 123, Street 5, Vikas Nagar, Delhi - 110001"
    ]
    
    for i, address in enumerate(examples, 1):
        print(f"\n{'-'*70}")
        print(f"Example {i}:")
        print(f"{'-'*70}")
        print("Original:")
        print(f"  {repr(address)}")
        
        result = await clean_address(address)
        
        print("\nCleaned:")
        print(f"  {result['cleaned_text']}")
        print(f"\nConfidence: {result['confidence']:.1%}")
        
        if result['components']['city']:
            print(f"City: {result['components']['city']}")
        if result['components']['state']:
            print(f"State: {result['components']['state']}")
        if result['components']['pincode']:
            print(f"PIN: {result['components']['pincode']}")
    
    print("\n" + "="*70)
    print("Demo complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(demo())
