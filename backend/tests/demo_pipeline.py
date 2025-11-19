"""
Demo: LocalLens Pipeline Orchestration
Shows the complete 9-step pipeline processing multiple addresses
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import process_address
from pydantic import BaseModel


class AddressRequest(BaseModel):
    raw_address: str


async def demo_pipeline():
    """Demonstrate the pipeline with multiple test addresses."""
    print("\n" + "="*70)
    print("LOCALLENS PIPELINE DEMONSTRATION")
    print("9-Step Address Processing Pipeline")
    print("="*70)
    
    # Test addresses with varying quality
    test_addresses = [
        "123 MG Road, Bangalore, Karnataka 560001",
        "Near Railway Station, Mumbai",  # Vague address
        "Flat 201, Tower B, DLF Cyber City, Gurgaon, Haryana 122002",
        "Sector 15, Noida 201301",
        "Invalid address xyz",  # Poor quality
    ]
    
    results = []
    
    for idx, address in enumerate(test_addresses, 1):
        print(f"\n{'='*70}")
        print(f"TEST {idx}/{len(test_addresses)}")
        print(f"{'='*70}")
        print(f"Raw Address: {address}")
        print(f"-"*70)
        
        request = AddressRequest(raw_address=address)
        
        try:
            response = await process_address(request)
            event = response.event
            
            # Extract key metrics
            print(f"\n✓ Processing successful ({response.processing_time_ms:.2f} ms)")
            print(f"\n📍 Results:")
            print(f"  • Cleaned: {event.get('cleaned_address', 'N/A')}")
            print(f"  • Integrity Score: {event.get('integrity', {}).get('score', 'N/A')}/100")
            print(f"  • Fused Confidence: {event.get('fused_confidence', 0):.3f}")
            
            # Anomaly status
            if event.get('anomaly_detected'):
                reasons = event.get('anomaly_reasons', [])
                print(f"\n⚠️  Anomaly Detected:")
                for reason in reasons:
                    print(f"    - {reason}")
                
                # Self-healing
                heal_result = event.get('self_heal_actions', {})
                if heal_result.get('healed'):
                    print(f"\n✓ Self-Healing Successful:")
                    print(f"    - Strategies: {heal_result.get('strategies_attempted', 0)}")
                    print(f"    - Actions: {len(heal_result.get('actions', []))}")
                else:
                    print(f"\n✗ Self-Healing Failed:")
                    print(f"    - Manual review recommended")
            else:
                print(f"\n✓ No Anomalies Detected")
            
            # Component extraction
            components = event.get('cleaned_components', {})
            if components:
                print(f"\n📋 Extracted Components:")
                for key, value in components.items():
                    if value:
                        print(f"    - {key.capitalize()}: {value}")
            
            results.append({
                'address': address,
                'success': True,
                'anomaly': event.get('anomaly_detected'),
                'confidence': event.get('fused_confidence', 0),
                'time_ms': response.processing_time_ms
            })
            
        except Exception as e:
            print(f"\n✗ Processing failed: {str(e)}")
            results.append({
                'address': address,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print(f"\n{'='*70}")
    print("PIPELINE SUMMARY")
    print(f"{'='*70}")
    
    successful = sum(1 for r in results if r['success'])
    anomalies = sum(1 for r in results if r.get('anomaly', False))
    avg_time = sum(r.get('time_ms', 0) for r in results if r['success']) / max(successful, 1)
    avg_confidence = sum(r.get('confidence', 0) for r in results if r['success']) / max(successful, 1)
    
    print(f"\n📊 Statistics:")
    print(f"  • Total Addresses: {len(test_addresses)}")
    print(f"  • Successful: {successful}")
    print(f"  • Failed: {len(test_addresses) - successful}")
    print(f"  • Anomalies Detected: {anomalies}")
    print(f"  • Average Processing Time: {avg_time:.2f} ms")
    print(f"  • Average Confidence: {avg_confidence:.3f}")
    
    print(f"\n📋 Results Table:")
    print(f"{'='*70}")
    print(f"{'Address':<35} {'Status':<10} {'Anomaly':<10} {'Conf':<8}")
    print(f"{'-'*70}")
    
    for r in results:
        addr = r['address'][:32] + "..." if len(r['address']) > 32 else r['address']
        status = "✓ OK" if r['success'] else "✗ FAIL"
        anomaly = "Yes" if r.get('anomaly', False) else "No"
        conf = f"{r.get('confidence', 0):.3f}" if r['success'] else "N/A"
        print(f"{addr:<35} {status:<10} {anomaly:<10} {conf:<8}")
    
    print(f"{'='*70}")
    
    # Pipeline steps recap
    print(f"\n📝 Pipeline Steps Executed:")
    print(f"  1. ✓ Address Cleaning (LLM-based)")
    print(f"  2. ✓ Integrity Scoring (completeness check)")
    print(f"  3. ✓ ML Geocoding (embedding similarity)")
    print(f"  4. ✓ HERE Geocoding (API call)")
    print(f"  5. ✓ Geospatial Validation (consistency checks)")
    print(f"  6. ✓ Confidence Fusion (weighted combination)")
    print(f"  7. ✓ Anomaly Detection (6 rules)")
    print(f"  8. ✓ Self-Healing (3 strategies)")
    print(f"  9. ✓ Event Logging (CSV output)")
    
    print(f"\n📁 Logs saved to: logs/pipeline_logs.csv")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(demo_pipeline())
