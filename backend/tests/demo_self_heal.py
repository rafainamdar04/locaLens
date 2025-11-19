"""
Demonstration of Self-Healing Service
Shows realistic healing scenarios with detailed output.
"""

import sys
from pathlib import Path
import asyncio

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.self_heal import self_heal


def print_scenario(title: str, description: str):
    """Print scenario header."""
    print("\n" + "=" * 80)
    print(f"SCENARIO: {title}")
    print(f"Description: {description}")
    print("=" * 80)


def print_result(result: dict):
    """Print healing result details."""
    print(f"\n[RESULT]")
    print(f"  Healed: {result['healed']}")
    print(f"  Final Confidence: {result['confidence']:.3f}")
    print(f"  Strategies Attempted: {result['strategies_attempted']}")
    print(f"  Original Anomalies: {', '.join(result['original_reasons'])}")
    
    print(f"\n[ACTIONS]")
    for i, action in enumerate(result['actions'], 1):
        print(f"  Action {i}: {action['strategy']}")
        print(f"    Reason: {action['reason']}")
        print(f"    Success: {action['success']}")
        
        if action.get('note'):
            print(f"    Note: {action['note']}")
        
        if action.get('improved'):
            print(f"    Improved: Yes (gain: {action.get('confidence_gain', 0):.3f})")
        
        if action.get('reverse_match'):
            print(f"    Reverse Match: Yes")
        
        if action.get('pincode_validated'):
            print(f"    Pincode Validated: Yes")
        
        if action.get('error'):
            print(f"    Error: {action['error']}")
    
    print(f"\n[SUMMARY]")
    summary_lines = result['summary'].split('\n')
    for line in summary_lines[:10]:  # Show first 10 lines
        print(f"  {line}")
    if len(summary_lines) > 10:
        print(f"  ... ({len(summary_lines) - 10} more lines)")


async def scenario_1_low_integrity():
    """Scenario 1: Low data integrity - needs strict cleaning."""
    print_scenario(
        "Low Data Integrity",
        "Messy address with whitespace issues and low integrity score"
    )
    
    raw = "  123   MAIN    STREET   mumbai   maharashtra  400001  "
    cleaned = "123 MAIN STREET mumbai maharashtra 400001"
    ml_candidates = {
        "top_result": {"address": "123 Main St, Mumbai 400001"},
        "confidence": 0.55
    }
    here_resp = None
    reasons = ["low_integrity"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    print_result(result)


async def scenario_2_geographic_mismatch():
    """Scenario 2: ML and HERE results differ significantly."""
    print_scenario(
        "Geographic Mismatch",
        "ML and HERE geocoding results point to different locations"
    )
    
    raw = "Andheri Station Road, Mumbai"
    cleaned = "Andheri Station Road Mumbai"
    ml_candidates = {
        "top_result": {
            "address": "Andheri East, Mumbai",
            "coordinates": {"lat": 19.1197, "lon": 72.8464},
            "city": "Mumbai",
            "state": "Maharashtra"
        },
        "confidence": 0.82
    }
    here_resp = {
        "primary_result": {
            "address": "Andheri West, Mumbai",
            "coordinates": {"lat": 19.1357, "lon": 72.8267}
        },
        "confidence": 0.78
    }
    reasons = ["ml_here_mismatch"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    print_result(result)


async def scenario_3_pincode_problem():
    """Scenario 3: Pincode validation failed."""
    print_scenario(
        "Pincode Validation Failure",
        "Geocoding result has wrong pincode for the location"
    )
    
    raw = "Sector 5, Vashi, Navi Mumbai 400703"
    cleaned = "Sector 5 Vashi Navi Mumbai 400703"
    ml_candidates = {
        "top_result": {
            "address": "Sector 5, Vashi",
            "city": "Navi Mumbai",
            "state": "Maharashtra",
            "pincode": "400001"  # Wrong pincode
        },
        "confidence": 0.75
    }
    here_resp = {
        "primary_result": {
            "address": "Vashi, Navi Mumbai"
        },
        "confidence": 0.68
    }
    reasons = ["pincode_mismatch"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    print_result(result)


async def scenario_4_multiple_problems():
    """Scenario 4: Multiple anomalies requiring all healing strategies."""
    print_scenario(
        "Multiple Critical Issues",
        "Low integrity, geographic mismatch, and pincode validation failure"
    )
    
    raw = "  sector  15   noida   201301  "
    cleaned = "sector 15 noida 201301"
    ml_candidates = {
        "top_result": {
            "address": "Sector 15, Noida",
            "coordinates": {"lat": 28.5833, "lon": 77.3167},
            "city": "Noida",
            "state": "Uttar Pradesh",
            "pincode": "110001"  # Wrong pincode
        },
        "confidence": 0.48
    }
    here_resp = {
        "primary_result": {
            "address": "Different Location, Noida",
            "coordinates": {"lat": 28.6000, "lon": 77.3500}
        },
        "confidence": 0.42
    }
    reasons = ["low_integrity", "ml_here_mismatch", "pincode_mismatch", "low_here_conf"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    print_result(result)


async def scenario_5_no_anomalies():
    """Scenario 5: Clean result with no healing needed."""
    print_scenario(
        "Clean Result - No Healing Needed",
        "High confidence results with no anomalies detected"
    )
    
    raw = "Connaught Place, New Delhi 110001"
    cleaned = "Connaught Place New Delhi 110001"
    ml_candidates = {
        "top_result": {
            "address": "Connaught Place, New Delhi 110001",
            "coordinates": {"lat": 28.6315, "lon": 77.2167}
        },
        "confidence": 0.95
    }
    here_resp = {
        "primary_result": {
            "address": "Connaught Place, New Delhi",
            "coordinates": {"lat": 28.6310, "lon": 77.2170}
        },
        "confidence": 0.93
    }
    reasons = []  # No anomalies
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    print_result(result)


async def scenario_6_missing_data():
    """Scenario 6: Healing with incomplete geocoding data."""
    print_scenario(
        "Missing Geocoding Data",
        "HERE geocoding failed, only ML results available"
    )
    
    raw = "  obscure  locality   mumbai  "
    cleaned = "obscure locality mumbai"
    ml_candidates = {
        "top_result": {
            "address": "Unknown Location, Mumbai",
            "city": "Mumbai",
            "state": "Maharashtra"
        },
        "confidence": 0.35
    }
    here_resp = None  # HERE geocoding failed
    reasons = ["low_integrity", "low_here_conf", "low_fused_conf"]
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    print_result(result)


async def scenario_7_performance_issue():
    """Scenario 7: High latency but good results."""
    print_scenario(
        "Performance Issue Only",
        "High processing latency but otherwise good geocoding results"
    )
    
    raw = "Bandra Kurla Complex, Mumbai 400051"
    cleaned = "Bandra Kurla Complex Mumbai 400051"
    ml_candidates = {
        "top_result": {
            "address": "BKC, Mumbai",
            "coordinates": {"lat": 19.0653, "lon": 72.8701}
        },
        "confidence": 0.88
    }
    here_resp = {
        "primary_result": {
            "address": "Bandra Kurla Complex, Mumbai"
        },
        "confidence": 0.85
    }
    reasons = ["high_latency"]  # Only performance issue
    
    result = await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)
    print_result(result)


async def main():
    """Run all demonstration scenarios."""
    print("\n" + "#" * 80)
    print("# SELF-HEALING SERVICE DEMONSTRATION")
    print("# Intelligent recovery from geocoding anomalies")
    print("#" * 80)
    
    await scenario_1_low_integrity()
    await scenario_2_geographic_mismatch()
    await scenario_3_pincode_problem()
    await scenario_4_multiple_problems()
    await scenario_5_no_anomalies()
    await scenario_6_missing_data()
    await scenario_7_performance_issue()
    
    print("\n" + "#" * 80)
    print("# DEMONSTRATION COMPLETE")
    print("#" * 80)
    print("\nKey Features Demonstrated:")
    print("  ✓ Strategy 1: Strict re-cleaning for low integrity")
    print("  ✓ Strategy 2: Reverse geocoding for ML-HERE mismatch")
    print("  ✓ Strategy 3: Structured queries for pincode validation")
    print("  ✓ Multiple strategies working together")
    print("  ✓ Comprehensive action logging")
    print("  ✓ Human-readable healing summaries")
    print("  ✓ Graceful handling of missing data")
    print("\nImplementation Status: COMPLETE")


if __name__ == "__main__":
    asyncio.run(main())
