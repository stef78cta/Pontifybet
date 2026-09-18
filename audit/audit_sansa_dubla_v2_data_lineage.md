# Data lineage – Șansă Dublă V2

Referință: `templates/11_model_analiza_pariu_sansadubla_optimizat_V2.xlsx`
(SHA-256 `321546054b7199ba1f4f7f96599cb7f6c43a88c526da25e24fa2a31d3235821b`).

Excel = source of truth. PontifyBet nu reimplementează formulele: scrie inputuri în
`Input_Meci` / `Surse_Date` și evaluează formulele native ale workbook-ului prin
`WorkbookEngine`. Tot ce urmează după `Input_Meci` este, prin construcție, logica Excel.

Rândurile de selecție: **1X = rândul 4**, **X2 = rândul 5**, **12 = rândul 6** pe foaia
`Double_Chance`.

---

## 1. Lanțul complet, etapă cu etapă

| # | Etapă | Python (fișier · funcție · linie aprox.) | Câmp intern | Excel |
| --- | --- | --- | --- | --- |
| 1 | Statistici brute FootyStats | `src/api/client.py` · `enrich_match` | `MatchData.home/away.*` | – |
| 2 | Medii per meci (goluri, xG, H/A) | `src/engines/double_chance/inputs.py` · `_per_match` L34 | – | `Input_Meci!B12:C17` |
| 3 | Prior de ligă + eșantion | `inputs.py` · `league_prior_rates` L162 | `league_avg_gf_home/away` | `Surse_Date!G10/H10` |
| 4 | Shrinkage empirical-Bayes | `inputs.py` · `empirical_bayes_rate` L136, `_maybe_shrink` L197 | `lambda` post-shrink | `Surse_Date!C10/I10/K10` |
| 5 | **Scoreline distribution** | `inputs.py` · `derived_1x2_distributions` L210 (ramura H/A + xG) | `p1/px/p2` scoreline | `Model_1X2!J6:L6` |
| 6 | **Strength distribution** | `inputs.py` · `derived_1x2_distributions` L210 (ramura overall) | `p1/px/p2` strength | `Model_1X2!J7:L7` |
| 7 | Piață 1X2 de-vig | `inputs.py` · `match_to_double_chance_inputs` L497 | `Input_Meci!B28:B30` | `Model_1X2!J8:L8` |
| 8 | Blend 50/25/25 | — (formulă Excel) | — | `Model_1X2!B9:D9` → normalizare `B10:D10` |
| 9 | `P_model` per selecție | `engine.py` · `compute_double_chance` L296 | `DoubleChanceSelection.p_model` | `Double_Chance!B4:B6` |
| 10 | `Pfail_model` | `engine.py` L297 | `.pfail_model` | `Double_Chance!D4:D6` |
| 11 | `Pfail_market` | `engine.py` L298 | `.pfail_market` | `Double_Chance!X4:X6` |
| 12 | `Pfail_DC` conservator | `engine.py` L299 | `.pfail_dc` | `Double_Chance!Y4:Y6` = `MAX(D, X)` |
| 13 | Haircut bază (confidence) | `engine.py` L300 | `.haircut_base` | `Uncertainty_v2!B8` |
| 14 | Haircut early season | `engine.py` L301 | `.haircut_early` | `Uncertainty_v2!B9` |
| 15 | Haircut total | `engine.py` L302 | `.haircut_total` | `Uncertainty_v2!B10` → `Double_Chance!E` |
| 16 | `P_adj` | `engine.py` L303 | `.p_adj` | `Double_Chance!F` = `MAX(0, B - E)` |
| 17 | Market Direction | `engine.py` L307 | `.market_direction` | `Double_Chance!O` |
| 18 | Protected Strength | `engine.py` L308 | `.protected_strength` | `Double_Chance!P` |
| 19 | Draw Gate | `engine.py` L309 | `.draw_gate` | `Double_Chance!Q` ← `P0_Gates_v2!I6/J6` |
| 20 | P0 final | `engine.py` L310 | `.p0_final` | `Double_Chance!U` |
| 21 | Componente Risk Score | `engine.py` · `_risk_breakdown` L332 | `.risk.*` | `Parametri!B35:B38`, `B44:B46` |
| 22 | Risk Score | `engine.py` L315 | `.score` | `Double_Chance!L` |
| 23 | Risk Level | `engine.py` L316 | `.level` | `Double_Chance!M` (praguri `B39:B42`) |
| 24 | Verdict | `engine.py` L317 | `.verdict` | `Double_Chance!N` |
| 25 | Ranking Eligible | `engine.py` L319 | `.ranking_eligible` | `Double_Chance!AA` |
| 26 | DEFENSIV flag | `engine.py` L320 | `.defensive_eligible` | `Double_Chance!AE` = `AND(AA="YES", N="DEFENSIV")` |
| 27 | Transport spre UI/CSV | `src/pipeline.py` L286, `src/ui_tables.py`, `src/excel/generator.py` | `dc_selections` | – |

---

## 2. Audit Pfail — **PARITY BUG găsit (display)**

### Ce era

```python
pfail=_as_number_or_none(col("D")),   # P_failure model
```

Un singur câmp `pfail`, alimentat din coloana `D` = **Pfail_model**. Coloana afișată în
UI, scrisă în CSV și scrisă înapoi în `Input_Meci!C61:C63` era Pfail-ul modelului.

### Ce folosește Excel

`Double_Chance!L4` (Risk Score) folosește `Y4`, nu `D4`:

```
L4 = MIN(Parametri!B43, ROUND(Y4*Parametri!B35 + E4*Parametri!B36 + surcharges, 0))
Y4 = MAX(D4, X4)
```

### Dovada numerică (fixture `baseline`, selecția 1X)

| Mărime | Celulă | Valoare |
| --- | --- | --- |
| Pfail_model | `D4` | 0.07 |
| Pfail_market | `X4` | 0.08 |
| Pfail_DC | `Y4` | **0.08** |

Scor Excel = 16. Verificare: `180·0.08 + 200·0.01 = 16.4 → ROUND = 16`. ✔
Cu `D4`: `180·0.07 + 200·0.01 = 14.6 → 15`. ✘

Deci **Risk Score-ul folosea deja valoarea corectă** (o calculează Excel), dar interfața
afișa 7.00% acolo unde motorul lucra cu 8.00%.

### Ce s-a schimbat

Câmpul ambiguu `pfail` a fost eliminat. Există acum `pfail_model`, `pfail_market`,
`pfail_dc`, expuse separat în UI și CSV. `Input_Meci!C61:C63` scrie `Pfail_DC (Y)`.

**Clasificare: DISPLAY ONLY.** Niciun verdict nu se schimbă — confirmat de
`audit/diff_sansa_dubla_v2.csv` (0 diferențe pe 129 rânduri).

---

## 3. Audit mapping gate-uri — **PARITY BUG găsit (naming)**

Numele câmpurilor Python nu corespundeau coloanelor Excel:

| Câmp Python (înainte) | Citea | Coloana Excel este de fapt |
| --- | --- | --- |
| `pfail_gate` | `O` | Market Direction |
| `draw_gate` | `P` | Protected Strength |
| `fragility_gate` | `Q` | Draw Market |

Nu exista niciun `pfail_gate` în workbook, iar `draw_gate` arăta Protected Strength.
Fragilitatea reală este pe `AB`. Corectat: `market_direction`=`O`, `protected_strength`=`P`,
`draw_gate`=`Q`, `fragility_gate`=`AB`.

**Clasificare: DISPLAY ONLY / DATA MAPPING FIX** (etichetă, nu valoare).

---

## 4. Audit motor 1X2 — **MODEL PARITY FAIL**

Excel cere trei componente independente, ponderate `Parametri!B32:B34` = 0.50 / 0.25 / 0.25:

| Componentă | Celule | Cerință metodologică |
| --- | --- | --- |
| Scoreline | `Model_1X2!J6:L6` | Dixon-Coles / Poisson bivariat |
| Strength | `Model_1X2!J7:L7` | Elo/rating + formă |
| Market | `Model_1X2!J8:L8` | 1X2 de-vig |

Ponderile **sunt corecte** în implementare: workbook-ul le aplică nativ, iar aplicația nu
le atinge. Blend-ul `Model_1X2!B10:D10` însumează 1.0 pe toate cele 37 de fixture-uri
(test `test_blended_1x2_sums_to_one_after_normalisation`).

Problema este **provenienței rândurilor 6 și 7**. În `derived_1x2_distributions`:

- rândul 6 = Poisson independent pe λ din goluri H/A combinate cu xG;
- rândul 7 = Poisson independent pe λ din goluri overall.

Ambele sunt **același estimator** (`poisson_1x2`, L112) aplicat pe două felii ale
aceluiași set de goluri. Nu există Dixon-Coles (fără parametru `tau` de corecție pentru
scoruri mici) și nu există Elo/rating (fără stare persistentă între meciuri, fără
actualizare secvențială).

**Consecință:** rândurile 6 și 7 nu sunt independente. Corelația dintre ele este ridicată
prin construcție, deci ponderea efectivă a modelului de goluri nu este 50%, ci se apropie
de 75%, iar piața rămâne singura sursă cu adevărat independentă la 25%.

Nu am inventat un Elo și nu am inventat un Dixon-Coles — ar fi însemnat parametri fără
sursă metodologică. Căutarea în codebase nu a găsit nicio implementare canonică existentă
a acestor două motoare. Componenta lipsă este raportată ca atare; aplicația marchează deja
acest lucru în UI („1X2 LIVE este DERIVED din goluri/xG (Poisson independent)”).

**Status: MODEL PARITY FAIL pe proveniența inputurilor. Paritatea formulelor Excel este
intactă.** Propunerea de remediere este în `V3_CHALLENGER_PROPOSAL.md`.

---

## 5. Audit prior / shrinkage — **METHOD CLOSURE REQUIRED – PRIOR STRENGTH**

### Ce expune acum aplicația

| Mărime | Sursă | Excel |
| --- | --- | --- |
| `N_current` | `matches_played_home/away` | `Input_Meci!B36/C36` |
| `N_prior` | `league_avg_gf_home/away` → `.n` | `Surse_Date!G10/H10` |
| `prior_source` | „FootyStats league averages” | `Surse_Date!D10` |
| `prior_cutoff` | kickoff − 1h | `Surse_Date!F10` |
| `prior_method` | text `empirical Bayes …` | `Surse_Date!I10` |
| `weight_current` | `n / (n + n_prior)` | – |
| `weight_prior` | `n_prior / (n + n_prior)` | – |
| λ înainte / după | `_maybe_shrink` L197 | `Model_1X2!J6:L7` |

Declanșator: `needs_early_season_prior` (L190) — se aplică dacă `N_current < Small_Sample_N`
(`Parametri!B17` = 8), exact pragul Excel.

### Problema deschisă

Formula implementată este empirical-Bayes standard:

```
rate_post = (n_current · rate_current + n_prior · rate_prior) / (n_current + n_prior)
```

cu `n_prior` = numărul total de meciuri H/A din ligă. Pentru o ligă cu ~180 de meciuri
jucate, un club cu `N_current = 5` primește o pondere proprie de `5/185 ≈ 2.7%`. Priorul
înghite practic semnalul echipei: Bayern și Union converg spre aceeași λ de ligă.

**Nu am găsit această regulă în documentația metodologică.** `Matrice_lipsa_date_v4`
prescrie „prior + shrinkage + confidence cap” pentru LD-0, iar `Cadru_unificat_v5` repetă
regula, dar **niciunul nu definește puterea priorului** (`kappa` / `n0`).

Nu am modificat `n_prior` ca să obțin probabilități mai mari pentru favoriți — ar fi fost
exact retrofitting-ul interzis. Regula rămâne ca în implementarea curentă și este marcată:

> **METHOD CLOSURE REQUIRED – PRIOR STRENGTH**
> Puterea priorului trebuie decisă metodologic (kappa fix, ex. 5–10 meciuri echivalente),
> nu preluată implicit din dimensiunea ligii. Vezi `V3_CHALLENGER_PROPOSAL.md` §2.

### Diagnostic comparativ

Rulează:

```
.venv\Scripts\python.exe scripts/audit_double_chance.py baseline early_season_A
```

`baseline` = eșantion adecvat (`Surse_Date!L10 = N/A`, fără shrinkage).
`early_season_A` = `N_current = 5`, confidence B, early season DA → `L10 = READY`, shrinkage activ.

---

## 6. Haircut — verificat, neschimbat

| Regim | `Uncertainty_v2!B8` | `B9` | `B10` |
| --- | --- | --- | --- |
| Confidence A, fără early season (`baseline`) | 0.010 | 0.000 | 0.010 |
| Confidence B + early season (`early_season_A`) | 0.025 | **0.020** | **0.045** |

Valorile cerute (2.5 pp, respectiv 2.5 + 2 = 4.5 pp) sunt confirmate empiric.
`EarlySeason_Extra_Haircut` = `Parametri!B25` = 0.02, neatins.
SMALL SAMPLE rămâne stare de date, nu hard fail: `Surse_Date!L9 = READY`.

Test: `test_haircut_total_is_base_plus_early_season`.

---

## 7. Risk Score — decompoziție, fără recalibrare

`_risk_breakdown` (engine.py L332) citește coeficienții **din `Parametri`**, nu din literali
Python, deci decompoziția nu poate devia de workbook.

Verificare pe `baseline`:

| Selecție | Failure | Haircut | Surcharges | Before cap | Excel `L` |
| --- | --- | --- | --- | --- | --- |
| 1X | 180·0.08 = 14.4 | 200·0.01 = 2.0 | 0 | 16 | **16** ✔ |
| X2 | 180·0.825 = 148.5 | 2.0 | 60 (FAIL) | 211 | **100** (plafon) ✔ |
| 12 | 200·0.105 = 21.0 | 120·0.01 = 1.2 | 0 | 22 | **22** ✔ |

`Risk_Score_Before_Cap` este păstrat: pe fixture-uri apar valori distincte peste 100
(ex. 211 vs 218), deci un FAIL marginal se distinge de unul extrem.
Test: `test_capped_scores_keep_distinguishable_raw_value`.

Coeficienții 180 / 200 / 200 / 120 și pragurile 20/40/60/80 sunt neatinse.
Analiza frontierei este în `risk_coherence_report.md`.

---

## 8. Audit special 12

`DrawDiagnostics` (engine.py L410) expune:

| Mărime | Sursă |
| --- | --- |
| `Pdraw_model_raw` | `Model_1X2!C10` |
| `Pdraw_model_plus_haircut` | `P0_Gates_v2!I6` = `MIN(1, C10 + E6)` |
| `Pdraw_market` | `P0_Gates_v2!J6` |
| `Pdraw_adj` | `MAX(I6, J6)` |

`baseline`: 0.105 / 0.115 / 0.100 / 0.115.
`early_season_A`: 0.105 / 0.150 / 0.100 / 0.150.

Haircut-ul nu a fost scos nici din Draw Gate, nici din Risk Score. Impactul fiecărei
componente este acum vizibil separat — tabelul de numărătoare este în
`risk_coherence_report.md`.

Test: `test_draw_gate_uses_model_plus_haircut_against_market`.

---

## 9. Gate ≠ verdict

`Double_Chance!N` (verdict) nu este `U` (P0 final):

```
N4 = ... IF(AND(M4=1, U4="PASS", F4>='Parametri'!B4), "DEFENSIV",
         IF(F4>='Parametri'!B5, "PRUDENT", "MODERAT")) ...
```

Un `U = PRUDENT` **nu** produce verdict PRUDENT; nivelul `M` decide întâi. Pentru 1X/X2,
DEFENSIV cere obligatoriu `M = 1`. Pentru 12, formula `N6` nu verifică deloc `F6` față de
`Min_P_DC_Strong` — o asimetrie reală a workbook-ului, documentată, nu corectată.

UI-ul separă acum `Market Direction`, `Protected Strength`, `Draw Gate`, `P0 final` de
`Nivel` și `Verdict`. Test: `test_gate_status_is_not_the_final_verdict`.

---

## 10. Rezumat findings

| # | Finding | Tip | Clasificare diff |
| --- | --- | --- | --- |
| 1 | `pfail` afișa `D` (model) în loc de `Y` (conservator) | implementare | DISPLAY ONLY |
| 2 | `pfail_gate`/`draw_gate`/`fragility_gate` mapate greșit pe O/P/Q | implementare | DISPLAY ONLY |
| 3 | Rândurile 6 și 7 din `Model_1X2` provin din același estimator Poisson | metodologic | MODEL PARITY FAIL |
| 4 | `n_prior` = mărimea ligii, fără sursă metodologică | metodologic | METHOD CLOSURE REQUIRED |
| 5 | `Min_P_DC_Strong = 0.82` nu este niciodată constrângerea activă pentru 1X/X2 | metodologic | doar diagnostic |
| 6 | Haircut contabilizat de 3 ori pentru selecția 12 | metodologic | doar diagnostic |
| 7 | `N6` nu aplică prag de probabilitate pentru DEFENSIV la 12 | metodologic (Excel) | doar diagnostic |

Findings 1–2 au fost reparate. Findings 3–7 sunt **documentate, nu modificate**, conform
regulii VERSION LOCK; propunerile sunt în `V3_CHALLENGER_PROPOSAL.md`.
