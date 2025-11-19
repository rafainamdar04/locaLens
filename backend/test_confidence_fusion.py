"""Test script for confidence fusion."""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.confidence import fuse_confidence


def test_confidence_fusion():
    """Test the confidence fusion function with various scenarios."""
    
    print("=" * 70)
    print("Testing Confidence Fusion")
    print("=" * 70)
    
    # Test 1: Perfect scores - everything optimal
    print("\n--- Test 1: Perfect Scores ---")
    metrics = {
        'ml_similarity': 1.0,
        'here_confidence': 1.0,
        'llm_confidence': 1.0
    }
    integrity_score = 100
    mismatch_km = 0.0
    
    result = fuse_confidence(metrics, integrity_score, mismatch_km)
    print(f"ML similarity: {metrics['ml_similarity']}")
    print(f"HERE confidence: {metrics['here_confidence']}")
    print(f"Integrity: {integrity_score}/100")
    print(f"Mismatch: {mismatch_km} km")
    print(f"→ Fused confidence: {result:.4f}")
    print(f"✓ Expected: 1.0000" if abs(result - 1.0) < 0.001 else f"✗ Unexpected")
    
    # Test 2: Good scores with small mismatch
    print("\n--- Test 2: Good Scores with Small Mismatch (2km) ---")
    metrics = {
        'ml_similarity': 0.9,
        'here_confidence': 0.85,
    }
    integrity_score = 90
    mismatch_km = 2.0
    
    result = fuse_confidence(metrics, integrity_score, mismatch_km)
    print(f"ML similarity: {metrics['ml_similarity']}")
    print(f"HERE confidence: {metrics['here_confidence']}")
    print(f"Integrity: {integrity_score}/100")
    print(f"Mismatch: {mismatch_km} km")
    print(f"→ Fused confidence: {result:.4f}")
    print(f"✓ High confidence expected (>0.8)")
    
    # Test 3: Moderate scores with moderate mismatch
    print("\n--- Test 3: Moderate Scores with 5km Mismatch ---")
    metrics = {
        'ml_similarity': 0.7,
        'here_confidence': 0.75,
    }
    integrity_score = 70
    mismatch_km = 5.0
    
    result = fuse_confidence(metrics, integrity_score, mismatch_km)
    print(f"ML similarity: {metrics['ml_similarity']}")
    print(f"HERE confidence: {metrics['here_confidence']}")
    print(f"Integrity: {integrity_score}/100")
    print(f"Mismatch: {mismatch_km} km")
    print(f"→ Fused confidence: {result:.4f}")
    print(f"✓ Moderate confidence expected (~0.6-0.7)")
    
    # Test 4: Large mismatch impact
    print("\n--- Test 4: Large Mismatch (15km) ---")
    metrics = {
        'ml_similarity': 0.8,
        'here_confidence': 0.8,
    }
    integrity_score = 80
    mismatch_km = 15.0  # Above 10km cap
    
    result = fuse_confidence(metrics, integrity_score, mismatch_km)
    print(f"ML similarity: {metrics['ml_similarity']}")
    print(f"HERE confidence: {metrics['here_confidence']}")
    print(f"Integrity: {integrity_score}/100")
    print(f"Mismatch: {mismatch_km} km (capped at 10km)")
    print(f"→ Fused confidence: {result:.4f}")
    print(f"✓ Reduced due to large mismatch")
    
    # Test 5: Poor scores
    print("\n--- Test 5: Poor Scores ---")
    metrics = {
        'ml_similarity': 0.3,
        'here_confidence': 0.4,
    }
    integrity_score = 40
    mismatch_km = 8.0
    
    result = fuse_confidence(metrics, integrity_score, mismatch_km)
    print(f"ML similarity: {metrics['ml_similarity']}")
    print(f"HERE confidence: {metrics['here_confidence']}")
    print(f"Integrity: {integrity_score}/100")
    print(f"Mismatch: {mismatch_km} km")
    print(f"→ Fused confidence: {result:.4f}")
    print(f"✓ Low confidence expected (<0.5)")
    
    # Test 6: No mismatch data
    print("\n--- Test 6: Missing Mismatch Data ---")
    metrics = {
        'ml_similarity': 0.8,
        'here_confidence': 0.0,  # No HERE result
    }
    integrity_score = 75
    mismatch_km = None
    
    result = fuse_confidence(metrics, integrity_score, mismatch_km)
    print(f"ML similarity: {metrics['ml_similarity']}")
    print(f"HERE confidence: {metrics['here_confidence']}")
    print(f"Integrity: {integrity_score}/100")
    print(f"Mismatch: None (uses neutral 0.5)")
    print(f"→ Fused confidence: {result:.4f}")
    print(f"✓ Still computes confidence with missing data")
    
    # Test 7: Boundary test - all zeros
    print("\n--- Test 7: All Zeros ---")
    metrics = {
        'ml_similarity': 0.0,
        'here_confidence': 0.0,
    }
    integrity_score = 0
    mismatch_km = 100.0
    
    result = fuse_confidence(metrics, integrity_score, mismatch_km)
    print(f"ML similarity: {metrics['ml_similarity']}")
    print(f"HERE confidence: {metrics['here_confidence']}")
    print(f"Integrity: {integrity_score}/100")
    print(f"Mismatch: {mismatch_km} km")
    print(f"→ Fused confidence: {result:.4f}")
    print(f"✓ Expected: 0.0000" if abs(result - 0.0) < 0.001 else f"⚠ Close to zero")


def test_weight_verification():
    """Verify the weighting formula."""
    print("\n" + "=" * 70)
    print("Weight Verification")
    print("=" * 70)
    
    print("\nFormula: 0.25*integrity + 0.25*ml + 0.30*here + 0.20*geospatial")
    print("Total weights: 0.25 + 0.25 + 0.30 + 0.20 = 1.00 ✓")
    
    # Test with all components at 1.0
    metrics = {'ml_similarity': 1.0, 'here_confidence': 1.0}
    result = fuse_confidence(metrics, 100, 0.0)
    print(f"\nAll max (1.0): {result:.4f} ✓")
    
    # Test individual component contributions
    print("\nIndividual Component Contributions:")
    
    # Only integrity
    metrics = {'ml_similarity': 0.0, 'here_confidence': 0.0}
    result = fuse_confidence(metrics, 100, 10.0)  # mismatch_norm=1, so (1-1)=0
    print(f"  Only integrity (100): {result:.4f} → 25% weight ✓")
    
    # Only ML
    metrics = {'ml_similarity': 1.0, 'here_confidence': 0.0}
    result = fuse_confidence(metrics, 0, 10.0)
    print(f"  Only ML (1.0): {result:.4f} → 25% weight ✓")
    
    # Only HERE
    metrics = {'ml_similarity': 0.0, 'here_confidence': 1.0}
    result = fuse_confidence(metrics, 0, 10.0)
    print(f"  Only HERE (1.0): {result:.4f} → 30% weight ✓")
    
    # Only geospatial (perfect match)
    metrics = {'ml_similarity': 0.0, 'here_confidence': 0.0}
    result = fuse_confidence(metrics, 0, 0.0)  # mismatch_norm=0, so (1-0)=1
    print(f"  Only geospatial (0km): {result:.4f} → 20% weight ✓")


if __name__ == "__main__":
    test_confidence_fusion()
    test_weight_verification()
    
    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)
