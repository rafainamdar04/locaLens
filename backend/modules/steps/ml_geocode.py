from core.pipeline import step, Context, Result
from services.ml_geocoder import ml_geocode as _ml


@step("ml_geocode")
def run(ctx: Context) -> Result:
    cleaned = ctx.get("cleaned_address") or ""
    res = _ml(cleaned)
    top = res.get("top_result") if res else None
    return {"ml_results": res, "ml_top": top}
