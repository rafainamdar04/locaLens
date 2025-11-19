from core.pipeline import step, Context, Result
from services.geospatial import geospatial_checks as _legacy_checks, check_geospatial_consistency


@step("geospatial_checks")
def run(ctx: Context) -> Result:
    ml_top = ctx.get("ml_top")
    here_primary = ctx.get("here_primary")
    cleaned_components = ctx.get("cleaned_components") or {}

    # Prefer new consistency check if components available; fallback to legacy wrapper
    if cleaned_components:
        checks = check_geospatial_consistency(ml_top, here_primary, cleaned_components)
        # Normalize to legacy shape used by rest of app
        res = {
            "score": 1.0,
            "distance_match": checks.get("mismatch_km"),
            "boundary_check": not checks.get("city_violation", False),
            "consistency": 1.0,
            "details": checks,
        }
        return {"geospatial_checks": res}
    else:
        res = _legacy_checks(ml_top=ml_top, here_primary=here_primary, cleaned=ctx.get("cleaned_address") or "")
        return {"geospatial_checks": res}
