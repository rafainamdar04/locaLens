"""
Demonstration of confidence fusion in a realistic scenario.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.confidence import fuse_confidence


def demo_confidence_scenarios():
    """Demonstrate confidence fusion in realistic geocoding scenarios."""
    
    print("\n" + "="*70)
    print("Confidence Fusion - Realistic Scenarios")
    print("="*70)
    
    # Scenario 1: High Confidence - Perfect Match
    print("\n" + "-"*70)
    print("SCENARIO 1: High Confidence Case")
    print("-"*70)
    print("Context: Clean address, both ML and HERE agree, close match")
    print()
    
    metrics = {
        'ml_similarity': 0.95,      # High ML confidence
        'here_confidence': 0.92,    # High HERE confidence
        'llm_confidence': 0.90      # Good cleaning
    }
    integrity_score = 95            # Clean, complete address
    mismatch_km = 0.3              # Less than 1km apart
    
    confidence = fuse_confidence(metrics, integrity_score, mismatch_km)
    
    print(f"  ML Similarity:     {metrics['ml_similarity']:.2f}")
    print(f"  HERE Confidence:   {metrics['here_confidence']:.2f}")
    print(f"  LLM Confidence:    {metrics['llm_confidence']:.2f}")
    print(f"  Integrity Score:   {integrity_score}/100")
    print(f"  Mismatch Distance: {mismatch_km} km")
    print(f"\n  → FUSED CONFIDENCE: {confidence:.4f} ({confidence*100:.1f}%)")
    print(f"\n  Decision: ✓ ACCEPT - High confidence result")
    
    # Scenario 2: Medium Confidence - Some Discrepancy
    print("\n" + "-"*70)
    print("SCENARIO 2: Medium Confidence Case")
    print("-"*70)
    print("Context: Address needs cleaning, moderate agreement, 4km difference")
    print()
    
    metrics = {
        'ml_similarity': 0.78,      # Decent ML match
        'here_confidence': 0.72,    # Moderate HERE confidence
        'llm_confidence': 0.65      # Some cleaning needed
    }
    integrity_score = 70            # Some data quality issues
    mismatch_km = 4.2              # Few km apart
    
    confidence = fuse_confidence(metrics, integrity_score, mismatch_km)
    
    print(f"  ML Similarity:     {metrics['ml_similarity']:.2f}")
    print(f"  HERE Confidence:   {metrics['here_confidence']:.2f}")
    print(f"  LLM Confidence:    {metrics['llm_confidence']:.2f}")
    print(f"  Integrity Score:   {integrity_score}/100")
    print(f"  Mismatch Distance: {mismatch_km} km")
    print(f"\n  → FUSED CONFIDENCE: {confidence:.4f} ({confidence*100:.1f}%)")
    print(f"\n  Decision: ⚠ REVIEW - Moderate confidence, may need validation")
    
    # Scenario 3: Low Confidence - Major Issues
    print("\n" + "-"*70)
    print("SCENARIO 3: Low Confidence Case")
    print("-"*70)
    print("Context: Poor address data, sources disagree, large mismatch")
    print()
    
    metrics = {
        'ml_similarity': 0.45,      # Low ML confidence
        'here_confidence': 0.38,    # Low HERE confidence
        'llm_confidence': 0.40      # Poor data quality
    }
    integrity_score = 35            # Bad data quality
    mismatch_km = 18.5             # Very far apart (>10km cap)
    
    confidence = fuse_confidence(metrics, integrity_score, mismatch_km)
    
    print(f"  ML Similarity:     {metrics['ml_similarity']:.2f}")
    print(f"  HERE Confidence:   {metrics['here_confidence']:.2f}")
    print(f"  LLM Confidence:    {metrics['llm_confidence']:.2f}")
    print(f"  Integrity Score:   {integrity_score}/100")
    print(f"  Mismatch Distance: {mismatch_km} km (capped at 10km)")
    print(f"\n  → FUSED CONFIDENCE: {confidence:.4f} ({confidence*100:.1f}%)")
    print(f"\n  Decision: ✗ REJECT - Low confidence, trigger self-healing")
    
    # Scenario 4: Only ML Available
    print("\n" + "-"*70)
    print("SCENARIO 4: Single Source (ML Only)")
    print("-"*70)
    print("Context: HERE API unavailable, rely on ML and data quality")
    print()
    
    metrics = {
        'ml_similarity': 0.85,      # Good ML confidence
        'here_confidence': 0.0,     # No HERE result
        'llm_confidence': 0.80      # Good cleaning
    }
    integrity_score = 85            # Good data quality
    mismatch_km = None             # No comparison possible
    
    confidence = fuse_confidence(metrics, integrity_score, mismatch_km)
    
    print(f"  ML Similarity:     {metrics['ml_similarity']:.2f}")
    print(f"  HERE Confidence:   {metrics['here_confidence']:.2f} (unavailable)")
    print(f"  LLM Confidence:    {metrics['llm_confidence']:.2f}")
    print(f"  Integrity Score:   {integrity_score}/100")
    print(f"  Mismatch Distance: None (uses neutral 0.5)")
    print(f"\n  → FUSED CONFIDENCE: {confidence:.4f} ({confidence*100:.1f}%)")
    print(f"\n  Decision: ⚠ ACCEPT - Reduced confidence without second source")
    
    # Scenario 5: Edge Case - Perfect Geocoding, Poor Data
    print("\n" + "-"*70)
    print("SCENARIO 5: Edge Case - Good Geocoding, Poor Input Data")
    print("-"*70)
    print("Context: Geocoders agree but input address had issues")
    print()
    
    metrics = {
        'ml_similarity': 0.90,      # High agreement
        'here_confidence': 0.88,    # High agreement
        'llm_confidence': 0.50      # Poor input quality
    }
    integrity_score = 45            # Poor input data
    mismatch_km = 0.8              # Close match
    
    confidence = fuse_confidence(metrics, integrity_score, mismatch_km)
    
    print(f"  ML Similarity:     {metrics['ml_similarity']:.2f}")
    print(f"  HERE Confidence:   {metrics['here_confidence']:.2f}")
    print(f"  LLM Confidence:    {metrics['llm_confidence']:.2f}")
    print(f"  Integrity Score:   {integrity_score}/100")
    print(f"  Mismatch Distance: {mismatch_km} km")
    print(f"\n  → FUSED CONFIDENCE: {confidence:.4f} ({confidence*100:.1f}%)")
    print(f"\n  Decision: ⚠ REVIEW - Good geocoding but poor input quality")
    
    # Summary
    print("\n" + "="*70)
    print("Summary: Confidence Thresholds")
    print("="*70)
    print("\n  ✓ HIGH (>0.80):   Accept result with high confidence")
    print("  ⚠ MEDIUM (0.50-0.80): Accept but may need validation")
    print("  ✗ LOW (<0.50):    Reject or trigger self-healing")
    print("\n" + "="*70)


if __name__ == "__main__":
    demo_confidence_scenarios()
