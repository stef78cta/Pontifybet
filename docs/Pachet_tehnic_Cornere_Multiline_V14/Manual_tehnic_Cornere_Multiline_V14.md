# Manual tehnic de implementare PontifyBet Cornere Multiline V14

Specificație de reproducere a workbook-ului, cu formule originale, dependențe, contracte de date, pseudocod și rezultate de test pentru toate cele 14 linii.

Data verificării: 19 septembrie 2026. Sursa metodologică analizată este fișierul `6_model_analiza_cornere_multiline_optimizat_V14(2).xlsx`. Copia fără sufix din sursele proiectului are exact aceiași octeți. Manualul documentează comportamentul existent și nu modifică formule, ponderi, praguri sau fișierele aplicației.

Concluzia tehnică: V14 pornește din istoricul meciurilor cu cornere native, construiește un singur motor comun pentru fiecare meci, apoi calculează șase selecții Over și opt Under. Media estimată, dispersia și Confidence Base sunt comune. Probabilitățile, frecvențele empirice de eșec, tail gates, Confidence Final, Risk Score, nivelul final și eligibilitatea sunt evaluate separat pe linie. Alegerea recomandării se face după evaluarea tuturor liniilor.

Cele trei exemple din fișier sunt REPLAY. Au fost recalculate în LibreOffice și într-un harness Python independent, pornind de la istoricul brut. Aceste verificări nu constituie backtest predictiv independent și nu certifică toate ramurile LIVE, prior sau promovare OOS. Limitele concrete sunt în secțiunea 5.

## Baza verificată în GitHub

Repository: `stef78cta/Pontifybet`, branch `main`, commit `bda2a1c632d916f1dfaf4d94eba22d085bb6a2f4`.

- SHA-256 al fișierului analizat: `c2ea1af7f97d82b189a5e45e097fe66aca8d11449d2aa62ee57896ae22fed268`.
- Git blob SHA-1 calculat din octeții fișierului: `c8188566b122d171e170223206021d5dd0784c50`. Este identic cu blob-urile din `templates/6_model_analiza_cornere_multiline_optimizat_V14.xlsx` și `modele_analize/6_model_analiza_cornere_multiline_optimizat_V14.xlsx` din commit-ul verificat.
- `config/model_registry.yaml` declară Cornere Multi-Line V14, `Input_Meci`, rândul 6, coloanele de scriere A:AG.
- `src/adapters/corners.py`, clasa `CornersAdapter`, metodele `write_matches` și `_row_values`, completează A:I și M. Cele 12 medii native și două eșantioane sunt serializate în `Notes`, coloana M. Adaptorul inspectat nu scrie `Istoric_Nativ` sau `Surse_Import`.
- `Input_Meci!M` nu este parsată de formulele modelului. O listă de medii în Notes nu reproduce istoricul necesar pentru varianță, deduplicare și frecvențele empirice.
- `src/pipeline.py`, `_build_rows_and_snapshot`, execută explicit motoarele Over 0.5 și Șansă Dublă. În funcția inspectată nu există ramură de calcul numeric pentru cele 14 linii Cornere. Exportul folosește `CornersAdapter().write_matches(...)`.
- `src/recalc/libreoffice.py` este un stub dezactivat; `recalculate` ridică o eroare dacă serviciul nu este activat. Recalcularea efectuată pentru acest manual este o verificare locală separată, nu o funcție activă a aplicației.
- `src/excel/integrity.py` verifică formulele și whitelist-ul. Limita implicită de scanare este 200 rânduri și 120 coloane: amprenta implicită nu cuprinde integral foile cu 405, 1205 sau 1405 rânduri. Inventarul din acest pachet acoperă toate cele 85.647 formule.

Ce este confirmat: versiunea template-ului și schema de export. Ce este incomplet în fluxul inspectat: alimentarea istoricului nativ și producerea rezultatelor Cornere în faza ANALYSIS. Ce nu trebuie presupus funcțional: faptul că Notes ar alimenta motorul sau că exportul declanșează automat recalcularea. Nu am rulat aplicația sau testele repository-ului; nu declar un audit exhaustiv al tuturor componentelor sale.

Pentru integrare, se păstrează metodologia de mai jos și se identifică mecanismul existent de snapshot/export. Harness-ul de verificare din pachet nu trebuie transformat implicit într-un al doilea motor de producție. Nu se adaugă o sursă sportivă nouă și nu se inventează mapping FootyStats. Football-Data este proveniența declarată a exemplului Excel, nu o decizie de modificare a sursei aplicației.

## 1 Arhitectura și structura foilor

### 1.1 Inventarul complet

| Foaie | Dimensiune utilizată | Tabel și interval | Formule | Rol |
| --- | --- | --- | --- | --- |
| Dashboard | 125 × 16 | fără tabel structurat | 1586 | Ieșire pe meci, selecția unică și Top 10 LIVE; nu modifică probabilitățile. |
| Config_v6 | 61 × 4 | fără tabel structurat | 3 | Parametri globali V14; numele istoric v6 al foii se păstrează. |
| Analiza_Linii | 1405 × 40 | LinesTable A5:AN1405 | 50400 | 14 selecții per meci: probabilități, failure, risc, gates, verdict și ranking. |
| Motor_Meciuri | 105 × 72 | MotorTable A5:BT105 | 7200 | Motor comun: Core efectiv, dispersie, lambda, Confidence Base și release. |
| Core_Nativ | 1205 × 21 | CoreTable A5:U1205 | 19200 | Șase ferestre CURRENT și șase PRIOR per meci; medii, N, sourcing și trasabilitate. |
| Distributie | 105 × 42 | DistributionTable A5:AP105 | 4200 | PMF_0…18 și CDF_0…18 pe fiecare meci, Poisson sau NB. |
| Input_Meci | 105 × 33 | MatchesTable A5:AG105 | 0 | Inputul meciului, cutoff, deciziile de sourcing, prior și context. |
| Istoric_Nativ | 405 × 19 | NativeTable A5:S405 | 2400 | Evenimentele brute și validare/deduplicare/totaluri. |
| Surse_Import | 13 × 13 | SourceTable A5:M13 | 8 | Jurnalul surselor și cheia League–Season. |
| Calibrare_Linii | 19 × 22 | LineConfigTable A5:V19 | 140 | Configurația a 14 linii și agregatele de promovare OOS. |
| OOS_Predictii | 255 × 21 | OOSTable A5:U255 | 500 | Snapshot-uri literale pre-match și rezultate ulterioare; gol la livrare. |
| Verificari | 15 × 4 | ChecksTable A5:D15 | 10 | Controale independente de integritate a rezultatelor. |
| Documentatie | 32 × 2 | DocumentationTable A5:B32 | 0 | Reguli descriptive; nu participă la calcul. |

Capacitățile fizice sunt: 100 meciuri, 1.400 selecții, 1.200 rânduri Core, 400 evenimente native, 8 surse și 250 înregistrări OOS. Acestea sunt dimensiunile intervalelor existente. Schimbarea unei celule de configurare nu extinde tabelele, formulele sau referințele fixe.

În fișier există 102.820 celule ne-goale și 85.647 formule. Nu există nume definite la nivel de workbook. Foile folosesc atât referințe A1 fixe, cât și referințe structurate de tabel. Unele tabele includ numeroase rânduri fără meci.

### 1.2 Ordinea logică de calcul

1. Citește constantele, schema și metadatele; validează `Config_v6!B40` și `Calibrare_Linii!U6:U19`.
2. Calculează `SourceTable[Source_Key]` și `NativeTable[Source_Row]`.
3. Calculează cheile canonice pentru toate rândurile istorice. Apoi clasifică fiecare rând, detectând conflictele față de întregul istoric și dublurile în ordinea rândurilor.
4. Construiește cele șase ferestre curente și șase ferestre prior pentru fiecare meci; derivează N, medii și stările surselor.
5. Derivează metadatele, valorile efective și sezonul dispersiei. Calculează N, media și varianța istorice; verifică release și G0.
6. Numai pentru G0 PASS, calculează D, distribuția, ajustările, lambda, mu, Confidence Base și Calibration Strength.
7. Recalculează registrul OOS și agregatele de validare a liniilor. OOS folosește snapshot-uri literale înghețate, nu probabilități curente legate prin formule de meciurile reevaluate.
8. Construiește PMF/CDF pentru meci; evaluează probabilitățile și failure gates pentru fiecare linie.
9. Calculează tail, Confidence Final și candidate confidence. Calculează P_FINAL înainte de a decide Defensive Candidate/Gate și verdictul, chiar dacă P_FINAL se află fizic în coloana AB.
10. Calculează eligibilitatea, rangul în meci, selecția unică, rangul LIVE și Top 10. `Analiza_Linii!AG` citește rangul din Dashboard; nu reprezintă un nou motor de ranking.
11. Rulează controalele independente din `Verificari`. Ele nu alimentează motorul.

Ordinea foilor în fișier și ordinea alfabetică a coloanelor nu constituie ordine executabilă. De exemplu `Motor_Meciuri!AR:AT` depind de `BL`, iar `Analiza_Linii!X:Y` depind de `AB` și `AN`.

### 1.3 Indexarea exactă a unui meci

Pentru slotul s, numerotat de la 1 la 100:

```text
input_row = motor_row = distribution_row = 5 + s
core_start = 6 + 12 * (s - 1)
line_start = 6 + 14 * (s - 1)
dashboard_row = 25 + s
line_config_row = 6 + line_index_zero_based
```

Cele 12 rânduri Core ale unui slot sunt:

| Offset | Side | Role | Split | Period | Date produse |
|---|---|---|---|---|---|
| 0 | H | CURRENT | ANY | SEASON | for și against gazde sezon |
| 1 | H | CURRENT | HOME | SEASON | for și against gazde acasă |
| 2 | H | CURRENT | ANY | RECENT | for și against gazde recent |
| 3 | A | CURRENT | ANY | SEASON | for și against oaspeți sezon |
| 4 | A | CURRENT | AWAY | SEASON | for și against oaspeți deplasare |
| 5 | A | CURRENT | ANY | RECENT | for și against oaspeți recent |
| 6–11 | H/H/H/A/A/A | PRIOR | aceleași splituri | aceleași perioade | aceleași statistici în sezonul prior |

Core 12 înseamnă două medii × șase ferestre curente, nu 12 meciuri și nici 12 ferestre independente. Rândurile prior sunt suport separat.

### 1.4 Schema exactă a coloanelor

Tabelele următoare conțin toate coloanele cu antet. `Config_v6` este o configurație pe celule, documentată separat. Dashboard are două structuri distincte, la rândurile 10 și 25; coloana J din blocul inferior nu are antet sau rol calculat.

Tipurile sunt contracte semantice deduse din formule și valorile curente. Excel nu declară tipuri stricte. O coloană numerică poate conține rezultatul `""`; în cod trebuie modelată ca valoare opțională. Probabilitățile sunt Float 0–1; scorurile și Confidence sunt pe scara 0–100. Tipul afișat pentru Confidence reflectă configurația curentă; dacă o penalizare configurabilă ar deveni fracționară, nu se trunchiază rezultatul la întreg.

#### Dashboard

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Rang | A11:A20 | Număr întreg | Rezultat formulă |
| B | Meci | B11:B20 | Text | Rezultat formulă |
| C | Linie | C11:C20 | Text | Rezultat formulă |
| D | P finală | D11:D20 | Float probabilitate 0–1 | Rezultat formulă |
| E | Risk Level | E11:E20 | Număr întreg | Rezultat formulă |
| F | Verdict | F11:F20 | Text | Rezultat formulă |
| G | Confidence | G11:G20 | Număr întreg | Rezultat formulă |
| H | Motiv | H11:H20 | Text | Rezultat formulă |
| A | Match_ID | A26:A125 | Text | Rezultat formulă |
| B | Meci | B26:B125 | Text | Rezultat formulă |
| C | Mod | C26:C125 | Text | Rezultat formulă |
| D | Release | D26:D125 | Text | Rezultat formulă |
| E | G0 | E26:E125 | Text | Rezultat formulă |
| F | Linie selectată | F26:F125 | Text | Rezultat formulă |
| G | Verdict | G26:G125 | Text | Rezultat formulă |
| H | P finală | H26:H125 | Float probabilitate 0–1 | Rezultat formulă |
| I | Motiv | I26:I125 | Text | Rezultat formulă |
| K | Index linie | K26:K125 | Număr întreg | Rezultat formulă |
| L | Risk Level | L26:L125 | Număr întreg | Rezultat formulă |
| M | Confidence | M26:M125 | Număr întreg | Rezultat formulă |
| N | Risk Score | N26:N125 | Float | Rezultat formulă |
| O | LIVE eligibil | O26:O125 | Număr întreg | Rezultat formulă |
| P | Rank LIVE | P26:P125 | Număr întreg | Rezultat formulă |

#### Analiza_Linii

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Slot | A6:A1405 | Număr întreg | Input sau constantă literală |
| B | Match_ID | B6:B1405 | Text | Rezultat formulă |
| C | League | C6:C1405 | Text | Rezultat formulă |
| D | Match | D6:D1405 | Text | Rezultat formulă |
| E | Mode | E6:E1405 | Text | Rezultat formulă |
| F | Line | F6:F1405 | Text | Input sau constantă literală |
| G | Type | G6:G1405 | Text | Input sau constantă literală |
| H | k | H6:H1405 | Număr întreg | Input sau constantă literală |
| I | Release | I6:I1405 | Text | Rezultat formulă |
| J | G0 | J6:J1405 | Text | Rezultat formulă |
| K | Mu | K6:K1405 | Float | Rezultat formulă |
| L | D | L6:L1405 | Float | Rezultat formulă |
| M | P_Raw | M6:M1405 | Float probabilitate 0–1 | Rezultat formulă |
| N | P_Calibrated | N6:N1405 | Float probabilitate 0–1 | Rezultat formulă |
| O | Failure_Model | O6:O1405 | Float probabilitate 0–1 | Rezultat formulă |
| P | Empirical_HA | P6:P1405 | Float probabilitate 0–1 | Rezultat formulă |
| Q | Empirical_L10 | Q6:Q1405 | Float probabilitate 0–1 | Rezultat formulă |
| R | Empirical_L20 | R6:R1405 | Float probabilitate 0–1 | Rezultat formulă |
| S | Failure_Gate | S6:S1405 | Float probabilitate 0–1 | Rezultat formulă |
| T | Risk_Score | T6:T1405 | Float | Rezultat formulă |
| U | Risk_Level_Raw | U6:U1405 | Număr întreg | Rezultat formulă |
| V | Confidence_Final | V6:V1405 | Număr întreg | Rezultat formulă |
| W | Tail_Gate | W6:W1405 | Text | Rezultat formulă |
| X | Defensive_Candidate | X6:X1405 | Text | Rezultat formulă |
| Y | Defensive_Gate | Y6:Y1405 | Text | Rezultat formulă |
| Z | Risk_Level_FINAL | Z6:Z1405 | Număr întreg | Rezultat formulă |
| AA | Verdict_FINAL | AA6:AA1405 | Text | Rezultat formulă |
| AB | P_FINAL | AB6:AB1405 | Float probabilitate 0–1 | Rezultat formulă |
| AC | Rank_In_Match | AC6:AC1405 | Număr întreg | Rezultat formulă |
| AD | Eligible | AD6:AD1405 | Număr întreg | Rezultat formulă |
| AE | Builder | AE6:AE1405 | Text | Rezultat formulă |
| AF | Live_Eligible_Best | AF6:AF1405 | Număr întreg | Rezultat formulă |
| AG | Rank_LIVE | AG6:AG1405 | Număr întreg | Rezultat formulă |
| AH | Reason | AH6:AH1405 | Text | Rezultat formulă |
| AI | Model_Signature | AI6:AI1405 | Text | Rezultat formulă |
| AJ | OOS_Status | AJ6:AJ1405 | Text | Rezultat formulă |
| AK | N_HA_Empirical | AK6:AK1405 | Număr întreg | Rezultat formulă |
| AL | N_L10_Empirical | AL6:AL1405 | Număr întreg | Rezultat formulă |
| AM | N_L20_Empirical | AM6:AM1405 | Număr întreg | Rezultat formulă |
| AN | Candidate_Confidence | AN6:AN1405 | Număr întreg | Rezultat formulă |

#### Motor_Meciuri

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Match_ID | A6:A105 | Text | Rezultat formulă |
| B | League | B6:B105 | Text | Rezultat formulă |
| C | Season | C6:C105 | Text | Rezultat formulă |
| D | Match | D6:D105 | Text | Rezultat formulă |
| E | Mode | E6:E105 | Text | Rezultat formulă |
| F | Kickoff_UTC | F6:F105 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Rezultat formulă |
| G | Cutoff_UTC | G6:G105 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Rezultat formulă |
| H | Release | H6:H105 | Text | Rezultat formulă |
| I | G0 | I6:I105 | Text | Rezultat formulă |
| J | Reason | J6:J105 | Text | Rezultat formulă |
| K | Core_Native_Count | K6:K105 | Număr întreg | Rezultat formulă |
| L | Core_Effective_Count | L6:L105 | Număr întreg | Rezultat formulă |
| M | Prior_Active | M6:M105 | Text | Rezultat formulă |
| N | N_H_Season | N6:N105 | Număr întreg | Rezultat formulă |
| O | N_H_HA | O6:O105 | Număr întreg | Rezultat formulă |
| P | N_H_Recent | P6:P105 | Număr întreg | Rezultat formulă |
| Q | N_A_Season | Q6:Q105 | Număr întreg | Rezultat formulă |
| R | N_A_HA | R6:R105 | Număr întreg | Rezultat formulă |
| S | N_A_Recent | S6:S105 | Număr întreg | Rezultat formulă |
| T | Raw_H_S_For | T6:T105 | Float | Rezultat formulă |
| U | Raw_H_S_Against | U6:U105 | Float | Rezultat formulă |
| V | Raw_H_HA_For | V6:V105 | Float | Rezultat formulă |
| W | Raw_H_HA_Against | W6:W105 | Float | Rezultat formulă |
| X | Raw_H_R_For | X6:X105 | Float | Rezultat formulă |
| Y | Raw_H_R_Against | Y6:Y105 | Float | Rezultat formulă |
| Z | Raw_A_S_For | Z6:Z105 | Float | Rezultat formulă |
| AA | Raw_A_S_Against | AA6:AA105 | Float | Rezultat formulă |
| AB | Raw_A_HA_For | AB6:AB105 | Float | Rezultat formulă |
| AC | Raw_A_HA_Against | AC6:AC105 | Float | Rezultat formulă |
| AD | Raw_A_R_For | AD6:AD105 | Float | Rezultat formulă |
| AE | Raw_A_R_Against | AE6:AE105 | Float | Rezultat formulă |
| AF | Effective_H_S_For | AF6:AF105 | Float | Rezultat formulă |
| AG | Effective_H_S_Against | AG6:AG105 | Float | Rezultat formulă |
| AH | Effective_H_HA_For | AH6:AH105 | Float | Rezultat formulă |
| AI | Effective_H_HA_Against | AI6:AI105 | Float | Rezultat formulă |
| AJ | Effective_H_R_For | AJ6:AJ105 | Float | Rezultat formulă |
| AK | Effective_H_R_Against | AK6:AK105 | Float | Rezultat formulă |
| AL | Effective_A_S_For | AL6:AL105 | Float | Rezultat formulă |
| AM | Effective_A_S_Against | AM6:AM105 | Float | Rezultat formulă |
| AN | Effective_A_HA_For | AN6:AN105 | Float | Rezultat formulă |
| AO | Effective_A_HA_Against | AO6:AO105 | Float | Rezultat formulă |
| AP | Effective_A_R_For | AP6:AP105 | Float | Rezultat formulă |
| AQ | Effective_A_R_Against | AQ6:AQ105 | Float | Rezultat formulă |
| AR | N_Dispersion | AR6:AR105 | Număr întreg | Rezultat formulă |
| AS | Mean_Total_History | AS6:AS105 | Float | Rezultat formulă |
| AT | Variance_Total_History | AT6:AT105 | Float | Rezultat formulă |
| AU | D | AU6:AU105 | Float | Rezultat formulă |
| AV | Distribution | AV6:AV105 | Text | Rezultat formulă |
| AW | NB_Size | AW6:AW105 | Float | Rezultat formulă |
| AX | Soft_H | AX6:AX105 | Float | Rezultat formulă |
| AY | Soft_A | AY6:AY105 | Float | Rezultat formulă |
| AZ | Context_H | AZ6:AZ105 | Float | Rezultat formulă |
| BA | Context_A | BA6:BA105 | Float | Rezultat formulă |
| BB | Lambda_H | BB6:BB105 | Float | Rezultat formulă |
| BC | Lambda_A | BC6:BC105 | Float | Rezultat formulă |
| BD | Mu | BD6:BD105 | Float | Rezultat formulă |
| BE | Soft_Missing | BE6:BE105 | Număr întreg | Rezultat formulă |
| BF | Confidence_Base | BF6:BF105 | Număr întreg | Rezultat formulă |
| BG | Calibration_Strength | BG6:BG105 | Float | Rezultat formulă |
| BH | Sensitivity | BH6:BH105 | Float | Rezultat formulă |
| BI | Context_Valid | BI6:BI105 | Text | Rezultat formulă |
| BJ | Source_Problems | BJ6:BJ105 | Număr întreg | Rezultat formulă |
| BK | Config_Valid | BK6:BK105 | Text | Rezultat formulă |
| BL | Dispersion_Season | BL6:BL105 | Text | Rezultat formulă |
| BM | H_L10_From | BM6:BM105 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Rezultat formulă |
| BN | A_L10_From | BN6:BN105 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Rezultat formulă |
| BO | H_L20_From | BO6:BO105 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Rezultat formulă |
| BP | A_L20_From | BP6:BP105 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Rezultat formulă |
| BQ | Metadata_Valid | BQ6:BQ105 | Text | Rezultat formulă |
| BR | N_Emp_HA | BR6:BR105 | Număr întreg | Rezultat formulă |
| BS | N_Emp_L10 | BS6:BS105 | Număr întreg | Rezultat formulă |
| BT | N_Emp_L20 | BT6:BT105 | Număr întreg | Rezultat formulă |

#### Core_Nativ

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Slot | A6:A1205 | Număr întreg | Input sau constantă literală |
| B | Match_ID | B6:B1205 | Text | Rezultat formulă |
| C | Side | C6:C1205 | Text | Input sau constantă literală |
| D | Role | D6:D1205 | Text | Input sau constantă literală |
| E | League | E6:E1205 | Text | Rezultat formulă |
| F | Season | F6:F1205 | Text | Rezultat formulă |
| G | Team | G6:G1205 | Text | Rezultat formulă |
| H | Split | H6:H1205 | Text | Input sau constantă literală |
| I | Period | I6:I1205 | Text | Input sau constantă literală |
| J | Before_Date | J6:J1205 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Rezultat formulă |
| K | N_scope | K6:K1205 | Număr întreg | Rezultat formulă |
| L | Recent_From | L6:L1205 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Rezultat formulă |
| M | N | M6:M1205 | Număr întreg | Rezultat formulă |
| N | Corners_For | N6:N1205 | Float | Rezultat formulă |
| O | Corners_Against | O6:O1205 | Float | Rezultat formulă |
| P | Target_N | P6:P1205 | Număr întreg | Rezultat formulă |
| Q | Source_Row | Q6:Q1205 | Număr întreg | Rezultat formulă |
| R | Source_State | R6:R1205 | Text | Rezultat formulă |
| S | Problem_Rows | S6:S1205 | Număr întreg | Rezultat formulă |
| T | Data_Status | T6:T1205 | Text | Rezultat formulă |
| U | Trace | U6:U1205 | Text | Rezultat formulă |

#### Distributie

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Match_ID | A6:A105 | Text | Rezultat formulă |
| B | Mu | B6:B105 | Float | Rezultat formulă |
| C | D | C6:C105 | Float | Rezultat formulă |
| D | Size | D6:D105 | Float | Rezultat formulă |
| E | PMF_0 | E6:E105 | Float probabilitate 0–1 | Rezultat formulă |
| F | PMF_1 | F6:F105 | Float probabilitate 0–1 | Rezultat formulă |
| G | PMF_2 | G6:G105 | Float probabilitate 0–1 | Rezultat formulă |
| H | PMF_3 | H6:H105 | Float probabilitate 0–1 | Rezultat formulă |
| I | PMF_4 | I6:I105 | Float probabilitate 0–1 | Rezultat formulă |
| J | PMF_5 | J6:J105 | Float probabilitate 0–1 | Rezultat formulă |
| K | PMF_6 | K6:K105 | Float probabilitate 0–1 | Rezultat formulă |
| L | PMF_7 | L6:L105 | Float probabilitate 0–1 | Rezultat formulă |
| M | PMF_8 | M6:M105 | Float probabilitate 0–1 | Rezultat formulă |
| N | PMF_9 | N6:N105 | Float probabilitate 0–1 | Rezultat formulă |
| O | PMF_10 | O6:O105 | Float probabilitate 0–1 | Rezultat formulă |
| P | PMF_11 | P6:P105 | Float probabilitate 0–1 | Rezultat formulă |
| Q | PMF_12 | Q6:Q105 | Float probabilitate 0–1 | Rezultat formulă |
| R | PMF_13 | R6:R105 | Float probabilitate 0–1 | Rezultat formulă |
| S | PMF_14 | S6:S105 | Float probabilitate 0–1 | Rezultat formulă |
| T | PMF_15 | T6:T105 | Float probabilitate 0–1 | Rezultat formulă |
| U | PMF_16 | U6:U105 | Float probabilitate 0–1 | Rezultat formulă |
| V | PMF_17 | V6:V105 | Float probabilitate 0–1 | Rezultat formulă |
| W | PMF_18 | W6:W105 | Float probabilitate 0–1 | Rezultat formulă |
| X | CDF_0 | X6:X105 | Float probabilitate 0–1 | Rezultat formulă |
| Y | CDF_1 | Y6:Y105 | Float probabilitate 0–1 | Rezultat formulă |
| Z | CDF_2 | Z6:Z105 | Float probabilitate 0–1 | Rezultat formulă |
| AA | CDF_3 | AA6:AA105 | Float probabilitate 0–1 | Rezultat formulă |
| AB | CDF_4 | AB6:AB105 | Float probabilitate 0–1 | Rezultat formulă |
| AC | CDF_5 | AC6:AC105 | Float probabilitate 0–1 | Rezultat formulă |
| AD | CDF_6 | AD6:AD105 | Float probabilitate 0–1 | Rezultat formulă |
| AE | CDF_7 | AE6:AE105 | Float probabilitate 0–1 | Rezultat formulă |
| AF | CDF_8 | AF6:AF105 | Float probabilitate 0–1 | Rezultat formulă |
| AG | CDF_9 | AG6:AG105 | Float probabilitate 0–1 | Rezultat formulă |
| AH | CDF_10 | AH6:AH105 | Float probabilitate 0–1 | Rezultat formulă |
| AI | CDF_11 | AI6:AI105 | Float probabilitate 0–1 | Rezultat formulă |
| AJ | CDF_12 | AJ6:AJ105 | Float probabilitate 0–1 | Rezultat formulă |
| AK | CDF_13 | AK6:AK105 | Float probabilitate 0–1 | Rezultat formulă |
| AL | CDF_14 | AL6:AL105 | Float probabilitate 0–1 | Rezultat formulă |
| AM | CDF_15 | AM6:AM105 | Float probabilitate 0–1 | Rezultat formulă |
| AN | CDF_16 | AN6:AN105 | Float probabilitate 0–1 | Rezultat formulă |
| AO | CDF_17 | AO6:AO105 | Float probabilitate 0–1 | Rezultat formulă |
| AP | CDF_18 | AP6:AP105 | Float probabilitate 0–1 | Rezultat formulă |

#### Input_Meci

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Match_ID | A6:A105 | Text | Input sau constantă literală |
| B | League | B6:B105 | Text | Input sau constantă literală |
| C | Season | C6:C105 | Text | Input sau constantă literală |
| D | Home | D6:D105 | Text | Input sau constantă literală |
| E | Away | E6:E105 | Text | Input sau constantă literală |
| F | Kickoff_UTC | F6:F105 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| G | Cutoff_UTC | G6:G105 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| H | Mode | H6:H105 | Text | Input sau constantă literală |
| I | Sourcing_Decision | I6:I105 | Text | Input sau constantă literală |
| J | Evidence_or_Attempts | J6:J105 | Text | Input sau constantă literală |
| K | Prior_Season | K6:K105 | Text | Input sau constantă literală |
| L | Prior_Allowed | L6:L105 | Text | Input sau constantă literală |
| M | Notes | M6:M105 | Text | Input sau constantă literală |
| N | Shots_H | N6:N105 | Float | Input sau constantă literală |
| O | Shots_A | O6:O105 | Float | Input sau constantă literală |
| P | Blocked_H | P6:P105 | Float | Input sau constantă literală |
| Q | Blocked_A | Q6:Q105 | Float | Input sau constantă literală |
| R | Crosses_H | R6:R105 | Float | Input sau constantă literală |
| S | Crosses_A | S6:S105 | Float | Input sau constantă literală |
| T | Possession_H | T6:T105 | Float | Input sau constantă literală |
| U | Possession_A | U6:U105 | Float | Input sau constantă literală |
| V | Field_Tilt_H | V6:V105 | Float | Input sau constantă literală |
| W | Field_Tilt_A | W6:W105 | Float | Input sau constantă literală |
| X | Attack_H | X6:X105 | Float | Input sau constantă literală |
| Y | Attack_A | Y6:Y105 | Float | Input sau constantă literală |
| Z | Chasing_H | Z6:Z105 | Float | Input sau constantă literală |
| AA | Chasing_A | AA6:AA105 | Float | Input sau constantă literală |
| AB | Wings_H | AB6:AB105 | Float | Input sau constantă literală |
| AC | Wings_A | AC6:AC105 | Float | Input sau constantă literală |
| AD | Absences_H | AD6:AD105 | Float | Input sau constantă literală |
| AE | Absences_A | AE6:AE105 | Float | Input sau constantă literală |
| AF | Stakes_H | AF6:AF105 | Float | Input sau constantă literală |
| AG | Stakes_A | AG6:AG105 | Float | Input sau constantă literală |

#### Istoric_Nativ

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Event_ID | A6:A405 | Text | Input sau constantă literală |
| B | League | B6:B405 | Text | Input sau constantă literală |
| C | Season | C6:C405 | Text | Input sau constantă literală |
| D | Match_Date | D6:D405 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| E | Home | E6:E405 | Text | Input sau constantă literală |
| F | Away | F6:F405 | Text | Input sau constantă literală |
| G | HC | G6:G405 | Număr întreg | Input sau constantă literală |
| H | AC | H6:H405 | Număr întreg | Input sau constantă literală |
| I | Source_ID | I6:I405 | Text | Input sau constantă literală |
| J | Source_URL | J6:J405 | Text | Input sau constantă literală |
| K | Retrieved_UTC | K6:K405 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| L | Definition | L6:L405 | Text | Input sau constantă literală |
| M | Evidence | M6:M405 | Text | Input sau constantă literală |
| N | Canonical_Key | N6:N405 | Text | Rezultat formulă |
| O | Row_State | O6:O405 | Text | Rezultat formulă |
| P | Use_Row | P6:P405 | Număr întreg | Rezultat formulă |
| Q | Total | Q6:Q405 | Număr întreg | Rezultat formulă |
| R | Total_Squared | R6:R405 | Număr întreg | Rezultat formulă |
| S | Source_Row | S6:S405 | Număr întreg | Rezultat formulă |

#### Surse_Import

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Source_ID | A6:A13 | Text | Input sau constantă literală |
| B | League | B6:B13 | Text | Input sau constantă literală |
| C | Season | C6:C13 | Text | Input sau constantă literală |
| D | Provider | D6:D13 | Text | Input sau constantă literală |
| E | URL | E6:E13 | Text | Input sau constantă literală |
| F | Retrieved_UTC | F6:F13 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| G | Coverage | G6:G13 | Text | Input sau constantă literală |
| H | Status | H6:H13 | Text | Input sau constantă literală |
| I | Rows | I6:I13 | Număr întreg | Input sau constantă literală |
| J | Missing_Corners | J6:J13 | Număr întreg | Input sau constantă literală |
| K | Attempts | K6:K13 | Text | Input sau constantă literală |
| L | SHA256 | L6:L13 | Text | Input sau constantă literală |
| M | Source_Key | M6:M13 | Text | Rezultat formulă |

#### Calibrare_Linii

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Line | A6:A19 | Text | Input sau constantă literală |
| B | Type | B6:B19 | Text | Input sau constantă literală |
| C | k | C6:C19 | Număr întreg | Input sau constantă literală |
| D | Calibration_Factor | D6:D19 | Float | Input sau constantă literală |
| E | PASS_Max | E6:E19 | Float probabilitate 0–1 | Input sau constantă literală |
| F | WATCH_Max | F6:F19 | Float probabilitate 0–1 | Input sau constantă literală |
| G | Review_Status | G6:G19 | Text | Input sau constantă literală |
| H | Scope_League | H6:H19 | Text | Input sau constantă literală |
| I | Training_End_UTC | I6:I19 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| J | Review_UTC | J6:J19 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| K | Report_URL | K6:K19 | Text | Input sau constantă literală |
| L | Reviewer | L6:L19 | Text | Input sau constantă literală |
| M | OOS_N | M6:M19 | Număr întreg | Rezultat formulă |
| N | OOS_Wins | N6:N19 | Număr întreg | Rezultat formulă |
| O | OOS_Hit_Rate | O6:O19 | Float probabilitate 0–1 | Rezultat formulă |
| P | OOS_P_Mean | P6:P19 | Float probabilitate 0–1 | Rezultat formulă |
| Q | Wilson_95_Lower | Q6:Q19 | Float probabilitate 0–1 | Rezultat formulă |
| R | Overconfidence | R6:R19 | Float probabilitate 0–1 | Rezultat formulă |
| S | Tail_Validated | S6:S19 | Text | Rezultat formulă |
| T | Defensive_Validated | T6:T19 | Text | Rezultat formulă |
| U | Parameters_Valid | U6:U19 | Text | Rezultat formulă |
| V | Model_Signature | V6:V19 | Text | Rezultat formulă |

#### OOS_Predictii

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Fixture_ID | A6:A255 | Text | Input sau constantă literală |
| B | League | B6:B255 | Text | Input sau constantă literală |
| C | Line | C6:C255 | Text | Input sau constantă literală |
| D | Snapshot_UTC | D6:D255 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| E | Kickoff_UTC | E6:E255 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| F | Training_End_UTC | F6:F255 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| G | P_Final | G6:G255 | Float probabilitate 0–1 | Input sau constantă literală |
| H | Candidate_Confidence | H6:H255 | Număr întreg | Input sau constantă literală |
| I | D | I6:I255 | Float | Input sau constantă literală |
| J | Risk_Score | J6:J255 | Float | Input sau constantă literală |
| K | Prior_Active | K6:K255 | Text | Input sau constantă literală |
| L | Native_Core_Count | L6:L255 | Număr întreg | Input sau constantă literală |
| M | Candidate_Tail | M6:M255 | Text | Input sau constantă literală |
| N | Total_Corners | N6:N255 | Număr întreg | Input sau constantă literală |
| O | Outcome_URL | O6:O255 | Text | Input sau constantă literală |
| P | Settled_UTC | P6:P255 | Dată UTC / serial Excel; unele formule pot întoarce 0 | Input sau constantă literală |
| Q | Frozen_Evidence_URL | Q6:Q255 | Text | Input sau constantă literală |
| R | Model_Signature | R6:R255 | Text | Input sau constantă literală |
| S | Mode | S6:S255 | Text | Input sau constantă literală |
| T | Record_Valid | T6:T255 | Număr întreg | Rezultat formulă |
| U | Win | U6:U255 | Număr întreg | Rezultat formulă |

#### Verificari

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Control | A6:A15 | Text | Input sau constantă literală |
| B | Rezultat | B6:B15 | Text sau număr în funcție de control | Rezultat formulă |
| C | Așteptat | C6:C15 | Text sau număr în funcție de control | Input sau constantă literală |
| D | Explicație | D6:D15 | Text | Input sau constantă literală |

#### Documentatie

| Coloană | Nume exact | Interval date | Tip | Sursă |
| --- | --- | --- | --- | --- |
| A | Subiect | A6:A32 | Text | Input sau constantă literală |
| B | Regulă | B6:B32 | Text | Input sau constantă literală |

Schema pentru fiecare coloană, celula exemplu, formula originală, formatul de afișare și proveniența sunt livrate și în `schema_coloane.json` / `.csv`. `Anexa_schema_si_formule.md` adaugă formulele reprezentative și dependențele lor. `celule_integrale.json` și `formule_integrale.csv` păstrează toate celulele, respectiv toate formulele, fără omisiunea rândurilor repetitive.

## 2 Date de intrare și configurații

### 2.1 Identitatea meciului și cutoff

`Input_Meci!A:G` conține ID, ligă, sezon, gazde, oaspeți, kickoff UTC și cutoff UTC. Pentru meciul de pe rândul 6, `Motor_Meciuri!BQ6` cere:

- Match_ID unic în `MatchesTable` și fixture unic prin ligă, sezon, gazde, oaspeți și kickoff.
- Ligă, sezon și ambele echipe ne-goale; gazde diferite de oaspeți.
- Kickoff și cutoff numerice în semantica serialului Excel; cutoff strict anterior kickoff.
- Mode `LIVE` sau `REPLAY`; Prior_Allowed `YES`, `NO` sau gol.

Formula originală `Motor_Meciuri!BQ6`:

```excel
=IF(A6="","",IF(AND(COUNTIF(MatchesTable[Match_ID],A6)=1,COUNTIFS(MatchesTable[League],B6,MatchesTable[Season],C6,MatchesTable[Home],'Input_Meci'!D6,MatchesTable[Away],'Input_Meci'!E6,MatchesTable[Kickoff_UTC],F6)=1,B6<>"",C6<>"",'Input_Meci'!D6<>"",'Input_Meci'!E6<>"",'Input_Meci'!D6<>'Input_Meci'!E6,ISNUMBER(F6),ISNUMBER(G6),G6<F6,OR(E6="LIVE",E6="REPLAY"),OR('Input_Meci'!L6="YES",'Input_Meci'!L6="NO",'Input_Meci'!L6="")),"VALID","INVALID"))
```

Nu există parser de nume de echipe sau normalizare a ligilor în formule. Matching-ul trebuie să reproducă semantica Excel, inclusiv comparațiile text fără diferențierea majusculelor în funcțiile uzuale. Nu se unesc în mod inventat aliasuri diferite.

Regula temporală pentru istoric este `Match_Date < INT(Cutoff_UTC)`. Se exclud toate evenimentele din ziua cutoff-ului, chiar dacă ora lor ar fi anterioară cutoff-ului. În exemplu, cutoff este 23 mai 2026 la 23:00 UTC; istoricul eligibil este strict anterior zilei de 23 mai. Nu înlocui această regulă cu `Match_Date < Cutoff_UTC`.

Pentru LIVE, `Retrieved_UTC > Cutoff_UTC` produce `POST CUTOFF`. Egalitatea nu produce această stare. REPLAY permite sursa importată ulterior, dar nu poate intra în Top LIVE.

### 2.2 Istoricul nativ și proveniența

Inputurile brute se completează în `Istoric_Nativ!A6:M405`. N:S sunt formule. Un rând reprezintă un meci istoric, cu HC și AC, definiție `FT90`, dată, identificator de sursă, URL, timestamp de import și evidence. HC/AC sunt întregi între 0 și 100 inclusiv; zero este observație validă. Blank, -1, -2 sau text nu reprezintă zero cornere valid.

`Surse_Import!A6:L13` sunt inputuri; M este Source_Key = League + `|` + Season. Pentru o fereastră, Core caută această cheie prin MATCH exact și cere unicitate. Pentru fiecare rând nativ, `Source_Row` se caută prin Source_ID.

Cheia canonică nativă este ligă + sezon + zi formatată `yyyymmdd` + gazde + oaspeți. Event_ID nu este criteriul de deduplicare. Nu include ora din zi. Formula exactă:

Formula originală `Istoric_Nativ!N6`:

```excel
=IF(AND(A6<>"",ISNUMBER(D6)),B6&"|"&C6&"|"&TEXT(D6,"yyyymmdd")&"|"&E6&"|"&F6,"")
```

`Row_State` verifică mai întâi integritatea rândului. După aceea, diferențe de HC sau AC la aceeași cheie produc `SOURCE CONFLICT`; dublurile identice ulterioare primei apariții sunt `DUPLICATE`; numai prima observație validă are `Use_Row=1`. Conflictele sunt comparate cu întregul interval de chei, nu numai cu rânduri deja admise în calcule.

Formula originală `Istoric_Nativ!O6`:

```excel
=IF(A6="","",IFERROR(IF(NOT(AND(B6<>"",C6<>"",ISNUMBER(D6),D6>0,E6<>"",F6<>"",E6<>F6,ISNUMBER(G6),ISNUMBER(H6),G6>=0,H6>=0,G6<=100,H6<=100,MOD(G6,1)=0,MOD(H6,1)=0,L6="FT90",S6>0,INDEX(SourceTable[League],MAX(1,S6))=B6,INDEX(SourceTable[Season],MAX(1,S6))=C6,ISNUMBER(K6),K6=INDEX(SourceTable[Retrieved_UTC],MAX(1,S6)),J6<>"",M6<>"")),"INVALID",IF(OR(COUNTIFS('Istoric_Nativ'!$N$6:$N$405,N6,'Istoric_Nativ'!$G$6:$G$405,G6)<>COUNTIF('Istoric_Nativ'!$N$6:$N$405,N6),COUNTIFS('Istoric_Nativ'!$N$6:$N$405,N6,'Istoric_Nativ'!$H$6:$H$405,H6)<>COUNTIF('Istoric_Nativ'!$N$6:$N$405,N6)),"SOURCE CONFLICT",IF(COUNTIF($N$6:N6,N6)>1,"DUPLICATE","VALID"))),"INVALID"))
```

`Total = HC+AC` numai pentru `Use_Row=1`; altfel este 0 auxiliar. Acest zero auxiliar nu este o imputare a unei observații lipsă: agregările istorice trebuie să filtreze `Use_Row=1`. `Total_Squared=Total^2`.

Sursa unei ferestre este CLOSED dacă cheia este unică, statusul este unul dintre `IMPORTED`, `PARTIAL`, `SOURCE CONFLICT`, Coverage este `FULL SEASON EXPORT`, URL și SHA256 sunt ne-goale și regula LIVE/cutoff este respectată. Exact acest set de statusuri apare în formulă. Un status de sursă numit SOURCE CONFLICT nu este, singur, același lucru cu `Row_State=SOURCE CONFLICT` sau cu decizia terminală din Input_Meci.

Formula originală `Core_Nativ!R6`:

```excel
=IF(B6="","",IF(F6="","UNUSED",IF(Q6=0,"NOT CHECKED",IF(COUNTIF(SourceTable[Source_Key],E6&"|"&F6)<>1,"SOURCE CONFLICT",IF(NOT(OR(INDEX(SourceTable[Status],MAX(1,Q6))="IMPORTED",INDEX(SourceTable[Status],MAX(1,Q6))="PARTIAL",INDEX(SourceTable[Status],MAX(1,Q6))="SOURCE CONFLICT")),"ACCESS BLOCKED",IF(OR(INDEX(SourceTable[Coverage],Q6)<>"FULL SEASON EXPORT",INDEX(SourceTable[URL],Q6)="",INDEX(SourceTable[SHA256],Q6)=""),"EVIDENCE INCOMPLETE",IF(AND('Input_Meci'!H6="LIVE",INDEX(SourceTable[Retrieved_UTC],Q6)>'Input_Meci'!G6),"POST CUTOFF","CLOSED")))))))
```

Nu presupune verificări suplimentare inexistente: formula nu recalculează SHA256 din conținutul web și nu verifică egalitatea dintre Rows și numărul real importat. Attempts este trasabilitate, nu un parser executat de Excel. Importatorul descris în Documentatie nu este încorporat în XLSX și nu a fost furnizat în acest atașament.

### 2.3 Cele 12 valori native și eșantioanele

Valorile comune sunt derivate, nu completate ca medii independente în Input_Meci:

| Componentă | N în Motor | Raw For / Against | Effective For / Against | Core CURRENT pentru primul meci |
|---|---|---|---|---|
| Gazde sezon | N6 | T6 / U6 | AF6 / AG6 | rând 6 |
| Gazde acasă | O6 | V6 / W6 | AH6 / AI6 | rând 7 |
| Gazde recent | P6 | X6 / Y6 | AJ6 / AK6 | rând 8 |
| Oaspeți sezon | Q6 | Z6 / AA6 | AL6 / AM6 | rând 9 |
| Oaspeți deplasare | R6 | AB6 / AC6 | AN6 / AO6 | rând 10 |
| Oaspeți recent | S6 | AD6 / AE6 | AP6 / AQ6 | rând 11 |

Ferestrele recente se construiesc prin a cincea dată cea mai recentă și includ toate rândurile cu dată ≥ acel prag. La egalități de dată, N poate depăși 5. Nu înlocui mecanic selecția cu ultimele cinci rânduri sortate.

### 2.4 Inputurile soft și contextuale

| Coloane Input_Meci | Inputuri | Domeniu valid în formule | Efect |
|---|---|---|---|
| N/O | Shots_H/A | numeric 0–200 | Soft H/A; neutru 12 când invalid/lipsă |
| P/Q | Blocked_H/A | numeric 0–200 | Soft H/A; neutru 3,5 |
| R/S | Crosses_H/A | numeric 0–200 | Soft H/A; neutru 18 |
| T/U | Possession_H/A | numeric 0–100 | numai Soft_Missing / Confidence; nu apare în Soft H/A |
| V/W | Field_Tilt_H/A | numeric 0–10 | Soft H/A; neutru 5 |
| X/Y | Attack_H/A | gol sau numeric 0–10 | context; gol devine factor neutru 5 |
| Z/AA | Chasing_H/A | gol sau numeric 0–10 | context; neutru 5 |
| AB/AC | Wings_H/A | gol sau numeric 0–10 | context; neutru 5 |
| AD/AE | Absences_H/A | gol sau numeric −2…2 | context; neutru 0 |
| AF/AG | Stakes_H/A | gol sau numeric −2…2 | context; neutru 0 |

Valorile contextuale nenumerice sau în afara domeniului invalidează `Context_Valid` și, după release, G0. Valorile soft invalide folosesc reperul neutru și cresc Soft_Missing; nu sunt hard fail prin ele însele. Nu există un gate separat pentru lineup sau arbitru în acest workbook.

Regula de produs privind sentinelii -1/-2 se aplică înainte de mapping-ul din sursa sportivă. În același timp, −1 și −2 sunt valori legitime ale unor scoruri contextuale semnate din acest Excel. Adapterul trebuie să distingă proveniența și unitatea; nu transforma un sentinel API într-un scor contextual valid și nici un scor contextual real într-o lipsă de date.

### 2.5 Configurația globală exactă

| Celulă Config_v6 | Parametru | Valoare curentă | Proveniență |
| --- | --- | --- | --- |
| B4 | Pondere sezon | 0.3 | Literal |
| B5 | Pondere H/A | 0.45 | Literal |
| B6 | Pondere recent | 0.25 | Literal |
| B7 | N minim sezon | 10 | Literal |
| B8 | N minim H/A | 5 | Literal |
| B9 | N minim recent | 3 | Literal |
| B10 | D prag Poisson | 1.1 | Literal |
| B11 | D NB mild | 1.35 | Literal |
| B12 | D NB moderat | 1.7 | Literal |
| B13 | D hard fail | 2.25 | Literal |
| B14 | Calibrare: reducere spre 50% | 0.82 | Literal |
| B15 | N țintă dispersie | 20 | Literal |
| B16 | P minim eligibilitate | 0.72 | Literal |
| B17 | Reper P informativ | 0.8 | Literal |
| B18 | Confidence minim | 65 | Literal |
| B19 | Pondere EV | 0 | Literal |
| B20 | Limită soft | 0.08 | Literal |
| B21 | Limită context | 0.12 | Literal |
| B26 | O3,5 PASS max pilot | 0.05 | Literal |
| C26 | O3,5 WATCH max pilot | 0.08 | Literal |
| B34 | Confidence maxim cu prior | 75 | Literal |
| B35 | Penalizare OOS pending | 10 | Literal |
| B36 | Penalizare D moderat | 5 | Literal |
| B37 | Penalizare D ridicat | 10 | Literal |
| B38 | Penalizare maximă soft lipsă | 5 | Literal |
| B39 | Suma ponderilor | 1 | Formulă |
| B40 | Validarea parametrilor | VALID | Formulă |
| B41 | N minim varianță | 2 | Literal |
| B42 | Floor fără DEFENSIV validat | 2 | Literal |
| B44 | Pondere failure | 0.55 | Literal |
| B45 | Pondere dispersie | 0.2 | Literal |
| B46 | Pondere incertitudine | 0.15 | Literal |
| B47 | Pondere context | 0.1 | Literal |
| B50 | P minim DEFENSIV | 0.9 | Literal |
| B51 | Confidence minim DEFENSIV | 90 | Literal |
| B52 | Score maxim DEFENSIV | 20 | Literal |
| B53 | D maxim DEFENSIV | 1.1 | Literal |
| B54 | Număr meciuri recente | 5 | Literal |
| B55 | Capacitate meciuri | 100 | Literal |
| B56 | N minim OOS pentru promovare | 200 | Literal |
| B57 | Wilson 95%: limită inferioară | 0.9 | Literal |
| B58 | Supraestimare OOS maximă | 0.05 | Literal |
| B60 | Semnătură parametri | Semnătură text; formula integrală în anexă | Formulă |

`B39=SUM(B4:B6)` trebuie să fie 1 în toleranța de validare 0,000001. Această toleranță aparține validatorului configurației, nu comparației rezultatelor.

Formula originală `Config_v6!B40`:

```excel
=IF(AND(COUNT(B4:B18)=15,MIN(B4:B18)>=0,ABS(B39-1)<0.000001,B7>=1,B8>=1,B9>=1,B10>0,B11>=B10,B12>=B11,B13>=B12,B14>0,B14<=1,B15>=2,B16>0.5,B16<1,B18>=0,B18<=100,B19=0,B20>=0,B20<=1,B21>=0,B21<=1,B26>=0,B26<C26,C26<=1,B34>=0,B34<=75,B35>=0,B36>=0,B37>=0,B38>=0,B41=2,B42=2,MIN(B44:B47)>=0,ABS(SUM(B44:B47)-1)<0.000001,B50>=0.9,B50<1,B51>=90,B51<=100,B52>=0,B52<=20,B53>0,B53<=1.1,B54=5,B55=100,B56>=200,B57>=0.9,B57<1,B58>=0,B58<=0.05),"VALID","CONFIG INVALID")
```

`B17` este reper informativ; nu este pragul efectiv de eligibilitate. `B19` trebuie să rămână 0, iar EV nu este un termen activ în calcule. `B55=100` nu redimensionează workbook-ul. Pragurile scorurilor 20/40/60/80, coeficienții de context, 1,96 din Wilson și plafonul Pcal 0,01–0,99 sunt literali în formule, nu celule configurabile separate.

### 2.6 Configurația fiecărei linii

| Rând Calibrare | Linie | Type | k | Factor | PASS max | WATCH max | Review | Praw |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | O3,5 | OVER | 3 | 1 | 0.05 | 0.08 | PILOT | 1−Distributie!AA(rând meci) |
| 7 | O4,5 | OVER | 4 | 1 | gol | gol | PENDING | 1−Distributie!AB(rând meci) |
| 8 | O5,5 | OVER | 5 | 1 | gol | gol | PENDING | 1−Distributie!AC(rând meci) |
| 9 | O6,5 | OVER | 6 | 1 | gol | gol | PENDING | 1−Distributie!AD(rând meci) |
| 10 | O7,5 | OVER | 7 | 1 | gol | gol | PENDING | 1−Distributie!AE(rând meci) |
| 11 | O8,5 | OVER | 8 | 1 | gol | gol | PENDING | 1−Distributie!AF(rând meci) |
| 12 | U10,5 | UNDER | 10 | 1 | gol | gol | PENDING | Distributie!AH(rând meci) |
| 13 | U11,5 | UNDER | 11 | 1 | gol | gol | PENDING | Distributie!AI(rând meci) |
| 14 | U12,5 | UNDER | 12 | 1 | gol | gol | PENDING | Distributie!AJ(rând meci) |
| 15 | U13,5 | UNDER | 13 | 1 | gol | gol | PENDING | Distributie!AK(rând meci) |
| 16 | U14,5 | UNDER | 14 | 1 | gol | gol | PENDING | Distributie!AL(rând meci) |
| 17 | U15,5 | UNDER | 15 | 1 | gol | gol | PENDING | Distributie!AM(rând meci) |
| 18 | U16,5 | UNDER | 16 | 1 | gol | gol | PENDING | Distributie!AN(rând meci) |
| 19 | U17,5 | UNDER | 17 | 1 | gol | gol | PENDING | Distributie!AO(rând meci) |

Toate liniile au `Calibration_Factor=1` și `Scope_League=E0` în fișierul livrat. O3,5 are bandă PILOT 5%/8%; celelalte 13 linii nu au PASS_Max/WATCH_Max completate. Nicio linie nu este Tail_Validated sau Defensive_Validated.

Line, Type și k sunt constante în `Analiza_Linii`, repetate pentru fiecare meci. Probabilitățile raw referă celule CDF fixate în formule. `Calibrare_Linii!C` este folosită inclusiv pentru settlement OOS. Nu presupune că editarea unei singure valori k generează automat o linie nouă și actualizează toate dependențele. Reproducerea V14 fixează lista și ordinea existente.

`Config_v6!B60` produce semnătura globală cu `TEXT(...,"0.000000")`. `Calibrare_Linii!V` îi adaugă linia, factorul și cele două praguri, folosind `NA` pentru pragurile goale. Ordinea câmpurilor și șasele zecimale sunt parte din identitatea snapshot-urilor; nu se sortează arbitrar și nu se reconstruiește dintr-un dicționar neordonat. Formula exactă integrală se află în anexă.

## 3 Logica matematică și ordinea operațiilor

### 3.1 Selectarea observațiilor pentru Core

Pentru fereastra cu League, Season, Team, Split și Before_Date:

```text
eligible(row) = row.League == League
             and row.Season == Season
             and row.Use_Row == 1
             and row.Match_Date < Before_Date
             and team belongs to requested HOME / AWAY / ANY role

N_scope = count(eligible rows)
if Period == RECENT and N_scope > 0:
    Recent_From = LARGE(eligible dates, min(5, N_scope))
else:
    Recent_From = 0
window = eligible rows with Match_Date >= Recent_From
N = count(window)
Corners_For = sum(HC when team home, AC when team away) / N
Corners_Against = sum(AC when team home, HC when team away) / N
if N == 0: both averages = EMPTY
```

În split HOME se folosesc doar meciurile în care Team este Home; în AWAY doar Away. Valorile for/against se inversează corect pentru echipa care joacă în deplasare.

Formulele pentru N și media nativă For sunt:

Formula originală `Core_Nativ!M6`:

```excel
=IF(OR(B6="",F6=""),0,IF(H6="HOME",COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6),IF(H6="AWAY",COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6),COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6)+COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6))))
```

Formula originală `Core_Nativ!N6`:

```excel
=IF(M6=0,"",IF(H6="HOME",SUMIFS('Istoric_Nativ'!$G$6:$G$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6),IF(H6="AWAY",SUMIFS('Istoric_Nativ'!$H$6:$H$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6),SUMIFS('Istoric_Nativ'!$G$6:$G$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6)+SUMIFS('Istoric_Nativ'!$H$6:$H$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6)))/M6)
```

Core `Data_Status` este Source_State dacă sursa nu este CLOSED; apoi `NATIVE INPUT ISSUE` pentru Problem_Rows>0, `NO HISTORY` pentru N=0, `SMALL SAMPLE` pentru N<Target_N, altfel `DERIVED`. Priorul nu înlocuiește retrospectiv valorile raw și N curent.

### 3.2 Prior și shrinkage

O valoare efectivă există doar dacă sursa curentă este CLOSED și nu are Problem_Rows. Dacă N curent ≥ țintă, valoarea efectivă este media curentă. Altfel trebuie simultan:

- Prior_Allowed=YES, Prior_Season ne-gol și comparat `<` Season exact cum apare în Excel.
- Fereastra prior corespunzătoare are Data_Status=DERIVED și N prior ≥ ținta ferestrei curente.
- Aceleași ligă și echipă prin construcția rândului Core prior; cutoff-ul rămâne cel al meciului.

```text
w = min(1, N_current / Target_N)
effective = w * (0 if N_current == 0 else mean_current)
          + (1 - w) * mean_prior
```

Zero din această expresie este termenul cu greutate zero când N=0; nu reprezintă completarea istoricului cu meciuri fără cornere. Dacă priorul nu este valid, valoarea efectivă rămâne goală.

Formula originală `Motor_Meciuri!AF6`:

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R6="CLOSED",'Core_Nativ'!S6=0),IF('Core_Nativ'!M6>='Core_Nativ'!P6,'Core_Nativ'!N6,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T12="DERIVED",'Core_Nativ'!M12>='Core_Nativ'!P6),MIN(1,'Core_Nativ'!M6/'Core_Nativ'!P6)*IF('Core_Nativ'!M6=0,0,'Core_Nativ'!N6)+(1-MIN(1,'Core_Nativ'!M6/'Core_Nativ'!P6))*'Core_Nativ'!N12,"")),""))
```

Sezonul este text în exemplu (`2025/26`); comparația `Prior_Season < Season` nu este o funcție calendaristică de înțelegere a sezoanelor. Păstrează formatul și semantica sursei.

`Prior_Active` devine YES când oricare din cele șase N curente este sub Target_N, chiar înainte de a demonstra că toate valorile efective au fost completate. Câmpul nu este singur dovada unui prior valid. `Core_Native_Count=COUNT(T:AE)` numără valori numerice existente, inclusiv medii cu sample mic. `Core_Effective_Count=COUNT(AF:AQ)` trebuie să fie 12 la G0.

### 3.3 Dispersia comună

Se selectează reuniunea fără dublare a tuturor meciurilor eligibile care implică oricare dintre cele două echipe. Condiția OR se construiește prin sumă de indicatori `>0`; un meci direct între echipe este numărat o dată. Se folosește sezonul din `Motor_Meciuri!BL`.

Sezonul dispersiei este sezonul curent când numărul de meciuri unice este cel puțin 2. Sub 2, se poate folosi Prior_Season numai dacă priorul este permis, sezonul este anterior, toate cele șase surse prior sunt CLOSED și suma Problem_Rows prior este zero. N prior pentru dispersie va fi verificat ulterior de G0. Nu se amestecă dispersia sezonului curent cu varianța altui sezon.

```text
N = count(union)
mean = SUM(total) / N                                  if N > 0
variance = MAX(0, (SUM(total^2) - N * mean^2) / (N - 1)) if N >= 2
D = variance / mean                                   if G0 == PASS
distribution = POISSON if D <= 1.10 else NEGATIVE BINOMIAL
size = 9999 if POISSON else mean / (D - 1)
```

Aceasta este varianță de eșantion, echivalentă matematic cu VAR.S, dar implementată prin SUMPRODUCT și sume de pătrate. Nu există apel `VAR.S` în formule. Pentru identitate numerică păstrează expresia și ordinea originală, în loc de a substitui fără verificare alt algoritm de varianță.

Formula originală `Motor_Meciuri!AT6`:

```excel
=IF(AR6<2,"",MAX(0,(SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405=B6)*('Istoric_Nativ'!$C$6:$C$405=BL6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT(G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6)+('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*'Istoric_Nativ'!$R$6:$R$405)-AR6*AS6^2)/(AR6-1)))
```

`mean` istoric nu este `Mu` ajustat. Pentru NB, size folosește `mean_history/(D−1)`, apoi PMF folosește acest size împreună cu Mu ajustat. Nu substitui size=`Mu/(D−1)`.

### 3.4 Release și G0 înainte de probabilități

`Release` este NOT RELEASED dacă metadata este invalidă. Cu metadata validă, o decizie explicită NOT AVAILABLE sau SOURCE CONFLICT și Evidence_or_Attempts ne-gol închide operațional cazul ca READY; G0 va fi FAIL. Pentru AUTO sau sourcing gol, sunt necesare șase surse CURRENT CLOSED și lipsa problemelor native. Celelalte stări, inclusiv ACCESS BLOCKED, nu eliberează calculul.

Formula originală `Motor_Meciuri!H6`:

```excel
=IF(A6="","",IF(BQ6<>"VALID","NOT RELEASED",IF(AND(OR('Input_Meci'!I6="NOT AVAILABLE",'Input_Meci'!I6="SOURCE CONFLICT"),'Input_Meci'!J6<>""),"READY",IF(OR(NOT(OR('Input_Meci'!I6="AUTO",'Input_Meci'!I6="")),COUNTIF('Core_Nativ'!R6:R11,"CLOSED")<>6,BJ6>0),"NOT RELEASED","READY"))))
```

G0 PASS cere READY, absența deciziei terminale de lipsă/conflict, 12 valori efective, N_Dispersion≥2, medie istorică pozitivă, varianță numerică, context valid și configurație validă.

Formula originală `Motor_Meciuri!I6`:

```excel
=IF(A6="","",IF(H6<>"READY","NOT RELEASED",IF(AND(NOT(OR('Input_Meci'!I6="NOT AVAILABLE",'Input_Meci'!I6="SOURCE CONFLICT")),L6=12,AR6>=2,AS6>0,ISNUMBER(AT6),BI6="VALID",BK6="VALID"),"PASS","FAIL")))
```

`D>2,25` nu este în acest G0. Probabilitățile pot fi calculate și păstrate când D depășește pragul, dar Risk_Level_FINAL devine 5 și verdictul NO BET. Nu șterge automat probabilitatea oricărei selecții cu nivel 5.

Un sample redus fără prior utilizabil poate lăsa Core_Effective_Count<12 și produce G0 FAIL după release. Cauza este imposibilitatea construirii valorilor efective conform regulilor, nu o transformare universală a etichetei SMALL SAMPLE în hard fail.

### 3.5 Ajustările soft

Pentru gazde și similar pentru oaspeți, înlocuirile neutre se fac numai conform testelor ISNUMBER și intervalelor din formula originală:

```text
soft = clip(
  1 + 0.02*(shots/12 - 1)
    + 0.02*(blocked/3.5 - 1)
    + 0.02*(crosses/18 - 1)
    + 0.02*((field_tilt-5)/5),
  1-B20, 1+B20)
```

Formula originală `Motor_Meciuri!AX6`:

```excel
=IF(A6="","",MAX(1-'Config_v6'!$B$20,MIN(1+'Config_v6'!$B$20,1+0.02*(IF(AND(ISNUMBER('Input_Meci'!N6),'Input_Meci'!N6>=0,'Input_Meci'!N6<=200),'Input_Meci'!N6,12)/12-1)+0.02*(IF(AND(ISNUMBER('Input_Meci'!P6),'Input_Meci'!P6>=0,'Input_Meci'!P6<=200),'Input_Meci'!P6,3.5)/3.5-1)+0.02*(IF(AND(ISNUMBER('Input_Meci'!R6),'Input_Meci'!R6>=0,'Input_Meci'!R6<=200),'Input_Meci'!R6,18)/18-1)+0.02*((IF(AND(ISNUMBER('Input_Meci'!V6),'Input_Meci'!V6>=0,'Input_Meci'!V6<=10),'Input_Meci'!V6,5)-5)/5))))
```

Posesia nu intră în această expresie. Numărul de câmpuri soft lipsă/invalid este `10 − count(valid N:W)`; include posesia ambelor echipe și produce o penalizare de până la 5 puncte în Confidence Base cu configurația actuală. Introducerea posesiei în lambda ar modifica modelul.

### 3.6 Ajustările de context

```text
context = clip(
  1 + 0.012*(attack-5)
    + 0.018*(chasing-5)
    + 0.012*(wings-5)
    + 0.015*absences
    + 0.020*stakes,
  1-B21, 1+B21)
sensitivity = min(1, (abs(context_H-1)+abs(context_A-1))*3)
```

Formula originală `Motor_Meciuri!AZ6`:

```excel
=IF(A6="","",MAX(1-'Config_v6'!$B$21,MIN(1+'Config_v6'!$B$21,1+0.012*(IF('Input_Meci'!X6="",5,IF(ISNUMBER('Input_Meci'!X6),'Input_Meci'!X6,5))-5)+0.018*(IF('Input_Meci'!Z6="",5,IF(ISNUMBER('Input_Meci'!Z6),'Input_Meci'!Z6,5))-5)+0.012*(IF('Input_Meci'!AB6="",5,IF(ISNUMBER('Input_Meci'!AB6),'Input_Meci'!AB6,5))-5)+0.015*IF('Input_Meci'!AD6="",0,IF(ISNUMBER('Input_Meci'!AD6),'Input_Meci'!AD6,0))+0.02*IF('Input_Meci'!AF6="",0,IF(ISNUMBER('Input_Meci'!AF6),'Input_Meci'!AF6,0)))))
```

Semnul scorurilor Absences și Stakes este cel deja introdus; formula adună termenul. Nu presupune că orice număr pozitiv de absențe trebuie transformat automat în penalizare. Sunt scoruri contextuale semnate, nu headcount de jucători.

### 3.7 Lambda și Mu

```text
lambda_H = (
   AVERAGE(H_season_for, A_season_against)*0.30
 + AVERAGE(H_home_for, A_away_against)*0.45
 + AVERAGE(H_recent_for, A_recent_against)*0.25
) * soft_H * context_H

lambda_A = (
   AVERAGE(A_season_for, H_season_against)*0.30
 + AVERAGE(A_away_for, H_home_against)*0.45
 + AVERAGE(A_recent_for, H_recent_against)*0.25
) * soft_A * context_A
Mu = lambda_H + lambda_A
```

Toate mediile din aceste expresii sunt valorile efective, după regulile de prior. Nu se face medie simplă a celor 12 valori și nu se rotunjește lambda.

Formula originală `Motor_Meciuri!BB6`:

```excel
=IF(I6<>"PASS","",(AVERAGE(AF6,AM6)*'Config_v6'!$B$4+AVERAGE(AH6,AO6)*'Config_v6'!$B$5+AVERAGE(AJ6,AQ6)*'Config_v6'!$B$6)*AX6*AZ6)
```

Formula originală `Motor_Meciuri!BC6`:

```excel
=IF(I6<>"PASS","",(AVERAGE(AL6,AG6)*'Config_v6'!$B$4+AVERAGE(AN6,AI6)*'Config_v6'!$B$5+AVERAGE(AP6,AK6)*'Config_v6'!$B$6)*AY6*BA6)
```

### 3.8 Confidence Base

Definim:

```text
sample = min(1,min(N_H_Season,N_A_Season)/10)
       * min(1,min(N_H_HA,N_A_HA)/5)
       * min(1,min(N_H_Recent,N_A_Recent)/3)
stability = max(0,15-2*abs(Effective_H_S_For-Effective_H_R_For)
                   -2*abs(Effective_A_S_For-Effective_A_R_For))
dispersion_points = 15 if D<=1.10
                    13 if D<=1.35
                    10 if D<=1.70
                     6 if D<=2.25
                     0 otherwise
rounded = ROUND(40 + 25*sample + stability + dispersion_points
                + 5 - Soft_Missing/10*5, 0)
cap = 75 if Prior_Active==YES or Dispersion_Season!=Season else 100
Confidence_Base = max(0,min(cap,rounded))
```

Formula originală `Motor_Meciuri!BF6`:

```excel
=IF(I6<>"PASS","",MAX(0,MIN(IF(OR(M6="YES",BL6<>C6),'Config_v6'!$B$34,100),ROUND(40+25*MIN(1,MIN(N6,Q6)/'Config_v6'!$B$7)*MIN(1,MIN(O6,R6)/'Config_v6'!$B$8)*MIN(1,MIN(P6,S6)/'Config_v6'!$B$9)+MAX(0,15-2*ABS(AF6-AJ6)-2*ABS(AL6-AP6))+IF(AU6<='Config_v6'!$B$10,15,IF(AU6<='Config_v6'!$B$11,13,IF(AU6<='Config_v6'!$B$12,10,IF(AU6<='Config_v6'!$B$13,6,0))))+5-BE6/10*'Config_v6'!$B$38,0))))
```

Stability folosește For, nu Against. Sample folosește N curent, nu N prior. Se rotunjește înainte de aplicarea cap-ului. ROUND Excel la zero zecimale nu se înlocuiește cu rotunjirea Python ties-to-even; la egalități de jumătate, Excel rotunjește în direcția îndepărtării de zero.

### 3.9 Intensitatea calibrării

```text
dispersion_factor = 1.00 if D<=1.10
                    0.95 if D<=1.35
                    0.88 if D<=1.70
                    0.78 otherwise
strength = min(1, 0.82
                   * (0.7 + 0.3*min(1,N_Dispersion/20))
                   * dispersion_factor
                   * (0.75+0.25*Confidence_Base/100))
```

Formula originală `Motor_Meciuri!BG6`:

```excel
=IF(I6<>"PASS","",MIN(1,'Config_v6'!$B$14*(0.7+0.3*MIN(1,AR6/'Config_v6'!$B$15))*IF(AU6<='Config_v6'!$B$10,1,IF(AU6<='Config_v6'!$B$11,0.95,IF(AU6<='Config_v6'!$B$12,0.88,0.78)))*(0.75+0.25*BF6/100)))
```

Confidence Final și penalizarea OOS nu sunt utilizate aici. Cu parametrii actuali și Confidence Base≤100, strength≤0,82. Astfel Pcal nu poate depăși 0,91 pentru Praw≤1 și Calibration_Factor≤1. Este un plafon teoretic rezultat din formulă, nu o validare că 91% este acuratețea reală.

### 3.10 Distribuția Poisson sau binomială negativă

Workbook-ul nu apelează POISSON.DIST sau NEGBINOM.DIST. Calculează recurența PMF pentru n=0…18 și apoi sume cumulative.

```text
if D <= 1.10:
    pmf[0] = exp(-Mu)
    for n in 1..18: pmf[n] = pmf[n-1] * Mu / n
else:
    r = Mean_Total_History/(D-1)
    pmf[0] = (r/(r+Mu))**r
    for n in 1..18:
        pmf[n] = pmf[n-1] * (r+n-1) / n * Mu / (r+Mu)
for k in 0..18:
    cdf[k] = min(1, SUM(pmf[0:k+1]))
```

Formula originală `Distributie!E6`:

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,EXP(-B6),(D6/(D6+B6))^D6))
```

Formula originală `Distributie!F6`:

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,E6*B6/1,E6*(D6+0)/1*B6/(D6+B6)))
```

Formula originală `Distributie!AA6`:

```excel
=IF(B6="","",MIN(1,SUM(E6:H6)))
```

NB are parametrul de formă real r, nu neapărat întreg; nu îl rotunji. Nu renormaliza PMF_0…PMF_18 la suma 1. Masa peste 18 rămâne în distribuție și nu este anulată printr-o trunchiere. Ultima linie utilizată este U17,5, dar workbook-ul construiește și CDF_18.

### 3.11 Probabilitățile pe linie

Pentru linia cu prag afișat k+0,5:

```text
OVER:  P_Raw = 1 - CDF[k]  # victorie la total >= k+1
UNDER: P_Raw = CDF[k]      # victorie la total <= k
P_Calibrated = max(0.01,min(0.99,0.5+(P_Raw-0.5)*strength*line_factor))
Failure_Model = 1-P_Raw
```

Formula originală `Analiza_Linii!M6`:

```excel
=IF(NOT(AND(J6="PASS",'Calibrare_Linii'!U6="VALID")),"",1-'Distributie'!AA6)
```

Formula originală `Analiza_Linii!N6`:

```excel
=IF(M6="","",MAX(0.01,MIN(0.99,0.5+(M6-0.5)*'Motor_Meciuri'!BG6*'Calibrare_Linii'!D6)))
```

Formula originală `Analiza_Linii!M12`:

```excel
=IF(NOT(AND(J12="PASS",'Calibrare_Linii'!U12="VALID")),"",'Distributie'!AH6)
```

Probabilitatea este goală dacă G0 nu este PASS sau dacă parametrii liniei sunt invalizi. Fiecare linie folosește aceeași PMF/CDF comună, dar un alt prag și o altă direcție. Nu există șase motoare Over și opt motoare Under independente.

### 3.12 Frecvențele empirice și plafonul final

Se folosesc numai meciuri native valide din sezonul curent, înainte de INT(cutoff), inclusiv atunci când dispersia a folosit un sezon prior.

- HA: reuniunea meciurilor cu gazda actuală acasă SAU oaspetele actual în deplasare.
- L10: reuniunea ultimelor zece date/meciuri ale fiecărei echipe, indiferent de teren; pragurile de dată sunt calculate separat.
- L20: aceeași regulă cu 20.
- Reuniunea este făcută cu indicator `>0`, fără dublarea unui meci direct. La egalități de dată pot intra mai mult de 10 sau 20 observații pentru o echipă.

Denominatoarele sunt `Motor!BR:BT` și sunt transferate în `Analiza!AK:AM`. Pentru fiecare fereastră:

```text
failed(row, OVER)  = row.Total <= k
failed(row, UNDER) = row.Total > k
Empirical = SUM(failed rows) / N   if N>0 else EMPTY
Failure_Gate = MAX(Failure_Model, Empirical_HA, Empirical_L10, Empirical_L20)
P_FINAL = MIN(P_Calibrated, 1-Failure_Gate)
```

Formula originală `Analiza_Linii!P6`:

```excel
=IF(OR(NOT(AND(J6="PASS",'Calibrare_Linii'!U6="VALID")),AK6=0),"",SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405='Input_Meci'!B6)*('Istoric_Nativ'!$C$6:$C$405='Input_Meci'!C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT('Input_Meci'!G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*('Istoric_Nativ'!$Q$6:$Q$405<=H6))/AK6)
```

Formula originală `Analiza_Linii!S6`:

```excel
=IF(M6="","",MAX(O6,P6,Q6,R6))
```

Formula originală `Analiza_Linii!AB6`:

```excel
=IF(N6="","",MIN(N6,1-S6))
```

MAX ignoră rezultatele goale din referințele celulare. O fereastră fără observații rămâne goală și nu se raportează ca rată de eșec zero. În exemplul O3,5 există ferestre cu rată zero și N pozitiv; acestea sunt observații distincte de lipsa istoricului.

Nu confunda `Failure_Model=1−Praw`, `Failure_Gate=max(...)` și `1−P_FINAL`. Risk Score folosește Failure_Gate, nu complementul probabilității calibrate finale.

## 4 Filtrele V14 și recomandarea finală

### 4.1 Risk Score și nivelul brut

```text
Risk_Score = min(100,
    Failure_Gate*100*0.55
  + min(100,D/2.25*100)*0.20
  + (100-Confidence_Base)*0.15
  + Sensitivity*100*0.10)
Risk_Level_Raw = 1 if score<=20
                 2 if score<=40
                 3 if score<=60
                 4 if score<=80
                 5 otherwise
```

Formula originală `Analiza_Linii!T6`:

```excel
=IF(M6="","",MIN(100,S6*100*'Config_v6'!$B$44+MIN(100,L6/'Config_v6'!$B$13*100)*'Config_v6'!$B$45+(100-'Motor_Meciuri'!BF6)*'Config_v6'!$B$46+'Motor_Meciuri'!BH6*100*'Config_v6'!$B$47))
```

Nu există rotunjire a scorului înainte de comparație. 20,000001 nu este nivel brut 1. Termenul de incertitudine folosește Confidence Base, nu Confidence Final. Cota și EV nu intervin nici aici, nici în ranking.

### 4.2 Tail Gate

Mai întâi: meci inexistent → gol; Release≠READY → NOT RELEASED; G0 sau parametri linie invalizi → INVALID.

Pentru O3,5 există mereu o bandă pilot aplicabilă. Dacă linia este Tail_Validated, are aceeași Scope_League și Review_UTC numeric ≤ Cutoff_UTC, se folosesc E/F din Calibrare_Linii. Altfel se folosesc Config B26/C26 = 0,05/0,08.

```text
failure <= pass_max: PASS
pass_max < failure <= watch_max: PENALTY
failure > watch_max: WATCH
```

Pentru celelalte 13 linii, lipsa unei validări tail aplicabile produce OOS PENDING, fără împrumutarea pragurilor O3,5. Dacă validarea este aplicabilă, se folosesc exact pragurile proprii E/F.

Formula originală `Analiza_Linii!W6`:

```excel
=IF(B6="","",IF(I6<>"READY","NOT RELEASED",IF(NOT(AND(J6="PASS",'Calibrare_Linii'!U6="VALID")),"INVALID",IF(NOT(TRUE),"OOS PENDING",IF(S6<=IF(AND('Calibrare_Linii'!S6="VALIDATED",AND('Calibrare_Linii'!H6=C6,ISNUMBER('Calibrare_Linii'!J6),'Calibrare_Linii'!J6<='Input_Meci'!G6)),'Calibrare_Linii'!E6,'Config_v6'!$B$26),"PASS",IF(S6<=IF(AND('Calibrare_Linii'!S6="VALIDATED",AND('Calibrare_Linii'!H6=C6,ISNUMBER('Calibrare_Linii'!J6),'Calibrare_Linii'!J6<='Input_Meci'!G6)),'Calibrare_Linii'!F6,'Config_v6'!$C$26),"PENALTY","WATCH"))))))
```

Formula originală `Analiza_Linii!W7`:

```excel
=IF(B7="","",IF(I7<>"READY","NOT RELEASED",IF(NOT(AND(J7="PASS",'Calibrare_Linii'!U7="VALID")),"INVALID",IF(NOT(AND('Calibrare_Linii'!S7="VALIDATED",AND('Calibrare_Linii'!H7=C7,ISNUMBER('Calibrare_Linii'!J7),'Calibrare_Linii'!J7<='Input_Meci'!G6))),"OOS PENDING",IF(S7<='Calibrare_Linii'!E7,"PASS",IF(S7<='Calibrare_Linii'!F7,"PENALTY","WATCH"))))))
```

O3,5 poate avea Tail_Gate=PASS și OOS_Status=OOS PENDING simultan. Prima stare descrie trecerea benzii pilot; a doua descrie absența validării independente. Penalizarea de 10 puncte este legată de Tail_Gate, nu de OOS_Status.

### 4.3 Confidence Final și Candidate Confidence

```text
dispersion_penalty = 10 if D>1.70 else 5 if D>1.35 else 0
Confidence_Final = max(0, Confidence_Base
                         - (10 if Tail_Gate==OOS PENDING else 0)
                         - dispersion_penalty)
Candidate_Confidence = max(0,Confidence_Base-dispersion_penalty)
```

Formula originală `Analiza_Linii!V6`:

```excel
=IF(M6="","",MAX(0,'Motor_Meciuri'!BF6-IF(W6="OOS PENDING",'Config_v6'!$B$35,0)-IF(L6>'Config_v6'!$B$12,'Config_v6'!$B$37,IF(L6>'Config_v6'!$B$11,'Config_v6'!$B$36,0))))
```

Formula originală `Analiza_Linii!AN6`:

```excel
=IF(M6="","",MAX(0,'Motor_Meciuri'!BF6-IF(L6>'Config_v6'!$B$12,'Config_v6'!$B$37,IF(L6>'Config_v6'!$B$11,'Config_v6'!$B$36,0))))
```

Nu se scad simultan 5 și 10 puncte de dispersie. Candidate Confidence omite exclusiv penalizarea OOS; nu promovează singură selecția.

### 4.4 Defensive Candidate și Defensive Gate

Candidate cere simultan:

1. G0 PASS și parametrii liniei valizi.
2. Core_Native_Count=12 și Core_Effective_Count=12.
3. Prior_Active=NO și Dispersion_Season=Season.
4. P_FINAL≥0,90; Candidate_Confidence≥90; Risk_Score≤20; D≤1,10.
5. PASS_Max propriu numeric și Failure_Gate≤PASS_Max.
6. Suma N empirice HA+L10+L20>0.

Formula originală `Analiza_Linii!X6`:

```excel
=IF(M6="","",IF(AND(AND(J6="PASS",'Calibrare_Linii'!U6="VALID"),'Motor_Meciuri'!K6=12,'Motor_Meciuri'!L6=12,'Motor_Meciuri'!M6="NO",'Motor_Meciuri'!BL6='Motor_Meciuri'!C6,AB6>='Config_v6'!$B$50,AN6>='Config_v6'!$B$51,T6<='Config_v6'!$B$52,L6<='Config_v6'!$B$53,ISNUMBER('Calibrare_Linii'!E6),S6<='Calibrare_Linii'!E6,SUM(AK6:AM6)>0),"CANDIDATE","NO"))
```

În fișierul livrat, E este gol pentru celelalte 13 linii, deci ele nu pot deveni CANDIDATE cu configurația nemodificată. Candidate nu înlocuiește pragurile lipsă cu zero.

Defensive Gate PASS cere în plus Candidate, Confidence Final≥90, Tail_Gate=PASS, `Calibrare_Linii!T=VALIDATED`, aceeași ligă și Review_UTC≤cutoff. Un candidat fără această închidere are Defensive_Gate=OOS PENDING; o selecție care nu este candidat are FAIL. NOT RELEASED se păstrează separat.

Formula originală `Analiza_Linii!Y6`:

```excel
=IF(B6="","",IF(I6<>"READY","NOT RELEASED",IF(AND(X6="CANDIDATE",V6>='Config_v6'!$B$51,W6="PASS",'Calibrare_Linii'!T6="VALIDATED",AND('Calibrare_Linii'!H6=C6,ISNUMBER('Calibrare_Linii'!J6),'Calibrare_Linii'!J6<='Input_Meci'!G6)),"PASS",IF(X6="CANDIDATE","OOS PENDING","FAIL"))))
```

V14 introduce această excepție la floor-ul 2 descris de Cadrul v5. Excepția este explicit documentată în `Documentatie!B30` și executată de formule. Pentru reproducerea V14 nu se reintroduce un floor 2 necondiționat și nici nu se acordă Level 1 doar fiindcă scorul brut este mic.

### 4.5 Validarea OOS

`OOS_Predictii!A:S` sunt valori înghețate/importate; T/U sunt formule. Registrul livrat este gol. `Record_Valid=1` cere:

- Fixture_ID prezent, ligă prezentă, linie recunoscută exact o dată în Calibrare_Linii și unicitate Fixture_ID+Line în întreg registrul. Unicitatea nu include liga sau semnătura; nu relaxa cheia fără decizie de metodologie.
- Training_End_UTC < Snapshot_UTC < Kickoff_UTC, toate numerice.
- P_Final în [0,90;1], Candidate_Confidence în [90;100], D în [0;1,10], Risk_Score în [0;20].
- Prior_Active=NO, Native_Core_Count=12, Candidate_Tail=PASS.
- Total_Corners întreg ≥0, Outcome_URL ne-gol, Settled_UTC>Kickoff_UTC, Frozen_Evidence_URL ne-gol, Model_Signature ne-gol și Mode=LIVE.

Formula originală `OOS_Predictii!T6`:

```excel
=IF(A6="",0,IFERROR(IF(AND(B6<>"",COUNTIF('Calibrare_Linii'!$A$6:$A$19,C6)=1,COUNTIFS(OOSTable[Fixture_ID],A6,OOSTable[Line],C6)=1,ISNUMBER(D6),ISNUMBER(E6),ISNUMBER(F6),F6<D6,D6<E6,ISNUMBER(G6),G6>='Config_v6'!$B$50,G6<=1,ISNUMBER(H6),H6>='Config_v6'!$B$51,H6<=100,ISNUMBER(I6),I6>=0,I6<='Config_v6'!$B$53,ISNUMBER(J6),J6>=0,J6<='Config_v6'!$B$52,K6="NO",L6=12,M6="PASS",ISNUMBER(N6),N6>=0,MOD(N6,1)=0,O6<>"",ISNUMBER(P6),P6>E6,Q6<>"",R6<>"",S6="LIVE"),1,0),0))
```

Win se calculează numai pentru Record_Valid=1: Over câștigă la Total>k; Under la Total≤k. Prefixul liniei este citit cu LEFT; pragul k se caută în Calibrare_Linii.

Agregarea pe linie include numai Record_Valid=1, aceeași Line, Scope_League și Model_Signature, Settled_UTC≤Review_UTC, Snapshot_UTC>Training_End_UTC al calibrării și Training_End_UTC identic cu cel al calibrării. Datele de training și review trebuie să fie numerice ca să se calculeze N.

```text
N = count(records matching all criteria)
Wins = sum(Win)
hit_rate = Wins/N
mean_probability = SUM(P_Final)/N
overconfidence = MAX(0,mean_probability-hit_rate)
z = 1.96
wilson_lower = (
    hit_rate + z*z/(2*N)
    - z*SQRT(hit_rate*(1-hit_rate)/N + z*z/(4*N*N))
) / (1+z*z/N)
```

Formula originală `Calibrare_Linii!Q6`:

```excel
=IF(M6=0,"",(O6+1.96^2/(2*M6)-1.96*SQRT(O6*(1-O6)/M6+1.96^2/(4*M6^2)))/(1+1.96^2/M6))
```

Tail_Validated devine VALIDATED numai pentru APPROVED, training<review, raport și evaluator prezenți, ligă prezentă, Parameters_Valid, ambele praguri numerice și N≥200. Defensive_Validated cere suplimentar Wilson lower≥0,90 și overconfidence≤0,05. `Record_Valid` cere doar semnătură ne-goală; egalitatea cu semnătura curentă se verifică în agregare.

Formula originală `Calibrare_Linii!S6`:

```excel
=IF(AND(G6="APPROVED",ISNUMBER(I6),ISNUMBER(J6),I6<J6,K6<>"",L6<>"",H6<>"",U6="VALID",ISNUMBER(E6),ISNUMBER(F6),M6>='Config_v6'!$B$56),"VALIDATED","PENDING")
```

Formula originală `Calibrare_Linii!T6`:

```excel
=IF(AND(S6="VALIDATED",Q6>='Config_v6'!$B$57,R6<='Config_v6'!$B$58),"VALIDATED","PENDING")
```

Unicitatea și URL-urile ne-goale nu demonstrează autenticitatea arhivei. Formula aplică verificările enumerate; revizuirea externă a dovezilor rămâne distinctă. Nu se fabrică 200 observații din exemplele REPLAY și nu se numără cele 14 linii ale aceluiași meci drept 14 meciuri independente pentru aceeași linie.

Capacitatea curentă de 250 rânduri OOS permite stocarea a 250 înregistrări linie–meci în total. Validarea simultană a 14 linii la minimum 200 de înregistrări/linie ar necesita minimum 2.800 rânduri, peste capacitatea existentă. Aceasta este o limită de volum a workbook-ului, nu motiv pentru scăderea pragului de validare.

### 4.6 Nivelul final și verdictul

```text
if match absent: level=EMPTY
elif release != READY: level=EMPTY
elif invalid(G0 or line_config) or D>2.25 or tail==WATCH: level=5
elif defensive_gate==PASS: level=1
else: level=min(5,max(2,raw_level)+(1 if tail==PENALTY else 0))

if match absent: verdict=EMPTY
elif release!=READY: verdict=NOT RELEASED
elif level==5: verdict=NO BET
elif P_FINAL<0.72 or Confidence_Final<65: verdict=WATCH
else: verdict=label(level) # DEFENSIV / PRUDENT / MODERAT / RIDICAT
```

Formula originală `Analiza_Linii!Z6`:

```excel
=IF(B6="","",IF(I6<>"READY","",IF(OR(NOT(AND(J6="PASS",'Calibrare_Linii'!U6="VALID")),L6>'Config_v6'!$B$13,W6="WATCH"),5,IF(Y6="PASS",1,MIN(5,MAX('Config_v6'!$B$42,U6)+IF(W6="PENALTY",1,0))))))
```

Formula originală `Analiza_Linii!AA6`:

```excel
=IF(B6="","",IF(I6<>"READY","NOT RELEASED",IF(Z6=5,"NO BET",IF(OR(AB6<'Config_v6'!$B$16,V6<'Config_v6'!$B$18),"WATCH",IF(Z6=1,"DEFENSIV",IF(Z6=2,"PRUDENT",IF(Z6=3,"MODERAT","RIDICAT")))))))
```

Distincții obligatorii pentru UI și teste:

| Situație | P_FINAL | Risk_Level_FINAL | Verdict |
|---|---|---|---|
| NOT RELEASED | gol | gol | NOT RELEASED |
| READY cu G0 FAIL | gol | 5 | NO BET |
| G0 PASS, D>2,25 | poate rămâne calculată | 5 | NO BET |
| G0 PASS, P<72% sau Confidence<65 | calculată | poate fi 2/3/4 | WATCH |
| Eligibil, fără gate defensiv | calculată | minimum 2 | PRUDENT/MODERAT/RIDICAT |
| Gate defensiv PASS | calculată | 1 | DEFENSIV |

Nu deriva automat verdictul din nivel și nu transforma orice WATCH în nivel 5. Pragurile de eligibilitate sunt inclusive: P=0,72 și Confidence=65 trec.

### 4.7 Selectorul și Builder

Eligible=1 numai pentru DEFENSIV, PRUDENT, MODERAT sau RIDICAT. Se sortează numai selecțiile eligibile ale aceluiași meci după:

```text
(Risk_Level_FINAL ascending,
 P_FINAL descending,
 Confidence_Final descending,
 physical line order ascending)
```

Nu există Risk Score ca tie-break suplimentar și nu se folosesc cote sau EV. Comparațiile sunt pe valori numerice ne-rotunjite; două valori afișate identic nu sunt obligatoriu egalități de ranking.

Formula originală `Analiza_Linii!AC6`:

```excel
=IF(AD6<>1,"",COUNTIFS($Z$6:$Z$19,"<"&Z6,$AD$6:$AD$19,1)+COUNTIFS($Z$6:$Z$19,Z6,$AB$6:$AB$19,">"&AB6,$AD$6:$AD$19,1)+COUNTIFS($Z$6:$Z$19,Z6,$AB$6:$AB$19,AB6,$V$6:$V$19,">"&V6,$AD$6:$AD$19,1)+COUNTIFS($Z$6:Z6,Z6,$AB$6:AB6,AB6,$V$6:V6,V6,$AD$6:AD6,1))
```

Builder este YES pentru eligibil + tail PASS, CONDITIONAL pentru eligibil + OOS PENDING, altfel NO. Prin urmare o selecție cu PENALTY poate rămâne eligibilă și poate fi selectată în Dashboard, dar Builder=NO.

Dashboard caută Rank_In_Match=1 și prezintă o singură linie. Dacă nu există linie eligibilă, Index linie=0, linia și P rămân goale; verdictul agregat este NO BET când G0=FAIL, altfel WATCH / NO BET. Acest verdict agregat nu se copiază peste verdictele individuale.

Pentru Top LIVE sunt eligibile doar selecțiile unice ale meciurilor LIVE. Ranking-ul global folosește aceleași trei criterii numerice și, la egalitate completă, ordinea meciurilor în Input_Meci. Dashboard afișează primele zece ranguri. REPLAY poate avea linie selectată în blocul inferior, dar nu apare în Top LIVE.

Formula originală `Dashboard!P26`:

```excel
=IF(O26<>1,"",COUNTIFS($O$26:$O$125,1,$L$26:$L$125,"<"&L26)+COUNTIFS($O$26:$O$125,1,$L$26:$L$125,L26,$H$26:$H$125,">"&H26)+COUNTIFS($O$26:$O$125,1,$L$26:$L$125,L26,$H$26:$H$125,H26,$M$26:$M$125,">"&M26)+COUNTIFS($O$26:O26,1,$L$26:L26,L26,$H$26:H26,H26,$M$26:M26,M26))
```

### 4.8 Semantica Excel care trebuie păstrată

- Blank literal, șirul gol întors de formulă, zero numeric și eroare Excel sunt stări distincte. Cache-ul citit de openpyxl poate reprezenta șirul gol ca None; formula originală rămâne dovada stării.
- ISNUMBER nu trebuie să accepte automat text numeric și nici bool Python ca număr. Nu transforma global null/-1/-2 în zero.
- SUM/COUNT/AVERAGE/MAX pe referințe urmează semantica Excel pentru text/gol. AVERAGE în lambda primește două valori numerice fiindcă G0 a trecut; nu se face skip pentru o medie efectivă lipsă.
- COUNTIFS combină condițiile prin AND; expresiile SUMPRODUCT cu sumă `>0` formează OR fără dublare. Criteriul `"*"` din Problem_Rows este criteriu text, nu expresie numerică.
- INDEX și MATCH folosesc indexare de la 1. MATCH(...,0) este exact și întoarce prima potrivire; validările de unicitate sunt separate.
- ROUND(...,0) apare în Confidence Base. Nu există ROUND pe probabilități, scor sau medii. Formatele procentuale și zecimalele afișate nu alterează valoarea calculată.
- TEXT cu șase zecimale produce șirul semnăturii. Separatoarele și formatarea trebuie verificate în mediul țintă, nu schimbate prin localizare arbitrară.
- Recurențele PMF sunt evaluate în ordinea n=0…18; cumulările CDF păstrează ordinea termenilor. Nu folosi rezultate deja rotunjite pentru etapele următoare.
- Pragurile se compară exact, fără epsilon introdus în decizia de business. Toleranța este numai pentru teste numerice.

Inventarul funcțiilor existente efectiv: `ABS`, `AND`, `AVERAGE`, `COUNT`, `COUNTA`, `COUNTIF`, `COUNTIFS`, `EXP`, `IF`, `IFERROR`, `INDEX`, `INT`, `ISNUMBER`, `LARGE`, `LEFT`, `MATCH`, `MAX`, `MIN`, `MOD`, `NOT`, `OR`, `ROUND`, `ROWS`, `SQRT`, `SUM`, `SUMIFS`, `SUMPRODUCT`, `TEXT`, `_xlfn._xlws.FILTER`. FILTER este stocat în OOXML cu prefixul `_xlfn._xlws.FILTER`. Nu există în acest model un algoritm ML, un ajusteazător de cotă, de-vig sau un proces de antrenare automat ascuns în Excel.

## 5 Corespondența rezultatelor și testarea

### 5.1 Ce s-a executat și ce nu

Au fost efectuate trei verificări distincte:

1. Extracție read-only a formulelor și a valorilor cached din fișierul original. Cache-ul este etichetat ca valoare salvată, nu declarat recalculare.
2. Recalculare a unei copii prin LibreOffice headless. Au fost comparate 5.495 celule cu formule din exemple, istoric populat, configurare, OOS gol și controale. Diferența numerică maximă observată a fost `4.973799150320701e-14`. Există șase diferențe text auxiliare, explicate mai jos; nu afirm identitate textuală integrală a workbook-ului.
3. Recalculare independentă Python din cele 380 rânduri brute furnizate. Harness-ul a reconstruit Core, N, varianță, Poisson/NB și 42 selecții. Cele 1.428 comparații de câmpuri ale selecțiilor au trecut la toleranța definită. Diferența numerică maximă observată față de cache a fost `7.105427357601002e-15`.

Nu a fost executat Microsoft Excel. Nu au fost testate toate combinațiile LIVE/prior/context/OOS. Nu au fost rulate testele aplicației PontifyBet. Nu am redescărcat sursa sportivă: rezultatele provin exclusiv din datele atașate, a căror autenticitate istorică nu este certificată independent prin acest manual.

### 5.2 Fixture-ul principal Brighton contra Manchester United

Input `Input_Meci!A6:AG6`:

| Câmp | Valoare |
|---|---|
| Match_ID | REPLAY_1 |
| League / Season | E0 / 2025/26 |
| Home / Away | Brighton / Man United |
| Kickoff_UTC | 2026-05-24 00:00:00 |
| Cutoff_UTC | 2026-05-23 23:00:00 |
| Mode / Sourcing_Decision | REPLAY / AUTO |
| Prior_Allowed / Prior_Season | NO / gol |
| Evidence_or_Attempts | gol |
| N:AG | toate goale |

Sursa din `Surse_Import!A6:L6`: ID `FD_E0_2526`, Football-Data, E0, sezon 2025/26, `FULL SEASON EXPORT`, `IMPORTED`, Rows=380, Missing_Corners=0, Retrieved_UTC=`2026-09-13 16:52:25`. SHA256 declarat în Excel: `3e3a8352f9ada6789c508d6ca184424421fed56a30400904a4a327c583407e62`. Notes descrie un exemplu retrospectiv cu cutoff convențional.

Cele 380 rânduri brute și toate inputurile celor trei exemple se află în `fixture_input_original.json`. Ele sunt necesare pentru reproducere end-to-end; introducerea exclusivă a celor 12 medii nu reproduce distribuția și failure gates.

| Coordonate | Fereastră | N | Corners For | Corners Against |
| --- | --- | --- | --- | --- |
| Core_Nativ!M6:O6 | Gazde sezon | 37 | 5 | 4.864864864864865 |
| Core_Nativ!M7:O7 | Gazde acasă | 18 | 5.222222222222222 | 4.611111111111111 |
| Core_Nativ!M8:O8 | Gazde recent | 5 | 7.2 | 4.4 |
| Core_Nativ!M9:O9 | Oaspeți sezon | 37 | 4.837837837837838 | 5.027027027027027 |
| Core_Nativ!M10:O10 | Oaspeți deplasare | 18 | 4.388888888888889 | 5.611111111111111 |
| Core_Nativ!M11:O11 | Oaspeți recent | 5 | 5.2 | 6 |

Intermediarii principali sunt:

| Celulă | Câmp | Valoare salvată |
| --- | --- | --- |
| Motor_Meciuri!AR6 | N_Dispersion | 73 |
| Motor_Meciuri!AS6 | Mean_Total_History | 9.904109589041095 |
| Motor_Meciuri!AT6 | Variance_Total_History | 8.92123287671235 |
| Motor_Meciuri!AU6 | D | 0.9007607192254518 |
| Motor_Meciuri!AV6 | Distribution | 'POISSON' |
| Motor_Meciuri!AW6 | NB_Size | 9999 |
| Motor_Meciuri!BB6 | Lambda_H | 5.591554054054054 |
| Motor_Meciuri!BC6 | Lambda_A | 4.680405405405406 |
| Motor_Meciuri!BD6 | Mu | 10.27195945945946 |
| Motor_Meciuri!BF6 | Confidence_Base | 90 |
| Motor_Meciuri!BG6 | Calibration_Strength | 0.7995 |

Release=READY, G0=PASS, Native Core=12, Effective Core=12, Prior_Active=NO, Soft_H/A=1, Context_H/A=1, Soft_Missing=10 și Sensitivity=0. N empiric HA=36, L10=20, L20=40. Cele 37 meciuri ale fiecărei echipe formează 73 observații unice pentru dispersie; un meci direct este numărat o dată.

### 5.3 Rezultatele așteptate pentru toate cele 14 linii

Tabelul următor arată probabilități ca fracții 0–1 cu 15 zecimale și scor cu 12 zecimale pentru lizibilitate. Fișierele JSON/CSV conțin valorile numerice salvate fără această rotunjire de prezentare. Rezultatele au fost confirmate prin recalculare în toleranță.

| Linie | Praw | P_FINAL | Risk Score | Confidence | Tail Gate | Nivel final | Verdict | Rang |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| O3,5 | 0.991537105865165 | 0.892983916139200 | 9.972221126087 | 90 | PASS | 2 | PRUDENT | 1 |
| O4,5 | 0.975491850498016 | 0.880155734473164 | 10.854710171280 | 80 | OOS PENDING | 2 | PRUDENT | 3 |
| O5,5 | 0.942528607968409 | 0.853801622070743 | 12.667688510408 | 80 | OOS PENDING | 2 | PRUDENT | 5 |
| O6,5 | 0.886095759482334 | 0.808683559706126 | 15.771495177142 | 80 | OOS PENDING | 2 | PRUDENT | 7 |
| O7,5 | 0.803284912077937 | 0.742476287206310 | 23.256761948671 | 80 | OOS PENDING | 2 | PRUDENT | 10 |
| O8,5 | 0.696956203660255 | 0.527777777777778 | 35.478984170893 | 80 | OOS PENDING | 2 | WATCH | gol |
| U10,5 | 0.549056228605127 | 0.450000000000000 | 39.756761948671 | 80 | OOS PENDING | 2 | WATCH | gol |
| U11,5 | 0.665462193204359 | 0.500000000000000 | 37.006761948671 | 80 | OOS PENDING | 2 | WATCH | gol |
| U12,5 | 0.765105305637907 | 0.700000000000000 | 26.006761948671 | 80 | OOS PENDING | 2 | WATCH | gol |
| U13,5 | 0.843838383432658 | 0.750000000000000 | 23.256761948671 | 80 | OOS PENDING | 2 | PRUDENT | 9 |
| U14,5 | 0.901605739377384 | 0.800000000000000 | 20.506761948671 | 80 | OOS PENDING | 2 | PRUDENT | 8 |
| U15,5 | 0.941164668600342 | 0.852711152545974 | 12.742705175652 | 80 | OOS PENDING | 2 | PRUDENT | 6 |
| U16,5 | 0.966561400927708 | 0.873015840041703 | 11.345884897647 | 80 | OOS PENDING | 2 | PRUDENT | 4 |
| U17,5 | 0.981906942390617 | 0.885284600441298 | 10.501880117187 | 80 | OOS PENDING | 2 | PRUDENT | 2 |

Toate liniile au Defensive_Candidate=NO, Defensive_Gate=FAIL și OOS_Status=OOS PENDING. Pentru O3,5 tail=PASS, Confidence Final=90 și Builder=YES. Pentru liniile eligibile rămase, tail=OOS PENDING, Confidence Final=80 și Builder=CONDITIONAL. Liniile WATCH au Builder=NO și nu primesc Rank_In_Match.

Exemplu numeric complet O3,5:

```text
Praw = 1-CDF_3 = 0.9915371058651653
Pcal = 0.5+(Praw-0.5)*0.7995 = 0.8929839161391997
Failure_Model = 0.008462894134834698
Empirical_HA = 0 / 36 = 0
Empirical_L10 = 0 / 20 = 0
Empirical_L20 = 0 / 40 = 0
Failure_Gate = 0.008462894134834698
P_FINAL = min(0.8929839161391997, 1-Failure_Gate)
        = 0.8929839161391997
Risk_Score = 9.972221126086591
Risk_Level_Raw = 1
Tail_Gate = PASS  # banda pilot, nu validare OOS
Confidence_Final = 90
Defensive_Candidate = NO  # P_FINAL < 0.90
Risk_Level_FINAL = 2
Verdict_FINAL = PRUDENT
Rank_In_Match = 1
```

Selecția Dashboard pentru REPLAY_1 este O3,5 / PRUDENT. Nu intră în Top LIVE, deoarece Mode=REPLAY. Pentru celelalte două exemple, selecția este U17,5 / PRUDENT; toate cele 42 linii sunt în `expected_42_selectii.csv` și JSON.

Al treilea exemplu, Crystal Palace–Arsenal, acoperă NB: D=`1.3207885304659515`, size=`29.12344072855269`, Mu=`9.505743243243243`. Astfel verificarea independentă nu este limitată la o singură distribuție.

### 5.4 Limitele recalculării și diferențele constatate

În LibreOffice au apărut 194 erori `#VALUE!`, exact în `Motor_Meciuri!AS9:AT105`, rândurile fără Match_ID. AR întoarce `""` pentru sloturile goale; formulele AS/AT testează AR numeric și ajung la expresii care nu sunt protejate direct prin Match_ID. Cache-ul original este gol în aceste celule. Nu afirm că Microsoft Excel produce aceeași eroare: nu a fost executat. Formula și diferența trebuie păstrate ca observație de compatibilitate, fără o remediere metodologică implicită.

Există șase diferențe de text în Trace pentru ferestrele RECENT ale priorului neutilizat: `Core_Nativ!U14`, `U17`, `U26`, `U29`, `U38`, `U41`. `TEXT(0,"yyyy-mm-dd")` este salvat în original ca `1900-01-00`, iar LibreOffice produce `1899-12-30`. Aceste texte nu alimentează probabilitățile, scorurile sau verdictele. Dacă se cere egalitate textuală integrală a unui export, trebuie aleasă și testată explicit semantica Excel pentru serialul zero; diferența nu poate fi ascunsă într-o toleranță numerică.

Pentru sloturile nepopulate, contractul aplicației este să nu creeze obiect de analiză. Aceasta păstrează ieșirea funcțională a modelului; nu reprezintă o certificare de egalitate a fiecărei celule auxiliare cu un anumit spreadsheet engine.

Fișierul sursă nu a fost suprascris. Copia recalculată nu este livrată ca versiune nouă V14 și nu înlocuiește originalul.

### 5.5 Toleranțe și câmpuri exacte

Pentru teste de paritate se propune:

```text
abs(actual-expected) <= max(1e-10, 1e-12*abs(expected))
```

Aceasta este toleranța de validare software a numerelor în virgulă mobilă, nu un prag nou de model. Nu o utiliza pentru a relaxa P≥0,72, P≥0,90, D≤1,10 sau alte gates.

Câmpurile care trebuie să coincidă exact: ID-uri, ligă, echipe, mod, cod/ordine linie, Type, k, N/count-uri, release, G0, toate stările/gates, nivelurile, verdictul, Eligible, Builder, rangurile, motivele, semnăturile și prezența/absența fiecărui rezultat. Datele se compară după serialul UTC/normalizarea definită, păstrând cutoff-ul pe zi pentru istoric.

Confidence Base este întreg în configurația curentă și trebuie să coincidă exact. Confidence Final/Candidate au de asemenea valori întregi în fixture-uri; nu introduce conversie la int care ar altera eventuale penalizări fracționare permise de configurație.

La cazurile de frontieră, egalitatea numerică în toleranță nu este suficientă dacă schimbă clasa sau ranking-ul. Un verdict diferit este FAIL chiar dacă diferența probabilității este 1e-12. Testele de frontieră trebuie să valideze operatorii inclusivi/exclusivi exact.

### 5.6 Contractul testelor unitare și de integrare

| Test | Intrare sau variație controlată | Rezultat cerut | Executat în acest pachet |
|---|---|---|---|
| Fixture Poisson | REPLAY_1 și REPLAY_2 originale | paritate pe toate cele 28 selecții | Da |
| Fixture NB | REPLAY_3 original | paritate pe toate cele 14 selecții | Da |
| Native întregi | HC/AC zero versus -1/-2/null/text/fracție | zero valid; celelalte conform Row_State, fără imputare | Nu; specificat |
| Dubluri | aceeași cheie și aceleași HC/AC | primul valid, restul DUPLICATE, N neschimbat | Nu; specificat |
| Conflict | aceeași cheie cu alt HC sau AC | SOURCE CONFLICT și flux de release corespunzător | Nu; specificat |
| Cutoff de zi | eveniment în aceeași zi ca cutoff | exclus, chiar dacă ora este anterioară | Aplicat fixture-urilor; variație sintetică nerulată |
| Import LIVE | Retrieved>cutoff / =cutoff | POST CUTOFF numai pentru > | Nu; specificat |
| Sourcing terminal | NOT AVAILABLE fără/cu evidence | NOT RELEASED / READY cu G0 FAIL | Nu; specificat |
| Prior | sample sub țintă, prior valid/invalid | blend exact / valoare efectivă goală; cap 75 | Nu; specificat |
| Recent cu egalități | mai multe evenimente la data-prag | toate datele ≥ prag incluse | Nu; specificat |
| Soft versus context | soft invalid / context invalid | neutru+penalizare / G0 invalid după release | Nu; specificat |
| Posesie | doar T/U trec din gol în valid | lambda neschimbat; Soft_Missing și Confidence se pot schimba | Nu; specificat |
| Distribuție | D exact 1,10 și imediat peste | Poisson / NB; size din mean_history | Nu; specificat |
| Dispersie hard | D=2,25 și imediat peste | hard override numai pentru > | Nu; specificat |
| Score boundaries | 20/40/60/80 și imediat peste | clase conform <=, fără ROUND(score) | Nu; specificat |
| Eligibilitate | P=0,72; Confidence=65 | trec dacă restul gates permit | Nu; specificat |
| Pilot | failure=0,05; 0,08; >0,08 | PASS / PENALTY / WATCH | Nu; specificat |
| OOS pending | linie fără prag validat | −10 Confidence; nu hard fail automat | Da, 39 selecții |
| WATCH cu nivel 2 | P insuficient în REPLAY_1 | WATCH, nivelul rămâne 2, fără rang | Da |
| OOS invalid | duplicat, snapshot post-kickoff, semnătură diferită | excludere conform T și agregării | Nu; specificat |
| Defensive Gate | toate condițiile plus/minus OOS | nivel 1 numai pentru gate PASS | Nu; specificat |
| Tie-break | nivel/P/Confidence egale | ordinea liniilor; global ordinea meciurilor | Nu; specificat |
| REPLAY versus LIVE | fixture-uri REPLAY originale | Top LIVE gol | Da |

Testele cu variații nu trebuie să inventeze observații sportive și apoi să le prezinte ca meciuri reale. Pentru validarea ramurilor se pot folosi fixture-uri sintetice explicit etichetate, iar rezultatele așteptate trebuie obținute prin formulele originale, fără ajustarea pragurilor pentru PASS.

### 5.7 Rularea harness-ului și folosirea anexelor

```bash
python verifica_replay.py
```

Comanda se rulează în folderul extras din ZIP. Scriptul folosește biblioteca standard, citește fixture-ul și configurația și scrie `rezultate_replay_recalculate.json`. Nu are nevoie de API, GitHub sau Excel și nu modifică workbook-ul ori repository-ul. Scriptul are guard-uri explicite pentru scope: trei exemple REPLAY, fără prior, fără soft/context populat, fără validare OOS aprobată. Nu trebuie prezentat drept implementare completă a V14.

| Fișier | Utilizare |
|---|---|
| Manual_tehnic_Cornere_Multiline_V14.md | specificația explicată și contractele de implementare |
| Anexa_schema_si_formule.md | schema tuturor foilor și formule reprezentative cu dependențe |
| formule_integrale.csv | toate cele 85.647 formule originale, la coordonatele lor |
| celule_integrale.json | formule, literali, cache, format și dependențe pentru toate celulele ne-goale |
| schema_coloane.json / .csv | mapping programatic pentru toate coloanele cu antet |
| tabele_excel.json | rezolvarea exactă a referințelor structurate |
| configuratie_exacta.json | valorile și formulele configurației globale |
| validari_input.json | validările Excel existente; nu înlocuiesc validarea din formule |
| fixture_input_original.json | inputurile brute originale ale celor trei exemple |
| expected_42_selectii_cache.json / .csv | outputurile saved-cache, validate în scope-ul declarat |
| verifica_replay.py | recalculare independentă limitată la fixture-urile livrate |
| rezultate_replay_recalculate.json | rezultate Python, intermediari și raportul celor 1.428 comparații |
| comparatie_cache_libreoffice.json | comparațiile individuale din recalcularea spreadsheet |
| raport_recalculare.json | diferențele text, erorile auxiliare și statisticile verificării |
| manifest_sursa.json | fingerprint workbook, commit GitHub, inventar și funcții |

Pentru acceptarea unei implementări complete în aplicație, agentul trebuie să demonstreze atât paritatea celor 42 selecții, cât și comportamentul ramurilor neacoperite de exemplu. Trebuie păstrate un singur motor oficial, separat de export, trasabilitatea inputurilor și stările distincte de release/risc. Acest document nu declară integrarea finalizată și nu autorizează schimbarea modelului pentru a face testele să treacă.
