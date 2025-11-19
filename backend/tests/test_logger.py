"""
Test suite for event logging utility.
Tests CSV logging, header creation, and statistics.
"""

import sys
from pathlib import Path
import asyncio
import csv
import json

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from utils.logger import log_event, get_log_stats, CSV_LOG_FILE, CSV_HEADERS


async def test_create_log_file():
    """Test that log file is created with headers."""
    print("\n[TEST 1] Create Log File with Headers")
    
    # Delete log file if exists
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
    
    # Create a test event
    event = {
        "timestamp": 1700000000.0,
        "raw_address": "123 Main St",
        "cleaned_address": "123 Main St",
        "integrity_score": 0.85,
        "fused_confidence": 0.78,
        "ml_results": {"confidence": 0.82},
        "here_results": {"confidence": 0.75},
        "geospatial_results": {"distance_match": 1.5},
        "anomaly_details": {"reasons": []},
        "self_heal_result": {"actions": []},
        "processing_time_ms": 850.5
    }
    
    # Log event
    await log_event(event)
    
    # Check file exists
    assert CSV_LOG_FILE.exists(), "Log file should exist"
    
    # Read and verify headers
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
    
    print(f"  Headers: {headers}")
    assert headers == CSV_HEADERS, "Headers should match CSV_HEADERS"
    print("  ✓ PASS")


async def test_log_single_event():
    """Test logging a single event."""
    print("\n[TEST 2] Log Single Event")
    
    # Delete log file
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
    
    event = {
        "timestamp": 1700000000.0,
        "raw_address": "123 Test Street, Mumbai 400001",
        "cleaned_address": "123 Test Street Mumbai 400001",
        "integrity_score": 0.92,
        "fused_confidence": 0.88,
        "ml_results": {"confidence": 0.90, "latency_ms": 250.5},
        "here_results": {"confidence": 0.85, "latency_ms": 320.8},
        "geospatial_results": {"distance_match": 0.8},
        "anomaly_details": {"reasons": []},
        "self_heal_result": {"actions": []},
        "cleaning_result": {"latency_ms": 180.2},
        "processing_time_ms": 950.3
    }
    
    await log_event(event)
    
    # Read and verify
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 1, "Should have 1 row"
    row = rows[0]
    
    print(f"  Raw: {row['raw']}")
    print(f"  Cleaned: {row['cleaned']}")
    print(f"  Integrity: {row['integrity_score']}")
    print(f"  Fused Confidence: {row['fused_confidence']}")
    print(f"  Processing Time: {row['processing_time_ms']} ms")
    
    assert row['raw'] == "X Test Street, Mumbai XXXXXX"
    assert row['cleaned'] == "X Test Street Mumbai XXXXXX"
    assert float(row['integrity_score']) == 0.92
    assert float(row['fused_confidence']) == 0.88
    print("  ✓ PASS")


async def test_log_with_anomalies():
    """Test logging event with anomalies."""
    print("\n[TEST 3] Log Event with Anomalies")
    
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
    
    event = {
        "timestamp": 1700000000.0,
        "raw_address": "Messy address",
        "cleaned_address": "Messy address",
        "integrity_score": 0.35,
        "fused_confidence": 0.42,
        "ml_results": {"confidence": 0.55},
        "here_results": {"confidence": 0.38},
        "geospatial_results": {"distance_match": 8.5},
        "anomaly_details": {
            "reasons": ["low_integrity", "ml_here_mismatch", "low_here_conf"]
        },
        "self_heal_result": {"actions": []},
        "processing_time_ms": 1200.0
    }
    
    await log_event(event)
    
    # Read and verify
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    row = rows[0]
    anomaly_reasons = json.loads(row['anomaly_reasons'])
    
    print(f"  Anomaly Reasons: {anomaly_reasons}")
    print(f"  Mismatch: {row['mismatch_km']} km")
    
    assert len(anomaly_reasons) == 3
    assert "low_integrity" in anomaly_reasons
    assert "ml_here_mismatch" in anomaly_reasons
    assert float(row['mismatch_km']) == 8.5
    print("  ✓ PASS")


async def test_log_with_healing_actions():
    """Test logging event with self-healing actions."""
    print("\n[TEST 4] Log Event with Healing Actions")
    
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
    
    event = {
        "timestamp": 1700000000.0,
        "raw_address": "Address",
        "cleaned_address": "Address",
        "integrity_score": 0.50,
        "fused_confidence": 0.55,
        "ml_results": {"confidence": 0.60},
        "here_results": {"confidence": 0.50},
        "geospatial_results": {"distance_match": 2.0},
        "anomaly_details": {"reasons": ["low_integrity"]},
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
        "processing_time_ms": 1500.0
    }
    
    await log_event(event)
    
    # Read and verify
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    row = rows[0]
    actions = json.loads(row['actions'])
    
    print(f"  Actions: {actions}")
    
    assert len(actions) == 1
    assert actions[0]['strategy'] == 'strict_recleaning'
    assert actions[0]['success'] == True
    print("  ✓ PASS")


async def test_multiple_events():
    """Test logging multiple events."""
    print("\n[TEST 5] Log Multiple Events")
    
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
    
    # Log 5 events
    for i in range(5):
        event = {
            "timestamp": 1700000000.0 + i,
            "raw_address": f"Address {i}",
            "cleaned_address": f"Address {i}",
            "integrity_score": 0.8 + (i * 0.02),
            "fused_confidence": 0.75 + (i * 0.03),
            "ml_results": {"confidence": 0.8},
            "here_results": {"confidence": 0.75},
            "geospatial_results": {"distance_match": 1.0},
            "anomaly_details": {"reasons": []},
            "self_heal_result": {"actions": []},
            "processing_time_ms": 800.0 + (i * 10)
        }
        await log_event(event)
    
    # Read and verify
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"  Total rows: {len(rows)}")
    assert len(rows) == 5
    
    # Check values are different
    print(f"  First address: {rows[0]['raw']}")
    print(f"  Last address: {rows[4]['raw']}")
    assert rows[0]['raw'] == "Address X"
    assert rows[4]['raw'] == "Address X"
    print("  ✓ PASS")


async def test_latency_tracking():
    """Test that latencies are logged correctly."""
    print("\n[TEST 6] Latency Tracking")
    
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
    
    event = {
        "timestamp": 1700000000.0,
        "raw_address": "Test",
        "cleaned_address": "Test",
        "integrity_score": 0.85,
        "fused_confidence": 0.80,
        "ml_results": {"confidence": 0.82, "latency_ms": 250.5},
        "here_results": {"confidence": 0.78, "latency_ms": 320.8},
        "geospatial_results": {"distance_match": 1.0},
        "anomaly_details": {"reasons": []},
        "self_heal_result": {"actions": []},
        "cleaning_result": {"latency_ms": 180.2},
        "processing_time_ms": 950.3
    }
    
    await log_event(event)
    
    # Read and verify
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    row = rows[0]
    
    print(f"  LLM Latency: {row['llm_latency_ms']} ms")
    print(f"  ML Latency: {row['ml_latency_ms']} ms")
    print(f"  HERE Latency: {row['here_latency_ms']} ms")
    print(f"  Total: {row['processing_time_ms']} ms")
    
    assert float(row['llm_latency_ms']) == 180.2
    assert float(row['ml_latency_ms']) == 250.5
    assert float(row['here_latency_ms']) == 320.8
    assert float(row['processing_time_ms']) == 950.3
    print("  ✓ PASS")


async def test_missing_fields():
    """Test logging with missing optional fields."""
    print("\n[TEST 7] Missing Fields Handling")
    
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
    
    # Minimal event with missing fields
    event = {
        "timestamp": 1700000000.0,
        "raw_address": "Minimal",
        "cleaned_address": "Minimal"
    }
    
    await log_event(event)
    
    # Read and verify - should have defaults
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    row = rows[0]
    
    print(f"  Integrity (default): {row['integrity_score']}")
    print(f"  Confidence (default): {row['fused_confidence']}")
    print(f"  Anomalies (default): {row['anomaly_reasons']}")
    
    assert float(row['integrity_score']) == 0.0
    assert float(row['fused_confidence']) == 0.0
    assert row['anomaly_reasons'] == "[]"
    print("  ✓ PASS")


async def test_log_stats():
    """Test log statistics function."""
    print("\n[TEST 8] Log Statistics")
    
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
    
    # Log several events with anomalies
    for i in range(10):
        event = {
            "timestamp": 1700000000.0 + i,
            "raw_address": f"Address {i}",
            "cleaned_address": f"Address {i}",
            "integrity_score": 0.8,
            "fused_confidence": 0.75,
            "ml_results": {"confidence": 0.8},
            "here_results": {"confidence": 0.75},
            "geospatial_results": {"distance_match": 1.0},
            "anomaly_details": {"reasons": ["low_integrity"] if i < 3 else []},
            "self_heal_result": {"actions": []},
            "processing_time_ms": 800.0 + i
        }
        await log_event(event)
    
    # Get statistics
    stats = get_log_stats()
    
    print(f"  Total Events: {stats['total_events']}")
    print(f"  File Size: {stats['file_size_kb']} KB")
    print(f"  Anomaly Count: {stats['anomaly_count']}")
    print(f"  Anomaly Rate: {stats['anomaly_rate_percent']}%")
    print(f"  Avg Processing Time: {stats['avg_processing_time_ms']} ms")
    
    assert stats['total_events'] == 10
    assert stats['anomaly_count'] == 3
    assert stats['anomaly_rate_percent'] == 30.0
    print("  ✓ PASS")


async def test_concurrent_logging():
    """Test concurrent logging from multiple tasks."""
    print("\n[TEST 9] Concurrent Logging")
    
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
    
    async def log_task(task_id: int):
        for i in range(5):
            event = {
                "timestamp": 1700000000.0 + task_id * 100 + i,
                "raw_address": f"Task {task_id} Address {i}",
                "cleaned_address": f"Task {task_id} Address {i}",
                "integrity_score": 0.8,
                "fused_confidence": 0.75,
                "ml_results": {"confidence": 0.8},
                "here_results": {"confidence": 0.75},
                "geospatial_results": {"distance_match": 1.0},
                "anomaly_details": {"reasons": []},
                "self_heal_result": {"actions": []},
                "processing_time_ms": 800.0
            }
            await log_event(event)
    
    # Run 3 tasks concurrently
    await asyncio.gather(
        log_task(1),
        log_task(2),
        log_task(3)
    )
    
    # Verify all events logged
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"  Total rows from 3 concurrent tasks: {len(rows)}")
    assert len(rows) == 15, "Should have 15 rows (3 tasks × 5 events)"
    print("  ✓ PASS")


async def test_timestamp_formatting():
    """Test timestamp formatting."""
    print("\n[TEST 10] Timestamp Formatting")
    
    if CSV_LOG_FILE.exists():
        CSV_LOG_FILE.unlink()
    
    event = {
        "timestamp": 1700000000.0,
        "raw_address": "Test",
        "cleaned_address": "Test",
        "integrity_score": 0.8,
        "fused_confidence": 0.75,
        "ml_results": {"confidence": 0.8},
        "here_results": {"confidence": 0.75},
        "geospatial_results": {"distance_match": 1.0},
        "anomaly_details": {"reasons": []},
        "self_heal_result": {"actions": []},
        "processing_time_ms": 800.0
    }
    
    await log_event(event)
    
    # Read and verify timestamp format
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    row = rows[0]
    timestamp = row['timestamp']
    
    print(f"  Timestamp: {timestamp}")
    
    # Should be in format: YYYY-MM-DD HH:MM:SS
    assert len(timestamp.split()) == 2, "Should have date and time"
    assert "-" in timestamp, "Should contain date separators"
    assert ":" in timestamp, "Should contain time separators"
    print("  ✓ PASS")


async def run_all_tests():
    """Run all test cases."""
    print("=" * 70)
    print("EVENT LOGGING TEST SUITE")
    print("=" * 70)
    
    tests = [
        test_create_log_file,
        test_log_single_event,
        test_log_with_anomalies,
        test_log_with_healing_actions,
        test_multiple_events,
        test_latency_tracking,
        test_missing_fields,
        test_log_stats,
        test_concurrent_logging,
        test_timestamp_formatting
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    # Show final log file info
    if CSV_LOG_FILE.exists():
        stats = get_log_stats()
        print(f"\nFinal Log File: {CSV_LOG_FILE}")
        print(f"  Total Events: {stats.get('total_events', 0)}")
        print(f"  File Size: {stats.get('file_size_kb', 0)} KB")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
