from core.pipeline import step, Context, Result
from services.integrity import compute_integrity


@step("integrity")
def run(ctx: Context) -> Result:
    raw = ctx.get("raw_address") or ctx.get("raw") or ""
    cleaned = ctx.get("cleaned_address") or ""
    integ = compute_integrity(raw, cleaned)
    return {"integrity": integ}
