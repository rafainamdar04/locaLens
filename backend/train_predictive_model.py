"""
Train Predictive Model

Script to train the predictive anomaly detection model on historical logs.
"""

import sys
from pathlib import Path
import asyncio

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.monitoring import monitoring_service
import pandas as pd

async def train_model():
    """Train the predictive model on historical data."""
    print("Loading historical logs...")

    # Load more data for training (last 7 days)
    df = await monitoring_service.load_recent_logs(hours=24 * 7)

    if df.empty:
        print("No historical data found. Run some requests first.")
        return

    print(f"Loaded {len(df)} records for training")

    # Train the model
    monitoring_service.train_predictive_model(df)

    print("Model training completed!")

    # Test the model
    metrics = monitoring_service.compute_metrics(df)
    prediction = monitoring_service.predict_anomalies(metrics)

    print(f"Test prediction: {prediction}")

if __name__ == "__main__":
    asyncio.run(train_model())