"""Istoric persistent și backtest (SQLite).

Responsabilități separate, câte un modul fiecare:

- `db` — conexiune, PRAGMA, schema versionată;
- `repository` — singurul loc cu SQL;
- `settlement` — regulile HIT/MISS, fără model;
- `snapshots` — jurnalul pre-match din faza ANALYSIS;
- `excel_ingest` — ingestia verdictelor calculate de Microsoft Excel;
- `results` — orchestrarea „Actualizează rezultate”;
- `backtest` — interogări read-only de măsurare.
"""

from __future__ import annotations

__all__ = [
    "backtest",
    "db",
    "excel_ingest",
    "models",
    "repository",
    "results",
    "settlement",
    "snapshots",
]
