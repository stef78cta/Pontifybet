#!/usr/bin/env python3
"""Afișează tabelele și versiunea schemei din baza de istoric (read-only).

Rulare:

    python scripts/show_history_schema.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import get_sqlite_path


def main() -> int:
    path = get_sqlite_path()
    print(f"DB: {path}")
    if not path.exists():
        print("Baza nu există încă. Rulează o analiză sau pornește aplicația.")
        return 1
    conn = sqlite3.connect(str(path))
    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]
        print("TABLES:", tables)
        for name in ("schema_version",):
            if name in tables:
                rows = list(conn.execute(f"SELECT * FROM {name}"))
                print(f"{name}: {rows}")
        for name in ("analysis_runs", "prediction_snapshots", "match_results", "settlements"):
            if name in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                print(f"{name}: {count} rânduri")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
