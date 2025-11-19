# LocalLens Backend API

Advanced address processing and geocoding service with ML-based validation, geospatial checks, and intelligent anomaly detection.

## Features

- **Multi-Source Geocoding**: Combines ML embeddings, HERE Maps API (with mock mode), and LLM (OpenRouter/OpenAI)
- **Data Integrity Scoring**: Validates address quality with component-based scoring
- **Geospatial Validation**: Cross-validates coordinates against pincode centroids and city boundaries
- **Confidence Fusion**: Weighted confidence scoring from multiple sources
- **Anomaly Detection**: 6-rule system detecting quality issues
- **Self-Healing**: Automatic correction strategies for detected anomalies
- **Event Logging**: CSV-based logging for auditing and analysis
- **Smart Caching**: In-memory cache with 1-hour TTL and LRU eviction

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file (or copy `.env.example`):

```env
# Required
HERE_API_KEY=your_here_api_key_here

# Optional
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here
OPENAI_API_KEY=your_openai_key_here
EMBED_MODEL=all-MiniLM-L6-v2
PORT=8000

# Mock mode for offline testing (set to 1 to enable)
MOCK_HERE=0
```

**Note**: For offline testing without a HERE API key, set `MOCK_HERE=1`.

### 3. Pre-Build ML Geocoder Indices (First Time Only)

```bash
python build_geocoder_indices.py
```

This will:
- Load `data/IndiaPostalCodes.csv` (155,570 records)
- Build PIN, city, and locality lookup indices
- Serialize to `data/indices/*.pkl` for instant loading (~700ms vs ~2-3s)

**Performance**: Pre-built indices load **~3-4x faster** than CSV rebuild on every request.

### 4. Generate ML Embeddings (First Time Only)

```bash
python generate_embeddings.py
```

This will:
- Extract unique cities (~19,238 addresses)
- Generate embeddings using SentenceTransformer
- Save to `data/address_embeddings.npy` and `data/addresses.npy`

### 5. Run the Server

```bash
# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000

# Development mode with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Mock HERE mode (offline testing)
MOCK_HERE=1 uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6. Test the API

**Interactive Documentation**: http://localhost:8000/docs

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Process an Address**:
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"raw_address": "123 MG Road, Bengaluru 560001"}'
```

## API Endpoints

### `GET /`
Health check endpoint returning service status.

### `GET /health`
Detailed health check with configuration info:
- Embedding model
- Port
- HERE API configured
- LLM API configured (OpenRouter or OpenAI)

### `POST /process`
Main endpoint for address processing.

**Request Body**:
```json
{
  "raw_address": "123 MG Road, Bengaluru 560001"
}
```

**Validation Rules**:
- Length: 5-500 characters
- Cannot be empty or whitespace-only

**Response**:
```json
{
  "success": true,
  "processing_time_ms": 1234.56,
  "event": {
    "timestamp": 1700000000.0,
    "raw_address": "123 MG Road, Bengaluru 560001",
    "cleaned_address": "123 MG Road, Bengaluru 560001",
    "integrity": {
      "score": 85,
      "issues": [],
      "components": {...}
    },
    "ml_results": {
      "top_result": {...},
      "confidence": 0.92,
      "candidates": [...]
    },
    "here_results": {
      "primary_result": {...},
      "confidence": 0.95
    },
    "fused_confidence": 0.89,
    "anomaly_detected": false,
    "anomaly_reasons": [],
    "self_heal_actions": null
  }
}
```

## Pipeline Architecture

The `/process` endpoint executes a 11-step pipeline:

1. **Cache Check**: Returns cached result if available (< 1 hour old)
2. **Address Cleaning**: LLM-based (OpenRouter/OpenAI) or deterministic fallback
3. **Integrity Scoring**: Component-based quality validation
4. **ML Geocoding**: Embedding similarity search against 19K+ addresses
5. **HERE Geocoding**: External validation (real or mock)
6. **Geospatial Checks**: Distance validation, pincode/city consistency
7. **Confidence Fusion**: Weighted scoring from all sources
8. **Anomaly Detection**: 6-rule system (low confidence, mismatches, etc.)
9. **Self-Healing**: Automatic correction if anomalies detected
10. **Event Logging**: CSV logging to `logs/events.csv`
11. **Result Caching**: Store for future identical requests

## Testing

Run the comprehensive test suite:

```bash
# All tests
python -X utf8 tests/test_comprehensive.py

# Specific test suites
python -X utf8 tests/test_helpers.py
python -X utf8 tests/test_integrity.py
python -X utf8 tests/test_here_geocoder.py

# Mock HERE mode tests
MOCK_HERE=1 python -X utf8 tests/test_comprehensive.py
```

## Mock HERE Mode

For development and testing without a real HERE API key:

1. Set `MOCK_HERE=1` in `.env` or as environment variable
2. Mock geocoder returns:
   - Pincode centroid coordinates (if pincode found)
   - City-based fallback for major cities
   - Confidence scores: 0.9 (pincode), 0.85 (city), 0.75 (fallback)

```bash
# Start with mock mode
MOCK_HERE=1 uvicorn main:app --host 0.0.0.0 --port 8000
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Settings and environment config
├── requirements.txt        # Python dependencies
├── generate_embeddings.py  # Embedding generation script
├── .env                    # Environment variables (create this)
│
├── data/
│   ├── IndiaPostalCodes.csv      # 155K postal code records
│   ├── address_embeddings.npy    # Pre-computed embeddings
│   ├── addresses.npy             # Address list
│   └── city_boundaries.json      # City boundary polygons (optional)
│
├── services/
│   ├── address_cleaner.py        # LLM (OpenRouter/OpenAI) + deterministic cleaning
│   ├── ml_geocoder.py            # Embedding-based geocoding
│   ├── here_geocoder.py          # HERE Maps API (+ mock)
│   ├── integrity.py              # Data quality scoring
│   ├── geospatial.py             # Coordinate validation
│   ├── confidence.py             # Multi-source fusion
│   ├── anomaly.py                # Anomaly detection (6 rules)
│   └── self_heal.py              # Automatic correction
│
├── utils/
│   ├── helpers.py          # Text processing, haversine, etc.
│   └── logger.py           # CSV event logging
│
├── models/
│   └── embedder.py         # SentenceTransformer wrapper
│
├── tests/
│   ├── test_comprehensive.py     # Full integration tests
│   ├── test_helpers.py           # Helper function tests
│   ├── test_integrity.py         # Integrity scoring tests
│   ├── test_here_geocoder.py     # Mock HERE tests
│   └── demo_*.py                 # Demo scripts
│
└── logs/
    └── events.csv          # Processing event logs
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HERE_API_KEY` | Yes* | - | HERE Maps API key (*not needed if `MOCK_HERE=1`) |
| `OPENROUTER_API_KEY` | No | - | OpenRouter API key for advanced cleaning (preferred) |
| `OPENAI_API_KEY` | No | - | OpenAI API key for advanced cleaning |
| `EMBED_MODEL` | No | `all-MiniLM-L6-v2` | SentenceTransformer model name |
| `PORT` | No | `8000` | Server port |
| `MOCK_HERE` | No | `False` | Enable mock HERE mode for offline testing |

### Caching Configuration

Configured in `main.py`:
- **Max cache size**: 1000 entries
- **TTL**: 1 hour
- **Eviction**: LRU (Least Recently Used)

### Logging

Event logs are written to `logs/events.csv` with the following columns:
- `timestamp`, `raw_address`, `cleaned_address`, `integrity_score`
- `ml_confidence`, `here_confidence`, `fused_confidence`
- `ml_lat`, `ml_lon`, `here_lat`, `here_lon`
- `ml_here_mismatch_km`, `anomaly_detected`, `anomaly_reasons`
- `self_heal_actions`, `processing_time_ms`, `success`

## Performance

- **ML Geocoding**: ~50-100ms (first call loads embeddings)
- **HERE API**: ~200-500ms (real API), ~5ms (mock)
- **LLM Cleaning**: ~500-1000ms (when enabled)
- **Cache Hit**: ~1-2ms
- **Total Pipeline**: ~1-2 seconds (uncached), ~1-2ms (cached)

## Development

### Adding New Anomaly Rules

Edit `services/anomaly.py`:

```python
def detect_anomaly(metrics, integrity_score, fused_conf, geospatial_checks):
    reasons = []
    
    # Add your custom rule
    if your_condition:
        reasons.append({
            "rule": "your_rule_name",
            "severity": "high",
            "message": "Description of the issue"
        })
    
    return len(reasons) > 0, reasons
```

### Adding New Self-Heal Strategies

Edit `services/self_heal.py`:

```python
async def self_heal(raw, cleaned, ml_candidates, here_resp, reasons):
    actions = []
    
    # Add your strategy
    if "your_rule_name" in [r["rule"] for r in reasons]:
        actions.append({
            "strategy": "your_strategy",
            "action": "Description of what you did",
            "result": {"your": "result"}
        })
    
    return actions
```

## Troubleshooting

### Embeddings Not Loading
```bash
# Regenerate embeddings
python generate_embeddings.py
```

### HERE API Errors
- Check `HERE_API_KEY` in `.env`
- Or enable mock mode: `MOCK_HERE=1`

### LLM Cleaning Failures
- Cleaning automatically falls back to deterministic method
- Check `OPENROUTER_API_KEY` or `OPENAI_API_KEY` if needed

### Cache Issues
- Restart server to clear in-memory cache
- Or implement Redis for persistent caching

## Production Deployment

### Security Recommendations

1. **Remove API keys from `.env`**: Use secrets management (AWS Secrets Manager, Azure Key Vault)
2. **Add API authentication**: Implement JWT or API key middleware
3. **Configure CORS properly**: Restrict `allow_origins` to your frontend domain
4. **Enable HTTPS**: Use reverse proxy (nginx, Caddy) with SSL certificates
5. **Rate limiting**: Add middleware to prevent abuse

### Scaling Recommendations

1. **Use Redis for caching**: Replace in-memory cache with Redis
2. **Use PostgreSQL for logs**: Replace CSV logging with database
3. **Add load balancer**: Run multiple uvicorn workers
4. **Use vector database**: Replace numpy search with Pinecone/Weaviate/Qdrant
5. **Add monitoring**: Integrate Prometheus, Grafana, or Datadog

### Example Production Start

```bash
# With 4 workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Behind nginx reverse proxy
uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4 --proxy-headers
```

## License

[Your License Here]

## Support

For issues, questions, or contributions, please [open an issue](your-repo-url).
