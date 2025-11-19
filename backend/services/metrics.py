"""
Prometheus Metrics Exporter

Exposes monitoring metrics to Prometheus for advanced observability.
"""

from prometheus_client import Gauge, Counter, Histogram, generate_latest
from fastapi import Response
import time
from services.monitoring import monitoring_service

# Define metrics
request_count = Counter('locallens_requests_total', 'Total number of requests processed')
processing_time = Histogram('locallens_processing_time_seconds', 'Request processing time',
                           buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0])
anomaly_count = Counter('locallens_anomalies_total', 'Total number of anomalies detected')
latency_gauge = Gauge('locallens_avg_latency_ms', 'Average processing latency')
confidence_gauge = Gauge('locallens_avg_confidence', 'Average fused confidence')
alert_count = Gauge('locallens_active_alerts', 'Number of active alerts')

def update_prometheus_metrics():
    """Update Prometheus metrics from monitoring service."""
    try:
        if monitoring_service.metrics_history:
            latest = monitoring_service.metrics_history[-1]

            latency_gauge.set(latest.get('avg_latency', 0))
            confidence_gauge.set(latest.get('avg_fused_confidence', 0))
            alert_count.set(len(monitoring_service.alerts))

    except Exception as e:
        print(f"Failed to update Prometheus metrics: {e}")

def get_metrics_response() -> Response:
    """Return Prometheus metrics as HTTP response."""
    update_prometheus_metrics()
    return Response(generate_latest(), media_type="text/plain; charset=utf-8")