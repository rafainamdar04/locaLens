"""
Quick benchmark: pickle load vs CSV rebuild for ML geocoder indices.
"""
import time
from pathlib import Path
import pickle

# Simulate pickle load
indices_dir = Path(__file__).parent / "data" / "indices"

print("="*60)
print("ML GEOCODER INDEX LOADING BENCHMARK")
print("="*60)

# Test pickle load
start = time.time()
with open(indices_dir / "pin_index.pkl", "rb") as f:
    pin_idx = pickle.load(f)
with open(indices_dir / "city_index.pkl", "rb") as f:
    city_idx = pickle.load(f)
with open(indices_dir / "locality_index.pkl", "rb") as f:
    locality_idx = pickle.load(f)
pickle_time_ms = (time.time() - start) * 1000

print(f"\n✓ Pickle load: {pickle_time_ms:.1f}ms")
print(f"  - PIN index: {len(pin_idx):,} entries")
print(f"  - City index: {len(city_idx):,} entries")
print(f"  - Locality index: {len(locality_idx):,} entries")

# Estimate CSV rebuild (from build_geocoder_indices.py logs: ~2-3s)
print(f"\n✗ CSV rebuild (without pickle): ~2000-3000ms")
print(f"\nSpeedup: ~{2500/pickle_time_ms:.1f}x faster with pre-built indices")
print("="*60)
