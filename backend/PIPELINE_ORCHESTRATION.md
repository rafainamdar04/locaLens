"""
LOCALLENS PIPELINE ORCHESTRATION DOCUMENTATION
==============================================

This document describes the complete 9-step address processing pipeline
implemented in the /process endpoint.

## PIPELINE OVERVIEW

The pipeline processes raw addresses through multiple stages of geocoding,
validation, and quality control to produce high-confidence location results.

## PIPELINE STEPS

### Step 1: Address Cleaning
Function: `await clean_address(raw_address)`
- Input: Raw address string
- Output: 
  * cleaned_text: Normalized, cleaned address
  * components: Extracted components (street, city, state, pincode, country)
  * confidence: LLM cleaning confidence score

### Step 2: Integrity Scoring
Function: `compute_integrity(raw_address, cleaned_address)`
- Input: Raw and cleaned address strings
- Output:
  * score: Data integrity score (0-100 scale)
  * completeness: Component completeness score
  * quality_flags: List of detected quality issues

### Step 3: ML Geocoding
Function: `ml_geocode(cleaned_address)`
- Input: Cleaned address string
- Output:
  * top_result: Best match with lat/lon coordinates
  * confidence: Similarity-based confidence score
  * candidates: Alternative matches
  * embedding: Address embedding vector

### Step 4: HERE Geocoding
Function: `here_geocode(cleaned_address)`
- Input: Cleaned address string
- Output:
  * primary_result: Primary geocoding result with lat/lon
  * confidence: HERE API confidence score
  * alternatives: Alternative results
  * raw_response: Full API response

### Step 5: Geospatial Validation
Function: `geospatial_checks(ml_top, here_primary, cleaned_address)`
- Input: ML result, HERE result, cleaned address
- Output:
  * score: Overall geospatial consistency score
  * distance_match: Distance between ML and HERE results (km)
  * boundary_check: City boundary validation result
  * details: Pincode mismatch, city violation details

### Step 6: Confidence Fusion
Function: `fuse_confidence(metrics, integrity_score, mismatch_km)`
- Input: 
  * metrics: ML similarity, HERE confidence, LLM confidence
  * integrity_score: Data integrity score (0-100)
  * mismatch_km: Distance between ML and HERE results
- Output: Fused confidence score (weighted combination)

### Step 7: Anomaly Detection
Function: `detect_anomaly(metrics, integrity_score, fused_conf, geospatial_checks)`
- Input: All metrics and scores
- Output:
  * anomaly: Boolean indicating if anomaly detected
  * reasons: List of anomaly reason codes

**Anomaly Rules:**
1. low_fused_conf: Fused confidence < 0.5
2. low_integrity: Integrity score < 40
3. ml_here_mismatch: ML-HERE distance > 3 km
4. low_here_conf: HERE confidence < 0.4
5. pincode_mismatch: Pincode location mismatch
6. high_latency: Processing time > 1500 ms

### Step 8: Self-Healing
Function: `await self_heal(raw, cleaned, ml_candidates, here_resp, reasons)`
- Input: Original data and anomaly reasons
- Output:
  * healed: Boolean indicating if healing successful
  * actions: List of actions taken
  * final_result: Healed result if successful
  * confidence: Confidence in healed result
  * strategies_attempted: Number of strategies tried

**Healing Strategies:**
1. Strict recleaning with higher LLM temperature
2. Reverse geocoding from ML/HERE coordinates
3. Pincode-based fallback geocoding

### Step 9: Event Logging
Function: `await log_event(event)`
- Input: Complete event dictionary
- Output: CSV log entry written to logs/pipeline_logs.csv

**Logged Fields:**
- timestamp, raw_address, cleaned_address
- integrity_score, ml_confidence, here_confidence
- fused_confidence, geospatial_score
- anomaly_detected, anomaly_reasons
- self_heal_actions, processing_time_ms

## DATA FLOW

```
Raw Address
    ↓
[1] Clean Address
    ↓
[2] Compute Integrity
    ↓
[3] ML Geocode ────────┐
    ↓                  │
[4] HERE Geocode ──────┤
    ↓                  │
[5] Geospatial Checks ←┘
    ↓
[6] Fuse Confidence
    ↓
[7] Detect Anomaly
    ↓
[8] Self-Heal (if anomaly)
    ↓
[9] Log Event
    ↓
Final Result
```

## EVENT STRUCTURE

The final event object returned contains all pipeline data:

```python
{
    "timestamp": float,                    # Unix timestamp
    "raw_address": str,                    # Original input
    "cleaned_address": str,                # Cleaned address
    "cleaned_components": dict,            # Address components
    "cleaning_result": dict,               # Full cleaning output
    "integrity": dict,                     # Integrity scores
    "ml_results": dict,                    # ML geocoding output
    "ml_top": dict,                        # Top ML result
    "here_results": dict,                  # HERE geocoding output
    "here_primary": dict,                  # Primary HERE result
    "geospatial_checks": dict,             # Validation results
    "metrics": dict,                       # Confidence metrics
    "fused_confidence": float,             # Final confidence
    "anomaly_detected": bool,              # Anomaly flag
    "anomaly_reasons": list,               # Reason codes
    "anomaly_details": dict,               # Detailed anomaly info
    "self_heal_actions": dict,             # Healing results
    "processing_time_ms": float,           # Total processing time
    "success": bool                        # Success flag
}
```

## ERROR HANDLING

If any step fails:
1. Exception is caught in try-except block
2. Error event is created with error details
3. Error event is logged to CSV
4. HTTPException(500) is raised with error details

## USAGE EXAMPLE

```python
# Request
POST /process
{
    "raw_address": "123 MG Road, Bangalore, Karnataka 560001"
}

# Response
{
    "success": true,
    "event": { ... full event data ... },
    "processing_time_ms": 245.3
}
```

## PERFORMANCE NOTES

- Average processing time: 100-300 ms (depends on API calls)
- High latency threshold: 1500 ms
- All I/O operations are async
- CSV logging is thread-safe with async locks

## TESTING

Test the pipeline using:
```bash
python tests/test_pipeline_endpoint.py
```

This will verify:
- All 9 steps execute in order
- Proper data flow between steps
- Event structure contains all required fields
- Error handling works correctly

## FUTURE ENHANCEMENTS

1. Implement actual ML geocoding (currently stub)
2. Implement HERE Maps API integration (currently stub)
3. Enhance integrity scoring with more checks
4. Add caching layer for repeated addresses
5. Implement rate limiting and quota management
6. Add A/B testing framework for healing strategies
"""
