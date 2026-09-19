# Raport-martor: Sporting CP vs FC Arouca

> Bayern - Union nu figureaza in calendarul FootyStats pentru 2026-09-19..21. Pentru a nu fabrica date, martorul este echivalentul structural disponibil: favorit clar acasa (piata 78,67%) cu esantion mic (N=3) si shrinkage activ.

- Ligă: Portugal Liga NOS
- match_id: 8574233
- Kickoff UTC: 2026-09-19 19:30:00+00:00
- Eșantion: `Surse_Date!C9` = SMALL SAMPLE
- Prior: `Surse_Date!C10` = PRIOR / SHRINKAGE
- Shrinkage aplicat: **DA**

## A. Date raw

| Mărime | Gazde | Oaspeți |
| --- | --- | --- |
| Meciuri jucate (H / A) | 3.0 | 3.0 |
| Meciuri jucate (overall) | 6.0 | 6.0 |
| Goluri marcate (H / A) | 8.0 | 1.0 |
| Goluri primite (H / A) | 3.0 | 2.0 |
| xG marcate (H / A) | 1.59 | 0.71 |
| xG primite (H / A) | 0.92 | 2.28 |
| Prior ligă (goluri/meci) | 1.3700 (acasă) | 1.3983 (deplasare) |
| N prior ligă | 53.0 | 53.0 |

## B/C. Parametri înainte și după shrinkage

| Parametru | N curent | N prior | Pondere curent | Pondere prior | Înainte | După | Δ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `scoreline.home_attack` | 3 | 53 | 5.4% | 94.6% | 2.1283 | 1.4106 | -0.7177 |
| `scoreline.away_defence` | 3 | 53 | 5.4% | 94.6% | 1.4733 | 1.3755 | -0.0978 |
| `scoreline.away_attack` | 3 | 53 | 5.4% | 94.6% | 0.5217 | 1.3514 | 0.8297 |
| `scoreline.home_defence` | 3 | 53 | 5.4% | 94.6% | 0.9600 | 1.3749 | 0.4149 |
| `strength.home_attack` | 6 | 106 | 5.4% | 94.6% | 2.0975 | 1.4224 | -0.6751 |
| `strength.away_defence` | 6 | 106 | 5.4% | 94.6% | 1.2617 | 1.3776 | 0.1159 |
| `strength.away_attack` | 6 | 106 | 5.4% | 94.6% | 1.2317 | 1.3760 | 0.1443 |
| `strength.home_defence` | 6 | 106 | 5.4% | 94.6% | 0.9225 | 1.3594 | 0.4369 |

### λ (goluri așteptate)

| Model | λ gazde înainte | λ gazde după | λ oaspeți înainte | λ oaspeți după |
| --- | --- | --- | --- | --- |
| Scoreline (H/A + xG) | 1.8008 | 1.3931 | 0.7408 | 1.3631 |
| Strength (overall) | 1.6796 | 1.4000 | 1.0771 | 1.3677 |

## D/E/F. Cele trei componente 1X2

| Componentă | P(1) | P(X) | P(2) | Sumă |
| --- | --- | --- | --- | --- |
| Scoreline ÎNAINTE de shrinkage | 62.68% | 22.45% | 14.87% | 100.00% |
| Scoreline (Model_1X2 rândul 6) | 37.93% | 25.51% | 36.56% | 100.00% |
| Strength ÎNAINTE de shrinkage | 51.45% | 24.21% | 24.34% | 100.00% |
| Strength (Model_1X2 rândul 7) | 38.01% | 25.45% | 36.54% | 100.00% |
| Piață de-vig (Model_1X2 rândul 8) | 78.67% | 13.33% | 8.00% | 100.00% |

## G. Blend final

Ponderi din `Parametri`: scoreline 0.5, strength 0.25, piață 0.25.

| Contribuție | P(1) | P(X) | P(2) |
| --- | --- | --- | --- |
| 0.5 × scoreline | 18.97% | 12.75% | 18.28% |
| 0.25 × strength | 9.50% | 6.36% | 9.14% |
| 0.25 × piață | 19.67% | 3.33% | 2.00% |
| **Sumă (rândul 9)** | 48.14% | 22.45% | 29.42% |
| **Final normalizat (rândul 10)** | 48.14% | 22.45% | 29.42% |

Verificare: P(1)+P(X)+P(2) = 1.000000000000

## H. Șansă Dublă

| Selecție | P_model | P_market | Δ (pp) | Pfail_model | Pfail_market | Pfail_DC | Haircut | P_adj | Risk Score | Nivel | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1X | 70.58% | 92.00% | -21.42 | 29.42% | 8.00% | 29.42% | 4.50% | 66.08% | 62 | 4 | RIDICAT |
| X2 | 51.86% | 21.33% | +30.54 | 48.14% | 78.67% | 78.67% | 4.50% | 47.36% | 100 | 5 | NO BET |
| 12 | 77.55% | 86.67% | -9.12 | 22.45% | 13.33% | 22.45% | 4.50% | 73.05% | 100 | 5 | NO BET |

Suma celor trei delte = -2.22e-14 pp (zero prin construcție).

