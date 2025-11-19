from core.pipeline import step, Context, Result
from services.self_heal import self_heal as _self_heal


@step("self_heal")
async def run(ctx: Context) -> Result:
    if not ctx.get("anomaly_detected"):
        return {"self_heal_actions": None}
    raw = ctx.get("raw_address") or ctx.get("raw") or ""
    cleaned = ctx.get("cleaned_address") or ""
    actions = await _self_heal(
        raw=raw,
        cleaned=cleaned,
        ml_candidates=ctx.get("ml_results"),
        here_resp=ctx.get("here_results"),
        reasons=ctx.get("anomaly_reasons") or [],
    )
    return {"self_heal_actions": actions}
