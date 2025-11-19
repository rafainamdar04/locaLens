import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.addons import deliverability, consensus, property_risk, fraud, neighborhood

# Deliverability

def test_deliverability_schema():
    result = deliverability.evaluate("123 MG Road, Bangalore, Karnataka 560001")
    assert 'breakdown' in result
    assert 'reasons' in result
    assert isinstance(result['breakdown'], dict)
    assert isinstance(result['reasons'], list)
    assert 'score' in result
    assert 0 <= result['score'] <= 1

def test_deliverability_timeout():
    # Simulate slow input or mock timeout
    result = deliverability.evaluate("timeout_test", timeout=0.001)
    assert result.get('timeout', False) is True

# Consensus

def test_consensus_schema():
    sources = [0.8, 0.7, 0.9]
    result = consensus.evaluate(sources)
    assert 'thresholds' in result
    assert 'sources' in result
    assert 'score' in result
    assert isinstance(result['sources'], list)
    assert 0 <= result['score'] <= 1

def test_consensus_timeout():
    result = consensus.evaluate([0.5], timeout=0.001)
    assert result.get('timeout', False) is True

# Property Risk

def test_property_risk_schema():
    result = property_risk.evaluate("123 MG Road, Bangalore, Karnataka 560001")
    assert 'reasons' in result
    assert 'missing_data' in result
    assert 'score' in result
    assert isinstance(result['reasons'], list)
    assert isinstance(result['missing_data'], list)
    assert 0 <= result['score'] <= 1

def test_property_risk_timeout():
    result = property_risk.evaluate("timeout_test", timeout=0.001)
    assert result.get('timeout', False) is True

# Fraud

def test_fraud_schema():
    result = fraud.evaluate("123 MG Road, Bangalore, Karnataka 560001")
    assert 'score' in result
    assert 0 <= result['score'] <= 1

def test_fraud_timeout():
    result = fraud.evaluate("timeout_test", timeout=0.001)
    assert result.get('timeout', False) is True

# Neighborhood

def test_neighborhood_schema():
    result = neighborhood.evaluate("123 MG Road, Bangalore, Karnataka 560001")
    assert 'score' in result
    assert 0 <= result['score'] <= 1

def test_neighborhood_timeout():
    result = neighborhood.evaluate("timeout_test", timeout=0.001)
    assert result.get('timeout', False) is True
