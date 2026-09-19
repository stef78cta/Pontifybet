"""Plan model-aware pentru ce date FootyStats sunt necesare."""

from __future__ import annotations


def needs_last5(model_ids: list[str]) -> bool:
    """Over 0.5 și Cornere consumă last5_* în motoare/adaptoare."""
    return "over05" in model_ids or "corners" in model_ids


def needs_last10(model_ids: list[str]) -> bool:
    """Modelele active MVP nu consumă last10_* — rămâne oprit."""
    _ = model_ids
    return False


def required_lastx_nums(model_ids: list[str]) -> set[int]:
    """Setul de `num` pentru apeluri lastx în fluxul Generate."""
    nums: set[int] = set()
    if needs_last5(model_ids):
        nums.add(5)
    if needs_last10(model_ids):
        nums.add(10)
    return nums


def needs_league_teams(model_ids: list[str]) -> bool:
    """Toate modelele active au nevoie de stats sezon / medii ligă."""
    return bool(model_ids)
