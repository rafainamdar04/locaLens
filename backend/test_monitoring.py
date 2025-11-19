"""
Test Monitoring Features

Script to test the new monitoring features without running the full server.
"""

import asyncio
import json
from services.monitoring import monitoring_service
from services.agent import monitoring_agent

async def test_monitoring():
    """Test the monitoring features."""
    print("=== Testing Monitoring Features ===\n")

    # Test 1: Load logs and compute metrics
    print("1. Loading logs and computing metrics...")
    df = await monitoring_service.load_recent_logs(hours=24)
    metrics = monitoring_service.compute_metrics(df)

    print(f"   Loaded {len(df)} log entries")
    print(f"   Metrics: {json.dumps(metrics, indent=2)}\n")

    # Test 2: Predictive model
    print("2. Testing predictive model...")
    prediction = monitoring_service.predict_anomalies(metrics)
    print(f"   Prediction: {json.dumps(prediction, indent=2)}\n")

    # Test 3: Generate insights
    print("3. Generating AI insights...")
    try:
        insights = await monitoring_service.generate_insights(metrics, prediction)
        print(f"   Insights: {insights}\n")
    except Exception as e:
        print(f"   Error generating insights: {e}\n")

    # Test 4: Agent analysis
    print("4. Testing AI agent...")
    try:
        agent_result = await monitoring_agent.run_monitoring_check()
        print(f"   Agent Analysis: {agent_result.get('agent_analysis', 'N/A')}\n")
    except Exception as e:
        print(f"   Error running agent: {e}\n")

    # Test 5: Check alerts
    print("5. Checking alerts...")
    alerts = await monitoring_service.check_alerts(metrics, prediction)
    print(f"   Alerts generated: {len(alerts)}")
    for alert in alerts:
        print(f"   - {alert['type']}: {alert['message']}\n")

    print("=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_monitoring())