# Audit Scoreline vs Strength – Șansă Dublă V2

Lot: **FootyStats LIVE, 2026-09-19**, 157 meciuri. Date brute:
`model_vs_market_diagnostic.csv`.

## Verdict

> **MODEL INDEPENDENCE FAIL** — cele două „motoare” sunt două transformări ale acelorași
> date, produse de aceeași funcție.
>
> **SCORELINE ENGINE PARITY FAIL** — scoreline-ul este un Poisson independent, nu
> Dixon-Coles și nici Poisson bivariat.

Nu am inventat parametri Dixon-Coles și nu am construit un Elo. Componentele lipsă sunt
raportate ca atare.

---

## 1. Ce cere specificația

`Model_1X2` așteaptă trei distribuții pe rândurile 6, 7 și 8, ponderate cu
`Parametri!B32:B34` = 0,50 / 0,25 / 0,25:

| Rând | Componentă | Metodă cerută |
| --- | --- | --- |
| 6 | Scoreline | Dixon-Coles / Poisson bivariat |
| 7 | Strength | Elo / rating + formă |
| 8 | Market | 1X2 de-vig |

Ponderarea 50/25/25 presupune surse cu erori **necorelate**. Acesta este întregul motiv
pentru care există trei componente în loc de una.

## 2. Ce există efectiv

| Aspect | Rândul 6 (scoreline) | Rândul 7 (strength) |
| --- | --- | --- |
| Fișier | `src/engines/double_chance/inputs.py` | idem |
| Funcție | `derived_1x2_trace` L298 | `derived_1x2_trace` L298 |
| Estimator final | `poisson_1x2` L112 | `poisson_1x2` L112 |
| Construcția λ | `_lambda_from_sides` L129 | `_lambda_from_sides` L129 |
| Inputuri | goluri H/A + xG H/A | goluri overall + xG overall |
| Sursa statisticilor | FootyStats team stats | **aceleași** FootyStats team stats |
| Stare persistentă între meciuri | nu | nu |
| Parametru de corecție pentru scoruri mici | nu | nu |
| Rating secvențial | nu | nu |

Ambele rânduri rulează **exact aceeași funcție** `poisson_1x2(λ_home, λ_away)`, pe λ
construite de **aceeași funcție** `_lambda_from_sides`, din **același set** de goluri și xG.
Singura diferență este felia: acasă/deplasare pentru rândul 6, sezon complet pentru rândul 7.

Un „model de forță” care nu are rating și nu are memorie între meciuri nu este un model de
forță. Este același model de goluri, agregat diferit.

## 3. Dovada empirică a dependenței

Corelații între P(1) produs de fiecare componentă, pe 157 de meciuri:

| Pereche | Corelație |
| --- | --- |
| scoreline brut ↔ strength brut | **0,774** |
| scoreline brut ↔ piață | 0,503 |
| strength brut ↔ piață | — |
| scoreline după shrinkage ↔ strength după shrinkage | 0,382 |
| scoreline după shrinkage ↔ piață | 0,137 |

Corelația de **0,774** între cele două componente „independente” confirmă dependența
structurală. Pentru comparație, corelația fiecăreia cu piața este 0,50 — adică cele două
modele seamănă între ele mai mult decât seamănă oricare dintre ele cu piața.

Distanța absolută medie între cele două distribuții este **0,067** (mediană 0,070,
maxim 0,220). Două motoare metodologic distincte ar diverge substanțial mai mult, mai ales
pe meciurile dezechilibrate.

### Consecința asupra ponderilor

Cu o corelație de 0,77 între rândurile 6 și 7, ponderea efectivă a informației de goluri nu
este 0,50, ci se apropie de **0,75**. Piața rămâne singura sursă cu adevărat independentă,
la 25%. Varianța blend-ului este subestimată: ponderarea 50/25/25 presupune o diversificare
care nu există.

## 4. Scoreline: ce lipsește față de Dixon-Coles

| Element Dixon-Coles | Prezent? |
| --- | --- |
| Poisson pe grilă de scoruri | da (`poisson_1x2`, grila 0..12) |
| Parametrul `tau` de corecție pentru 0-0, 1-0, 0-1, 1-1 | **nu** |
| Ponderare temporală exponențială a meciurilor | **nu** |
| Estimare simultană atac/apărare prin maximum likelihood | **nu** |
| Corelație între golurile celor două echipe | **nu** (independență presupusă) |

Corecția `tau` există tocmai pentru că Poisson-ul independent greșește sistematic în zona
scorurilor mici — exact zona care decide 1X / X2 / 12.

Efectul este vizibil în lot:

- P(X) model, medie = 0,2468
- P(X) piață, medie = 0,2526
- diferență medie = **−0,59 pp**

Modelul subestimează egalul, ceea ce este semnătura clasică a Poisson-ului independent.
Diferența este mică în medie, dar are semn constant și afectează direct selecția 12, unde
`Pfail_DC` este chiar P(X).

## 5. Construcția lui λ

```python
def _lambda_from_sides(attack, defence):
    return _clamp_lambda(_blend_rate(attack, defence))   # media aritmetică
```

λ este **media aritmetică** dintre rata de atac a unei echipe și rata de apărare a
adversarei. Forma standard Poisson este multiplicativă, raportată la media ligii:

```
λ_home = (atac_gazde / medie_ligă) · (apărare_oaspeți / medie_ligă) · medie_ligă
```

Media aritmetică înjumătățește abaterea față de medie: dacă atacul este cu +80% peste medie
și apărarea adversarei cu +30% peste medie, forma multiplicativă dă +134%, iar media
aritmetică dă +55%.

Măsurat însă pe lotul real, scoreline-ul **brut** păstrează 95,2% din semnalul pieței
(97,5% pe subsetul cu eșantion mic). Pe intervalele de valori întâlnite efectiv, media
aritmetică nu este cauza principală a compresiei. Este o abatere de la forma canonică,
merită documentată, dar **nu este vinovatul principal** — spre deosebire de prior.

Aceasta este o corecție a unei ipoteze pe care auditul anterior o formulase analitic:
măsurătoarea o infirmă.

## 6. Unde apare, pe etape, diferența față de piață

| Etapă | raport vs piață | pierdere la etapa respectivă |
| --- | --- | --- |
| Piață de-vig | 1,000 | — |
| Scoreline brut | 0,952 | −4,8% (estimatorul Poisson + λ mediat) |
| Scoreline după shrinkage | 0,722 | **−23,0%** (priorul) |
| Strength brut | 0,749 | −20,3% (agregarea overall pierde avantajul de teren) |
| Strength după shrinkage | 0,337 | **−41,2%** (priorul) |
| Blend final | 0,620 | — |

Ierarhia cauzelor, în ordinea impactului:

1. **PRIOR / SHRINKAGE** — de departe cel mai mare efect (−23 până la −41 puncte de raport).
2. **Agregarea overall din rândul 7** — pierde distincția acasă/deplasare, deci comprimă
   independent de prior (0,749 chiar fără shrinkage).
3. **Lipsa corecției Dixon-Coles** — efect mic pe favorit, dar sistematic pe egal (−0,59 pp).
4. **Media aritmetică în λ** — abatere de formă, impact măsurat mic pe acest lot.

## 7. Căutare de implementări canonice existente

Am căutat în codebase un motor Dixon-Coles, un Elo sau un rating secvențial reutilizabil.
Nu există: singurii estimatori de probabilitate sunt `poisson_1x2` (Șansă Dublă) și motorul
Over 0.5, care folosește tot Poisson. Nu există stare persistentă între meciuri nicăieri,
deci un Elo nu poate fi „reconectat” — ar trebui construit, cu decizii metodologice
(factor K, rating inițial, tratamentul promovaților) care nu sunt specificate nicăieri.

Conform regulii din cerință, componenta lipsă este raportată, nu inventată.

## 8. Ce NU am modificat

- `poisson_1x2`, `_lambda_from_sides`, `_blend_rate` — neatinse;
- ponderile 50/25/25 — neatinse;
- felierea H/A vs overall între rândurile 6 și 7 — neatinsă;
- fallback-ul prin care o distribuție lipsă o împrumută pe cealaltă — neatins.

Singura modificare este instrumentarea. `diff_dc_v2.csv` are 0 rânduri.
