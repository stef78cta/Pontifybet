# Raport-martor: Molde vs Aalesund

- Ligă: Norway Eliteserien
- match_id: 8411811
- Kickoff UTC: 2026-09-19 16:00:00+00:00
- Eșantion: `Surse_Date!C9` = VERIFIED
- Prior: `Surse_Date!C10` = N/A
- Shrinkage aplicat: **NU**

## A. Date raw

| Mărime | Gazde | Oaspeți |
| --- | --- | --- |
| Meciuri jucate (H / A) | 10.0 | 9.0 |
| Meciuri jucate (overall) | 20.0 | 20.0 |
| Goluri marcate (H / A) | 23.0 | 9.0 |
| Goluri primite (H / A) | 11.0 | 19.0 |
| xG marcate (H / A) | 1.73 | 1.32 |
| xG primite (H / A) | 1.17 | 2.01 |
| Prior ligă (goluri/meci) | 1.8481 (acasă) | 1.3044 (deplasare) |
| N prior ligă | 160.0 | 160.0 |

## B/C. Parametri înainte și după shrinkage

| Parametru | N curent | N prior | Pondere curent | Pondere prior | Înainte | După | Δ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `scoreline.home_attack` | 10 | 160 | 100.0% | 0.0% | 2.0150 | 2.0150 | 0.0000 |
| `scoreline.away_defence` | 9 | 160 | 100.0% | 0.0% | 2.0606 | 2.0606 | 0.0000 |
| `scoreline.away_attack` | 9 | 160 | 100.0% | 0.0% | 1.1600 | 1.1600 | 0.0000 |
| `scoreline.home_defence` | 10 | 160 | 100.0% | 0.0% | 1.1350 | 1.1350 | 0.0000 |
| `strength.home_attack` | 20 | 320 | 100.0% | 0.0% | 1.9550 | 1.9550 | 0.0000 |
| `strength.away_defence` | 20 | 320 | 100.0% | 0.0% | 2.0925 | 2.0925 | 0.0000 |
| `strength.away_attack` | 20 | 320 | 100.0% | 0.0% | 1.6025 | 1.6025 | 0.0000 |
| `strength.home_defence` | 20 | 320 | 100.0% | 0.0% | 1.4350 | 1.4350 | 0.0000 |

### λ (goluri așteptate)

| Model | λ gazde înainte | λ gazde după | λ oaspeți înainte | λ oaspeți după |
| --- | --- | --- | --- | --- |
| Scoreline (H/A + xG) | 2.0378 | 2.0378 | 1.1475 | 1.1475 |
| Strength (overall) | 2.0238 | 2.0238 | 1.5188 | 1.5188 |

## D/E/F. Cele trei componente 1X2

| Componentă | P(1) | P(X) | P(2) | Sumă |
| --- | --- | --- | --- | --- |
| Scoreline ÎNAINTE de shrinkage | 57.92% | 21.17% | 20.91% | 100.00% |
| Scoreline (Model_1X2 rândul 6) | 57.92% | 21.17% | 20.91% | 100.00% |
| Strength ÎNAINTE de shrinkage | 49.48% | 21.47% | 29.06% | 100.00% |
| Strength (Model_1X2 rândul 7) | 49.48% | 21.47% | 29.06% | 100.00% |
| Piață de-vig (Model_1X2 rândul 8) | 71.17% | 14.60% | 14.23% | 100.00% |

## G. Blend final

Ponderi din `Parametri`: scoreline 0.5, strength 0.25, piață 0.25.

| Contribuție | P(1) | P(X) | P(2) |
| --- | --- | --- | --- |
| 0.5 × scoreline | 28.96% | 10.58% | 10.46% |
| 0.25 × strength | 12.37% | 5.37% | 7.26% |
| 0.25 × piață | 17.79% | 3.65% | 3.56% |
| **Sumă (rândul 9)** | 59.12% | 19.60% | 21.28% |
| **Final normalizat (rândul 10)** | 59.12% | 19.60% | 21.28% |

Verificare: P(1)+P(X)+P(2) = 1.000000000000

## H. Șansă Dublă

| Selecție | P_model | P_market | Δ (pp) | Pfail_model | Pfail_market | Pfail_DC | Haircut | P_adj | Risk Score | Nivel | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1X | 78.72% | 85.77% | -7.05 | 21.28% | 14.23% | 21.28% | 2.50% | 76.22% | 43 | 3 | MODERAT |
| X2 | 40.88% | 28.83% | +12.05 | 59.12% | 71.17% | 71.17% | 2.50% | 38.38% | 100 | 5 | NO BET |
| 12 | 80.40% | 85.40% | -5.00 | 19.60% | 14.60% | 19.60% | 2.50% | 77.90% | 52 | 3 | MODERAT |

Suma celor trei delte = 1.67e-14 pp (zero prin construcție).

