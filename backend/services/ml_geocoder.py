"""Hybrid ML geocoder optimized for Indian addresses.

Implements a robust, signal-first approach:
- Primary: Pincode-based geolocation using India postal dataset
- Secondary: City-level matching with fuzzy matching
- Fallback: Embedding similarity (paraphrase-multilingual-mpnet-base-v2) only when no PIN/city

Strict rules:
- Never cross states when PIN present
- Never allow >150 km deviation when PIN present
- Embeddings never override PIN or City when present
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import math
import pickle

import pandas as pd

try:
    from rapidfuzz import fuzz, process as rf_process
    from rapidfuzz.distance import Levenshtein
    RAPIDFUZZ_AVAILABLE = True
except Exception:
    RAPIDFUZZ_AVAILABLE = False
    Levenshtein = None  # type: ignore

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except Exception:
    np = None  # type: ignore
    SentenceTransformer = None  # type: ignore
    ST_AVAILABLE = False

from utils.helpers import haversine


# Caches
_DF: Optional[pd.DataFrame] = None
_PIN_INDEX: Optional[Dict[str, Dict[str, Any]]] = None
_CITY_INDEX: Optional[Dict[Tuple[str, Optional[str]], Dict[str, Any]]] = None
_LOCALITY_INDEX: Optional[Dict[str, Dict[str, Any]]] = None
_LANDMARK_INDEX: Optional[Dict[str, Dict[str, Any]]] = None
_CITY_ALIASES: Dict[str, str] = {
    'bombay': 'mumbai', 'bangalore': 'bengaluru', 'calcutta': 'kolkata',
    'madras': 'chennai', 'poona': 'pune', 'banaras': 'varanasi',
    'trivandrum': 'thiruvananthapuram', 'pondicherry': 'puducherry',
    'cawnpore': 'kanpur', 'baroda': 'vadodara', 'mysore': 'mysuru',
}
_EMB_MODEL: Optional[SentenceTransformer] = None
_EMB_CORPUS: Optional[List[str]] = None
_EMB_CENTERS: Optional[List[Tuple[float, float, str, str]]] = None  # (lat, lon, city, state)
_EMB_VECTORS: Optional["np.ndarray"] = None


def _load_dataset() -> pd.DataFrame:
    global _DF
    if _DF is not None:
        return _DF
    data_path = Path(__file__).parent.parent / "data" / "IndiaPostalCodes.csv"
    if not data_path.exists():
        print("[ML GEOCODER] IndiaPostalCodes.csv not found, ML geocoding disabled")
        _DF = pd.DataFrame()  # Empty dataframe
        return _DF
    _DF = pd.read_csv(data_path)
    # basic cleaning
    _DF = _DF.dropna(subset=["Lat", "Lng"]).copy()
    if "PIN" in _DF.columns:
        _DF["PIN"] = _DF["PIN"].astype(str).str.strip()
    for col in ["City", "District", "State"]:
        if col in _DF.columns:
            _DF[col] = _DF[col].astype(str).str.strip()
    print(f"[ML GEOCODER] Loaded {len(_DF)} records from IndiaPostalCodes.csv")
    return _DF


def _build_pin_index() -> Dict[str, Dict[str, Any]]:
    global _PIN_INDEX
    if _PIN_INDEX is not None:
        return _PIN_INDEX
    # Try loading pre-built pickle first
    indices_dir = Path(__file__).parent.parent / "data" / "indices"
    pin_pkl = indices_dir / "pin_index.pkl"
    if pin_pkl.exists():
        try:
            with open(pin_pkl, "rb") as f:
                _PIN_INDEX = pickle.load(f)
            print(f"[ML GEOCODER] Loaded PIN index from pickle: {len(_PIN_INDEX)} entries")
            return _PIN_INDEX
        except Exception as e:
            print(f"[ML GEOCODER] Failed to load PIN pickle: {e}. Rebuilding...")
    # Fallback: build from CSV
    df = _load_dataset()
    grp = df.groupby("PIN")
    index: Dict[str, Dict[str, Any]] = {}
    for pin, g in grp:
        lat = float(g["Lat"].mean())
        lon = float(g["Lng"].mean())
        city = g["City"].mode().iloc[0] if "City" in g else None
        dist = g["District"].mode().iloc[0] if "District" in g else None
        state = g["State"].mode().iloc[0] if "State" in g else None
        index[str(pin)] = {
            "pincode": str(pin),
            "city": city,
            "district": dist,
            "state": state,
            "lat": lat,
            "lon": lon,
        }
    _PIN_INDEX = index
    print(f"[ML GEOCODER] Built PIN index from CSV: {len(_PIN_INDEX)} entries")
    return _PIN_INDEX


def _fuzzy_pin_lookup(query_pin: str, max_distance: int = 2) -> Optional[Dict[str, Any]]:
    """Find closest matching PIN using Levenshtein distance for typos."""
    if not query_pin or not RAPIDFUZZ_AVAILABLE or Levenshtein is None:
        return None
    index = _build_pin_index()
    # Quick exact check first
    if query_pin in index:
        return index[query_pin]
    # Fuzzy search only for 6-digit PINs with typos
    if not query_pin.isdigit() or len(query_pin) not in (5, 6, 7):
        return None
    best_pin = None
    best_dist = max_distance + 1
    for pin in index.keys():
        dist = Levenshtein.distance(query_pin, pin)
        if dist < best_dist:
            best_dist = dist
            best_pin = pin
    return index[best_pin] if best_pin and best_dist <= max_distance else None


def _build_city_index() -> Dict[Tuple[str, Optional[str]], Dict[str, Any]]:
    global _CITY_INDEX
    if _CITY_INDEX is not None:
        return _CITY_INDEX
    # Try loading pre-built pickle first
    indices_dir = Path(__file__).parent.parent / "data" / "indices"
    city_pkl = indices_dir / "city_index.pkl"
    if city_pkl.exists():
        try:
            with open(city_pkl, "rb") as f:
                _CITY_INDEX = pickle.load(f)
            print(f"[ML GEOCODER] Loaded city index from pickle: {len(_CITY_INDEX)} entries")
            return _CITY_INDEX
        except Exception as e:
            print(f"[ML GEOCODER] Failed to load city pickle: {e}. Rebuilding...")
    # Fallback: build from CSV
    df = _load_dataset()
    key_rows: Dict[Tuple[str, Optional[str]], Dict[str, Any]] = {}
    if "City" not in df.columns:
        _CITY_INDEX = {}
        return _CITY_INDEX
    grp = df.groupby(["City", "State"], dropna=False)
    for (city, state), g in grp:
        try:
            lat = float(g["Lat"].mean())
            lon = float(g["Lng"].mean())
        except Exception:
            continue
        district = g["District"].mode().iloc[0] if "District" in g else None
        any_pin = str(g["PIN"].iloc[0]) if "PIN" in g else None
        city_key = str(city).strip().lower() if isinstance(city, str) else None
        state_key = str(state).strip().lower() if isinstance(state, str) else None
        info = {
            "city": str(city) if isinstance(city, str) else None,
            "state": str(state) if isinstance(state, str) else None,
            "district": district,
            "lat": lat,
            "lon": lon,
            "example_pincode": any_pin,
        }
        key_rows[(city_key, state_key)] = info
        if city_key and city_key in _CITY_ALIASES:
            alias = _CITY_ALIASES[city_key]
            key_rows[(alias, state_key)] = info
    _CITY_INDEX = key_rows
    print(f"[ML GEOCODER] Built city index from CSV: {len(_CITY_INDEX)} entries")
    return _CITY_INDEX


def _build_locality_index() -> Dict[str, Dict[str, Any]]:
    """Build index for sub-city localities (e.g., Andheri West, Koramangala)."""
    global _LOCALITY_INDEX
    if _LOCALITY_INDEX is not None:
        return _LOCALITY_INDEX
    # Try loading pre-built pickle first
    indices_dir = Path(__file__).parent.parent / "data" / "indices"
    locality_pkl = indices_dir / "locality_index.pkl"
    if locality_pkl.exists():
        try:
            with open(locality_pkl, "rb") as f:
                _LOCALITY_INDEX = pickle.load(f)
            print(f"[ML GEOCODER] Loaded locality index from pickle: {len(_LOCALITY_INDEX)} entries")
            return _LOCALITY_INDEX
        except Exception as e:
            print(f"[ML GEOCODER] Failed to load locality pickle: {e}. Rebuilding...")
    # Fallback: build from CSV
    df = _load_dataset()
    index: Dict[str, Dict[str, Any]] = {}
    if "City" in df.columns:
        for _, row in df.iterrows():
            city_val = str(row.get("City", "")).strip().lower()
            if ' - ' in city_val or ', ' in city_val:
                parts = city_val.replace(' - ', ',').split(',')
                for part in parts:
                    part = part.strip()
                    if len(part) > 3 and part not in index:
                        try:
                            index[part] = {
                                "locality": part,
                                "city": str(row.get("City", "")),
                                "state": str(row.get("State", "")),
                                "district": str(row.get("District", "")),
                                "lat": float(row["Lat"]),
                                "lon": float(row["Lng"]),
                                "pincode": str(row["PIN"]),
                            }
                        except Exception:
                            continue
    _LOCALITY_INDEX = index
    print(f"[ML GEOCODER] Built locality index from CSV: {len(_LOCALITY_INDEX)} entries")
    return _LOCALITY_INDEX


def _build_landmark_index() -> Dict[str, Dict[str, Any]]:
    """Build index for major landmarks (simplified - can be extended with external data)."""
    global _LANDMARK_INDEX
    if _LANDMARK_INDEX is not None:
        return _LANDMARK_INDEX
    # Static landmark database (can be loaded from file)
    landmarks = {
        'gateway of india': {'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 18.9220, 'lon': 72.8347},
        'india gate': {'city': 'New Delhi', 'state': 'Delhi', 'lat': 28.6129, 'lon': 77.2295},
        'qutub minar': {'city': 'New Delhi', 'state': 'Delhi', 'lat': 28.5244, 'lon': 77.1855},
        'taj mahal': {'city': 'Agra', 'state': 'Uttar Pradesh', 'lat': 27.1751, 'lon': 78.0421},
        'charminar': {'city': 'Hyderabad', 'state': 'Telangana', 'lat': 17.3616, 'lon': 78.4747},
        'victoria memorial': {'city': 'Kolkata', 'state': 'West Bengal', 'lat': 22.5448, 'lon': 88.3426},
    }
    _LANDMARK_INDEX = landmarks
    return _LANDMARK_INDEX


def _best_city_match(query_city: str, query_state: Optional[str]) -> Optional[Dict[str, Any]]:
    index = _build_city_index()
    locality_idx = _build_locality_index()
    landmark_idx = _build_landmark_index()
    
    qcity = (query_city or "").strip().lower()
    qstate = (query_state or None)
    
    # Check if it's a landmark first
    if qcity in landmark_idx:
        lm = landmark_idx[qcity]
        # Try to enrich with PIN from city
        city_key = (lm['city'].lower(), lm['state'].lower())
        if city_key in index:
            return index[city_key]
    
    # Check locality index
    if qcity in locality_idx:
        return locality_idx[qcity]
    
    # Apply alias
    if qcity in _CITY_ALIASES:
        qcity = _CITY_ALIASES[qcity]
    
    # Exact match with same state if provided
    key = (qcity, qstate.strip().lower() if isinstance(qstate, str) else None)
    if key in index:
        return index[key]
    
    # Try any state for that city
    for (c, s), v in index.items():
        if c == qcity:
            return v
    
    # Fuzzy search with token_sort_ratio for better matching
    if RAPIDFUZZ_AVAILABLE and qcity and len(qcity) >= 3:
        candidates = []
        for (c, s), v in index.items():
            if not c:
                continue
            # Use token_sort_ratio for better handling of word order
            score = fuzz.token_sort_ratio(qcity, c)  # 0-100
            if qstate and isinstance(qstate, str) and s:
                state_score = fuzz.ratio(qstate.lower(), s)
                score = 0.7 * score + 0.3 * state_score
            candidates.append((score, v))
        candidates.sort(key=lambda x: x[0], reverse=True)
        # Lower threshold to 75 for better recall
        if candidates and candidates[0][0] >= 75:
            return candidates[0][1]
    
    # Check locality index with fuzzy matching
    if RAPIDFUZZ_AVAILABLE and qcity and len(qcity) >= 4:
        loc_candidates = []
        for loc_key, loc_val in locality_idx.items():
            score = fuzz.token_sort_ratio(qcity, loc_key)
            if score >= 80:
                loc_candidates.append((score, loc_val))
        if loc_candidates:
            loc_candidates.sort(key=lambda x: x[0], reverse=True)
            return loc_candidates[0][1]
    
    return None


def _ensure_same_state(pin_info: Dict[str, Any], city_info: Optional[Dict[str, Any]]) -> bool:
    if not pin_info or not city_info:
        return True
    a = (pin_info.get("state") or "").strip().lower()
    b = (city_info.get("state") or "").strip().lower()
    return (not a) or (not b) or (a == b)


def _embeddings_setup() -> bool:
    global _EMB_MODEL, _EMB_CORPUS, _EMB_VECTORS, _EMB_CENTERS
    print(f"DEBUG: At start - _EMB_VECTORS id: {id(_EMB_VECTORS)}")
    if not ST_AVAILABLE:
        return False
    
    # Try to load pre-generated embeddings first
    if _EMB_VECTORS is None or _EMB_CORPUS is None or _EMB_CENTERS is None:
        try:
            data_dir = Path(__file__).parent.parent / "data"
            embeddings_file = data_dir / "address_embeddings.npy"
            addresses_file = data_dir / "addresses.npy"
            centers_file = data_dir / "indices" / "centers.pkl"
            
            if embeddings_file.exists() and addresses_file.exists() and centers_file.exists():
                print("[ML GEOCODER] Loading pre-generated embeddings and centers...")
                _EMB_VECTORS = np.load(embeddings_file)
                print(f"DEBUG: _EMB_VECTORS assigned, shape: {_EMB_VECTORS.shape}, id: {id(_EMB_VECTORS)}")
                _EMB_CORPUS = np.load(addresses_file, allow_pickle=True).tolist()
                print(f"DEBUG: _EMB_CORPUS assigned, length: {len(_EMB_CORPUS)}, id: {id(_EMB_CORPUS)}")
                
                # Load pre-built centers mapping
                with open(centers_file, "rb") as f:
                    centers_dict = pickle.load(f)
                
                _EMB_CENTERS = []
                for addr in _EMB_CORPUS:
                    if addr in centers_dict:
                        _EMB_CENTERS.append(centers_dict[addr])
                    else:
                        # Fallback for addresses not found in centers
                        _EMB_CENTERS.append((0.0, 0.0, addr, ""))
                
                print(f"DEBUG: _EMB_CENTERS assigned, length: {len(_EMB_CENTERS)}, id: {id(_EMB_CENTERS)}")
                print(f"[ML GEOCODER] Loaded {len(_EMB_CORPUS)} pre-generated embeddings and centers")
                return True
        except Exception as e:
            print(f"[ML GEOCODER] Failed to load pre-generated embeddings: {e}. Falling back to runtime generation...")
            import traceback
            traceback.print_exc()
    
    # Fallback: generate embeddings at runtime (original behavior)
    if _EMB_MODEL is None:
        try:
            _EMB_MODEL = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
        except Exception:
            _EMB_MODEL = None
            return False
    if _EMB_CORPUS is None or _EMB_VECTORS is None or _EMB_CENTERS is None:
        df = _load_dataset()
        # Build corpus from unique city+state rows
        uniq = df.dropna(subset=["City", "State"]).drop_duplicates(subset=["City", "State"])
        _EMB_CORPUS = [f"{row.City}, {row.State}" for _, row in uniq.iterrows()]
        _EMB_CENTERS = [(float(row.Lat), float(row.Lng), str(row.City), str(row.State)) for _, row in uniq.iterrows()]
        try:
            _EMB_VECTORS = _EMB_MODEL.encode(_EMB_CORPUS, normalize_embeddings=True, show_progress_bar=False)  # type: ignore
        except Exception:
            _EMB_CORPUS, _EMB_VECTORS, _EMB_CENTERS = None, None, None
            return False
    return True


def _embedding_search(cleaned: str, top_k: int = 5) -> Tuple[List[Dict[str, Any]], Optional[List[float]]]:
    print(f"DEBUG: _embedding_search called with: '{cleaned}'")
    if not cleaned or not _embeddings_setup():
        print(f"DEBUG: Early return - cleaned: {bool(cleaned)}, setup: {_embeddings_setup()}")
        return [], None
    # When using pre-generated embeddings, we don't need the model for search
    print(f"DEBUG: About to assert - _EMB_VECTORS is None: {_EMB_VECTORS is None}")
    assert _EMB_VECTORS is not None and _EMB_CORPUS is not None and _EMB_CENTERS is not None
    print("DEBUG: Assertion passed")
    try:
        print("DEBUG: Entering try block")
        # For pre-generated embeddings, we need the model for encoding queries
        if _EMB_MODEL is None:
            print("DEBUG: Loading SentenceTransformer model")
            try:
                _EMB_MODEL = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
                print("DEBUG: Model loaded successfully")
            except Exception as e:
                print(f"DEBUG: Failed to load model: {e}")
                raise
        print("DEBUG: About to encode query")
        q = _EMB_MODEL.encode([cleaned], normalize_embeddings=True, show_progress_bar=False)  # type: ignore
        print(f"DEBUG: Query encoded successfully, shape: {q.shape}")
        print(f"DEBUG: Query encoded, shape: {q.shape}")
        sims = (q @ _EMB_VECTORS.T).flatten()  # cosine similarity
        print(f"DEBUG: Similarities computed, shape: {sims.shape}, max: {sims.max():.4f}, min: {sims.min():.4f}")
        idx = sims.argsort()[-top_k:][::-1]
        print(f"DEBUG: Top {top_k} indices: {idx}, scores: {sims[idx]}")
        candidates: List[Dict[str, Any]] = []
        for i in idx:
            lat, lon, city, state = _EMB_CENTERS[i]
            sim = float(sims[i])
            candidates.append({
                "city": city,
                "state": state,
                "district": None,
                "pincode": None,
                "lat": float(lat),
                "lon": float(lon),
                "embedding_similarity": sim,
                "score": min(sim * 0.5, 0.5),
            })
        return candidates, q[0].tolist()  # type: ignore
    except Exception:
        return [], None


def compute_ml_geocode(context: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
    """
    Hybrid geocoder combining PIN, City, and embedding fallback.
    Pure function; reads context and returns dict.
    """
    cleaned = context.get("cleaned_address") or context.get("cleaned") or ""
    integrity = context.get("integrity") or {}
    integ_comp = integrity.get("components") or {}
    pincode = (integ_comp.get("pincode") or "").strip() if integ_comp else ""
    city_hint = (integ_comp.get("city") or "").strip() if integ_comp else ""
    state_hint = (context.get("cleaned_components") or {}).get("state")

    pin_index = _build_pin_index()

    # PRIMARY: exact pincode match
    if pincode and pincode in pin_index:
        info = pin_index[pincode]
        top = {
            "city": info.get("city"),
            "district": info.get("district"),
            "state": info.get("state"),
            "pincode": info.get("pincode"),
            "lat": info.get("lat"),
            "lon": info.get("lon"),
        }
        return {
            "top_result": top,
            "candidates": [top],
            "confidence": 1.0,
            "embedding": None,
        }
    
    # PRIMARY-B: fuzzy pincode match (for typos)
    if pincode:
        fuzzy_info = _fuzzy_pin_lookup(pincode, max_distance=2)
        if fuzzy_info:
            top = {
                "city": fuzzy_info.get("city"),
                "district": fuzzy_info.get("district"),
                "state": fuzzy_info.get("state"),
                "pincode": fuzzy_info.get("pincode"),
                "lat": fuzzy_info.get("lat"),
                "lon": fuzzy_info.get("lon"),
            }
            return {
                "top_result": top,
                "candidates": [top],
                "confidence": 0.95,  # slightly lower for fuzzy match
                "embedding": None,
            }

    # SECONDARY: city-level matching (includes localities and landmarks)
    if city_hint:
        city_info = _best_city_match(city_hint, state_hint)
        if city_info:
            # Adjust confidence based on presence of locality vs just city
            conf = 0.8 if city_info.get("locality") else 0.7
            top = {
                "city": city_info.get("city"),
                "district": city_info.get("district"),
                "state": city_info.get("state"),
                "pincode": city_info.get("example_pincode") or city_info.get("pincode"),
                "lat": city_info.get("lat"),
                "lon": city_info.get("lon"),
            }
            return {
                "top_result": top,
                "candidates": [top],
                "confidence": conf,
                "embedding": None,
            }

    # FALLBACK: embedding search (only when both PIN and city missing)
    candidates, emb_vec = _embedding_search(cleaned, top_k=top_k)
    # Sort by score descending
    candidates = sorted(candidates, key=lambda x: x.get("score", 0.0), reverse=True)[:top_k]
    top = candidates[0] if candidates else None
    
    # Weighted ensemble: combine embedding with any partial signals
    final_conf = 0.0
    if top:
        emb_score = float(top.get("score", 0.0))
        # Boost confidence if city name appears in cleaned text
        city_in_text = 0.0
        if top.get("city"):
            city_lower = str(top["city"]).lower()
            if city_lower in cleaned.lower():
                city_in_text = 0.2
        final_conf = min(emb_score + city_in_text, 0.7)  # cap at 0.7 for embedding-only

    return {
        "top_result": top,
        "candidates": candidates,
        "confidence": round(final_conf, 4),
        "embedding": emb_vec[:10] if isinstance(emb_vec, list) else None,
    }


# Backward-compatible wrapper for pipeline
def compute_ml(context: Dict[str, Any]) -> Dict[str, Any]:
    res = compute_ml_geocode(context)
    top = res.get("top_result")
    return {
        "ml_results": res,
        "ml_top": top,
        "ml_confidence": res.get("confidence", 0.0),
    }


# Legacy function signature for older callers
# Accepts a cleaned address and returns geocode results
from typing import Optional as _Optional  # local alias to avoid name shadowing

def ml_geocode(cleaned_address: str, top_k: int = 5) -> _Optional[Dict[str, Any]]:
    # Check if dataset is available
    df = _load_dataset()
    if df.empty:
        return {
            "top_result": None,
            "candidates": [],
            "confidence": 0.0,
            "embedding": None,
        }
    
    if not cleaned_address or not cleaned_address.strip():
        return {
            "top_result": None,
            "candidates": [],
            "confidence": 0.0,
            "embedding": None,
        }
    try:
        # Compute minimal integrity to extract pincode/city without side effects
        from services.integrity import compute_integrity as _compute_integrity
        integ = _compute_integrity(cleaned_address, cleaned_address)
    except Exception:
        integ = {"score": 0, "components": {}}
    ctx = {
        "cleaned_address": cleaned_address,
        "integrity": integ,
    }
    return compute_ml_geocode(ctx, top_k=top_k)
