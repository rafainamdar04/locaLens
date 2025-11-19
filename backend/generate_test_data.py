"""
Generate Test Data for Monitoring

Script to generate sample log data for testing monitoring features.
"""

import csv
import random
from datetime import datetime, timedelta
import os

def generate_test_logs(num_entries=100):
    """Generate sample log entries for testing."""
    logs_path = "logs/pipeline_logs.csv"

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Check if file exists and has header
    file_exists = os.path.exists(logs_path)

    with open(logs_path, 'a', newline='') as csvfile:
        fieldnames = [
            'timestamp', 'raw', 'cleaned', 'integrity_score', 'fused_confidence',
            'top_similarity', 'here_confidence', 'mismatch_km', 'anomaly_reasons', 'actions',
            'llm_latency_ms', 'ml_latency_ms', 'here_latency_ms', 'processing_time_ms'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        base_time = datetime.now() - timedelta(days=1)

        for i in range(num_entries):
            timestamp = base_time + timedelta(minutes=i*10)  # Every 10 minutes

            # Generate realistic data
            integrity_score = random.uniform(50, 100)
            fused_confidence = random.uniform(0.3, 1.0)
            here_confidence = random.uniform(0.4, 1.0)
            processing_time = random.uniform(1000, 15000)  # 1-15 seconds

            # Sometimes add anomalies
            anomaly_reasons = []
            if fused_confidence < 0.5:
                anomaly_reasons.append('"low_fused_conf"')
            if integrity_score < 60:
                anomaly_reasons.append('"low_integrity"')
            if processing_time > 10000:
                anomaly_reasons.append('"high_latency"')

            anomaly_str = f"[{', '.join(anomaly_reasons)}]" if anomaly_reasons else "[]"

            writer.writerow({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'raw': f'Test Address {i}',
                'cleaned': f'Test Address {i}',
                'integrity_score': f"{integrity_score:.4f}",
                'fused_confidence': f"{fused_confidence:.4f}",
                'top_similarity': f"{random.uniform(0.8, 1.0):.4f}",
                'here_confidence': f"{here_confidence:.4f}",
                'mismatch_km': f"{random.uniform(0, 20):.2f}",
                'anomaly_reasons': anomaly_str,
                'actions': "[]",
                'llm_latency_ms': "0.0",
                'ml_latency_ms': "0.0",
                'here_latency_ms': "0.0",
                'processing_time_ms': f"{processing_time:.1f}"
            })

    print(f"Generated {num_entries} test log entries in {logs_path}")

if __name__ == "__main__":
    generate_test_logs(200)  # Generate 200 entries