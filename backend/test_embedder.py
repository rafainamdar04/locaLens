"""
Test script for the Embedder class.
Quick verification that the embedder loads and encodes correctly.
"""
from pathlib import Path
import sys

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from models.embedder import Embedder


def test_embedder():
    """Test the Embedder class functionality."""
    
    print("=" * 70)
    print("Testing Embedder Class")
    print("=" * 70)
    
    # Test 1: Initialize embedder
    print("\n1️⃣ Testing initialization...")
    embedder = Embedder()
    print(f"   ✓ Embedder created: {embedder}")
    
    # Test 2: Encode single string
    print("\n2️⃣ Testing single string encoding...")
    test_text = "123 Main Street, Mumbai, Maharashtra"
    embedding = embedder.encode(test_text, show_progress_bar=False)
    print(f"   Input: '{test_text}'")
    print(f"   Output shape: {embedding.shape}")
    print(f"   Output dtype: {embedding.dtype}")
    print(f"   Sample values: {embedding[:5]}")
    print(f"   ✓ Single string encoding works")
    
    # Test 3: Encode multiple strings
    print("\n3️⃣ Testing batch encoding...")
    test_texts = [
        "Delhi, India",
        "Bangalore, Karnataka",
        "Kolkata, West Bengal",
        "Chennai, Tamil Nadu"
    ]
    embeddings = embedder.encode(test_texts, show_progress_bar=False)
    print(f"   Input: {len(test_texts)} addresses")
    print(f"   Output shape: {embeddings.shape}")
    print(f"   Expected: ({len(test_texts)}, {embedder.embedding_dimension})")
    print(f"   ✓ Batch encoding works")
    
    # Test 4: Check embedding dimension
    print("\n4️⃣ Testing embedding dimension property...")
    dim = embedder.embedding_dimension
    print(f"   Embedding dimension: {dim}")
    print(f"   ✓ Dimension property works")
    
    # Test 5: Verify normalization
    print("\n5️⃣ Testing embedding normalization...")
    import numpy as np
    norms = np.linalg.norm(embeddings, axis=1)
    print(f"   L2 norms: {norms}")
    print(f"   All close to 1.0: {np.allclose(norms, 1.0)}")
    print(f"   ✓ Embeddings are normalized")
    
    print("\n" + "=" * 70)
    print("✨ All tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    test_embedder()
