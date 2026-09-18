"""
Smoke-test conexiune FootyStats LIVE.

Nu afișează cheia API și nu dump-uiește JSON brut.

Rulare (din rădăcina proiectului, cu .venv activat):

    python scripts/test_footystats_live.py

Așteptări:
    - PASS test-call
    - ligi alese > 0 (altfel vezi mesajul despre API Settings)
    - meciurile zilei (pot fi 0 dacă nu e rundă)
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import DEFAULT_TIMEZONE, FORCE_MOCK, get_footystats_api_key, is_mock_mode
from src.api.cache import ResponseCache
from src.api.client import FootyStatsClient, FootyStatsError, current_season_id


def _fail(msg: str, code: int = 2) -> int:
    print(f"FAIL  {msg}")
    return code


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print("Pontifybet - test conexiune FootyStats")
    print(f"UTC: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} | TZ local: {DEFAULT_TIMEZONE}")

    if FORCE_MOCK:
        return _fail("FORCE_MOCK=true in .env. Seteaza FORCE_MOCK=false pentru date reale.")

    if not get_footystats_api_key():
        print("FAIL  Lipseste FOOTYSTATS_API_KEY.")
        print("      1. Deschide https://footystats.org/api/u/api-settings")
        print("      2. Copiaza API Key in .env: FOOTYSTATS_API_KEY=...")
        print("      3. Alege ligile din acelasi ecran (chosen leagues).")
        print("      4. Seteaza FORCE_MOCK=false")
        print("      5. Re-ruleaza: python scripts/test_footystats_live.py")
        return 2

    if is_mock_mode():
        return _fail("Aplicatia e inca in mod MOCK. Verifica FORCE_MOCK si cheia API.")

    cache = ResponseCache(use_disk=True)
    today = datetime.now(ZoneInfo(DEFAULT_TIMEZONE)).date().isoformat()

    try:
        with FootyStatsClient(cache=cache) as client:
            ping = client.test_call()
            if not ping.get("ok"):
                return _fail("test-call nu a confirmat succesul.")
            remaining = ping.get("request_remaining")
            limit = ping.get("request_limit")
            quota = f"{remaining}/{limit}" if remaining and limit else "n/a"
            print(f"PASS  test-call  (cereri ramase/ora: {quota})")

            chosen = client.list_leagues(chosen_only=True)
            print(f"PASS  league-list chosen={len(chosen)}")
            if not chosen:
                print("INFO  Nicio liga aleasa. Alege ligile la https://footystats.org/api/u/api-settings")
                print("      Fara ligi alese, todays-matches va fi gol.")
            else:
                preview = []
                for lg in chosen[:8]:
                    sid = current_season_id(lg)
                    preview.append(f"{lg.get('name') or lg.get('league_name')} (season_id={sid})")
                print("      " + " | ".join(preview))

            matches = client.matches_by_date(today, timezone_name=DEFAULT_TIMEZONE)
            print(f"PASS  todays-matches {today}: {len(matches)} meciuri")
            for m in matches[:5]:
                home = m.get("home_name") or "?"
                away = m.get("away_name") or "?"
                print(f"      {home} vs {away}  id={m.get('id')}  competition_id={m.get('competition_id')}")

            if matches:
                sample = matches[0]
                md = client.enrich_match(sample, tz_name=DEFAULT_TIMEZONE)
                home_n = md.home.matches_played_overall.numeric_or_none()
                last5 = md.home.last5_n.numeric_or_none()
                print(
                    f"PASS  enrich  {md.home.name} vs {md.away.name} | "
                    f"played={home_n} last5_n={last5} source={md.source_mode}"
                )
            else:
                print("INFO  Nu sunt meciuri azi pe ligile alese - schimba data in UI sau alege alte ligi.")

    except FootyStatsError as exc:
        return _fail(exc.user_message)

    print("Gata. Poti porni UI: streamlit run app.py  (mod LIVE)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
