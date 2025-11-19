
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import _get_cache_key

def test_cache_key_order_insensitive():
    key1 = _get_cache_key('address deliverability consensus')
    key2 = _get_cache_key('address consensus deliverability')
    assert key1 == key2, "Cache key should be order-insensitive for addons if normalized"

def test_cache_key_distinct_sets():
    key1 = _get_cache_key('address deliverability consensus')
    key2 = _get_cache_key('address property_risk consensus')
    assert key1 != key2, "Different addon sets should yield distinct cache keys"
