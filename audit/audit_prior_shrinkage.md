# Audit PRIOR / SHRINKAGE – Șansă Dublă V2

Lot: **FootyStats LIVE, 2026-09-19**, 157 meciuri, 471 selecții, dintre care 429 cu
probabilități complete. Date brute: `model_vs_market_diagnostic.csv`.

## Verdict

> **METHOD CLOSURE REQUIRED — PRIOR / SHRINKAGE**
>
> Priorul este dominant. Pe cele 393 de selecții cu shrinkage activ, datele proprii ale
> echipei contribuie în medie cu **5,3%**, iar priorul de ligă cu **94,7%**.
> Regula care produce această pondere nu are sursă metodologică.

Nu am înlocuit-o cu alt kappa/n0. O presupunere nu se repară cu altă presupunere.

---

## 1. Unde este implementată formula

| Element | Locație |
| --- | --- |
| Formula de blending | `src/engines/double_chance/inputs.py` · `empirical_bayes_rate` L136 |
| Declanșatorul | `inputs.py` · `needs_early_season_prior` L190 |
| Sursa lui `N_prior` | `inputs.py` · `league_prior_rates` L162 → `match.league_avg_gf_home/away.n` |
| Populează `.n` | `src/api/client.py` · `league_goal_averages` / `build_match_data` |
| Decizia de aplicare | `inputs.py` L602: `needs_early_season_prior(...) and league_prior_is_valid(match)` |

Formula:

```
rate_post = (n_current · rate_current + n_prior · rate_prior) / (n_current + n_prior)
```

`n_prior` = numărul de meciuri din care s-a calculat media de ligă acasă/deplasare,
adică practic **toate meciurile jucate în ligă în acel sezon**.

Declanșator: `min(N_home, N_away) < Parametri!B17` (= 8). Pragul provine din Excel și
este corect. **Puterea priorului nu provine de nicăieri.**

## 2. Verificare în specificații

| Document | Ce spune | Definește puterea priorului? |
| --- | --- | --- |
| `Matrice_lipsa_date_v4` | SMALL SAMPLE = LD-0; tratament „prior + shrinkage + confidence cap” | **Nu** |
| `Cadru_unificat_analiza_si_risc_pariuri_v5` | aceeași regulă; ranking blocat de market audit, nu de N mic | **Nu** |
| `Manual_tehnic_Sansa_Dubla_V2` | `Small_Sample_N = 8`, haircut early-season 2 pp | **Nu** |
| Workbook V2 | rândul 10 din `Surse_Date` doar *documentează* shrinkage-ul aplicat extern | **Nu** |

Niciun document nu prescrie `n_prior`. Valoarea folosită este o consecință accidentală a
sursei de date (dimensiunea ligii), nu o decizie metodologică.

## 3. Ponderile efective pe lotul real

Pe cele 393 de selecții cu shrinkage activ:

| Mărime | Valoare |
| --- | --- |
| Pondere prior, medie | **94,7%** |
| Pondere prior, mediană | 94,8% |
| Pondere prior, maxim | 97,6% |
| Pondere date proprii, medie | **5,3%** |
| `N_current` (gazde), medie | 2,8 meciuri |
| `N_prior` (ligă), medie | 52,3 meciuri |

Cu `N_current = 3` și `N_prior = 53`, ponderea proprie este `3/56 = 5,4%`.
Pragul `Small_Sample_N = 8` își pierde sensul: nu mai separă „puțină informație proprie”
de „suficientă”, ci „aproape numai prior” de „numai date proprii”. Trecerea de la N=7 la
N=8 mută ponderea proprie de la ~12% la 100% — o discontinuitate, nu o tranziție.

## 4. Efectul măsurat asupra probabilităților

Metrica: `top1` = cea mai mare dintre P(1), P(X), P(2). Excesul peste 1/3 arată cât de
departe de uniform este distribuția. Raportul față de piață = ce fracțiune din semnalul
de diferențiere al pieței se păstrează.

| Componentă | exces peste 1/3 | raport vs piață |
| --- | --- | --- |
| Piață de-vig | 0,1531 | 1,000 |
| Scoreline **înainte** de shrinkage | 0,1459 | **0,952** |
| Scoreline **după** shrinkage | 0,1106 | **0,722** |
| Strength **înainte** de shrinkage | 0,1147 | 0,749 |
| Strength **după** shrinkage | 0,0516 | **0,337** |
| Blend final | 0,0950 | 0,620 |

Pe subsetul cu shrinkage activ, comparație în interiorul acelorași meciuri:

| Segment | n | scoreline brut | scoreline final | blend final |
| --- | --- | --- | --- | --- |
| Fără shrinkage (VERIFIED) | 36 | 0,741 | 0,741 | 0,729 |
| Cu shrinkage | 393 | **0,975** | **0,720** | 0,609 |

Citirea corectă: pe meciurile cu eșantion mic, scoreline-ul brut păstrează **97,5%** din
semnalul pieței — estimatorul în sine este bun. Shrinkage-ul îl coboară la **72,0%**.
**Shrinkage-ul distruge aproximativ un sfert din capacitatea de diferențiere a modelului.**

## 5. Caz-martor: Sporting CP – FC Arouca

Raport complet în `bayern_union_witness_report.md`.

> Bayern – Union nu figurează în calendarul FootyStats pentru 2026-09-19..21, deci nu
> putea fi folosit ca martor fără date fabricate. Sporting CP – Arouca este echivalentul
> structural disponibil: favorit clar acasă (piață 78,67%), eșantion mic (N=3).

| Parametru | N curent | N prior | Pondere proprie | Înainte | După | Δ |
| --- | --- | --- | --- | --- | --- | --- |
| `scoreline.home_attack` (Sporting) | 3 | 53 | 5,4% | 2,128 | 1,411 | **−0,718** |
| `scoreline.away_attack` (Arouca) | 3 | 53 | 5,4% | 0,522 | 1,351 | **+0,830** |
| `scoreline.home_defence` | 3 | 53 | 5,4% | 0,960 | 1,375 | +0,415 |
| `scoreline.away_defence` | 3 | 53 | 5,4% | 1,473 | 1,376 | −0,098 |

λ pentru oaspeți: **0,741 → 1,363**. Atacul lui Arouca este aproape dublat de prior.

| Distribuție | P(1) | P(X) | P(2) |
| --- | --- | --- | --- |
| Scoreline înainte de shrinkage | **62,68%** | 22,45% | 14,87% |
| Scoreline după shrinkage | **37,93%** | 25,51% | 36,56% |
| Piață de-vig | **78,67%** | 13,33% | 8,00% |
| Blend final | 48,14% | 22,45% | 29,42% |

Priorul mută P(1) cu **−24,75 pp** și transformă un favorit clar într-un meci aproape
echilibrat. Rezultatul: 1X are `P_model = 70,58%` față de `P_market = 92,00%`, Risk Score
62, Nivel 4, verdict RIDICAT.

## 6. Contra-martor VERIFIED: Molde – Aalesund

Raport complet în `verified_match_witness_report.md`.

`N_home = 10`, `N_away = 9`, deci **pondere proprie 100%**, shrinkage inactiv, toate
Δ = 0,0000. Scoreline rămâne identic înainte și după.

| Selecție | P_model | P_market | Δ |
| --- | --- | --- | --- |
| 1X | 78,72% | 85,77% | **−7,05 pp** |
| 12 | 80,40% | 85,40% | −5,00 pp |

Comparație directă pe partea de favorit:

| Caz | Eșantion | Pondere prior | Δ(1X) |
| --- | --- | --- | --- |
| Sporting – Arouca | SMALL SAMPLE | 94,6% | **−21,42 pp** |
| Molde – Aalesund | VERIFIED | 0% | **−7,05 pp** |

**Bias-ul este de trei ori mai mare când shrinkage-ul este activ.** Răspunsul la întrebarea
din §11 a cerinței: da, abaterea se reduce semnificativ când dispare shrinkage-ul
early-season — dar nu dispare complet. Reziduul de −7 pp aparține motorului, nu priorului
(vezi `audit_scoreline_vs_strength.md`).

## 7. Ce NU am modificat

- `empirical_bayes_rate` — formula de blending rămâne neschimbată;
- `n_prior` — rămâne dimensiunea ligii;
- `Small_Sample_N = 8` — neatins;
- haircut-ul early-season de 2 pp — neatins;
- niciun kappa sau n0 nou nu a fost introdus.

Singura modificare de cod în acest audit este instrumentarea: `derived_1x2_distributions`
deleagă acum către `derived_1x2_trace`, care expune aceleași calcule cu urmă completă.
Verificat ca neutru numeric: `diff_dc_v2.csv` are 0 rânduri.

## 8. Ce trebuie decis metodologic

1. Puterea priorului trebuie exprimată ca un `kappa` fix, în meciuri echivalente,
   independent de câte meciuri are liga. O ligă cu 300 de meciuri jucate nu trebuie să
   producă un prior de trei ori mai greu decât una cu 100.
2. Tranziția la `Small_Sample_N = 8` trebuie să fie continuă, nu o treaptă de la 12% la 100%.
3. Priorul ar trebui probabil condiționat pe forța echipei (de ex. poziția în clasament sau
   ratingul de sezon precedent), nu pe media brută a ligii — altfel un promovat și un
   campion primesc același prior.

Propunerile cuantificate sunt în `V3_CHALLENGER_PROPOSAL.md` §2. Niciuna nu se activează
fără backtest frozen out-of-sample.
