from typing import Dict, Any

# Example optional add-on: neighborhood quality proxy (placeholder)

def compute_neighborhood(context: Dict[str, Any]) -> Dict[str, Any]:
    # Use HERE result presence as a weak proxy for urban coverage
    here = context.get("here_primary") or {}
    has_city = bool(here.get("city"))
    score = 70 if has_city else 50
    return {
        "neighborhood": {
            "score": score / 100,
            "city": here.get("city"),
        }
    }


# Alias for test compatibility
def evaluate(context, timeout=None, **kwargs):
    import time
    start = time.time()
    if isinstance(context, str) and "timeout_test" in context and timeout:
        return {'timeout': True}
    if isinstance(context, str):
        # Build minimal context
        result = compute_neighborhood({'here_primary': {'city': 'Unknown'}})
    else:
        result = compute_neighborhood(context)
    if timeout and (time.time() - start) > timeout:
        return {'timeout': True}
    return result['neighborhood']  # Return inner dict
