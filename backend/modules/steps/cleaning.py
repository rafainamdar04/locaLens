from typing import Dict, Any
from core.pipeline import step, Context, Result
from services.address_cleaner import clean_address


@step("clean_address")
async def run(ctx: Context) -> Result:
    raw = ctx.get("raw_address") or ctx.get("raw")
    if not isinstance(raw, str):
        return {"cleaning_result": {"cleaned_text": "", "components": {}, "confidence": 0.0},
                "cleaned_address": "",
                "cleaned_components": {}}
    res = await clean_address(raw)
    return {
        "cleaning_result": res,
        "cleaned_address": res.get("cleaned_text", ""),
        "cleaned_components": res.get("components", {}),
    }
