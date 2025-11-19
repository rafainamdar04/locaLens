"""
Script to generate embeddings for addresses from the postal codes dataset.

This script:
1. Loads the IndiaPostalCodes.csv dataset
2. Extracts unique addresses (City column)
3. Generates embeddings using the Embedder class
4. Saves embeddings and addresses to .npy files for fast loading
"""
import os
import warnings

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add backend to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from models.embedder import Embedder


def main():
    """Generate and save address embeddings."""
    
    # Define paths
    data_dir = backend_dir / "data"
    input_csv = data_dir / "IndiaPostalCodes.csv"
    output_embeddings = data_dir / "address_embeddings.npy"
    output_addresses = data_dir / "addresses.npy"
    
    print("=" * 70)
    print("Address Embedding Generation")
    print("=" * 70)
    
    # Check if input file exists
    if not input_csv.exists():
        print(f"Error: Input file not found: {input_csv}")
        sys.exit(1)
    
    # Load the dataset
    print(f"\n[LOAD] Loading dataset from: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"   Loaded {len(df):,} records")
    print(f"   Columns: {', '.join(df.columns.tolist())}")
    
    # Extract addresses from City column
    print("\n[EXTRACT] Extracting unique addresses from 'City' column...")
    addresses = df['City'].dropna().unique().tolist()
    print(f"   Found {len(addresses):,} unique addresses")
    
    # Initialize embedder
    print("\n[INIT] Initializing Embedder...")
    embedder = Embedder()
    print(f"   Using model: {embedder.model_name}")
    
    # Generate embeddings
    print("\n[PROCESS] Generating embeddings...")
    print(f"   Processing {len(addresses):,} addresses in batches...")
    embeddings = embedder.encode(
        addresses,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    
    print(f"\n[SUCCESS] Embeddings generated successfully!")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Embedding dimension: {embeddings.shape[1]}")
    print(f"   Data type: {embeddings.dtype}")
    print(f"   Memory size: {embeddings.nbytes / 1024 / 1024:.2f} MB")
    
    # Save embeddings
    print(f"\n[SAVE] Saving embeddings to: {output_embeddings}")
    np.save(output_embeddings, embeddings)
    print(f"   Embeddings saved")
    
    # Save addresses (for reference)
    print(f"\n[SAVE] Saving addresses to: {output_addresses}")
    addresses_array = np.array(addresses, dtype=object)
    np.save(output_addresses, addresses_array)
    print(f"   Addresses saved")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total unique addresses: {len(addresses):,}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print(f"Output files:")
    print(f"  - {output_embeddings.name}")
    print(f"  - {output_addresses.name}")
    print("\n[COMPLETE] Embedding generation completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
