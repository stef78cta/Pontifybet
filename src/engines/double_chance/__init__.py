"""Motor Șansă Dublă — Optimizat V2."""

from src.engines.double_chance.engine import (
    OFFICIAL_CELLS,
    PYTHON_RESULT_CELLS,
    SELECTIONS,
    DoubleChanceOfficialResult,
    DoubleChanceSelection,
    compute_double_chance,
    python_result_writes,
)
from src.engines.double_chance.inputs import match_to_double_chance_inputs

__all__ = [
    "OFFICIAL_CELLS",
    "PYTHON_RESULT_CELLS",
    "SELECTIONS",
    "DoubleChanceOfficialResult",
    "DoubleChanceSelection",
    "compute_double_chance",
    "match_to_double_chance_inputs",
    "python_result_writes",
]
