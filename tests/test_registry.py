"""Test registry + cache key."""

from src.adapters.base import load_registry
from src.api.cache import cache_key


def test_registry_has_three_pilots():
    reg = load_registry()
    models = reg["models"]
    assert set(models) >= {"over05", "double_chance", "corners"}
    assert models["over05"]["input_sheet"] == "Analize meciuri"
    assert models["double_chance"]["layout"] == "single_match"


def test_cache_key_ignores_api_key():
    a = cache_key("todays-matches", {"date": "2026-03-15", "key": "SECRET1"})
    b = cache_key("todays-matches", {"date": "2026-03-15", "key": "SECRET2"})
    assert a == b
