from core.pipeline import step, Context, Result
from services.here_geocoder import here_geocode as _here


@step("here_geocode")
def run(ctx: Context) -> Result:
    cleaned = ctx.get("cleaned_address") or ""
    res = _here(cleaned)
    primary = res.get("primary_result") if res else None
    return {"here_results": res, "here_primary": primary}
