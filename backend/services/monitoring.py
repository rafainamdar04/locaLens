"""
Monitoring Service

Aggregates logs, computes metrics, and provides proactive insights.
Includes predictive anomaly detection and early warning system.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any
import asyncio
import os
from pathlib import Path
from datetime import datetime, timedelta
import openai
from loguru import logger
from prometheus_client import Counter

# Prometheus counters
monitoring_cycles = Counter('locallens_monitoring_cycles_total', 'Total monitoring cycles run')
alerts_generated = Counter('locallens_alerts_generated_total', 'Total alerts generated')
predictions_made = Counter('locallens_predictions_total', 'Total predictions made')

class MonitoringService:
    def __init__(self, logs_path: str = "logs/pipeline_logs.csv"):
        self.logs_path = Path(__file__).parent.parent / logs_path
        self.model = None
        self.scaler = None
        self.metrics_history = []
        self.alerts = []

    async def load_recent_logs(self, hours: int = 24) -> pd.DataFrame:
        """Load logs from the last N hours."""
        if not self.logs_path.exists():
            logger.warning(f"Logs file not found: {self.logs_path}")
            return pd.DataFrame()

        df = pd.read_csv(self.logs_path)
        if df.empty:
            return df

        # Parse timestamp and filter recent
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = df[df['timestamp'] >= cutoff].copy()

        return recent

    def compute_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute key metrics from logs."""
        if df.empty:
            return {}

        metrics = {
            'total_requests': len(df),
            'avg_latency': df['processing_time_ms'].mean(),
            'avg_fused_confidence': df['fused_confidence'].mean(),
            'avg_integrity_score': df['integrity_score'].mean(),
            'anomaly_rate': df['anomaly_reasons'].notna().sum() / len(df),
            'high_latency_rate': (df['processing_time_ms'] > 5000).sum() / len(df),
            'low_confidence_rate': (df['fused_confidence'] < 0.5).sum() / len(df),
            'timestamp': datetime.now().isoformat()
        }

        return metrics

    def train_predictive_model(self, df: pd.DataFrame):
        """Train IsolationForest for anomaly prediction."""
        if len(df) < 10:
            logger.warning("Not enough data for training predictive model")
            return

        # Features for prediction
        features = df[['processing_time_ms', 'fused_confidence', 'integrity_score']].fillna(0)

        # Scale features
        self.scaler = StandardScaler()
        scaled_features = self.scaler.fit_transform(features)

        # Train model
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(scaled_features)

        logger.info("Predictive model trained successfully")

    def predict_anomalies(self, metrics: Dict) -> Dict[str, Any]:
        """Predict if current metrics indicate anomalies."""
        if not self.model or not self.scaler:
            return {'prediction': 'unknown', 'confidence': 0.0}

        # Prepare features
        features = np.array([[
            metrics.get('avg_latency', 0),
            metrics.get('avg_fused_confidence', 0),
            metrics.get('avg_integrity_score', 0)
        ]])

        scaled = self.scaler.transform(features)
        prediction = self.model.predict(scaled)[0]
        scores = self.model.decision_function(scaled)[0]

        return {
            'prediction': 'anomaly' if prediction == -1 else 'normal',
            'confidence': float(scores),
            'threshold': -0.1  # IsolationForest decision function threshold
        }

    async def generate_insights(self, metrics: Dict, prediction: Dict) -> str:
        """Use LLM to generate human-readable insights."""
        try:
            from config import settings
            api_key = settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY
            if not api_key:
                return "LLM API key not configured for insights generation."

            import openai
            if settings.OPENROUTER_API_KEY:
                client = openai.AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            else:
                client = openai.AsyncOpenAI(api_key=api_key)

            prompt = f"""
            Analyze these geocoding service metrics and provide insights:

            Current Metrics (last 24h):
            - Total Requests: {metrics.get('total_requests', 0)}
            - Average Latency: {metrics.get('avg_latency', 0):.2f}ms
            - Average Confidence: {metrics.get('avg_fused_confidence', 0):.3f}
            - Anomaly Rate: {metrics.get('anomaly_rate', 0):.3f}
            - High Latency Rate: {metrics.get('high_latency_rate', 0):.3f}

            Predictive Analysis:
            - Status: {prediction.get('prediction', 'unknown')}
            - Confidence: {prediction.get('confidence', 0):.3f}

            Provide 2-3 key insights and any recommended actions.
            """

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )

            raw_insights = response.choices[0].message.content.strip()
            
            # Format insights neatly
            formatted_insights = self._format_insights(raw_insights)
            return formatted_insights

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return f"Error generating insights: {str(e)}"

    def _format_insights(self, raw_insights: str) -> str:
        """Format raw LLM insights into neat, readable text."""
        lines = raw_insights.split('\n')
        formatted = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Check if it's numbered (e.g., "1.", "2.")
            if line[0].isdigit() and len(line) > 1 and line[1] in ['.', ')']:
                formatted.append(f"• {line[2:].strip()}")
            elif line.startswith('-'):
                formatted.append(f"• {line[1:].strip()}")
            else:
                formatted.append(line)
        
        return '\n'.join(formatted)

    async def check_alerts(self, metrics: Dict, prediction: Dict):
        """Check for alert conditions and generate alerts."""
        alerts = []

        # High latency alert
        if metrics.get('high_latency_rate', 0) > 0.2:
            alerts.append({
                'type': 'high_latency',
                'severity': 'warning',
                'message': f"High latency rate: {metrics['high_latency_rate']:.1%}",
                'timestamp': datetime.now().isoformat()
            })

        # Low confidence alert
        if metrics.get('low_confidence_rate', 0) > 0.3:
            alerts.append({
                'type': 'low_confidence',
                'severity': 'warning',
                'message': f"Low confidence rate: {metrics['low_confidence_rate']:.1%}",
                'timestamp': datetime.now().isoformat()
            })

        # Predictive anomaly alert
        if prediction.get('prediction') == 'anomaly':
            alerts.append({
                'type': 'predictive_anomaly',
                'severity': 'critical',
                'message': f"Predictive model detected anomaly (confidence: {prediction['confidence']:.3f})",
                'timestamp': datetime.now().isoformat()
            })

        self.alerts.extend(alerts)
        return alerts

    async def run_monitoring_cycle(self):
        """Complete monitoring cycle: load data, compute metrics, predict, generate insights."""
        try:
            # Load recent logs
            df = await self.load_recent_logs(hours=24)

            # Compute metrics
            metrics = self.compute_metrics(df)
            self.metrics_history.append(metrics)

            # Keep only last 100 metrics
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]

            # Train/update model periodically
            if len(self.metrics_history) % 10 == 0:  # Every 10 cycles
                self.train_predictive_model(df)

            # Predict anomalies
            prediction = self.predict_anomalies(metrics)

            # Generate insights
            insights = await self.generate_insights(metrics, prediction)

            # Check alerts
            alerts = await self.check_alerts(metrics, prediction)

            logger.info(f"Monitoring cycle completed. Metrics: {len(metrics)}, Alerts: {len(alerts)}")

            # Update Prometheus counters
            monitoring_cycles.inc()
            alerts_generated.inc(len(alerts))
            predictions_made.inc()

            return {
                'metrics': metrics,
                'prediction': prediction,
                'insights': insights,
                'alerts': alerts
            }

        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}")
            return {'error': str(e)}

# Global instance
monitoring_service = MonitoringService()