# Performance report — optimizare „Generează analiza”

Benchmark MOCK: 3 meciuri, modele `over05` + `double_chance` + `corners`, dată `2026-03-15`.

Generat cu: `.venv\Scripts\python.exe scripts\benchmark_analysis.py`

## BEFORE (flux monolitic HEAD anterior)

| Metrică | Valoare estimată |
| --- | --- |
| league-teams calls | 1 × meci (≈3) |
| last5 calls | 2 × meci fără dedup garantat (≈6) |
| last10 calls | 2 × meci (≈6) — **nefolosit de modele** |
| compute_over05 | 2 × meci eligibil (pipeline + adaptor) |
| compute_double_chance | 2 × meci (pipeline + adaptor) |
| derived_1x2_trace | 2+ × meci (mapping + audit prior) |
| TIME TO TABLE | include Excel + fingerprint + ZIP |
| TIME TO EXPORT | N/A (amestecat) |

## AFTER (ANALYSIS separat de EXPORT)

| Metrică | Valoare măsurată |
| --- | --- |
| league-teams calls | 2 (1 per sezon) |
| last5 calls | 6 (deduplicat pe `(team_id, 5)`) |
| last10 calls | **0** |
| compute_over05 | 3 (1 × meci) |
| compute_double_chance | 3 (1 × meci) |
| derived_1x2_trace | 3 (1 × meci) |
| TIME TO TABLE | **1.70 s** |
| TIME TO EXPORT | **25.59 s** (doar la „Pregătește fișierele Excel”) |
| total ANALYSIS+EXPORT | 27.29 s |

## Speedup percepție UI

- **Tabel vizibil**: de la ~47 s (flux monolitic estimat) la **~1.7 s** → ~**28×** mai rapid la afișarea verdictului.
- **Export Excel/ZIP**: ~26 s (Cornere + 3× Șansă Dublă domină), dar nu blochează UI-ul inițial.

## Request count BEFORE vs AFTER (3 meciuri MOCK)

| Tip | BEFORE (estim.) | AFTER |
| --- | --- | --- |
| league-teams | 3 | 2 |
| last5 | 6 | 6 |
| last10 | 6 | 0 |
| FootyStats total lastx | 12 | 6 |

## Note

- Nu s-a modificat niciun prag, formulă sau motor metodologic.
- Exportul nu refetch-uiește și nu recalculează motoarele (`counters` export = 0).
- Profilul complet JSON: `docs/performance_report_analysis.json`
