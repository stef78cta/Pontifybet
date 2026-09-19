"""Generează `mocks/league_matches.json` — FIXTURE SINTETIC pentru modul MOCK.

Datele nu provin din FootyStats: sunt evenimente construite determinist, cu
singurul scop de a alimenta istoricul nativ Cornere V14 în testele offline și în
modul MOCK al aplicației. Câmpurile folosite sunt exact cele citite din
`league-matches` de `src/orchestration/native_history.py`:
`id`, `status`, `date_unix`, `home_name`, `away_name`, `team_a_corners`,
`team_b_corners`, `homeID`, `awayID`, `competition_id`.

Rulează: python scripts/build_mock_league_matches.py
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from config.settings import MOCKS_DIR

# Ancoră: meciurile mock din `matches.json` se joacă pe 2026-03-15, deci istoricul
# se construieşte săptămânal în urmă, ca ferestrele L10/L20 să fie populate.
ANCHOR = datetime(2026, 3, 8, 15, 0, tzinfo=timezone.utc)
CYCLES = 6

# Profil de cornere per echipă: (medie ofensivă acasă, medie ofensivă în deplasare).
# Valori alese ca să acopere ambele ramuri de distribuție (Poisson pentru dispersie
# mică, Negative Binomial pentru dispersie mare).
PROFILES: dict[int, tuple[str, int, float, float]] = {
    101: ("Arsenal", 2012, 6.4, 5.1),
    102: ("Chelsea", 2012, 5.8, 4.6),
    103: ("Liverpool", 2012, 7.1, 5.6),
    104: ("Everton", 2012, 4.3, 3.4),
    201: ("Real Madrid", 2013, 7.6, 6.2),
    202: ("Sevilla", 2013, 4.9, 3.9),
}


def _wobble(seed: int) -> float:
    """Oscilație deterministă în [-1.5, 1.5], fără dependență de `random`."""
    return ((seed * 2654435761) % 31 - 15) / 10.0


def _corners(base: float, seed: int) -> int:
    return max(0, round(base + _wobble(seed)))


def build() -> dict[str, list[dict[str, object]]]:
    out: dict[str, list[dict[str, object]]] = {}
    fixture_id = 800000
    for season_id in sorted({cfg[1] for cfg in PROFILES.values()}):
        team_ids = [tid for tid, cfg in PROFILES.items() if cfg[1] == season_id]
        fixtures: list[dict[str, object]] = []
        slot = 0
        for cycle in range(CYCLES):
            for home_id in team_ids:
                for away_id in team_ids:
                    if home_id == away_id:
                        continue
                    fixture_id += 1
                    slot += 1
                    kickoff = ANCHOR - timedelta(days=7 * (CYCLES * len(team_ids) - slot))
                    home_name, _, home_base, _ = PROFILES[home_id]
                    away_name, _, _, away_base = PROFILES[away_id]
                    fixtures.append(
                        {
                            "id": fixture_id,
                            "competition_id": season_id,
                            "status": "complete",
                            "date_unix": int(kickoff.timestamp()),
                            "homeID": home_id,
                            "awayID": away_id,
                            "home_name": home_name,
                            "away_name": away_name,
                            "team_a_corners": _corners(home_base, fixture_id + cycle),
                            "team_b_corners": _corners(away_base, fixture_id * 3 + cycle),
                        }
                    )
        fixtures.sort(key=lambda item: item["date_unix"])
        out[str(season_id)] = fixtures
    return out


def main() -> None:
    payload = {
        "_fixture": "SINTETIC — generat de scripts/build_mock_league_matches.py; "
        "nu sunt date FootyStats reale.",
        "seasons": build(),
    }
    path = MOCKS_DIR / "league_matches.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    counts = {key: len(value) for key, value in payload["seasons"].items()}
    print(f"scris {path}: {counts}")


if __name__ == "__main__":
    main()
