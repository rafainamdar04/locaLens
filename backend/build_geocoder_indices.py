"""
Pre-build and serialize ML geocoder indices to avoid runtime overhead.
Run once after updating IndiaPostalCodes.csv:
    python build_geocoder_indices.py
"""
import pickle
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
INDICES_DIR = DATA_DIR / "indices"
INDICES_DIR.mkdir(exist_ok=True)

_CITY_ALIASES: Dict[str, str] = {
    'bombay': 'mumbai', 'bangalore': 'bengaluru', 'calcutta': 'kolkata',
    'madras': 'chennai', 'poona': 'pune', 'banaras': 'varanasi',
    'trivandrum': 'thiruvananthapuram', 'pondicherry': 'puducherry',
    'cawnpore': 'kanpur', 'baroda': 'vadodara', 'mysore': 'mysuru',
}


def build_pin_index(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Build PIN -> location index."""
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
    return index


def build_city_index(df: pd.DataFrame) -> Dict[Tuple[str, Optional[str]], Dict[str, Any]]:
    """Build (city, state) -> location index."""
    key_rows: Dict[Tuple[str, Optional[str]], Dict[str, Any]] = {}
    if "City" not in df.columns:
        return key_rows
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
        # Add alias entries
        if city_key and city_key in _CITY_ALIASES:
            alias = _CITY_ALIASES[city_key]
            key_rows[(alias, state_key)] = info
    return key_rows


def build_locality_index(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Build locality -> location index."""
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
    return index


def main():
    print("[BUILD] Loading IndiaPostalCodes.csv...")
    csv_path = DATA_DIR / "IndiaPostalCodes.csv"
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["Lat", "Lng"]).copy()
    if "PIN" in df.columns:
        df["PIN"] = df["PIN"].astype(str).str.strip()
    for col in ["City", "District", "State"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    print(f"[BUILD] Loaded {len(df)} records")

    print("[BUILD] Building PIN index...")
    pin_index = build_pin_index(df)
    print(f"[BUILD] PIN index: {len(pin_index)} entries")

    print("[BUILD] Building city index...")
    city_index = build_city_index(df)
    print(f"[BUILD] City index: {len(city_index)} entries")

    print("[BUILD] Building locality index...")
    locality_index = build_locality_index(df)
    print(f"[BUILD] Locality index: {len(locality_index)} entries")

    # Serialize
    with open(INDICES_DIR / "pin_index.pkl", "wb") as f:
        pickle.dump(pin_index, f)
    with open(INDICES_DIR / "city_index.pkl", "wb") as f:
        pickle.dump(city_index, f)
    with open(INDICES_DIR / "locality_index.pkl", "wb") as f:
        pickle.dump(locality_index, f)

    print(f"[BUILD] Saved indices to {INDICES_DIR}")
    print("[BUILD] Done! ML geocoder will now load pre-built indices at startup.")


if __name__ == "__main__":
    main()
