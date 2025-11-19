"""
Demonstrate New Features

Complete demonstration of the new monitoring features for the HERE Intern application.
"""

import asyncio
import json
from services.monitoring import monitoring_service
from services.agent import monitoring_agent
from services.metrics import get_metrics_response

async def demonstrate_features():
    """Demonstrate all the new monitoring features."""
    print("🚀 LocalLens Enhanced - HERE Intern Project Demonstration")
    print("=" * 60)

    # Load and analyze logs
    print("\n📊 1. LOG ANALYSIS & METRICS COMPUTATION")
    print("-" * 40)
    df = await monitoring_service.load_recent_logs(hours=24)
    metrics = monitoring_service.compute_metrics(df)

    print(f"✅ Loaded {len(df)} log entries from the past 24 hours")
    print(f"📈 Key Metrics:")
    print(f"   • Total Requests: {metrics['total_requests']}")
    print(f"   • Average Latency: {metrics['avg_latency']:.1f}ms")
    print(f"   • Average Confidence: {metrics['avg_fused_confidence']:.3f}")
    print(f"   • Anomaly Rate: {metrics['anomaly_rate']:.1%}")
    print(f"   • High Latency Rate: {metrics['high_latency_rate']:.1%}")

    # Predictive anomaly detection
    print("\n🤖 2. PREDICTIVE ANOMALY DETECTION")
    print("-" * 40)
    prediction = monitoring_service.predict_anomalies(metrics)

    print("✅ ML Model Status: Trained on historical data")
    print(f"🔮 Current Prediction: {prediction['prediction'].upper()}")
    print(f"📊 Confidence Score: {prediction['confidence']:.3f}")

    # AI-powered insights
    print("\n🧠 3. AI-POWERED INSIGHTS")
    print("-" * 40)
    try:
        insights = await monitoring_service.generate_insights(metrics, prediction)
        print("✅ Generated insights using LLM (OpenRouter/OpenAI)")
        print(f"💡 {insights}")
    except Exception as e:
        print(f"⚠️  Insights generation failed: {e}")

    # Agentic AI monitoring
    print("\n🎯 4. AGENTIC AI MONITORING")
    print("-" * 40)
    try:
        agent_result = await monitoring_agent.run_monitoring_check()
        print("✅ Autonomous agent analysis completed")
        analysis = agent_result.get('agent_analysis', 'Analysis not available')
        print(f"🤖 Agent Assessment: {analysis[:200]}...")
    except Exception as e:
        print(f"⚠️  Agent analysis failed: {e}")

    # Alert system
    print("\n🚨 5. REAL-TIME ALERT SYSTEM")
    print("-" * 40)
    alerts = await monitoring_service.check_alerts(metrics, prediction)
    print(f"✅ Alert check completed - {len(alerts)} active alerts")

    for alert in alerts:
        severity_icon = "🔴" if alert['severity'] == 'critical' else "🟡"
        print(f"   {severity_icon} {alert['type'].upper()}: {alert['message']}")

    # Prometheus metrics
    print("\n📈 6. PROMETHEUS METRICS EXPORT")
    print("-" * 40)
    metrics_response = get_metrics_response()
    metrics_text = metrics_response.body.decode('utf-8')
    lines = [line for line in metrics_text.split('\n') if line.strip()][:8]

    print("✅ Metrics exported for observability")
    print("📊 Sample Prometheus metrics:")
    for line in lines:
        print(f"   {line}")

    # Summary
    print("\n🎉 SUMMARY: HERE INTERN PROJECT FEATURES")
    print("=" * 60)
    features = [
        "✅ Proactive monitoring of geocoding service health",
        "✅ Predictive anomaly detection using ML (IsolationForest)",
        "✅ Early warning system with automated alerts",
        "✅ Agentic AI for autonomous analysis and recommendations",
        "✅ Advanced observability with Prometheus metrics",
        "✅ LLM-powered insights for human-readable analysis",
        "✅ Self-healing capabilities (existing anomaly correction)",
        "✅ Comprehensive logging and metrics aggregation"
    ]

    for feature in features:
        print(feature)

    print("\n🚀 Ready for HERE Intern Role!")
    print("This demonstrates expertise in:")
    print("• Data-driven AI/ML automation")
    print("• Proactive monitoring and observability")
    print("• Predictive analytics for failure prevention")
    print("• Agentic AI frameworks")
    print("• Production-ready service monitoring")

if __name__ == "__main__":
    asyncio.run(demonstrate_features())