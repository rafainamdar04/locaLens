"""
Event Logging Utility

Logs pipeline events to CSV file with comprehensive metrics tracking.
Maintains a structured log for analysis, monitoring, and debugging.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import asyncio


# Ensure logs directory exists
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# CSV log file path
CSV_LOG_FILE = LOGS_DIR / "pipeline_logs.csv"

# CSV headers in specified order
CSV_HEADERS = [
    "timestamp",
    "raw",
    "cleaned",
    "integrity_score",
    "fused_confidence",
    "top_similarity",
    "here_confidence",
    "mismatch_km",
    "anomaly_reasons",
    "actions",
    "llm_latency_ms",
    "ml_latency_ms",
    "here_latency_ms",
    "processing_time_ms"
]

# Lock for thread-safe CSV writing
_csv_lock = asyncio.Lock()


async def log_event(event: Dict[str, Any]) -> None:
    """
    Log processing event to CSV file with standardized headers.
    
    Extracts key metrics from the event dictionary and appends them to
    pipeline_logs.csv. Creates the file with headers if it doesn't exist.
    
    Args:
        event: Event dictionary containing pipeline processing results
               Expected keys match the structure from main.py:
               - timestamp: Unix timestamp
               - raw_address: Original raw address
               - cleaned_address: Cleaned address
               - integrity_score: Data integrity score (0-1)
               - fused_confidence: Fused confidence score (0-1)
               - ml_results: ML geocoding results with confidence
               - here_results: HERE geocoding results with confidence
               - geospatial_results: Contains distance_match (mismatch_km)
               - anomaly_detected: Boolean
               - anomaly_details: Contains reasons list
               - self_heal_result: Contains actions list
               - processing_time_ms: Total processing time
               
    CSV Format:
        - Creates file if not exists
        - Writes headers on first write
        - Appends one row per event
        - JSON-encodes complex fields (anomaly_reasons, actions)
        - Thread-safe with async lock
    """
    try:
        async with _csv_lock:
            # Check if file exists
            file_exists = CSV_LOG_FILE.exists()
            
            # Open in append mode
            with open(CSV_LOG_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                
                # Write headers if file is new
                if not file_exists:
                    writer.writeheader()
                
                # Extract values from event
                row = _extract_csv_row(event)
                
                # Write row
                writer.writerow(row)
                
    except Exception as e:
        # Don't let logging errors break the main flow
        print(f"[ERROR] Failed to log event to CSV: {e}")
        
        # Fallback: log to JSONL for recovery
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            fallback_file = LOGS_DIR / f"events_fallback_{date_str}.jsonl"
            with open(fallback_file, "a", encoding="utf-8") as f:
                json.dump(event, f, ensure_ascii=False)
                f.write("\n")
        except:
            pass  # Silent fallback failure


def _mask_address(addr: str) -> str:
    """Lightweight PII scrubbing for addresses: mask long digit sequences and house numbers."""
    try:
        import re
        s = addr or ""
        # Mask 4+ consecutive digits
        s = re.sub(r"\d{4,}", lambda m: "X" * len(m.group(0)), s)
        # Partially mask 1-3 digit tokens (e.g., house/apartment numbers)
        s = re.sub(r"\b(\d{1,3})([A-Za-z]?)\b", r"X\2", s)
        return s
    except Exception:
        return addr


def _extract_csv_row(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract CSV row data from event dictionary.
    
    Args:
        event: Full event dictionary from pipeline
        
    Returns:
        Dictionary with keys matching CSV_HEADERS
    """
    # Extract timestamp
    timestamp = event.get("timestamp")
    if timestamp:
        # Convert to ISO format for readability
        try:
            dt = datetime.fromtimestamp(timestamp)
            timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            timestamp_str = str(timestamp)
    else:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract addresses
    raw = _mask_address(event.get("raw_address", ""))
    cleaned = event.get("cleaned_address") or event.get("cleaned") or ""
    cleaned = _mask_address(cleaned)
    
    # Extract integrity score
    # v3: integrity under event.integrity.score; legacy: integrity_score
    integrity_score = (
        (event.get("integrity") or {}).get("score")
        if event.get("integrity") is not None
        else event.get("integrity_score", 0.0)
    )
    
    # Extract fused confidence
    fused_confidence = event.get("fused_confidence", event.get("confidence", 0.0))
    
    # Extract ML confidence (top_similarity)
    ml_results = event.get("ml_results") or {}
    top_similarity = ml_results.get("confidence", 0.0)
    
    # Extract HERE confidence
    here_results = event.get("here_results") or {}
    here_confidence = here_results.get("confidence", 0.0)
    
    # Extract mismatch distance
    geo = event.get("geospatial_results") or event.get("geospatial_checks") or event.get("checks") or {}
    mismatch_km = geo.get("distance_match", 0.0)
    
    # Extract anomaly reasons (JSON encoded)
    anomaly_details = event.get("anomaly_details") or (event.get("anomaly") or {}).get("details") or {}
    anomaly_reasons_list = anomaly_details.get("reasons") or (event.get("anomaly") or {}).get("reasons") or []
    anomaly_reasons = json.dumps(anomaly_reasons_list) if anomaly_reasons_list else "[]"
    
    # Extract healing actions (JSON encoded)
    self_heal_result = event.get("self_heal_result") or {}
    actions_list = self_heal_result.get("actions") or (event.get("self_heal") or {}).get("actions") or []
    
    # Simplify actions for CSV (keep only strategy and success)
    simplified_actions = [
        {
            "strategy": action.get("strategy", "unknown"),
            "success": action.get("success", False),
            "reason": action.get("reason", "")
        }
        for action in actions_list
    ]
    actions = json.dumps(simplified_actions) if simplified_actions else "[]"
    
    # Extract latencies
    # LLM latency from cleaning result
    cleaning_result = event.get("cleaning_result") or {}
    llm_latency_ms = cleaning_result.get("latency_ms", 0.0)
    
    # ML latency (would come from ml_results if available)
    ml_latency_ms = ml_results.get("latency_ms", 0.0)
    
    # HERE latency (would come from here_results if available)
    here_latency_ms = here_results.get("latency_ms", 0.0)
    
    # Total processing time
    processing_time_ms = event.get("processing_time_ms", 0.0)
    
    # Build row dictionary
    row = {
        "timestamp": timestamp_str,
        "raw": raw,
        "cleaned": cleaned,
        "integrity_score": f"{integrity_score:.4f}",
        "fused_confidence": f"{fused_confidence:.4f}",
        "top_similarity": f"{top_similarity:.4f}",
        "here_confidence": f"{here_confidence:.4f}",
        "mismatch_km": f"{mismatch_km:.2f}",
        "anomaly_reasons": anomaly_reasons,
        "actions": actions,
        "llm_latency_ms": f"{llm_latency_ms:.1f}",
        "ml_latency_ms": f"{ml_latency_ms:.1f}",
        "here_latency_ms": f"{here_latency_ms:.1f}",
        "processing_time_ms": f"{processing_time_ms:.1f}"
    }
    
    return row


def get_log_stats() -> Dict[str, Any]:
    """
    Get statistics about the pipeline logs.
    
    Returns:
        Dictionary with log statistics:
        - total_events: Total number of logged events
        - file_size_kb: Log file size in KB
        - first_event: Timestamp of first event
        - last_event: Timestamp of last event
        - avg_processing_time: Average processing time
        - anomaly_rate: Percentage of events with anomalies
    """
    try:
        if not CSV_LOG_FILE.exists():
            return {
                "total_events": 0,
                "file_size_kb": 0,
                "message": "No logs found"
            }
        
        # Get file size
        file_size_kb = CSV_LOG_FILE.stat().st_size / 1024
        
        # Read and analyze logs
        with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            return {
                "total_events": 0,
                "file_size_kb": file_size_kb,
                "message": "Log file empty"
            }
        
        # Calculate statistics
        total_events = len(rows)
        first_event = rows[0].get("timestamp", "unknown")
        last_event = rows[-1].get("timestamp", "unknown")
        
        # Average processing time
        processing_times = [
            float(row.get("processing_time_ms", 0))
            for row in rows
        ]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Anomaly rate
        anomaly_count = sum(
            1 for row in rows
            if row.get("anomaly_reasons", "[]") != "[]"
        )
        anomaly_rate = (anomaly_count / total_events * 100) if total_events > 0 else 0
        
        return {
            "total_events": total_events,
            "file_size_kb": round(file_size_kb, 2),
            "first_event": first_event,
            "last_event": last_event,
            "avg_processing_time_ms": round(avg_processing_time, 2),
            "anomaly_count": anomaly_count,
            "anomaly_rate_percent": round(anomaly_rate, 2)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to read log statistics"
        }
