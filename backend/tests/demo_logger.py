"""
Demonstration of Event Logging
Shows CSV logging with various event types.
"""

import sys
from pathlib import Path
import asyncio
import csv

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from utils.logger import log_event, get_log_stats, CSV_LOG_FILE


async def demo_clean_result():
    """Demo: Clean result with no anomalies."""
    print("\n" + "=" * 70)
    print("DEMO 1: Clean Result - No Anomalies")
    print("=" * 70)
    
    event = {
        "timestamp": 1700000000.0,
        "raw_address": "123 Brigade Road, Bangalore 560001",
        "cleaned_address": "123 Brigade Road Bangalore 560001",
        "integrity_score": 0.95,
        "fused_confidence": 0.92,
        "ml_results": {
            "confidence": 0.93,
            "latency_ms": 245.3
        },
        "here_results": {
            "confidence": 0.90,
            "latency_ms": 312.5
        },
        "geospatial_results": {
            "distance_match": 0.5
        },
        "anomaly_details": {
            "reasons": []
        },
        "self_heal_result": {
            "actions": []
        },
        "cleaning_result": {
            "latency_ms": 175.8
        },
        "processing_time_ms": 895.2
    }
    
    await log_event(event)
    print("✓ Logged clean result")
    print(f"  Integrity: {event['integrity_score']}")
    print(f"  Confidence: {event['fused_confidence']}")
    print(f"  Processing Time: {event['processing_time_ms']} ms")


async def demo_anomaly_detected():
    """Demo: Anomalies detected - low confidence."""
    print("\n" + "=" * 70)
    print("DEMO 2: Anomalies Detected - Low Confidence")
    print("=" * 70)
    
    event = {
        "timestamp": 1700000001.0,
        "raw_address": "Obscure locality near station",
        "cleaned_address": "Obscure locality near station",
        "integrity_score": 0.42,
        "fused_confidence": 0.38,
        "ml_results": {
            "confidence": 0.45,
            "latency_ms": 280.5
        },
        "here_results": {
            "confidence": 0.32,
            "latency_ms": 425.8
        },
        "geospatial_results": {
            "distance_match": 2.1
        },
        "anomaly_details": {
            "reasons": ["low_fused_conf", "low_integrity", "low_here_conf"]
        },
        "self_heal_result": {
            "actions": []
        },
        "cleaning_result": {
            "latency_ms": 195.2
        },
        "processing_time_ms": 1250.8
    }
    
    await log_event(event)
    print("✓ Logged anomalous result")
    print(f"  Anomalies: {', '.join(event['anomaly_details']['reasons'])}")
    print(f"  Integrity: {event['integrity_score']}")
    print(f"  Confidence: {event['fused_confidence']}")


async def demo_with_healing():
    """Demo: Anomalies with self-healing actions."""
    print("\n" + "=" * 70)
    print("DEMO 3: Anomalies with Self-Healing")
    print("=" * 70)
    
    event = {
        "timestamp": 1700000002.0,
        "raw_address": "  sector   15    noida  201301  ",
        "cleaned_address": "sector 15 noida 201301",
        "integrity_score": 0.38,
        "fused_confidence": 0.52,
        "ml_results": {
            "confidence": 0.58,
            "latency_ms": 265.3
        },
        "here_results": {
            "confidence": 0.48,
            "latency_ms": 385.2
        },
        "geospatial_results": {
            "distance_match": 1.8
        },
        "anomaly_details": {
            "reasons": ["low_integrity"]
        },
        "self_heal_result": {
            "actions": [
                {
                    "strategy": "strict_recleaning",
                    "success": True,
                    "reason": "low_integrity",
                    "improved": True,
                    "confidence_gain": 0.15
                }
            ]
        },
        "cleaning_result": {
            "latency_ms": 220.5
        },
        "processing_time_ms": 1520.3
    }
    
    await log_event(event)
    print("✓ Logged result with healing")
    print(f"  Original Integrity: {event['integrity_score']}")
    print(f"  Healing Actions: {len(event['self_heal_result']['actions'])}")
    print(f"  Strategy: {event['self_heal_result']['actions'][0]['strategy']}")
    print(f"  Success: {event['self_heal_result']['actions'][0]['success']}")


async def demo_geographic_mismatch():
    """Demo: Geographic mismatch between ML and HERE."""
    print("\n" + "=" * 70)
    print("DEMO 4: Geographic Mismatch")
    print("=" * 70)
    
    event = {
        "timestamp": 1700000003.0,
        "raw_address": "Andheri Station Road, Mumbai",
        "cleaned_address": "Andheri Station Road Mumbai",
        "integrity_score": 0.78,
        "fused_confidence": 0.65,
        "ml_results": {
            "confidence": 0.82,
            "latency_ms": 255.8
        },
        "here_results": {
            "confidence": 0.75,
            "latency_ms": 342.5
        },
        "geospatial_results": {
            "distance_match": 8.5  # 8.5 km mismatch
        },
        "anomaly_details": {
            "reasons": ["ml_here_mismatch"]
        },
        "self_heal_result": {
            "actions": [
                {
                    "strategy": "reverse_geocode_reconciliation",
                    "success": True,
                    "reason": "ml_here_mismatch",
                    "reverse_match": False
                }
            ]
        },
        "cleaning_result": {
            "latency_ms": 182.3
        },
        "processing_time_ms": 1180.5
    }
    
    await log_event(event)
    print("✓ Logged geographic mismatch")
    print(f"  Mismatch Distance: {event['geospatial_results']['distance_match']} km")
    print(f"  ML Confidence: {event['ml_results']['confidence']}")
    print(f"  HERE Confidence: {event['here_results']['confidence']}")


async def demo_high_latency():
    """Demo: High latency but good results."""
    print("\n" + "=" * 70)
    print("DEMO 5: High Latency Performance Issue")
    print("=" * 70)
    
    event = {
        "timestamp": 1700000004.0,
        "raw_address": "Connaught Place, New Delhi 110001",
        "cleaned_address": "Connaught Place New Delhi 110001",
        "integrity_score": 0.92,
        "fused_confidence": 0.88,
        "ml_results": {
            "confidence": 0.90,
            "latency_ms": 850.5  # High
        },
        "here_results": {
            "confidence": 0.86,
            "latency_ms": 920.8  # High
        },
        "geospatial_results": {
            "distance_match": 0.8
        },
        "anomaly_details": {
            "reasons": ["high_latency"]
        },
        "self_heal_result": {
            "actions": []
        },
        "cleaning_result": {
            "latency_ms": 450.2  # High
        },
        "processing_time_ms": 2850.5  # High total
    }
    
    await log_event(event)
    print("✓ Logged high latency event")
    print(f"  LLM Latency: {event['cleaning_result']['latency_ms']} ms")
    print(f"  ML Latency: {event['ml_results']['latency_ms']} ms")
    print(f"  HERE Latency: {event['here_results']['latency_ms']} ms")
    print(f"  Total: {event['processing_time_ms']} ms")


async def demo_pincode_issue():
    """Demo: Pincode validation failure."""
    print("\n" + "=" * 70)
    print("DEMO 6: Pincode Validation Failure")
    print("=" * 70)
    
    event = {
        "timestamp": 1700000005.0,
        "raw_address": "Sector 5, Vashi, Navi Mumbai 400703",
        "cleaned_address": "Sector 5 Vashi Navi Mumbai 400703",
        "integrity_score": 0.75,
        "fused_confidence": 0.68,
        "ml_results": {
            "confidence": 0.72,
            "latency_ms": 268.5
        },
        "here_results": {
            "confidence": 0.65,
            "latency_ms": 358.2
        },
        "geospatial_results": {
            "distance_match": 2.3
        },
        "anomaly_details": {
            "reasons": ["pincode_mismatch"]
        },
        "self_heal_result": {
            "actions": [
                {
                    "strategy": "pincode_fallback_query",
                    "success": True,
                    "reason": "pincode_mismatch",
                    "pincode_validated": True
                }
            ]
        },
        "cleaning_result": {
            "latency_ms": 195.8
        },
        "processing_time_ms": 1285.3
    }
    
    await log_event(event)
    print("✓ Logged pincode mismatch")
    print(f"  Anomaly: pincode_mismatch")
    print(f"  Healing Strategy: pincode_fallback_query")
    print(f"  Validated: True")


async def show_log_preview():
    """Show preview of logged events."""
    print("\n" + "=" * 70)
    print("LOG FILE PREVIEW")
    print("=" * 70)
    
    if not CSV_LOG_FILE.exists():
        print("No log file found")
        return
    
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"\nTotal Events: {len(rows)}")
    print(f"Log File: {CSV_LOG_FILE}")
    
    print("\nFirst 3 Events:")
    for i, row in enumerate(rows[:3], 1):
        print(f"\n  Event {i}:")
        print(f"    Timestamp: {row['timestamp']}")
        print(f"    Address: {row['raw'][:50]}...")
        print(f"    Confidence: {row['fused_confidence']}")
        print(f"    Anomalies: {row['anomaly_reasons']}")
        print(f"    Processing: {row['processing_time_ms']} ms")


async def show_statistics():
    """Show log statistics."""
    print("\n" + "=" * 70)
    print("LOG STATISTICS")
    print("=" * 70)
    
    stats = get_log_stats()
    
    if "error" in stats:
        print(f"Error: {stats['error']}")
        return
    
    print(f"\nTotal Events: {stats['total_events']}")
    print(f"File Size: {stats['file_size_kb']} KB")
    print(f"First Event: {stats.get('first_event', 'N/A')}")
    print(f"Last Event: {stats.get('last_event', 'N/A')}")
    print(f"\nPerformance:")
    print(f"  Average Processing Time: {stats['avg_processing_time_ms']} ms")
    print(f"\nQuality:")
    print(f"  Anomaly Count: {stats['anomaly_count']}")
    print(f"  Anomaly Rate: {stats['anomaly_rate_percent']}%")


async def main():
    """Run all demonstrations."""
    print("\n" + "#" * 70)
    print("# EVENT LOGGING DEMONSTRATION")
    print("# Comprehensive pipeline logging to CSV")
    print("#" * 70)
    
    # Clear existing log for clean demo
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
        print("\nCleared existing log file for demo")
    
    # Run demos
    await demo_clean_result()
    await demo_anomaly_detected()
    await demo_with_healing()
    await demo_geographic_mismatch()
    await demo_high_latency()
    await demo_pincode_issue()
    
    # Show results
    await show_log_preview()
    await show_statistics()
    
    print("\n" + "#" * 70)
    print("# DEMONSTRATION COMPLETE")
    print("#" * 70)
    print("\nKey Features:")
    print("  ✓ CSV format with 14 standardized headers")
    print("  ✓ Automatic file creation with headers")
    print("  ✓ JSON encoding for complex fields")
    print("  ✓ Timestamp formatting (YYYY-MM-DD HH:MM:SS)")
    print("  ✓ Latency tracking (LLM, ML, HERE, Total)")
    print("  ✓ Anomaly reason logging")
    print("  ✓ Healing action logging")
    print("  ✓ Thread-safe with async lock")
    print("  ✓ Statistics function for analysis")
    print("  ✓ Graceful error handling with fallback")
    print(f"\nLog file location: {CSV_LOG_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
