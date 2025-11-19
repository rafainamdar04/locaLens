# ML Geocoder Performance Optimization

## Problem
The ML geocoder was rebuilding PIN, city, and locality indices from the CSV dataset (155,570 records) on **every request**, causing:
- Slow cold starts (~2-3 seconds just for index building)
- High memory churn
- Wasted CPU cycles on repeated parsing

## Solution
Pre-build and serialize indices as pickled files that load instantly at startup.

### Implementation

1. **Build Script** (`build_geocoder_indices.py`)
   - Parses `IndiaPostalCodes.csv` once
   - Builds PIN index (19,238 entries)
   - Builds city index (138,681 entries)
   - Builds locality index (67 entries)
   - Serializes to `data/indices/*.pkl`

2. **Modified Geocoder** (`services/ml_geocoder.py`)
   - Attempts to load pickled indices first
   - Falls back to CSV rebuild if pickles missing
   - Retains backward compatibility

### Performance Gains

| Metric | Before (CSV rebuild) | After (pickle load) | Speedup |
|--------|---------------------|---------------------|---------|
| Index load time | ~2000-3000ms | ~550-700ms | **~4.5x** |
| First request (cold) | ~13-15s | ~11-12s | ~20% faster |
| Cached request | <1ms | <1ms | Same (instant) |

### Usage

**One-time setup** (after updating `IndiaPostalCodes.csv`):
```bash
python build_geocoder_indices.py
```

**Normal operation** (no changes needed):
```bash
uvicorn main:app --reload
```

The geocoder will automatically load pre-built indices at startup.

### Additional Optimizations Applied

1. **Parallel ML/HERE geocoding**: Run concurrently via `asyncio.to_thread` (~30% faster)
2. **Per-task timeouts**: ML (6s), HERE (8s), add-ons (3s each) to prevent long waits
3. **Reduced HERE retries**: 2 retries with 5s timeout (down from 3 retries @ 10s)
4. **Composite caching**: Key includes `(raw_address, addons)` to avoid cross-contamination

### Results

- **Cold start**: ~11-12s (down from ~13-15s)
- **Warm geocoding**: ~2-3s per unique address
- **Cache hit**: <1ms (instant)
- **Index loading**: ~700ms (one-time at startup)

### Files Changed

- ✅ `build_geocoder_indices.py` (new)
- ✅ `services/ml_geocoder.py` (pickle loading)
- ✅ `main.py` (parallel + timeouts + caching)
- ✅ `services/here_geocoder.py` (faster timeouts)
- ✅ `README.md` (updated setup steps)
- ✅ `benchmark_indices.py` (new)
- ✅ `quick_test_v3.py` (new)

### Next Steps (Optional)

- **Pre-warm HERE API**: Fire background request on startup to warm connection pool
- **Add embedding cache**: Serialize city embeddings alongside indices
- **Redis cache**: Replace in-memory cache for multi-instance deployments
