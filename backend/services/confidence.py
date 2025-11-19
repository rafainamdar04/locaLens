"""Confidence fusion service."""
from typing import Dict, Any, Optional


def fuse_confidence(
    metrics: Dict[str, float],
    integrity_score: float,
    mismatch_km: Optional[float] = None
) -> float:
    """
    Fuse multiple confidence scores into a single confidence metric.
    
    Uses a weighted formula combining:
    - Data integrity score (25%)
    - ML similarity score (25%)
    - HERE confidence score (30%)
    - Geospatial consistency via mismatch distance (20%)
    
    Args:
        metrics: Dictionary containing confidence metrics:
            - ml_similarity: ML geocoding confidence (0-1)
            - here_confidence: HERE geocoding confidence (0-1)
            - llm_confidence: Optional LLM cleaning confidence (0-1)
        integrity_score: Data integrity score (0-100 scale)
        mismatch_km: Distance between ML and HERE results in km (None if unavailable)
        
    Returns:
        Fused confidence score between 0.0 and 1.0
        
    Formula:
        confidence = 0.25 * integrity_norm + 
                    0.25 * ml_similarity + 
                    0.30 * here_confidence + 
                    0.20 * (1 - mismatch_norm)
        
        where:
        - integrity_norm = integrity_score / 100
        - mismatch_norm = min(mismatch_km / 10, 1.0)
    """
    # Extract metrics with defaults
    ml_similarity = metrics.get('ml_similarity', 0.0)
    here_confidence = metrics.get('here_confidence', 0.0)
    llm_confidence = metrics.get('llm_confidence', None)  # Optional, not used in formula
    
    # Normalize integrity score (0-100 scale to 0-1)
    integrity_norm = min(max(integrity_score / 100.0, 0.0), 1.0)
    
    # Normalize mismatch distance (cap at 10km)
    if mismatch_km is not None:
        mismatch_norm = min(mismatch_km / 10.0, 1.0)
        geospatial_component = 1.0 - mismatch_norm
    else:
        # If no mismatch data, use neutral value (0.5)
        geospatial_component = 0.5
    
    # Weighted formula
    fused = (
        0.25 * integrity_norm +
        0.25 * ml_similarity +
        0.30 * here_confidence +
        0.20 * geospatial_component
    )
    
    # Clamp to [0.0, 1.0] range
    fused = min(max(fused, 0.0), 1.0)
    
    return round(fused, 4)


# Legacy function for backwards compatibility
def fuse_confidence_legacy(
    ml_confidence: float,
    here_confidence: float,
    integrity_score: float,
    geospatial_score: float
) -> float:
    """
    Legacy confidence fusion function for backwards compatibility.
    
    This is a simpler version that uses equal weighting.
    Use fuse_confidence() for the new weighted formula.
    
    Args:
        ml_confidence: Confidence from ML geocoding (0-1)
        here_confidence: Confidence from HERE geocoding (0-1)
        integrity_score: Data integrity score (0-1)
        geospatial_score: Geospatial validation score (0-1)
        
    Returns:
        Fused confidence score (0-1)
    """
    # Simple weighted average as placeholder
    weights = {
        "ml": 0.3,
        "here": 0.3,
        "integrity": 0.2,
        "geospatial": 0.2
    }
    
    fused = (
        weights["ml"] * ml_confidence +
        weights["here"] * here_confidence +
        weights["integrity"] * integrity_score +
        weights["geospatial"] * geospatial_score
    )
    
    return min(max(fused, 0.0), 1.0)


# New architecture-compatible entry
def compute_fusion(context: Dict[str, Any]) -> Dict[str, Any]:
    ml_conf = (context.get("ml_results") or {}).get("confidence", 0.0)
    here_conf = (context.get("here_results") or {}).get("confidence", 0.0)
    llm_conf = (context.get("cleaning_result") or {}).get("confidence", 0.0)
    integrity_score = (context.get("integrity") or {}).get("score", 0)
    mismatch_km = (context.get("geospatial_checks") or {}).get("distance_match")

    metrics = {
        "ml_similarity": ml_conf or 0.0,
        "here_confidence": here_conf or 0.0,
        "llm_confidence": llm_conf or 0.0,
    }
    # Compute provenance components for transparency
    integrity_norm = max(0.0, min(1.0, (integrity_score or 0) / 100.0))
    if mismatch_km is not None:
        mismatch_norm = min(max((mismatch_km or 0.0) / 10.0, 0.0), 1.0)
        geospatial_component = 1.0 - mismatch_norm
    else:
        geospatial_component = 0.5

    fused = fuse_confidence(metrics=metrics, integrity_score=integrity_score, mismatch_km=mismatch_km)
    confidence_sources = {
        "ml": float(ml_conf or 0.0),
        "here": float(here_conf or 0.0),
        "integrity": float(integrity_norm),
        "geospatial": float(round(geospatial_component, 4)),
    }
    return {"metrics": metrics, "fused_confidence": fused, "confidence_sources": confidence_sources}
