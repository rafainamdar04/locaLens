"""Quick test of embedding generation with a small sample."""
import os
import warnings

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from pathlib import Path
import sys

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from models.embedder import Embedder

print("=" * 70)
print("Quick Embedding Test (100 addresses)")
print("=" * 70)

# Load dataset
data_dir = backend_dir / "data"
input_csv = data_dir / "IndiaPostalCodes.csv"

print(f"\n[LOAD] Loading dataset...")
df = pd.read_csv(input_csv)
print(f"   Total records: {len(df):,}")

# Extract first 100 unique addresses
print("\n[EXTRACT] Extracting first 100 unique addresses...")
addresses = df['City'].dropna().unique()[:100].tolist()
print(f"   Selected {len(addresses)} addresses")

# Initialize embedder
print("\n[INIT] Initializing Embedder...")
embedder = Embedder()

# Generate embeddings
print("\n[PROCESS] Generating embeddings...")
embeddings = embedder.encode(addresses, batch_size=32, show_progress_bar=True)

print(f"\n[SUCCESS] Complete!")
print(f"   Shape: {embeddings.shape}")
print(f"   Size: {embeddings.nbytes / 1024:.2f} KB")

print("\n" + "=" * 70)
