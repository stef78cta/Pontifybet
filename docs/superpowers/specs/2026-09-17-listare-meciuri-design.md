# Listare meciuri pe dată și ligă (tabel selectabil)

Dată: 2026-09-17  
Proiect: Pontifybet  
Status: agreat în dialog; așteaptă review înainte de planul de implementare

## Problemă

Sidebar-ul încarcă automat meciurile într-un multiselect care arată doar „echipă vs echipă (id)”. Nu se văd liga și ora, nu se sortează, iar „selectează toate / unul / mai multe” e greu de folosit. Listarea se face la fiecare rerun Streamlit, inclusiv apel `todays-matches`.

## Scop

Un buton lângă **Generează analiza** încarcă și afișează meciurile din **data** și **ligile** din filtru. Tabelul arată ligă și oră, se sortează pe ligă sau pe ora de începere, și permite bifarea unuia, a mai multor sau a tuturor meciurilor. **Generează analiza** rulează doar pe rândurile bifațe.

## Decizii

- Varianta C: tabelul înlocuiește multiselect-ul **Meciuri** din sidebar.
- Widget: `st.data_editor` cu coloană booleană de bifă, plus butoane **Selectează toate** și **Debifează toate**.
- După listare, toate rândurile sunt bifațe implicit.
- Listarea apelează doar `matches_by_date` (programul zilei). Nu apelează `enrich_match`, validatorul sau Excel-ul.
- `run_analysis` rămâne neschimbat ca contract: primește `match_ids` din bife.
- Filtrul de ligi rămâne **multiselect** (una sau mai multe ligi).

## În afara scopului

- Modificări la șabloane Excel, adaptoare, formule, praguri, validator, client HTTP FootyStats, autentificare.
- A doua sursă de date, paginare UI, grafice.
- Recalcul server-side.

## UI

### Sidebar

Rămân: dată, fus orar, ligi, modele.  
Dispare: multiselect **Meciuri**.

### Zona principală

Pe același rând, în ordine:

1. **Listează meciurile** (secundar)
2. **Generează analiza** (primary, neschimbat ca etichetă)

Sub butoane, dacă există listă în sesiune:

- Control sortare: **Ligă** | **Oră de începere** (implicit: oră de începere, crescător).
- Butoane **Selectează toate** | **Debifează toate**.
- Tabel: coloane vizibile **Selectat**, **Ligă**, **Oră**, **Echipe**. `match_id` nu e coloană vizibilă.
- **Oră** = kickoff în fusul din filtru, format `HH:MM`.
- Caption scurt: număr de meciuri listate și câte sunt bifațe.

Doar coloana **Selectat** este editabilă. Sortarea din antetul tabelului Streamlit nu înlocuiește controlul de sortare; controlul este sursa de adevăr.

## Flux de date

```
Filtre (dată, fus, ligi)
        │
        ▼
[Listează meciurile] → matches_by_date → filtru competition_id ∈ league_ids
        │
        ▼
session_state.listed_matches (rânduri + selected=True)
        │
        ▼
tabel (sortare + bife)
        │
        ▼
[Generează analiza] → run_analysis(match_ids = rândurile cu selected=True)
```

### Helper

Funcție pură, testabilă, în `src/pipeline.py`:

```python
def list_matches_for_filters(
    *,
    date_iso: str,
    league_ids: list[int],
    timezone_name: str,
    client: FootyStatsClient | None = None,
) -> list[dict[str, Any]]:
```

Comportament:

1. Dacă `league_ids` e gol, returnează `[]` fără apel API (UI-ul afișează warning înainte).
2. Apelează `client.matches_by_date(date_iso, timezone_name=timezone_name)`.
3. Păstrează meciurile cu `int(competition_id) ∈ league_ids`. `league_ids` sunt season id-urile din filtru, același mapping ca în `run_analysis` azi.
4. Pentru fiecare meci, construiește un dict:

| Cheie | Sursă | Note |
| --- | --- | --- |
| `match_id` | `id` | string |
| `liga` | `league_name` sau `competition_name` | string, `""` dacă lipsește |
| `ora` | `date_unix` convertit în `timezone_name` | `HH:MM`; `""` dacă `date_unix` e `-1`/`-2`/`null` |
| `ora_sort` | același `date_unix` ca int, sau `None` | doar pentru sortare, nu se afișează |
| `echipe` | `{home_name} vs {away_name}` | |
| `selected` | — | `True` la creare |

5. Închide clientul dacă helper-ul l-a creat; dacă primește client injectat, nu îl închide (teste).
6. Nu inventează ore sau ligi. Sentinel `-1`/`-2`/`null` pe `date_unix` → `ora=""`, `ora_sort=None`.

### Sortare

- **Ligă:** `liga` A–Z, tie-break `ora_sort` (cele fără oră la sfârșit), apoi `echipe`.
- **Oră de începere:** `ora_sort` crescător (fără oră la sfârșit), tie-break `liga`, apoi `echipe`.

Sortarea reordonează rândurile din sesiune; bifele rămân legate de `match_id`, nu de poziția în tabel. Înainte de reordonare, valorile curente din `st.data_editor` se scriu înapoi în sesiune, altfel o bifă nedeclarată se pierde la rerun.

### Invalidare

Se reține o amprentă `(date_iso, timezone_name, tuple(sorted(league_ids)))`. Dacă amprenta diferă de cea a listei din sesiune, lista se golește (fără apel API) până la un nou **Listează meciurile**.

## Comportament butoane

**Listează meciurile**

- Fără ligi: `st.warning`, nu apelează API, nu scrie listă.
- Cu ligi: apelează helper-ul, salvează lista (toate `selected=True`), resetează widget-ul editorului ca bifele să coincidă. O re-listare înlocuiește lista anterioară și re-bifează tot.
- Zero meciuri: `st.info`, tabel gol.
- `FootyStatsError`: `st.error(exc.user_message)`.

**Selectează toate / Debifează toate**

- Setează `selected` pe toate rândurile din sesiune și resetează cheia `st.data_editor` ca UI-ul să reflecte valoarea (workaround Streamlit: starea internă a editorului altfel ignoră update-ul din sesiune).

**Generează analiza**

- `match_ids` = `match_id` ale rândurilor cu `selected is True`.
- Fără listă în sesiune, sau zero bife, sau zero modele: `st.error`, `run_analysis` nu pornește.
- Restul fluxului (progres, tabel validare, ZIP) rămâne identic.

Sidebar-ul **nu** mai apelează `matches_by_date` la fiecare rerun. Ligile rămân încărcate prin `list_leagues` (necesare pentru filtru).

## Erori (rezumat)

| Situație | UI | API / pipeline |
| --- | --- | --- |
| Nicio ligă | warning | fără `todays-matches` |
| Zero meciuri | info, tabel gol | apel făcut, rezultat gol |
| Eroare FootyStats | mesaj scurt existent | fără listă nouă |
| Generează fără listă / fără bife | error | fără `run_analysis` |
| Fără model | error (ca azi) | fără `run_analysis` |

## Teste

Fișier nou `tests/test_list_matches.py`, client MOCK, fără cheie API.

- Dată `2026-03-15` + ligă `2012` → 2 meciuri: 90001, 90002; ligă Premier League; ore din `date_unix` în Europe/Bucharest.
- Aceeași dată + `2012` și `2013` → 3 meciuri.
- Ligă inexistentă (ex. `9999`) → `[]`.
- `league_ids=[]` → `[]` (și mock-ul nu e apelat dacă putem verifica pe un client stub; altfel doar rezultat gol).
- Sortare ligă: La Liga după Premier League sau invers, A–Z pe nume; în MOCK: La Liga, Premier League.
- Sortare oră: 90001 înaintea 90002 înaintea 90003 (unix 1773550800 < 1773558000 < 1773565200).
- `date_unix` lipsă / `-1` → `ora=""`, `ora_sort=None`, rândul rămâne în listă.

`pytest -q` rămâne PASS. Testele existente de pipeline nu se schimbă (`match_ids` explicit).

Verificare manuală: `streamlit run app.py` → http://localhost:8501, MOCK, dată 2026-03-15, ambele ligi, **Listează meciurile**, sortare, bife, apoi **Generează analiza** doar pe un meci.

## Fișiere de modificat

| Fișier | Schimbare |
| --- | --- |
| `src/pipeline.py` | adaugă `list_matches_for_filters` |
| `app.py` | buton listare, tabel, bife, scoate multiselect meciuri, nu mai fetch-uiește meciuri în sidebar |
| `tests/test_list_matches.py` | nou |
| `docs/PSD_Pontifybet_MVP.md` | secțiunea Interfață: buton **Listează meciurile**, tabel ligă/oră/echipe, bife; sidebar fără meciuri |

Nu se atinge `modele_analize/`, `templates/`, adaptoarele, validatorul, `src/api/client.py`.
