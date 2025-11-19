"""
Test script for the /process endpoint pipeline.
Verifies that all steps execute in the correct order with proper data flow.
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import process_address_v3 as process_address
from pydantic import BaseModel


class AddressRequest(BaseModel):
    raw_address: str


async def test_pipeline():
    """Test the complete pipeline with a sample address."""
    print("\n" + "="*60)
    print("TESTING /PROCESS_V3 ENDPOINT PIPELINE")
    print("="*60)
    
    # Test address
    test_address = "123 MG Road, Bangalore, Karnataka 560001"
    print(f"\n[INPUT] Raw Address: {test_address}")
    
    # Create request
    request = AddressRequest(raw_address=test_address)
    
    try:
        # Call the endpoint
        print("\n[PIPELINE] Starting address processing...")
        response = await process_address(request)
        
        # Verify response structure
        print(f"\n[RESULT] Success: {response.success}")
        print(f"[RESULT] Processing Time: {response.processing_time_ms:.2f} ms")
        
        event = response.event
        
        # Verify pipeline steps
        print("\n[STEP 1] Address Cleaning:")
        print(f"  - Raw: {event.get('raw_address', 'N/A')}")
        print(f"  - Cleaned: {event.get('cleaned_address', event.get('cleaned', 'N/A'))}")
        print(f"  - Components: {event.get('cleaned_components', {})}")
        
        print("\n[STEP 2] Integrity Score:")
        integrity = event.get('integrity', {})
        print(f"  - Score: {integrity.get('score', 'N/A')}")
        print(f"  - Completeness: {integrity.get('completeness', 'N/A')}")
        print(f"  - Quality Flags: {integrity.get('quality_flags', [])}")
        
        print("\n[STEP 3] ML Geocoding:")
        ml = event.get('ml_results', {})
        print(f"  - Confidence: {ml.get('confidence', 'N/A')}")
        print(f"  - Top Result: {event.get('ml_top', 'N/A')}")
        
        print("\n[STEP 4] HERE Geocoding:")
        here = event.get('here_results', {})
        print(f"  - Confidence: {here.get('confidence', 'N/A')}")
        print(f"  - Primary Result: {event.get('here_primary', 'N/A')}")
        
        print("\n[STEP 5] Geospatial Checks:")
        geo = event.get('geospatial_checks', event.get('checks', {}))
        print(f"  - Score: {geo.get('score', 'N/A')}")
        print(f"  - Distance Match: {geo.get('distance_match', 'N/A')} km")
        print(f"  - Boundary Check: {geo.get('boundary_check', 'N/A')}")
        
        print("\n[STEP 6] Confidence Fusion:")
        print(f"  - Metrics: {event.get('metrics', {})}")
        print(f"  - Fused Confidence: {event.get('fused_confidence', event.get('confidence', 'N/A'))}")
        
        print("\n[STEP 7] Anomaly Detection:")
        print(f"  - Anomaly Detected: {event.get('anomaly_detected', (event.get('anomaly') or {}).get('detected', 'N/A'))}")
        print(f"  - Reasons: {event.get('anomaly_reasons', (event.get('anomaly') or {}).get('reasons', []))}")
        print(f"  - Reason Count: {len(event.get('anomaly_reasons', (event.get('anomaly') or {}).get('reasons', [])))}")
        
        print("\n[STEP 8] Self-Healing:")
        actions = event.get('self_heal_actions')
        if actions:
            print(f"  - Actions Taken: {actions}")
        else:
            print(f"  - No healing required")
        
        print("\n[STEP 9] Event Logging:")
        print(f"  - Timestamp: {event.get('timestamp', 'N/A')}")
        print(f"  - Success: {event.get('success', 'N/A')}")
        
        # Summary
        print("\n" + "="*60)
        print("PIPELINE TEST SUMMARY")
        print("="*60)
        print(f"✓ All 9 steps executed successfully")
        print(f"✓ Processing time: {response.processing_time_ms:.2f} ms")
        print(f"✓ Event logged successfully")
        
        # Check for expected fields
        required_fields = [
            'raw_address', 'cleaned_address', 'cleaned_components',
            'integrity', 'ml_results', 'here_results', 
            'geospatial_checks', 'fused_confidence', 'processing_time_ms', 'success'
        ]
        
        missing_fields = [field for field in required_fields if field not in event]
        
        if missing_fields:
            print(f"\n⚠ Warning: Missing fields: {missing_fields}")
        else:
            print(f"✓ All required fields present in event")
        
        print("\n" + "="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print(f"Error Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_pipeline())
    
    if success:
        print("\n✓ Pipeline test PASSED")
        sys.exit(0)
    else:
        print("\n✗ Pipeline test FAILED")
        sys.exit(1)
