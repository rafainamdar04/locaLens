"""
Simplified Agentic AI Service

Uses OpenAI directly for autonomous monitoring and decision-making.
"""

import os
import openai
from typing import Dict, Any
import asyncio
from loguru import logger

class MonitoringAgent:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not found. Agent functionality will be limited.")

    async def run_monitoring_check(self) -> Dict[str, Any]:
        """Run autonomous monitoring check using AI."""
        try:
            # Get current metrics (simplified)
            from services.monitoring import monitoring_service
            df = await monitoring_service.load_recent_logs(hours=24)
            metrics = monitoring_service.compute_metrics(df) if not df.empty else {}
            prediction = monitoring_service.predict_anomalies(metrics) if metrics else {}

            # Create prompt for AI analysis
            prompt = f"""
            You are an autonomous monitoring agent for a geocoding service. Analyze this data and provide insights:

            Current Metrics (last 24h):
            - Total Requests: {metrics.get('total_requests', 0)}
            - Average Latency: {metrics.get('avg_latency', 0):.2f}ms
            - Average Confidence: {metrics.get('avg_fused_confidence', 0):.3f}
            - Anomaly Rate: {metrics.get('anomaly_rate', 0):.3f}

            Predictive Analysis:
            - Status: {prediction.get('prediction', 'unknown')}
            - Confidence: {prediction.get('confidence', 0):.3f}

            Provide:
            1. A brief assessment of system health
            2. Any recommended actions
            3. Risk level (Low/Medium/High)
            """

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )
            )

            analysis = response.choices[0].message.content.strip()

            return {
                "agent_analysis": analysis,
                "timestamp": asyncio.get_event_loop().time(),
                "metrics_summary": metrics,
                "prediction_summary": prediction
            }

        except Exception as e:
            logger.error(f"Agent monitoring failed: {e}")
            return {"error": str(e)}

# Global instance
monitoring_agent = MonitoringAgent()