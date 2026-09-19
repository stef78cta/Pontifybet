# Diagnostic upstream: model vs piață

Sursă date: **FootyStats LIVE**, data 2026-09-19. 429 selecții (143 meciuri).

Delta este `P_model - P_market`, în puncte procentuale.

## Identitatea de sumă (verificare de sanitate)

Pentru orice meci, fiecare rezultat (1, X, 2) apare în exact două șanse duble,
deci `P(1X) + P(X2) + P(12) = 2` atât pentru model, cât și pentru piață —
ambele distribuții fiind normalizate la 1 în `Model_1X2`.
Prin urmare **suma celor trei delte ale unui meci este 0 prin construcție**.

Meciuri cu toate cele trei selecții: 143. Cea mai mare abatere de la suma zero: 4.44e-14 pp.

Consecință: o afirmație de tip „toate selecțiile au P_model < P_market” nu poate
descrie un lot complet; descrie un subset filtrat (de regulă selecțiile cu
probabilitate mare). Semnalul real nu este o deplasare în jos, ci o **compresie**.

## Statistici delta (pp)

| Segment | n | medie | mediană | min | max | abatere std | % model<piață | % model>piață | % egal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TOTAL | 429 | 0.00 | 0.31 | -25.79 | 33.85 | 7.81 | 46.2% | 53.8% | 0.0% |
| VERIFIED | 36 | 0.00 | -0.17 | -15.39 | 18.10 | 6.23 | 50.0% | 50.0% | 0.0% |
| SMALL SAMPLE | 393 | -0.00 | 0.32 | -25.79 | 33.85 | 7.93 | 45.8% | 54.2% | 0.0% |
| shrinkage DA | 393 | -0.00 | 0.32 | -25.79 | 33.85 | 7.93 | 45.8% | 54.2% | 0.0% |
| shrinkage NU | 36 | 0.00 | -0.17 | -15.39 | 18.10 | 6.23 | 50.0% | 50.0% | 0.0% |
| 1X | 143 | -1.78 | -2.73 | -25.79 | 33.85 | 8.96 | 61.5% | 38.5% | 0.0% |
| X2 | 143 | 1.19 | 1.15 | -25.54 | 30.54 | 9.62 | 44.8% | 55.2% | 0.0% |
| 12 | 143 | 0.59 | 0.92 | -9.12 | 5.01 | 2.26 | 32.2% | 67.8% | 0.0% |

## Segmentare pe bandă de probabilitate a pieței

Dacă bias-ul ar fi o deplasare uniformă în jos, delta ar fi negativă în toate benzile.
Dacă este compresie, delta este negativă sus și pozitivă jos.

| Bandă P_market | n | medie | mediană | min | max | abatere std | % model<piață | % model>piață | % egal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [0.00, 0.50) | 53 | 12.49 | 11.87 | 0.08 | 33.85 | 6.29 | 0.0% | 100.0% | 0.0% |
| [0.50, 0.65) | 99 | 2.70 | 3.32 | -8.54 | 17.96 | 5.19 | 30.3% | 69.7% | 0.0% |
| [0.65, 0.75) | 162 | -1.28 | 0.49 | -14.24 | 5.01 | 4.39 | 43.2% | 56.8% | 0.0% |
| [0.75, 0.85) | 102 | -5.47 | -3.77 | -17.98 | 3.53 | 5.63 | 83.3% | 16.7% | 0.0% |
| [0.85, 1.01) | 13 | -12.64 | -9.61 | -25.79 | -4.39 | 7.05 | 100.0% | 0.0% | 0.0% |

## Măsura compresiei

`top1` = cea mai mare dintre P(1), P(X), P(2); excesul peste 1/3 arată cât de
departe de uniform este distribuția. Raportul component/piață măsoară ce fracțiune
din semnalul de diferențiere al pieței păstrează fiecare etapă.

| Componentă | top1 mediu | exces peste 1/3 | raport vs piață |
| --- | --- | --- | --- |
| Piață de-vig (rândul 8) | 0.4865 | 0.1531 | 1.000 |
| Scoreline ÎNAINTE de shrinkage | 0.4792 | 0.1459 | 0.952 |
| Scoreline DUPĂ shrinkage (rândul 6) | 0.4439 | 0.1106 | 0.722 |
| Strength ÎNAINTE de shrinkage | 0.4480 | 0.1147 | 0.749 |
| Strength DUPĂ shrinkage (rândul 7) | 0.3849 | 0.0516 | 0.337 |
| Blend final (rândul 10) | 0.4283 | 0.0950 | 0.620 |

### Compresie separată: cu și fără shrinkage

| Segment | n | raport scoreline brut | raport scoreline final | raport blend final |
| --- | --- | --- | --- | --- |
| Fără shrinkage (VERIFIED) | 36 | 0.741 | 0.741 | 0.729 |
| Cu shrinkage | 393 | 0.975 | 0.720 | 0.609 |

## Cât din estimare vine din datele echipei și cât din priorul de ligă

Pe cele 393 selecții cu shrinkage activ:

- pondere prior, medie = **94.7%**, mediană = 94.8%, max = 97.6%
- pondere date proprii, medie = **5.3%**
- N_current (gazde), medie = 2.8
- N_prior (ligă), medie = 52.3

## Probabilitatea de egal: model vs piață

- P(X) model, medie = 0.2468
- P(X) piață, medie = 0.2526
- diferență medie = -0.59 pp

## Distanța dintre scoreline și strength

Diferența absolută maximă între cele două distribuții, per meci.
Două modele cu adevărat independente ar diverge substanțial.

- medie = 0.0674
- mediană = 0.0703
- max = 0.2199

