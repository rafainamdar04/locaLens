"""
Test API Endpoints

Script to test the new monitoring API endpoints.
"""

import requests
import json
import subprocess
import time
import sys

def start_server():
    """Start the server in background."""
    print("Starting server...")
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1", "--port", "8001"
    ], cwd="backend")
    time.sleep(5)  # Wait for server to start
    return process

def test_endpoints():
    """Test the monitoring endpoints."""
    base_url = "http://127.0.0.1:8001"

    print("=== Testing API Endpoints ===\n")

    try:
        # Test 1: Health endpoint
        print("1. Testing /health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✓ Health check passed")
            print(f"   Status: {response.json().get('status')}")
        else:
            print(f"   ✗ Health check failed: {response.status_code}")

        # Test 2: Prometheus metrics
        print("\n2. Testing /metrics endpoint...")
        response = requests.get(f"{base_url}/metrics")
        if response.status_code == 200:
            print("   ✓ Metrics endpoint accessible")
            lines = response.text.split('\n')[:10]  # First 10 lines
            print("   Sample metrics:")
            for line in lines:
                if line.strip():
                    print(f"     {line}")
        else:
            print(f"   ✗ Metrics endpoint failed: {response.status_code}")

        # Test 3: Monitoring metrics
        print("\n3. Testing /monitoring/metrics endpoint...")
        response = requests.get(f"{base_url}/monitoring/metrics")
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Monitoring metrics retrieved")
            print(f"   Total requests: {data.get('metrics', {}).get('total_requests', 'N/A')}")
            print(f"   Prediction: {data.get('prediction', {}).get('prediction', 'N/A')}")
        else:
            print(f"   ✗ Monitoring metrics failed: {response.status_code}")

        # Test 4: Monitoring alerts
        print("\n4. Testing /monitoring/alerts endpoint...")
        response = requests.get(f"{base_url}/monitoring/alerts")
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Alerts endpoint accessible")
            print(f"   Total alerts: {data.get('total_alerts', 0)}")
        else:
            print(f"   ✗ Alerts endpoint failed: {response.status_code}")

        # Test 5: Agent check
        print("\n5. Testing /monitoring/agent-check endpoint...")
        response = requests.post(f"{base_url}/monitoring/agent-check")
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Agent check completed")
            analysis = data.get('agent_analysis', 'N/A')
            print(f"   Analysis length: {len(analysis)} characters")
        else:
            print(f"   ✗ Agent check failed: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on http://127.0.0.1:8001")
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")

    print("\n=== Endpoint Testing Complete ===")

if __name__ == "__main__":
    # Start server
    server_process = start_server()

    try:
        # Test endpoints
        test_endpoints()
    finally:
        # Clean up
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()