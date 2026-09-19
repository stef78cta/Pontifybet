"""Inspectează payload-urile din .cache pentru a confirma numele câmpurilor FootyStats."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"

for path in sorted(CACHE.glob("*.json")):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        continue
    first = data[0]
    if "homeGoalCount" not in first and "team_a_corners" not in first:
        continue
    print(f"\n=== {path.name} ({len(data)} elemente)")
    keys = [k for k in first if "corner" in k.lower() or "Corner" in k]
    print("chei corner:", keys)
    print("chei identitate:", [k for k in first if k in {
        "id", "homeID", "awayID", "home_name", "away_name", "season", "competition_id",
        "date_unix", "status", "game_week", "roundID", "stadium_name",
    }])
    sample = {
        k: first.get(k)
        for k in ["id", "homeID", "awayID", "home_name", "away_name", "season",
                  "competition_id", "date_unix", "status", "team_a_corners",
                  "team_b_corners", "totalCornerCount"]
    }
    print("exemplu:", json.dumps(sample, ensure_ascii=False)[:600])
    statuses: dict[str, int] = {}
    for item in data:
        statuses[str(item.get("status"))] = statuses.get(str(item.get("status")), 0) + 1
    print("status:", statuses)
