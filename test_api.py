import requests
import json

url = "http://127.0.0.1:8000/process_v3"
params = {"addons": "deliverability,property_risk,fraud,neighborhood,consensus"}
payload = {"raw_address": "123 MG Road, Bengaluru 560001"}

try:
    response = requests.post(url, json=payload, params=params, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2))
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response text: {e.response.text}")
