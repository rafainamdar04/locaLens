"""
LocalLens FastAPI Application
Main entry point for the address processing and geocoding service.
"""
import time
import hashlib
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from services.addons.drivability import compute_drivability
from services.addons.parking import compute_parking
from services.addons.navigation import compute_navigation
from services.addons.traffic import compute_traffic

from config import settings
from services.address_cleaner import clean_address, compute_clean
try:
    from services.ml_geocoder import ml_geocode, compute_ml
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML geocoding not available: {e}")
    ML_AVAILABLE = False
    ml_geocode = None
    compute_ml = None
from services.here_geocoder import here_geocode, compute_here
from services.integrity import compute_integrity, compute_integrity_ctx
from services.geospatial import geospatial_checks, compute_checks, validate_reverse_geocoding, analyze_poi_proximity
from services.here_geocoder import here_geocode, compute_here, here_routing, here_places_search
from services.confidence import fuse_confidence, compute_fusion
from services.anomaly import detect_anomaly, compute_anomaly
from services.self_heal import self_heal
from services.monitoring import monitoring_service
from services.agent import monitoring_agent
from services.metrics import get_metrics_response
from services.addons.deliverability import compute_deliverability
from services.addons.activity_validation import compute_fraud, detect_fraud
from services.addons.neighborhood import compute_neighborhood
from services.addons.property_assessment import compute_property_risk
from services.addons.emergency import compute_emergency_access
from services.addons.safety import compute_safety
from services.delivery_navigator import get_delivery_navigation
from services.safety_assessor import assess_residential_safety
from services.delivery_navigator import get_delivery_navigation
from utils.logger import log_event
from core.pipeline import Pipeline
from modules.registry import default_steps


# Initialize FastAPI app
app = FastAPI(
    title="LocalLens API",
    description="Advanced address processing and geocoding service with ML and geospatial validation",
    version="1.0.0"
)

# Simple in-memory cache for processed addresses
_ADDRESS_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_MAX_SIZE = settings.CACHE_MAX_SIZE


def _get_cache_key(raw_address: str) -> str:
    """Generate a cache key for an address or addons string."""
    # If contains spaces, assume addons, sort them for order-insensitivity
    parts = raw_address.strip().split()
    if len(parts) > 1:
        parts = sorted(parts)
        raw_address = ' '.join(parts)
    return hashlib.md5(raw_address.lower().encode()).hexdigest()


def _get_cached_result(raw_address: str) -> Optional[Dict[str, Any]]:
    """Retrieve cached result if available and fresh (< 1 hour)."""
    cache_key = _get_cache_key(raw_address)
    if cache_key in _ADDRESS_CACHE:
        cached = _ADDRESS_CACHE[cache_key]
        age_seconds = time.time() - cached['cached_at']
        if age_seconds < settings.CACHE_TTL_SECONDS:
            return cached['result']
        else:
            # Expired, remove it
            del _ADDRESS_CACHE[cache_key]
    return None


def _set_cached_result(raw_address: str, result: Dict[str, Any]):
    """Store result in cache with LRU eviction."""
    cache_key = _get_cache_key(raw_address)
    
    # Simple LRU: if cache full, remove oldest
    if len(_ADDRESS_CACHE) >= _CACHE_MAX_SIZE:
        oldest_key = min(_ADDRESS_CACHE.keys(), key=lambda k: _ADDRESS_CACHE[k]['cached_at'])
        del _ADDRESS_CACHE[oldest_key]
    
    _ADDRESS_CACHE[cache_key] = {
        'result': result,
        'cached_at': time.time()
    }


# Remove old app initialization
# Initialize FastAPI app

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Warmup heavy services on startup (non-blocking)
@app.on_event("startup")
async def _warmup_background():
    print("\n" + "="*60)
    print("LOCALENS API STARTUP")
    print("="*60)
    api_key = settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY
    if api_key:
        if api_key.startswith("sk-or-"):
            print(f"LLM Provider: OpenRouter (key configured: True)")
        else:
            print(f"LLM Provider: OpenAI (key configured: True)")
    else:
        print("LLM Provider: None (will use deterministic fallback)")
    print(f"HERE Maps API Key configured: {bool(settings.HERE_API_KEY)}")
    print(f"Embedding Model: {settings.EMBED_MODEL}")
    print(f"Port: {settings.PORT}")
    print("="*60 + "\n")
    
    # Start background monitoring
    # asyncio.create_task(_background_monitoring())


async def _background_monitoring():
    """Background task for proactive monitoring."""
    while True:
        try:
            await monitoring_service.run_monitoring_cycle()
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            print(f"[MONITORING] Background task error: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute on error


# Request/Response Models
class AddressRequest(BaseModel):
    """Request model for address processing."""
    raw_address: str = Field(
        ...,
        description="Raw address string to process",
        min_length=5,
        max_length=500,
        json_schema_extra={
            "examples": [
                "123 MG Road, Bengaluru 560001",
                "45 Connaught Place, New Delhi 110001",
                "18 Marine Drive, Fort, Mumbai 400001"
            ]
        }
    )
    
    @field_validator('raw_address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate address content."""
        if not v.strip():
            raise ValueError("Address cannot be empty or whitespace only")
        
        # Check for reasonable character set
        if len(v.strip()) < 5:
            raise ValueError("Address too short (minimum 5 characters)")
        
        return v.strip()


class AddressResponse(BaseModel):
    """Response model for processed address."""
    success: bool
    event: Dict[str, Any]
    processing_time_ms: float


# API Routes
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "LocalLens API",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint with comprehensive system status."""
    import os
    from services.monitoring import monitoring_service
    
    # Compute metrics from logs
    df = await monitoring_service.load_recent_logs(hours=24)
    metrics = monitoring_service.compute_metrics(df) if not df.empty else {}
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - getattr(settings, 'START_TIME', time.time()),
        "config": {
            "embed_model": settings.EMBED_MODEL,
            "port": settings.PORT,
            "here_api_configured": bool(settings.HERE_API_KEY),
            "llm_api_configured": bool(settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY),
            "cache_enabled": settings.CACHE_MAX_SIZE > 0,
            "cache_size": len(_ADDRESS_CACHE)
        },
        "services": {
            "embedder_loaded": False,
            "here_api_reachable": False,
            "llm_api_reachable": False
        },
        "performance": {
            "total_requests_processed": metrics.get('total_requests', 0),
            "average_processing_time_ms": metrics.get('avg_latency', 0)
        }
    }
    
    # Check embedder
    try:
        from models.embedder import Embedder
        embedder = Embedder()
        # Quick test
        test_embed = embedder.encode(["test"])
        health_status["services"]["embedder_loaded"] = True
    except Exception as e:
        health_status["services"]["embedder_loaded"] = False
        health_status["services"]["embedder_error"] = str(e)
    
    # Check HERE API
    if settings.HERE_API_KEY:
        try:
            # Quick test with a simple geocode
            test_result = here_geocode("Mumbai Central Station")
            health_status["services"]["here_api_reachable"] = test_result is not None and "error" not in test_result
        except Exception as e:
            health_status["services"]["here_api_reachable"] = False
            health_status["services"]["here_api_error"] = str(e)
    
    # Check LLM API (OpenRouter or OpenAI)
    api_key = settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY
    if api_key:
        try:
            import openai
            openai.api_key = api_key
            if settings.OPENROUTER_API_KEY:
                openai.api_base = "https://openrouter.ai/api/v1"
            # For now, just check if key is set and format looks right
            health_status["services"]["llm_api_reachable"] = len(api_key) > 20
        except Exception as e:
            health_status["services"]["llm_api_reachable"] = False
            health_status["services"]["llm_api_error"] = str(e)
    
    # Determine overall status
    services_ok = all(health_status["services"].values())
    
    if not services_ok:
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/monitoring/metrics")
async def get_monitoring_metrics():
    """Get current monitoring metrics and predictions."""
    try:
        # Run a fresh monitoring cycle
        result = await monitoring_service.run_monitoring_cycle()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring error: {str(e)}")


@app.get("/monitoring/alerts")
async def get_monitoring_alerts():
    """Get recent monitoring alerts."""
    try:
        return {
            "alerts": monitoring_service.alerts[-10:],  # Last 10 alerts
            "total_alerts": len(monitoring_service.alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alerts error: {str(e)}")


@app.post("/monitoring/agent-check")
async def run_agent_monitoring():
    """Run autonomous agent monitoring check."""
    try:
        result = await monitoring_agent.run_monitoring_check()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint for observability."""
    return get_metrics_response()


@app.post("/process", response_model=AddressResponse)
async def process_address(request: AddressRequest):
    """
    Process a raw address through the complete geocoding and validation pipeline.
    
    Pipeline steps:
    1. Check cache for previous results
    2. Clean the raw address
    3. ML-based geocoding
    4. HERE Maps geocoding
    5. Compute data integrity score
    6. Run geospatial validation checks
    7. Fuse confidence scores
    8. Detect anomalies
    9. Self-heal if anomalies detected
    10. Log the processing event
    11. Cache the result
    
    Args:
        request: AddressRequest containing raw_address (5-500 chars)
        
    Returns:
        AddressResponse with success status, full event data, and processing time
        
    Examples:
        ```json
        {
            "raw_address": "123 MG Road, Bengaluru 560001"
        }
        ```
    """
    start_time = time.time()
    
    # Check cache first
    cached_result = _get_cached_result(request.raw_address)
    if cached_result:
        cached_result['from_cache'] = True
        cached_result['processing_time_ms'] = (time.time() - start_time) * 1000
        return AddressResponse(
            success=True,
            event=cached_result['event'],
            processing_time_ms=cached_result['processing_time_ms']
        )
    
    try:
        # Step 1: Clean the raw address
        cleaned_result = await clean_address(request.raw_address)
        cleaned_address = cleaned_result["cleaned_text"]
        cleaned_components = cleaned_result.get("components", {})
        
        # Step 2: Compute integrity score
        integrity = compute_integrity(request.raw_address, cleaned_address)
        
        # Step 3: ML-based geocoding
        ml_results = None
        ml_top = None
        if ML_AVAILABLE and ml_geocode:
            try:
                ml_results = ml_geocode(cleaned_address)
                ml_top = ml_results.get("top_result") if ml_results else None
            except Exception as e:
                print(f"[ML GEOCODING] Error: {e}")
                ml_results = None
                ml_top = None
        
        # Step 4: HERE Maps geocoding
        here_results = here_geocode(cleaned_address)
        here_primary = here_results.get("primary_result") if here_results else None
        
        # Step 5: Run geospatial validation checks
        geo_checks = geospatial_checks(
            ml_top=ml_top,
            here_primary=here_primary,
            cleaned=cleaned_address
        )
        
        # Step 5.5: Reverse geocoding validation
        ml_coords = ml_top.get("coordinates") or ml_top if ml_top and ("lat" in ml_top or "latitude" in ml_top) else None
        here_coords = here_primary.get("coordinates") or here_primary if here_primary and ("lat" in here_primary or "latitude" in here_primary) else None
        
        reverse_validation = await validate_reverse_geocoding(
            ml_coords=ml_coords,
            here_coords=here_coords,
            cleaned_address=cleaned_address
        )
        
        # Step 5.5: Analyze POI proximity for address validation
        poi_analysis = None
        if here_coords:
            try:
                poi_analysis = await analyze_poi_proximity(
                    location=here_coords,
                    address_type="",  # Could be inferred from address
                    radius=500
                )
            except Exception as e:
                print(f"[POI ANALYSIS] Error: {e}")
                poi_analysis = None
        
        # Step 5.6: Calculate routing information from default origin (Delhi)
        routing_info = None
        if here_primary and here_primary.get("lat") and here_primary.get("lon"):
            # Default origin: Connaught Place, New Delhi (central location for routing calculations)
            default_origin = {"lat": 28.6304, "lon": 77.2177}  # Connaught Place coordinates
            destination = {"lat": here_primary["lat"], "lon": here_primary["lon"]}
            
            try:
                routing_info = await here_routing(
                    origin=default_origin,
                    destination=destination,
                    transport_mode="car"
                )
            except Exception as e:
                print(f"[ROUTING] Error calculating route: {e}")
                routing_info = None
        
        # Step 5.6.1: Calculate places information near the destination
        places_info = []
        if here_primary and here_primary.get("lat") and here_primary.get("lon"):
            try:
                location = {"lat": here_primary["lat"], "lon": here_primary["lon"]}
                # Search for safety-related places (police, hospitals, security)
                categories = ["police", "hospital", "emergency", "security"]
                places_info = await here_places_search(
                    location=location,
                    radius=1000,  # 1km radius
                    categories=categories
                )
            except Exception as e:
                print(f"[PLACES] Error fetching places data: {e}")
                places_info = []
        
        # Step 6: Fuse confidence scores
        # Prepare metrics for confidence fusion
        metrics = {
            'ml_similarity': ml_results.get("confidence", 0.0) if ml_results else 0.0,
            'here_confidence': here_results.get("confidence", 0.0) if here_results else 0.0,
            'llm_confidence': cleaned_result.get("confidence", 0.0)
        }
        
        # Get distance match (ensure not None)
        distance_match = geo_checks.get("distance_match")
        if distance_match is None:
            distance_match = 0.0
        
        # Fuse confidence using weighted formula
        fused = fuse_confidence(
            metrics=metrics,
            integrity_score=integrity["score"],
            mismatch_km=distance_match
        )
        
        # Step 7: Detect anomalies
        # Prepare metrics for anomaly detection
        anomaly_metrics = {
            'ml_result': ml_results if ml_results else {},
            'here_result': here_results if here_results else {},
            'ml_here_mismatch_km': distance_match,
            'latency_ms': (time.time() - start_time) * 1000  # Current processing time
        }
        
        anomaly, reasons = detect_anomaly(
            metrics=anomaly_metrics,
            integrity_score=integrity["score"],
            fused_conf=fused,
            geospatial_checks=geo_checks
        )
        
        # Format anomaly details from reasons
        anomaly_details = {
            "detected": anomaly,
            "reasons": reasons,
            "reason_count": len(reasons)
        }
        
        # Step 8: Self-heal if anomaly detected
        actions = None
        if anomaly:
            actions = await self_heal(
                raw=request.raw_address,
                cleaned=cleaned_address,
                ml_candidates=ml_results,
                here_resp=here_results,
                reasons=reasons
            )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Step 9: Build complete event object and log
        # Compute emergency access
        emergency_access = compute_emergency_access({
            "here_results": here_results,
            "routing": routing_info,
            "places": places_info      # Places data from HERE Places API
        })
        # Compute drivability score
        drivability = compute_drivability({
            "here_results": here_results,
            "routing": routing_info
        })
        # Compute parking/drop-off feasibility
        parking = compute_parking({
            "here_results": here_results,
            "routing": routing_info,
            "places": places_info      # Places data from HERE Places API
        })
        # Compute navigation insights
        navigation = compute_navigation({
            "routing": routing_info
        })
        # Compute traffic/road condition alerts
        traffic = compute_traffic({
            "traffic": None  # Add traffic data if available
        })
        # Compute deliverability score
        deliverability = compute_deliverability({
            "integrity": integrity,
            "geospatial_checks": geo_checks,
            "here_results": here_results,
            "metrics": metrics,
            "ml_results": ml_results,
            "routing": routing_info,
            "places": places_info  # Places data from HERE Places API
        })
        # Compute location mismatch (distance in km between ML and HERE geocoder)
        location_mismatch = None
        try:
            ml_coords = ml_top if ml_top and ml_top.get("lat") is not None and ml_top.get("lon") is not None else None
            here_coords = here_primary if here_primary and here_primary.get("lat") is not None and here_primary.get("lon") is not None else None
            if ml_coords and here_coords:
                from utils.helpers import haversine
                location_mismatch = haversine(
                    float(ml_coords["lat"]), float(ml_coords["lon"]),
                    float(here_coords["lat"]), float(here_coords["lon"])
                )
        except Exception:
            location_mismatch = None

        event = {
            "timestamp": time.time(),
            "raw_address": request.raw_address,
            "cleaned_address": cleaned_address,
            "cleaned_components": cleaned_components,
            "cleaning_result": cleaned_result,
            "integrity": integrity,
            "ml_results": ml_results,
            "ml_top": ml_top,
            "here_results": here_results,
            "here_primary": here_primary,
            "geospatial_checks": geo_checks,
            "reverse_geocoding_validation": reverse_validation,
            "poi_proximity_analysis": poi_analysis,
            "metrics": metrics,
            "fused_confidence": fused,
            "location_mismatch": {"distance_km": location_mismatch, "feature_category": "Logistics & Delivery Intelligence"},
            "deliverability": {**deliverability, "feature_category": "Logistics & Delivery Intelligence"},
            "drivability": {**drivability, "feature_category": "Vehicle & Navigation Insights"},
            "parking": {**parking, "feature_category": "Logistics & Delivery Intelligence"},
            "navigation": {**navigation, "feature_category": "Vehicle & Navigation Insights"},
            "traffic": {**traffic, "feature_category": "Vehicle & Navigation Insights"},
            "emergency_access": {**emergency_access, "feature_category": "Safety & Emergency Access"},
            "anomaly_detected": anomaly,
            "anomaly_reasons": reasons,
            "anomaly_details": anomaly_details,
            "self_heal_actions": actions,
            "processing_time_ms": processing_time_ms,
            "success": True
        }
        
        # Log the event
        await log_event(event)
        
        # Cache the result
        response_data = {
            'event': event,
            'processing_time_ms': processing_time_ms
        }
        _set_cached_result(request.raw_address, response_data)
        
        return AddressResponse(
            success=True,
            event=event,
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Log error event
        error_event = {
            "timestamp": time.time(),
            "raw_address": request.raw_address,
            "error": str(e),
            "error_type": type(e).__name__,
            "processing_time_ms": processing_time_ms,
            "success": False
        }
        
        try:
            await log_event(error_event)
        except Exception as log_error:
            print(f"Failed to log error event: {log_error}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "error_type": type(e).__name__,
                "processing_time_ms": processing_time_ms
            }
        )


@app.post("/process_v2", response_model=AddressResponse)
async def process_address_v2(request: AddressRequest):
    """
    Clean-architecture pipeline variant: each step takes a context dict and returns a dict.
    This endpoint preserves existing event shape while eliminating step side-effects.
    """
    start_time = time.time()
    try:
        # Compose and run pipeline
        pipe = Pipeline(default_steps())
        ctx_in = {"raw_address": request.raw_address}
        ctx_out = await pipe.run(ctx_in)

        # Build final event from context
        event = {
            "timestamp": time.time(),
            "raw_address": request.raw_address,
            "cleaned_address": ctx_out.get("cleaned_address"),
            "cleaned_components": ctx_out.get("cleaned_components"),
            "cleaning_result": ctx_out.get("cleaning_result"),
            "integrity": ctx_out.get("integrity"),
            "ml_results": ctx_out.get("ml_results"),
            "ml_top": ctx_out.get("ml_top"),
            "here_results": ctx_out.get("here_results"),
            "here_primary": ctx_out.get("here_primary"),
            "geospatial_checks": ctx_out.get("geospatial_checks"),
            "metrics": ctx_out.get("metrics"),
            "fused_confidence": ctx_out.get("fused_confidence"),
            "anomaly_detected": ctx_out.get("anomaly_detected"),
            "anomaly_reasons": ctx_out.get("anomaly_reasons"),
            "anomaly_details": ctx_out.get("anomaly_details"),
            "self_heal_actions": ctx_out.get("self_heal_actions"),
            "processing_time_ms": (time.time() - start_time) * 1000,
            "success": True,
        }

        try:
            await log_event(event)
        except Exception as log_error:
            print(f"Event logging failed (non-fatal): {log_error}")

        return AddressResponse(
            success=True,
            event=event,
            processing_time_ms=event["processing_time_ms"],
        )

    except Exception as e:
        processing_time_ms = (time.time() - start_time) * 1000
        error_event = {
            "timestamp": time.time(),
            "raw_address": request.raw_address,
            "error": str(e),
            "error_type": type(e).__name__,
            "processing_time_ms": processing_time_ms,
            "success": False,
        }
        try:
            await log_event(error_event)
        except Exception as log_error:
            print(f"Failed to log error event: {log_error}")

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "error_type": type(e).__name__,
                "processing_time_ms": processing_time_ms,
            },
        )


@app.post("/process_v3", response_model=AddressResponse)
async def process_address_v3(
    request: AddressRequest,
    addons: Optional[str] = Query(
        default=None,
        description="Optional add-ons: 'all' or comma-separated list of: deliverability,property_risk,fraud,neighborhood",
    ),
):
    """
    Architecture-aligned pipeline: compute_* modules receive a shared context and return structured dicts.
    Orchestration only; no business logic lives here.
    Order: clean → integrity → ml → here → checks → fusion → anomaly → addons → final
    """
    start = time.time()

    # Normalize addons for stable cache keys
    def _normalize_addons(param: Optional[str]) -> str:
        if param is None or not param:
            return "none"
        val = str(param).strip().lower()
        if val in {"all", ""}:
            return "all" if val == "all" else "none"
        if val in {"none", "false", "0"}:
            return "none"
        parts = sorted({p.strip() for p in val.split(",") if p.strip()})
        return ",".join(parts) if parts else "none"

    addons_norm = _normalize_addons(addons)

    # Composite cache key including addons selection
    cache_key = f"{request.raw_address}|addons={addons_norm}"
    cached_v3 = _get_cached_result(cache_key)
    if cached_v3:
        return AddressResponse(
            success=True,
            event=cached_v3.get("event", {}),
            processing_time_ms=(time.time() - start) * 1000,
        )

    ctx: Dict[str, Any] = {"raw_address": request.raw_address}
    try:
        # Core pipeline
        ctx.update(await compute_clean(ctx))
        ctx.update(compute_integrity_ctx(ctx))
        # Run ML and HERE in parallel with per-task timeouts to avoid long waits
        ml_task = None
        if ML_AVAILABLE:
            ml_task = asyncio.to_thread(compute_ml, ctx)
        here_task = asyncio.to_thread(compute_here, ctx)
        
        ml_out = {}
        if ml_task:
            try:
                ml_out = await asyncio.wait_for(ml_task, timeout=6.0)
            except asyncio.TimeoutError:
                ml_out = {}
            except Exception as e:
                print(f"[ML COMPUTATION] Error: {e}")
                ml_out = {}
        else:
            print("[ML COMPUTATION] ML geocoding not available, skipping")
        
        try:
            here_out = await asyncio.wait_for(here_task, timeout=8.0)
        except asyncio.TimeoutError:
            here_out = {"here_results": {"primary_result": None, "confidence": 0.0, "alternatives": [], "raw_response": None}, "here_primary": None, "here_confidence": 0.0}
        if isinstance(ml_out, dict):
            ctx.update(ml_out)
        if isinstance(here_out, dict):
            ctx.update(here_out)
        ctx.update(compute_checks(ctx))
        ctx.update(compute_fusion(ctx))
        ctx.update(compute_anomaly(ctx))

        # Optional self-heal if anomaly detected
        actions = None
        if ctx.get("anomaly_detected"):
            try:
                actions = await self_heal(
                    raw=request.raw_address,
                    cleaned=ctx.get("cleaned_address"),
                    ml_candidates=ctx.get("ml_results"),
                    here_resp=ctx.get("here_results"),
                    reasons=ctx.get("anomaly_reasons") or [],
                )
            except Exception as _she:
                print(f"Self-heal failed: {_she}")

        # Optional add-ons (industry-agnostic), collected under one section
        addons_payload: Dict[str, Any] = {}
        supported = {"deliverability", "property_risk", "fraud", "neighborhood", "safety"}
        default_addons = {"deliverability", "safety"}  # Compute these by default for better UX

        def _parse_addons(param: Optional[str]) -> set:
            if param is None or not param:
                return default_addons  # Return defaults when no param specified
            val = str(param).strip().lower()
            if val == "all":
                return set(supported)
            if val in {"none", "false", "0", ""}:
                return set()
            parsed = {p.strip() for p in val.split(",") if p.strip() in supported}
            print(f"DEBUG: parsing '{param}' -> '{val}' -> {parsed} from {supported}")  # Debug
            return parsed

        selected = _parse_addons(addons)

        # Prepare parallel addon computations
        async def _addon_deliverability():
            try:
                result = await asyncio.to_thread(compute_deliverability, ctx)
                # Pass through detailed breakdown and issues for UI
                payload = {
                    "deliverability_score": result.get("score", 0) * 100.0,
                    # Normalized score for frontend: 0-1
                    "score": result.get("score", 0),
                    "breakdown": result.get("breakdown", {}),
                    "issues": result.get("issues", []),
                    # Simple one-line explanation for quick explainability
                    "explanation": result.get("reasons", ["Estimated deliverability based on integrity, geocoding and routing signals."])[0] if result.get("reasons") else "Estimated deliverability based on integrity, geocoding and routing signals.",
                    # Convenience mirrors
                    "integrity_contribution": (ctx.get("integrity", {}).get("score", 0) / 100.0),
                    "here_confidence": (ctx.get("here_results") or {}).get("confidence", 0),
                    "ml_similarity": (ctx.get("metrics") or {}).get("ml_similarity", 0),
                    "mismatch_km": (ctx.get("geospatial_checks") or {}).get("distance_match", 0),
                }
                return ("deliverability", payload)
            except Exception as e:
                return ("deliverability", {"error": str(e)})

        async def _addon_property_risk():
            try:
                pr = await asyncio.to_thread(compute_property_risk, ctx)
                pr_data = pr.get("property_risk", {})
                factors = pr_data.get("factors", {})
                return (
                    "property_risk",
                    {
                        "risk_score": pr_data.get("risk_score", 0) / 100.0,
                        "score": pr_data.get("risk_score", 0) / 100.0,
                        "flood_risk": factors.get("flood_risk", 0) / 100.0,
                        "fire_access_risk": factors.get("fire_access_risk", 0) / 100.0,
                        "road_connectivity_index": factors.get("road_connectivity_index", factors.get("neighborhood_density_index", 0)) / 100.0,
                        "hospital_access_risk": factors.get("hospital_access_risk", 0) / 100.0,
                        "explanation": f"Risk assessment using {pr_data.get('source', 'heuristic')} data",
                        "reasons": pr_data.get("reasons", []),
                        "missing_data": pr_data.get("missing_data", []),
                    },
                )
            except Exception as e:
                return ("property_risk", {"error": str(e)})

        async def _addon_fraud():
            try:
                fr = await asyncio.to_thread(detect_fraud, ctx)
                fr_data = fr.get("fraud_detection", {})
                return (
                    "fraud",
                    {
                        "fraud_risk": fr_data.get("fraud_risk", 0),
                        "score": fr_data.get("fraud_risk", 0),
                        "flags": fr_data.get("flags", []),
                        "anomaly_count": len(ctx.get("anomaly_reasons", [])),
                        "explanation": fr_data.get("summary", "No fraud indicators detected."),
                    },
                )
            except Exception as e:
                return ("fraud", {"error": str(e)})

        async def _addon_neighborhood():
            try:
                nb = await asyncio.to_thread(compute_neighborhood, ctx)
                nb_data = nb.get("neighborhood", {})
                return (
                    "neighborhood",
                    {
                        "neighborhood_score": nb_data.get("score", 0) / 100.0,
                        "score": nb_data.get("score", 0) / 100.0,
                        "city": nb_data.get("city"),
                        "density": "unknown",
                        "poi_count": 0,
                        "safety_index": 0.5,
                        "explanation": "Neighborhood quality proxy based on geocoding coverage.",
                    },
                )
            except Exception as e:
                return ("neighborhood", {"error": str(e)})

        async def _addon_safety():
            try:
                print(f"DEBUG: Computing safety addon")  # Debug
                safety = await asyncio.to_thread(compute_safety, ctx)
                safety_data = safety.get("safety_score", 0)
                breakdown = safety.get("breakdown", {})
                print(f"DEBUG: Safety computed: {safety_data}")  # Debug
                return (
                    "safety",
                    {
                        "safety_score": safety_data,
                        "score": safety_data,
                        "breakdown": breakdown,
                        "issues": safety.get("issues", []),
                        "recommendations": safety.get("recommendations", []),
                        "safety_factors": safety.get("safety_factors", {}),
                        "explanation": "Safety estimate based on routing, places and city intelligence.",
                    },
                )
            except Exception as e:
                print(f"DEBUG: Safety addon error: {e}")  # Debug
                return ("safety", {"error": str(e)})

        named_addon_tasks = []
        if "deliverability" in selected:
            named_addon_tasks.append(("deliverability", _addon_deliverability()))
        if "property_risk" in selected:
            named_addon_tasks.append(("property_risk", _addon_property_risk()))
        if "fraud" in selected:
            named_addon_tasks.append(("fraud", _addon_fraud()))
        if "neighborhood" in selected:
            named_addon_tasks.append(("neighborhood", _addon_neighborhood()))
        if "safety" in selected:
            named_addon_tasks.append(("safety", _addon_safety()))

        if named_addon_tasks:
            # Run each addon with its own timeout budget to prevent long tails
            async def _run_with_timeout(name: str, coro, timeout: float = 3.0):
                try:
                    return await asyncio.wait_for(coro, timeout=timeout)
                except asyncio.TimeoutError:
                    return (name, {"error": "timeout"})

            timed_results = await asyncio.gather(
                *[_run_with_timeout(name, coro, float(settings.ADDON_TIMEOUT_S)) for name, coro in named_addon_tasks],
                return_exceptions=True,
            )
            for res in timed_results:
                if isinstance(res, Exception) or res is None:
                    continue
                k, v = res
                addons_payload[k] = v

        processing_time_ms = (time.time() - start) * 1000
        ctx["processing_time_ms"] = processing_time_ms

        # Health scoring
        fused = float(ctx.get("fused_confidence") or 0.0)
        anomaly_detected = bool(ctx.get("anomaly_detected"))
        severity = ((ctx.get("anomaly_details") or {}).get("severity") or "none").lower()
        if fused > 0.8 and not anomaly_detected:
            health = "OK"
        elif (0.5 <= fused <= 0.8) or (anomaly_detected and severity in {"low", "medium"}):
            health = "UNCERTAIN"
        else:
            health = "BAD"

        # Skip expensive optional processing for speed

        event = {
            "timestamp": time.time(),
            "raw_address": request.raw_address,
            "cleaned": ctx.get("cleaned_address"),
            "integrity": ctx.get("integrity"),
            "ml_results": ctx.get("ml_results"),
            "here_results": ctx.get("here_results"),
            "checks": ctx.get("geospatial_checks"),
            "confidence": ctx.get("fused_confidence"),
            "confidence_sources": ctx.get("confidence_sources"),
            "anomaly": {
                "detected": anomaly_detected,
                "reasons": ctx.get("anomaly_reasons"),
                "details": ctx.get("anomaly_details"),
            },
            "self_heal": actions,
            "addons": addons_payload,
            "health": health,
            "processing_time_ms": processing_time_ms,
            "success": True,
        }

        # Backward-compatibility keys for existing clients/tests
        event["cleaned_address"] = ctx.get("cleaned_address")
        event["cleaned_components"] = ctx.get("cleaned_components")
        event["geospatial_checks"] = ctx.get("geospatial_checks")
        event["fused_confidence"] = ctx.get("fused_confidence")
        event["anomaly_detected"] = anomaly_detected
        event["anomaly_reasons"] = ctx.get("anomaly_reasons")
        event["anomaly_details"] = ctx.get("anomaly_details")
        event["self_heal_actions"] = actions

        try:
            await log_event(event)
        except Exception as log_error:
            print(f"Event logging failed (non-fatal): {log_error}")

        # Cache composite result keyed by raw_address+addons
        try:
            _set_cached_result(cache_key, {"event": event, "processing_time_ms": processing_time_ms})
        except Exception:
            pass

        return AddressResponse(success=True, event=event, processing_time_ms=processing_time_ms)
    except Exception as e:
        import traceback
        print(f"\n{'='*60}")
        print(f"ERROR in process_address_v3:")
        print(f"{'='*60}")
        print(traceback.format_exc())
        print(f"{'='*60}\n")
        processing_time_ms = (time.time() - start) * 1000
        error_event = {
            "timestamp": time.time(),
            "raw_address": request.raw_address,
            "error": str(e),
            "error_type": type(e).__name__,
            "processing_time_ms": processing_time_ms,
            "success": False,
        }
        try:
            await log_event(error_event)
        except Exception as log_error:
            print(f"Failed to log error event: {log_error}")
        raise HTTPException(status_code=500, detail={
            "error": str(e),
            "error_type": type(e).__name__,
            "processing_time_ms": processing_time_ms,
        })


@app.post("/delivery-navigation")
async def delivery_navigation(request: Dict[str, Any]):
    """Get delivery navigation insights.

    Preferred request body:
    {
        "destination": {"lat": float, "lon": float},
        "transport_mode": "car"  # optional, default "car"
    }

    Note: If an explicit `origin` is provided it will be ignored by the
    current implementation which selects the nearest warehouse as origin.
    """
    try:
        # Only destination is required for the warehouse-based navigation flow
        destination = request.get("destination")
        transport_mode = request.get("transport_mode", "car")

        if not destination:
            raise HTTPException(status_code=400, detail="Destination required")

        # Call the service using explicit keyword args to avoid argument-order bugs
        result = get_delivery_navigation(destination=destination, transport_mode=transport_mode)
        return result
    except HTTPException:
        # Re-raise HTTPExceptions unchanged
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/residential-safety")
async def residential_safety(request: Dict[str, Any]):
    """Assess residential safety for a location.

    Request body:
    {
        "lat": float,
        "lon": float
    }
    """
    try:
        lat = request.get("lat")
        lon = request.get("lon")

        if lat is None or lon is None:
            raise HTTPException(status_code=400, detail="Latitude and longitude required")

        result = assess_residential_safety(lat, lon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Uvicorn run guard
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=False,
        log_level="info"
    )
