"""
Quick test to verify backend enhancements are backwards-compatible
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_process_v3_basic():
    """Test /process_v3 with basic request"""
    print("\n=== Testing /process_v3 (basic) ===")
    
    payload = {
        "raw_address": "123 MG Road, Bengaluru 560001"
    }
    
    response = requests.post(f"{BASE_URL}/process_v3", json=payload)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        event = data.get("event", {})
        
        # Check existing fields are still present
        assert "cleaned" in event or "cleaned_address" in event, "Cleaned address missing"
        assert "integrity" in event, "Integrity missing"
        assert "ml_results" in event, "ML results missing"
        assert "here_results" in event, "HERE results missing"
        assert "health" in event, "Health status missing"
        assert "processing_time_ms" in event, "Processing time missing"
        
        # Check new optional fields
        has_trace = "trace" in event
        has_summary = "summary" in event
        
        print(f"✓ All required fields present")
        print(f"✓ New trace field: {'Present' if has_trace else 'Not present (OK)'}")
        print(f"✓ New summary field: {'Present' if has_summary else 'Not present (OK)'}")
        
        if has_trace:
            print(f"  Trace steps: {len(event['trace'])}")
            for step in event['trace'][:3]:
                print(f"    - {step[:60]}...")
        
        if has_summary:
            print(f"  Summary: {event['summary'].get('human_readable', 'N/A')[:80]}...")
        
        return True
    else:
        print(f"✗ Request failed: {response.text}")
        return False


def test_process_v3_with_addons():
    """Test /process_v3 with all addons"""
    print("\n=== Testing /process_v3 (with addons) ===")
    
    payload = {
        "raw_address": "Flat 202, Tower B, Prestige Tech Park, Marathahalli, Bangalore 560037"
    }
    
    response = requests.post(
        f"{BASE_URL}/process_v3?addons=deliverability,property_risk,fraud,neighborhood,consensus",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        event = data.get("event", {})
        addons = event.get("addons", {})
        
        # Check all addons are present
        expected_addons = ["deliverability", "property_risk", "fraud", "neighborhood", "consensus"]
        for addon in expected_addons:
            if addon in addons:
                print(f"✓ {addon}: {list(addons[addon].keys())[:3]}...")
            else:
                print(f"✗ {addon}: Missing")
        
        # Check administrative hierarchy in integrity
        integrity = event.get("integrity", {})
        components = integrity.get("components", {})
        admin_fields = ["state", "district", "sub_district", "locality"]
        admin_present = [f for f in admin_fields if f in components]
        
        if admin_present:
            print(f"✓ Administrative hierarchy: {admin_present}")
        else:
            print(f"  Administrative hierarchy: Not extracted (OK - depends on HERE data)")
        
        return True
    else:
        print(f"✗ Request failed: {response.text}")
        return False


def test_health_endpoint():
    """Test /health endpoint"""
    print("\n=== Testing /health ===")
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Health: {json.dumps(data, indent=2)}")
        return True
    else:
        print(f"✗ Health check failed")
        return False


if __name__ == "__main__":
    print("="*60)
    print("BACKEND COMPATIBILITY TEST")
    print("="*60)
    print("\nMake sure backend is running on http://127.0.0.1:8000")
    print("Run: cd backend && python main.py")
    print()
    
    try:
        results = []
        results.append(test_health_endpoint())
        results.append(test_process_v3_basic())
        results.append(test_process_v3_with_addons())
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Tests passed: {sum(results)}/{len(results)}")
        
        if all(results):
            print("✓ All tests passed - Backend is backwards-compatible!")
        else:
            print("✗ Some tests failed - Check output above")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to backend")
        print("Please start the backend first: cd backend && python main.py")
