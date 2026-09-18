# Conexiune FootyStats LIVE

Documentație oficială: https://footystats.org/api/documentations

## Ce folosește Pontifybet

- Bază: `https://api.football-data-api.com`
- Autentificare: query `key` (din `FOOTYSTATS_API_KEY`, niciodată în Git/loguri)
- Envelope JSON: `{success, pager, metadata, data}`
- Sentinel `-1` / `-2` = date lipsă, **nu** zero

Endpoint-uri:

| Metodă | Endpoint | Rol |
| --- | --- | --- |
| `test_call` | `/test-call` | verificare cheie |
| `list_leagues` | `/league-list?chosen_leagues_only=true` | ligile alese |
| `matches_by_date` | `/todays-matches?date=&timezone=` | meciuri pe zi (max 200/pagină) |
| `league_season` | `/league-season` | stats ligă |
| `league_matches` | `/league-matches` | program ligă |
| `league_teams` | `/league-teams?include=stats` | echipe + stats sezon |
| `team` | `/team?include=stats` | filtrat pe `competition_id` |
| `last_x` | `/lastx?num=5\|10` | formă recentă (bloc overall) |
| `match_details` | `/match` | detalii meci |

## Test local

```powershell
cd C:\_Software\SAAS\Pontifybet
.\.venv\Scripts\Activate.ps1
python scripts/test_footystats_live.py
```

PASS așteptat: `test-call`, număr ligi, număr meciuri. Dacă ligile sunt 0, alege-le la https://footystats.org/api/u/api-settings.
