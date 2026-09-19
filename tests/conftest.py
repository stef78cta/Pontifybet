"""Fixture pytest: ROOT pe sys.path + bază SQLite izolată per test."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def isolated_history_db(tmp_path_factory, monkeypatch):
    """Redirecționează istoricul către o bază temporară.

    `run_analysis` jurnalizează predicțiile în SQLite, iar testele nu au voie să
    scrie în `data/pontifybet.sqlite3` real — istoricul de producție trebuie să
    rămână curat și reproductibil.

    Baza stă într-un director propriu, nu în `tmp_path`: multe teste folosesc
    `tmp_path` ca `OUTPUTS_DIR` și verifică exact ce fișiere apar acolo.
    """
    db_dir = tmp_path_factory.mktemp("history-db")
    db_path = db_dir / "history.sqlite3"
    monkeypatch.setenv("PONTIFYBET_DB_PATH", str(db_path))
    yield db_path
