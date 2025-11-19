from core.pipeline import step, Context, Result
from services.confidence import fuse_confidence


@step("fuse_confidence")
def run(ctx: Context) -> Result:
    ml_conf = (ctx.get("ml_results") or {}).get("confidence", 0.0)
    here_conf = (ctx.get("here_results") or {}).get("confidence", 0.0)
    llm_conf = (ctx.get("cleaning_result") or {}).get("confidence", 0.0)
    integrity_score = (ctx.get("integrity") or {}).get("score", 0)
    mismatch_km = (ctx.get("geospatial_checks") or {}).get("distance_match")

    metrics = {
        "ml_similarity": ml_conf or 0.0,
        "here_confidence": here_conf or 0.0,
        "llm_confidence": llm_conf or 0.0,
    }

    fused = fuse_confidence(metrics=metrics, integrity_score=integrity_score, mismatch_km=mismatch_km)
    return {"metrics": metrics, "fused_confidence": fused}
