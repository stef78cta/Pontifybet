# Risk coherence report – Șansă Dublă V2

Raport **exclusiv diagnostic**. Formula V2 rămâne neschimbată; nimic de aici
nu modifică un verdict. Scopul este să arate ce frontieră de Pfail impune
efectiv Risk Score-ul, comparat cu pragurile probabilistice documentate.

## Coeficienți citiți din workbook

| Parametru | Celulă | Valoare |
| --- | --- | --- |
| min_p_strong | `Parametri!B4` | 0.82 |
| min_p_prudent | `Parametri!B5` | 0.76 |
| max_draw_strong | `Parametri!B8` | 0.2 |
| haircut_a | `Parametri!B13` | 0.01 |
| haircut_b | `Parametri!B14` | 0.025 |
| haircut_c | `Parametri!B15` | 0.05 |
| early_extra | `Parametri!B25` | 0.02 |
| risk_fail_1x | `Parametri!B35` | 180.0 |
| risk_hc_1x | `Parametri!B36` | 200.0 |
| risk_fail_12 | `Parametri!B37` | 200.0 |
| risk_hc_12 | `Parametri!B38` | 120.0 |
| level1_max | `Parametri!B39` | 20.0 |
| level2_max | `Parametri!B40` | 40.0 |

## 1X / X2 – frontiera Pfail_DC

Scor = ROUND(`B35`·Pfail_DC + `B36`·Haircut_Total + surcharges, 0), fără surcharges.

| Regim haircut | Haircut_Total | Pfail_DC max pentru Nivel 1 | Pfail_DC max pentru Nivel 2 | P_model implicit la Nivel 1 | P_adj implicit la Nivel 1 |
| --- | --- | --- | --- | --- | --- |
| A | 0.010 | 0.1028 (10.28 pp) | 0.2139 (21.39 pp) | 0.8972 | 0.8872 |
| A + early season | 0.030 | 0.0806 (8.06 pp) | 0.1917 (19.17 pp) | 0.9194 | 0.8894 |
| B | 0.025 | 0.0861 (8.61 pp) | 0.1972 (19.72 pp) | 0.9139 | 0.8889 |
| B + early season | 0.045 | 0.0639 (6.39 pp) | 0.1750 (17.50 pp) | 0.9361 | 0.8911 |
| C | 0.050 | 0.0583 (5.83 pp) | 0.1694 (16.94 pp) | 0.9417 | 0.8917 |
| C + early season | 0.070 | 0.0361 (3.61 pp) | 0.1472 (14.72 pp) | 0.9639 | 0.8939 |

### Consecința matematică

`Min_P_DC_Strong` = 0.82 nu este niciodată constrângerea activă pentru 1X/X2.
Verdictul DEFENSIV cere `M=1` (Nivel 1), iar Nivel 1 impune deja un P_adj mult peste prag:

- Regim A: Nivel 1 forțează P_adj >= 0.8872, adică 6.72 pp peste pragul documentat de 0.82.
- Regim A + early season: Nivel 1 forțează P_adj >= 0.8894, adică 6.94 pp peste pragul documentat de 0.82.
- Regim B: Nivel 1 forțează P_adj >= 0.8889, adică 6.89 pp peste pragul documentat de 0.82.
- Regim B + early season: Nivel 1 forțează P_adj >= 0.8911, adică 7.11 pp peste pragul documentat de 0.82.
- Regim C: Nivel 1 forțează P_adj >= 0.8917, adică 7.17 pp peste pragul documentat de 0.82.
- Regim C + early season: Nivel 1 forțează P_adj >= 0.8939, adică 7.39 pp peste pragul documentat de 0.82.

## 12 – frontiera Pfail_DC (egal)

Scor = ROUND(`B37`·Pfail_DC + `B38`·Haircut_Total + surcharge Draw Gate, 0).

| Regim haircut | Haircut_Total | Pdraw max pentru Nivel 1 | Pdraw max pentru Nivel 2 |
| --- | --- | --- | --- |
| A | 0.010 | 0.0965 (9.65 pp) | 0.1965 (19.65 pp) |
| A + early season | 0.030 | 0.0845 (8.45 pp) | 0.1845 (18.45 pp) |
| B | 0.025 | 0.0875 (8.75 pp) | 0.1875 (18.75 pp) |
| B + early season | 0.045 | 0.0755 (7.55 pp) | 0.1755 (17.55 pp) |
| C | 0.050 | 0.0725 (7.25 pp) | 0.1725 (17.25 pp) |
| C + early season | 0.070 | 0.0605 (6.05 pp) | 0.1605 (16.05 pp) |

Draw Gate declară PASS până la 0.2 (20 pp), dar Nivel 1 cere Pdraw <= 0.0965 (9.65 pp) chiar în cel mai favorabil regim de haircut.
Gate-ul este deci cu un factor de ~2.1x mai permisiv decât scorul care decide nivelul.

## Unde intră haircut-ul (numărătoare)

| Selecție | Haircut în P_adj | Haircut în gate | Haircut în Risk Score |
| --- | --- | --- | --- |
| 1X / X2 | da (`F = B - E`) | nu | da (`B36`·E) |
| 12 | da (`F = B - E`) | da (`P0_Gates_v2!I6 = C10 + E`) | da (`B38`·E) |

Pentru 12 haircut-ul este contabilizat de trei ori pe căi diferite. Nu este o eroare de implementare — Excel V2 face exact asta — dar este o observație metodologică documentată în `V3_CHALLENGER_PROPOSAL.md`.

