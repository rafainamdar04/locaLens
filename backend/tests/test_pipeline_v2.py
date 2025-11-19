import pytest
from core.pipeline import Pipeline
from modules.registry import default_steps


@pytest.mark.asyncio
async def test_pipeline_runs_minimal_context():
    pipe = Pipeline(default_steps())
    ctx = await pipe.run({"raw_address": "123 MG Road, Bengaluru 560001"})

    # Core outputs exist and are shaped as dicts/numbers
    assert isinstance(ctx.get("cleaning_result"), dict)
    assert isinstance(ctx.get("integrity"), dict)
    assert "ml_results" in ctx
    assert "here_results" in ctx
    assert "geospatial_checks" in ctx
    assert isinstance(ctx.get("fused_confidence", 0.0), float)
    assert "anomaly_detected" in ctx
    # Step purity: raw_address unchanged
    assert ctx["raw_address"] == "123 MG Road, Bengaluru 560001"
