# Anexa tehnică V14

Schema este extrasă din fișierul original. Tipurile sunt contracte semantice deduse din formule, nu tipuri declarate de Excel. Celulele cu formule pot întoarce șirul gol. În JSON, cache-ul Excel gol este null; nu înseamnă zero.

Formulele integrale, inclusiv toate variațiile de rând, sunt în formule_integrale.csv și celule_integrale.json. Referințele fără nume de foaie sunt locale. Referințele Table[Coloană] se rezolvă exact prin tabele_excel.json.

## Dashboard

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
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

### Dashboard!B4

```excel
=COUNTA('Input_Meci'!A6:A105)
```

Dependențe directe: `'Input_Meci'!A6:A105`.

Cache original: `3`. Format afișare: `General`.


### Dashboard!E4

```excel
=COUNTIFS(MotorTable[Mode],"LIVE",MotorTable[G0],"PASS")
```

Dependențe directe: `MotorTable[Mode]`; `MotorTable[G0]`.

Cache original: `0`. Format afișare: `General`.


### Dashboard!H4

```excel
=COUNTIF(MotorTable[Release],"NOT RELEASED")
```

Dependențe directe: `MotorTable[Release]`.

Cache original: `0`. Format afișare: `General`.


### Dashboard!B6

```excel
=COUNTIF(MotorTable[Mode],"REPLAY")
```

Dependențe directe: `MotorTable[Mode]`.

Cache original: `3`. Format afișare: `General`.


### Dashboard!E6

```excel
=COUNTIF(LinesTable[Live_Eligible_Best],1)
```

Dependențe directe: `LinesTable[Live_Eligible_Best]`.

Cache original: `0`. Format afișare: `General`.


### Dashboard!H6

```excel
=COUNTIFS(LinesTable[Verdict_FINAL],"DEFENSIV",LinesTable[Mode],"LIVE")
```

Dependențe directe: `LinesTable[Verdict_FINAL]`; `LinesTable[Mode]`.

Cache original: `0`. Format afișare: `General`.


### Dashboard!A11

```excel
=IF(IFERROR(MATCH(1,$P$26:$P$125,0),0)=0,"",1)
```

Dependențe directe: `$P$26:$P$125`.

Cache original: `None`. Format afișare: `General`.


### Dashboard!B11

```excel
=IF(A11="","",INDEX($B$26:$B$125,MATCH(A11,$P$26:$P$125,0)))
```

Dependențe directe: `A11`; `$B$26:$B$125`; `$P$26:$P$125`.

Cache original: `None`. Format afișare: `General`.


### Dashboard!C11

```excel
=IF(A11="","",INDEX($F$26:$F$125,MATCH(A11,$P$26:$P$125,0)))
```

Dependențe directe: `A11`; `$F$26:$F$125`; `$P$26:$P$125`.

Cache original: `None`. Format afișare: `General`.


### Dashboard!D11

```excel
=IF(A11="","",INDEX($H$26:$H$125,MATCH(A11,$P$26:$P$125,0)))
```

Dependențe directe: `A11`; `$H$26:$H$125`; `$P$26:$P$125`.

Cache original: `None`. Format afișare: `0.0%`.


### Dashboard!E11

```excel
=IF(A11="","",INDEX($L$26:$L$125,MATCH(A11,$P$26:$P$125,0)))
```

Dependențe directe: `A11`; `$L$26:$L$125`; `$P$26:$P$125`.

Cache original: `None`. Format afișare: `General`.


### Dashboard!F11

```excel
=IF(A11="","",INDEX($G$26:$G$125,MATCH(A11,$P$26:$P$125,0)))
```

Dependențe directe: `A11`; `$G$26:$G$125`; `$P$26:$P$125`.

Cache original: `None`. Format afișare: `General`.


### Dashboard!G11

```excel
=IF(A11="","",INDEX($M$26:$M$125,MATCH(A11,$P$26:$P$125,0)))
```

Dependențe directe: `A11`; `$M$26:$M$125`; `$P$26:$P$125`.

Cache original: `None`. Format afișare: `General`.


### Dashboard!H11

```excel
=IF(A11="","",INDEX($I$26:$I$125,MATCH(A11,$P$26:$P$125,0)))
```

Dependențe directe: `A11`; `$I$26:$I$125`; `$P$26:$P$125`.

Cache original: `None`. Format afișare: `General`.


### Dashboard!A26

```excel
=IF('Motor_Meciuri'!A6="","",'Motor_Meciuri'!A6)
```

Dependențe directe: `'Motor_Meciuri'!A6`.

Cache original: `REPLAY_1`. Format afișare: `General`.


### Dashboard!B26

```excel
=IF('Motor_Meciuri'!A6="","",'Motor_Meciuri'!D6)
```

Dependențe directe: `'Motor_Meciuri'!A6`; `'Motor_Meciuri'!D6`.

Cache original: `Brighton – Man United`. Format afișare: `General`.


### Dashboard!C26

```excel
=IF('Motor_Meciuri'!A6="","",'Motor_Meciuri'!E6)
```

Dependențe directe: `'Motor_Meciuri'!A6`; `'Motor_Meciuri'!E6`.

Cache original: `REPLAY`. Format afișare: `General`.


### Dashboard!D26

```excel
=IF('Motor_Meciuri'!A6="","",'Motor_Meciuri'!H6)
```

Dependențe directe: `'Motor_Meciuri'!A6`; `'Motor_Meciuri'!H6`.

Cache original: `READY`. Format afișare: `General`.


### Dashboard!E26

```excel
=IF('Motor_Meciuri'!A6="","",'Motor_Meciuri'!I6)
```

Dependențe directe: `'Motor_Meciuri'!A6`; `'Motor_Meciuri'!I6`.

Cache original: `PASS`. Format afișare: `General`.


### Dashboard!F26

```excel
=IF(K26=0,"",INDEX('Analiza_Linii'!F6:F19,K26))
```

Dependențe directe: `K26`; `'Analiza_Linii'!F6:F19`.

Cache original: `O3,5`. Format afișare: `General`.


### Dashboard!G26

```excel
=IF(A26="","",IF(D26<>"READY","NOT RELEASED",IF(K26=0,IF(E26="FAIL","NO BET","WATCH / NO BET"),INDEX('Analiza_Linii'!AA6:AA19,K26))))
```

Dependențe directe: `A26`; `D26`; `K26`; `E26`; `'Analiza_Linii'!AA6:AA19`.

Cache original: `PRUDENT`. Format afișare: `General`.


### Dashboard!H26

```excel
=IF(K26=0,"",INDEX('Analiza_Linii'!AB6:AB19,K26))
```

Dependențe directe: `K26`; `'Analiza_Linii'!AB6:AB19`.

Cache original: `0.8929839161391997`. Format afișare: `0.0%`.


### Dashboard!I26

```excel
=IF(A26="","",IF(E26<>"PASS",'Motor_Meciuri'!J6,IF(K26=0,"Nicio linie eligibila; vezi motivele din Analiza_Linii",INDEX('Analiza_Linii'!AH6:AH19,K26))))
```

Dependențe directe: `A26`; `E26`; `'Motor_Meciuri'!J6`; `K26`; `'Analiza_Linii'!AH6:AH19`.

Cache original: `Exemplu retrospectiv; exclus din Top LIVE`. Format afișare: `General`.


### Dashboard!K26

```excel
=IF(A26="",0,IFERROR(MATCH(1,'Analiza_Linii'!AC6:AC19,0),0))
```

Dependențe directe: `A26`; `'Analiza_Linii'!AC6:AC19`.

Cache original: `1`. Format afișare: `General`.


### Dashboard!L26

```excel
=IF(K26=0,"",INDEX('Analiza_Linii'!Z6:Z19,K26))
```

Dependențe directe: `K26`; `'Analiza_Linii'!Z6:Z19`.

Cache original: `2`. Format afișare: `General`.


### Dashboard!M26

```excel
=IF(K26=0,"",INDEX('Analiza_Linii'!V6:V19,K26))
```

Dependențe directe: `K26`; `'Analiza_Linii'!V6:V19`.

Cache original: `90`. Format afișare: `General`.


### Dashboard!N26

```excel
=IF(K26=0,"",INDEX('Analiza_Linii'!T6:T19,K26))
```

Dependențe directe: `K26`; `'Analiza_Linii'!T6:T19`.

Cache original: `9.972221126086591`. Format afișare: `General`.


### Dashboard!O26

```excel
=IF(AND(C26="LIVE",K26>0),1,0)
```

Dependențe directe: `C26`; `K26`.

Cache original: `0`. Format afișare: `General`.


### Dashboard!P26

```excel
=IF(O26<>1,"",COUNTIFS($O$26:$O$125,1,$L$26:$L$125,"<"&L26)+COUNTIFS($O$26:$O$125,1,$L$26:$L$125,L26,$H$26:$H$125,">"&H26)+COUNTIFS($O$26:$O$125,1,$L$26:$L$125,L26,$H$26:$H$125,H26,$M$26:$M$125,">"&M26)+COUNTIFS($O$26:O26,1,$L$26:L26,L26,$H$26:H26,H26,$M$26:M26,M26))
```

Dependențe directe: `O26`; `$O$26:$O$125`; `$L$26:$L$125`; `L26`; `$H$26:$H$125`; `H26`; `$M$26:$M$125`; `M26`; `$O$26:O26`; `$L$26:L26`; `$H$26:H26`; `$M$26:M26`.

Cache original: `None`. Format afișare: `General`.



## Config_v6


`A2` = `PARAMETRI ACTIVI | V14`


`A4` = `Pondere sezon`


`B4` = `0.3`


`A5` = `Pondere H/A`


`B5` = `0.45`


`A6` = `Pondere recent`


`B6` = `0.25`


`A7` = `N minim sezon`


`B7` = `10`


`A8` = `N minim H/A`


`B8` = `5`


`A9` = `N minim recent`


`B9` = `3`


`A10` = `D prag Poisson`


`B10` = `1.1`


`A11` = `D NB mild`


`B11` = `1.35`


`A12` = `D NB moderat`


`B12` = `1.7`


`A13` = `D hard fail`


`B13` = `2.25`


`A14` = `Calibrare: reducere spre 50%`


`B14` = `0.82`


`A15` = `N țintă dispersie`


`B15` = `20`


`A16` = `P minim eligibilitate`


`B16` = `0.72`


`A17` = `Reper P informativ`


`B17` = `0.8`


`A18` = `Confidence minim`


`B18` = `65`


`A19` = `Pondere EV`


`B19` = `0`


`A20` = `Limită soft`


`B20` = `0.08`


`A21` = `Limită context`


`B21` = `0.12`


`A26` = `O3,5 PASS max pilot`


`B26` = `0.05`


`C26` = `0.08`


`D26` = `Failure ≤5% PASS; >5%–8% PENALTY; >8% WATCH. Bandă pilot.`


`A34` = `Confidence maxim cu prior`


`B34` = `75`


`A35` = `Penalizare OOS pending`


`B35` = `10`


`A36` = `Penalizare D moderat`


`B36` = `5`


`A37` = `Penalizare D ridicat`


`B37` = `10`


`A38` = `Penalizare maximă soft lipsă`


`B38` = `5`


### Config_v6!B39

```excel
=SUM(B4:B6)
```

Dependențe directe: `B4:B6`.

Cache original: `1`. Format afișare: `General`.


### Config_v6!B40

```excel
=IF(AND(COUNT(B4:B18)=15,MIN(B4:B18)>=0,ABS(B39-1)<0.000001,B7>=1,B8>=1,B9>=1,B10>0,B11>=B10,B12>=B11,B13>=B12,B14>0,B14<=1,B15>=2,B16>0.5,B16<1,B18>=0,B18<=100,B19=0,B20>=0,B20<=1,B21>=0,B21<=1,B26>=0,B26<C26,C26<=1,B34>=0,B34<=75,B35>=0,B36>=0,B37>=0,B38>=0,B41=2,B42=2,MIN(B44:B47)>=0,ABS(SUM(B44:B47)-1)<0.000001,B50>=0.9,B50<1,B51>=90,B51<=100,B52>=0,B52<=20,B53>0,B53<=1.1,B54=5,B55=100,B56>=200,B57>=0.9,B57<1,B58>=0,B58<=0.05),"VALID","CONFIG INVALID")
```

Dependențe directe: `B4:B18`; `B39`; `B7`; `B8`; `B9`; `B10`; `B11`; `B12`; `B13`; `B14`; `B15`; `B16`; `B18`; `B19`; `B20`; `B21`; `B26`; `C26`; `B34`; `B35`; `B36`; `B37`; `B38`; `B41`; `B42`; `B44:B47`; `B50`; `B51`; `B52`; `B53`; `B54`; `B55`; `B56`; `B57`; `B58`.

Cache original: `VALID`. Format afișare: `General`.


`A41` = `N minim varianță`


`B41` = `2`


`A42` = `Floor fără DEFENSIV validat`


`B42` = `2`


`D42` = `Minimum 2, cu excepția Defensive Gate PASS.`


`A44` = `Pondere failure`


`B44` = `0.55`


`A45` = `Pondere dispersie`


`B45` = `0.2`


`A46` = `Pondere incertitudine`


`B46` = `0.15`


`A47` = `Pondere context`


`B47` = `0.1`


`A50` = `P minim DEFENSIV`


`B50` = `0.9`


`A51` = `Confidence minim DEFENSIV`


`B51` = `90`


`A52` = `Score maxim DEFENSIV`


`B52` = `20`


`A53` = `D maxim DEFENSIV`


`B53` = `1.1`


`A54` = `Număr meciuri recente`


`B54` = `5`


`A55` = `Capacitate meciuri`


`B55` = `100`


`A56` = `N minim OOS pentru promovare`


`B56` = `200`


`D56` = `Control conservator propus pentru promovare; nu validare statistică deja demonstrată.`


`A57` = `Wilson 95%: limită inferioară`


`B57` = `0.9`


`D57` = `Calcul Wilson 95% pe predicții candidate distincte, înghețate înainte de meci.`


`A58` = `Supraestimare OOS maximă`


`B58` = `0.05`


`A60` = `Semnătură parametri`


### Config_v6!B60

```excel
="CORNERS_NATIVE_V14"&"|"&TEXT(B4,"0.000000")&"|"&TEXT(B5,"0.000000")&"|"&TEXT(B6,"0.000000")&"|"&TEXT(B7,"0.000000")&"|"&TEXT(B8,"0.000000")&"|"&TEXT(B9,"0.000000")&"|"&TEXT(B10,"0.000000")&"|"&TEXT(B11,"0.000000")&"|"&TEXT(B12,"0.000000")&"|"&TEXT(B13,"0.000000")&"|"&TEXT(B14,"0.000000")&"|"&TEXT(B15,"0.000000")&"|"&TEXT(B16,"0.000000")&"|"&TEXT(B18,"0.000000")&"|"&TEXT(B19,"0.000000")&"|"&TEXT(B20,"0.000000")&"|"&TEXT(B21,"0.000000")&"|"&TEXT(B26,"0.000000")&"|"&TEXT(B34,"0.000000")&"|"&TEXT(B35,"0.000000")&"|"&TEXT(B36,"0.000000")&"|"&TEXT(B37,"0.000000")&"|"&TEXT(B38,"0.000000")&"|"&TEXT(B41,"0.000000")&"|"&TEXT(B42,"0.000000")&"|"&TEXT(B44,"0.000000")&"|"&TEXT(B45,"0.000000")&"|"&TEXT(B46,"0.000000")&"|"&TEXT(B47,"0.000000")&"|"&TEXT(B50,"0.000000")&"|"&TEXT(B51,"0.000000")&"|"&TEXT(B52,"0.000000")&"|"&TEXT(B53,"0.000000")&"|"&TEXT(B54,"0.000000")&"|"&TEXT(B56,"0.000000")&"|"&TEXT(B57,"0.000000")&"|"&TEXT(B58,"0.000000")&"|"&TEXT(C26,"0.000000")
```

Dependențe directe: `B4`; `B5`; `B6`; `B7`; `B8`; `B9`; `B10`; `B11`; `B12`; `B13`; `B14`; `B15`; `B16`; `B18`; `B19`; `B20`; `B21`; `B26`; `B34`; `B35`; `B36`; `B37`; `B38`; `B41`; `B42`; `B44`; `B45`; `B46`; `B47`; `B50`; `B51`; `B52`; `B53`; `B54`; `B56`; `B57`; `B58`; `C26`.

Cache original: `CORNERS_NATIVE_V14|0.300000|0.450000|0.250000|10.000000|5.000000|3.000000|1.100000|1.350000|1.700000|2.250000|0.820000|20.000000|0.720000|65.000000|0.000000|0.080000|0.120000|0.050000|75.000000|10.000000|5.000000|10.000000|5.000000|2.000000|2.000000|0.550000|0.200000|0.150000|0.100000|0.900000|90.000000|20.000000|1.100000|5.000000|200.000000|0.900000|0.050000|0.080000`. Format afișare: `General`.



## Analiza_Linii

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
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

### Analiza_Linii!B6

```excel
=IF('Motor_Meciuri'!A6="","",'Motor_Meciuri'!A6)
```

Dependențe directe: `'Motor_Meciuri'!A6`.

Cache original: `REPLAY_1`. Format afișare: `General`.


### Analiza_Linii!C6

```excel
=IF(B6="","",'Motor_Meciuri'!B6)
```

Dependențe directe: `B6`; `'Motor_Meciuri'!B6`.

Cache original: `E0`. Format afișare: `General`.


### Analiza_Linii!D6

```excel
=IF(B6="","",'Motor_Meciuri'!D6)
```

Dependențe directe: `B6`; `'Motor_Meciuri'!D6`.

Cache original: `Brighton – Man United`. Format afișare: `General`.


### Analiza_Linii!E6

```excel
=IF(B6="","",'Motor_Meciuri'!E6)
```

Dependențe directe: `B6`; `'Motor_Meciuri'!E6`.

Cache original: `REPLAY`. Format afișare: `General`.


### Analiza_Linii!I6

```excel
=IF(B6="","",'Motor_Meciuri'!H6)
```

Dependențe directe: `B6`; `'Motor_Meciuri'!H6`.

Cache original: `READY`. Format afișare: `General`.


### Analiza_Linii!J6

```excel
=IF(B6="","",'Motor_Meciuri'!I6)
```

Dependențe directe: `B6`; `'Motor_Meciuri'!I6`.

Cache original: `PASS`. Format afișare: `General`.


### Analiza_Linii!K6

```excel
=IF(J6<>"PASS","",'Motor_Meciuri'!BD6)
```

Dependențe directe: `J6`; `'Motor_Meciuri'!BD6`.

Cache original: `10.27195945945946`. Format afișare: `0.00`.


### Analiza_Linii!L6

```excel
=IF(J6<>"PASS","",'Motor_Meciuri'!AU6)
```

Dependențe directe: `J6`; `'Motor_Meciuri'!AU6`.

Cache original: `0.9007607192254518`. Format afișare: `0.00`.


### Analiza_Linii!M6

```excel
=IF(NOT(AND(J6="PASS",'Calibrare_Linii'!U6="VALID")),"",1-'Distributie'!AA6)
```

Dependențe directe: `J6`; `'Calibrare_Linii'!U6`; `'Distributie'!AA6`.

Cache original: `0.9915371058651653`. Format afișare: `0.0%`.


### Analiza_Linii!N6

```excel
=IF(M6="","",MAX(0.01,MIN(0.99,0.5+(M6-0.5)*'Motor_Meciuri'!BG6*'Calibrare_Linii'!D6)))
```

Dependențe directe: `M6`; `'Motor_Meciuri'!BG6`; `'Calibrare_Linii'!D6`.

Cache original: `0.8929839161391997`. Format afișare: `0.0%`.


### Analiza_Linii!O6

```excel
=IF(M6="","",1-M6)
```

Dependențe directe: `M6`.

Cache original: `0.008462894134834698`. Format afișare: `0.0%`.


### Analiza_Linii!P6

```excel
=IF(OR(NOT(AND(J6="PASS",'Calibrare_Linii'!U6="VALID")),AK6=0),"",SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405='Input_Meci'!B6)*('Istoric_Nativ'!$C$6:$C$405='Input_Meci'!C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT('Input_Meci'!G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*('Istoric_Nativ'!$Q$6:$Q$405<=H6))/AK6)
```

Dependențe directe: `J6`; `'Calibrare_Linii'!U6`; `AK6`; `'Istoric_Nativ'!$B$6:$B$405`; `'Input_Meci'!B6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Input_Meci'!C6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `'Input_Meci'!G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Input_Meci'!E6`; `'Istoric_Nativ'!$Q$6:$Q$405`; `H6`.

Cache original: `0`. Format afișare: `0.0%`.


### Analiza_Linii!Q6

```excel
=IF(OR(NOT(AND(J6="PASS",'Calibrare_Linii'!U6="VALID")),AL6=0),"",SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405='Input_Meci'!B6)*('Istoric_Nativ'!$C$6:$C$405='Input_Meci'!C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT('Input_Meci'!G6))*((((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6))>0)*('Istoric_Nativ'!$D$6:$D$405>='Motor_Meciuri'!BM6)+((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*('Istoric_Nativ'!$D$6:$D$405>='Motor_Meciuri'!BN6))>0)*('Istoric_Nativ'!$Q$6:$Q$405<=H6))/AL6)
```

Dependențe directe: `J6`; `'Calibrare_Linii'!U6`; `AL6`; `'Istoric_Nativ'!$B$6:$B$405`; `'Input_Meci'!B6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Input_Meci'!C6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `'Input_Meci'!G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Motor_Meciuri'!BM6`; `'Input_Meci'!E6`; `'Motor_Meciuri'!BN6`; `'Istoric_Nativ'!$Q$6:$Q$405`; `H6`.

Cache original: `0`. Format afișare: `0.0%`.


### Analiza_Linii!R6

```excel
=IF(OR(NOT(AND(J6="PASS",'Calibrare_Linii'!U6="VALID")),AM6=0),"",SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405='Input_Meci'!B6)*('Istoric_Nativ'!$C$6:$C$405='Input_Meci'!C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT('Input_Meci'!G6))*((((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6))>0)*('Istoric_Nativ'!$D$6:$D$405>='Motor_Meciuri'!BO6)+((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*('Istoric_Nativ'!$D$6:$D$405>='Motor_Meciuri'!BP6))>0)*('Istoric_Nativ'!$Q$6:$Q$405<=H6))/AM6)
```

Dependențe directe: `J6`; `'Calibrare_Linii'!U6`; `AM6`; `'Istoric_Nativ'!$B$6:$B$405`; `'Input_Meci'!B6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Input_Meci'!C6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `'Input_Meci'!G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Motor_Meciuri'!BO6`; `'Input_Meci'!E6`; `'Motor_Meciuri'!BP6`; `'Istoric_Nativ'!$Q$6:$Q$405`; `H6`.

Cache original: `0`. Format afișare: `0.0%`.


### Analiza_Linii!S6

```excel
=IF(M6="","",MAX(O6,P6,Q6,R6))
```

Dependențe directe: `M6`; `O6`; `P6`; `Q6`; `R6`.

Cache original: `0.008462894134834698`. Format afișare: `0.0%`.


### Analiza_Linii!T6

```excel
=IF(M6="","",MIN(100,S6*100*'Config_v6'!$B$44+MIN(100,L6/'Config_v6'!$B$13*100)*'Config_v6'!$B$45+(100-'Motor_Meciuri'!BF6)*'Config_v6'!$B$46+'Motor_Meciuri'!BH6*100*'Config_v6'!$B$47))
```

Dependențe directe: `M6`; `S6`; `'Config_v6'!$B$44`; `L6`; `'Config_v6'!$B$13`; `'Config_v6'!$B$45`; `'Motor_Meciuri'!BF6`; `'Config_v6'!$B$46`; `'Motor_Meciuri'!BH6`; `'Config_v6'!$B$47`.

Cache original: `9.972221126086591`. Format afișare: `0.00`.


### Analiza_Linii!U6

```excel
=IF(T6="","",IF(T6<=20,1,IF(T6<=40,2,IF(T6<=60,3,IF(T6<=80,4,5)))))
```

Dependențe directe: `T6`.

Cache original: `1`. Format afișare: `General`.


### Analiza_Linii!V6

```excel
=IF(M6="","",MAX(0,'Motor_Meciuri'!BF6-IF(W6="OOS PENDING",'Config_v6'!$B$35,0)-IF(L6>'Config_v6'!$B$12,'Config_v6'!$B$37,IF(L6>'Config_v6'!$B$11,'Config_v6'!$B$36,0))))
```

Dependențe directe: `M6`; `'Motor_Meciuri'!BF6`; `W6`; `'Config_v6'!$B$35`; `L6`; `'Config_v6'!$B$12`; `'Config_v6'!$B$37`; `'Config_v6'!$B$11`; `'Config_v6'!$B$36`.

Cache original: `90`. Format afișare: `General`.


### Analiza_Linii!W6

```excel
=IF(B6="","",IF(I6<>"READY","NOT RELEASED",IF(NOT(AND(J6="PASS",'Calibrare_Linii'!U6="VALID")),"INVALID",IF(NOT(TRUE),"OOS PENDING",IF(S6<=IF(AND('Calibrare_Linii'!S6="VALIDATED",AND('Calibrare_Linii'!H6=C6,ISNUMBER('Calibrare_Linii'!J6),'Calibrare_Linii'!J6<='Input_Meci'!G6)),'Calibrare_Linii'!E6,'Config_v6'!$B$26),"PASS",IF(S6<=IF(AND('Calibrare_Linii'!S6="VALIDATED",AND('Calibrare_Linii'!H6=C6,ISNUMBER('Calibrare_Linii'!J6),'Calibrare_Linii'!J6<='Input_Meci'!G6)),'Calibrare_Linii'!F6,'Config_v6'!$C$26),"PENALTY","WATCH"))))))
```

Dependențe directe: `B6`; `I6`; `J6`; `'Calibrare_Linii'!U6`; `S6`; `'Calibrare_Linii'!S6`; `'Calibrare_Linii'!H6`; `C6`; `'Calibrare_Linii'!J6`; `'Input_Meci'!G6`; `'Calibrare_Linii'!E6`; `'Config_v6'!$B$26`; `'Calibrare_Linii'!F6`; `'Config_v6'!$C$26`.

Cache original: `PASS`. Format afișare: `General`.


### Analiza_Linii!X6

```excel
=IF(M6="","",IF(AND(AND(J6="PASS",'Calibrare_Linii'!U6="VALID"),'Motor_Meciuri'!K6=12,'Motor_Meciuri'!L6=12,'Motor_Meciuri'!M6="NO",'Motor_Meciuri'!BL6='Motor_Meciuri'!C6,AB6>='Config_v6'!$B$50,AN6>='Config_v6'!$B$51,T6<='Config_v6'!$B$52,L6<='Config_v6'!$B$53,ISNUMBER('Calibrare_Linii'!E6),S6<='Calibrare_Linii'!E6,SUM(AK6:AM6)>0),"CANDIDATE","NO"))
```

Dependențe directe: `M6`; `J6`; `'Calibrare_Linii'!U6`; `'Motor_Meciuri'!K6`; `'Motor_Meciuri'!L6`; `'Motor_Meciuri'!M6`; `'Motor_Meciuri'!BL6`; `'Motor_Meciuri'!C6`; `AB6`; `'Config_v6'!$B$50`; `AN6`; `'Config_v6'!$B$51`; `T6`; `'Config_v6'!$B$52`; `L6`; `'Config_v6'!$B$53`; `'Calibrare_Linii'!E6`; `S6`; `AK6:AM6`.

Cache original: `NO`. Format afișare: `General`.


### Analiza_Linii!Y6

```excel
=IF(B6="","",IF(I6<>"READY","NOT RELEASED",IF(AND(X6="CANDIDATE",V6>='Config_v6'!$B$51,W6="PASS",'Calibrare_Linii'!T6="VALIDATED",AND('Calibrare_Linii'!H6=C6,ISNUMBER('Calibrare_Linii'!J6),'Calibrare_Linii'!J6<='Input_Meci'!G6)),"PASS",IF(X6="CANDIDATE","OOS PENDING","FAIL"))))
```

Dependențe directe: `B6`; `I6`; `X6`; `V6`; `'Config_v6'!$B$51`; `W6`; `'Calibrare_Linii'!T6`; `'Calibrare_Linii'!H6`; `C6`; `'Calibrare_Linii'!J6`; `'Input_Meci'!G6`.

Cache original: `FAIL`. Format afișare: `General`.


### Analiza_Linii!Z6

```excel
=IF(B6="","",IF(I6<>"READY","",IF(OR(NOT(AND(J6="PASS",'Calibrare_Linii'!U6="VALID")),L6>'Config_v6'!$B$13,W6="WATCH"),5,IF(Y6="PASS",1,MIN(5,MAX('Config_v6'!$B$42,U6)+IF(W6="PENALTY",1,0))))))
```

Dependențe directe: `B6`; `I6`; `J6`; `'Calibrare_Linii'!U6`; `L6`; `'Config_v6'!$B$13`; `W6`; `Y6`; `'Config_v6'!$B$42`; `U6`.

Cache original: `2`. Format afișare: `General`.


### Analiza_Linii!AA6

```excel
=IF(B6="","",IF(I6<>"READY","NOT RELEASED",IF(Z6=5,"NO BET",IF(OR(AB6<'Config_v6'!$B$16,V6<'Config_v6'!$B$18),"WATCH",IF(Z6=1,"DEFENSIV",IF(Z6=2,"PRUDENT",IF(Z6=3,"MODERAT","RIDICAT")))))))
```

Dependențe directe: `B6`; `I6`; `Z6`; `AB6`; `'Config_v6'!$B$16`; `V6`; `'Config_v6'!$B$18`.

Cache original: `PRUDENT`. Format afișare: `General`.


### Analiza_Linii!AB6

```excel
=IF(N6="","",MIN(N6,1-S6))
```

Dependențe directe: `N6`; `S6`.

Cache original: `0.8929839161391997`. Format afișare: `0.0%`.


### Analiza_Linii!AC6

```excel
=IF(AD6<>1,"",COUNTIFS($Z$6:$Z$19,"<"&Z6,$AD$6:$AD$19,1)+COUNTIFS($Z$6:$Z$19,Z6,$AB$6:$AB$19,">"&AB6,$AD$6:$AD$19,1)+COUNTIFS($Z$6:$Z$19,Z6,$AB$6:$AB$19,AB6,$V$6:$V$19,">"&V6,$AD$6:$AD$19,1)+COUNTIFS($Z$6:Z6,Z6,$AB$6:AB6,AB6,$V$6:V6,V6,$AD$6:AD6,1))
```

Dependențe directe: `AD6`; `$Z$6:$Z$19`; `Z6`; `$AD$6:$AD$19`; `$AB$6:$AB$19`; `AB6`; `$V$6:$V$19`; `V6`; `$Z$6:Z6`; `$AB$6:AB6`; `$V$6:V6`; `$AD$6:AD6`.

Cache original: `1`. Format afișare: `General`.


### Analiza_Linii!AD6

```excel
=IF(OR(AA6="DEFENSIV",AA6="PRUDENT",AA6="MODERAT",AA6="RIDICAT"),1,0)
```

Dependențe directe: `AA6`.

Cache original: `1`. Format afișare: `General`.


### Analiza_Linii!AE6

```excel
=IF(AD6<>1,"NO",IF(W6="PASS","YES",IF(W6="OOS PENDING","CONDITIONAL","NO")))
```

Dependențe directe: `AD6`; `W6`.

Cache original: `YES`. Format afișare: `General`.


### Analiza_Linii!AF6

```excel
=IF(AND(AD6=1,AC6=1,E6="LIVE"),1,0)
```

Dependențe directe: `AD6`; `AC6`; `E6`.

Cache original: `0`. Format afișare: `General`.


### Analiza_Linii!AG6

```excel
=IF(AF6<>1,"",'Dashboard'!P26)
```

Dependențe directe: `AF6`; `'Dashboard'!P26`.

Cache original: `None`. Format afișare: `General`.


### Analiza_Linii!AH6

```excel
=IF(B6="","",IF(J6<>"PASS",'Motor_Meciuri'!J6,IF('Calibrare_Linii'!U6<>"VALID","Parametri linie invalizi",IF(L6>'Config_v6'!$B$13,"Dispersie peste limita",IF(W6="WATCH","Failure peste limita",IF(AB6<'Config_v6'!$B$16,"P finala sub prag",IF(V6<'Config_v6'!$B$18,"Confidence sub prag",IF(E6="REPLAY","Exemplu retrospectiv; exclus din Top LIVE",IF(Y6="PASS","DEFENSIV validat",IF(W6="OOS PENDING","Eligibil; calibrare linie in monitorizare","Eligibil"))))))))))
```

Dependențe directe: `B6`; `J6`; `'Motor_Meciuri'!J6`; `'Calibrare_Linii'!U6`; `L6`; `'Config_v6'!$B$13`; `W6`; `AB6`; `'Config_v6'!$B$16`; `V6`; `'Config_v6'!$B$18`; `E6`; `Y6`.

Cache original: `Exemplu retrospectiv; exclus din Top LIVE`. Format afișare: `General`.


### Analiza_Linii!AI6

```excel
=IF(B6="","",'Calibrare_Linii'!V6)
```

Dependențe directe: `B6`; `'Calibrare_Linii'!V6`.

Cache original: `CORNERS_NATIVE_V14|0.300000|0.450000|0.250000|10.000000|5.000000|3.000000|1.100000|1.350000|1.700000|2.250000|0.820000|20.000000|0.720000|65.000000|0.000000|0.080000|0.120000|0.050000|75.000000|10.000000|5.000000|10.000000|5.000000|2.000000|2.000000|0.550000|0.200000|0.150000|0.100000|0.900000|90.000000|20.000000|1.100000|5.000000|200.000000|0.900000|0.050000|0.080000|O3,5|1.000000|0.050000|0.080000`. Format afișare: `General`.


### Analiza_Linii!AJ6

```excel
=IF(B6="","",IF(AND('Calibrare_Linii'!T6="VALIDATED",AND('Calibrare_Linii'!H6=C6,ISNUMBER('Calibrare_Linii'!J6),'Calibrare_Linii'!J6<='Input_Meci'!G6)),"DEFENSIVE VALIDATED",IF(AND('Calibrare_Linii'!S6="VALIDATED",AND('Calibrare_Linii'!H6=C6,ISNUMBER('Calibrare_Linii'!J6),'Calibrare_Linii'!J6<='Input_Meci'!G6)),"TAIL VALIDATED","OOS PENDING")))
```

Dependențe directe: `B6`; `'Calibrare_Linii'!T6`; `'Calibrare_Linii'!H6`; `C6`; `'Calibrare_Linii'!J6`; `'Input_Meci'!G6`; `'Calibrare_Linii'!S6`.

Cache original: `OOS PENDING`. Format afișare: `General`.


### Analiza_Linii!AK6

```excel
=IF(J6<>"PASS",0,'Motor_Meciuri'!BR6)
```

Dependențe directe: `J6`; `'Motor_Meciuri'!BR6`.

Cache original: `36`. Format afișare: `General`.


### Analiza_Linii!AL6

```excel
=IF(J6<>"PASS",0,'Motor_Meciuri'!BS6)
```

Dependențe directe: `J6`; `'Motor_Meciuri'!BS6`.

Cache original: `20`. Format afișare: `General`.


### Analiza_Linii!AM6

```excel
=IF(J6<>"PASS",0,'Motor_Meciuri'!BT6)
```

Dependențe directe: `J6`; `'Motor_Meciuri'!BT6`.

Cache original: `40`. Format afișare: `General`.


### Analiza_Linii!AN6

```excel
=IF(M6="","",MAX(0,'Motor_Meciuri'!BF6-IF(L6>'Config_v6'!$B$12,'Config_v6'!$B$37,IF(L6>'Config_v6'!$B$11,'Config_v6'!$B$36,0))))
```

Dependențe directe: `M6`; `'Motor_Meciuri'!BF6`; `L6`; `'Config_v6'!$B$12`; `'Config_v6'!$B$37`; `'Config_v6'!$B$11`; `'Config_v6'!$B$36`.

Cache original: `90`. Format afișare: `General`.


### Analiza_Linii!W7

```excel
=IF(B7="","",IF(I7<>"READY","NOT RELEASED",IF(NOT(AND(J7="PASS",'Calibrare_Linii'!U7="VALID")),"INVALID",IF(NOT(AND('Calibrare_Linii'!S7="VALIDATED",AND('Calibrare_Linii'!H7=C7,ISNUMBER('Calibrare_Linii'!J7),'Calibrare_Linii'!J7<='Input_Meci'!G6))),"OOS PENDING",IF(S7<='Calibrare_Linii'!E7,"PASS",IF(S7<='Calibrare_Linii'!F7,"PENALTY","WATCH"))))))
```

Dependențe directe: `B7`; `I7`; `J7`; `'Calibrare_Linii'!U7`; `'Calibrare_Linii'!S7`; `'Calibrare_Linii'!H7`; `C7`; `'Calibrare_Linii'!J7`; `'Input_Meci'!G6`; `S7`; `'Calibrare_Linii'!E7`; `'Calibrare_Linii'!F7`.

Cache original: `OOS PENDING`. Format afișare: `General`.


### Analiza_Linii!M12

```excel
=IF(NOT(AND(J12="PASS",'Calibrare_Linii'!U12="VALID")),"",'Distributie'!AH6)
```

Dependențe directe: `J12`; `'Calibrare_Linii'!U12`; `'Distributie'!AH6`.

Cache original: `0.5490562286051273`. Format afișare: `0.0%`.


### Analiza_Linii!P12

```excel
=IF(OR(NOT(AND(J12="PASS",'Calibrare_Linii'!U12="VALID")),AK12=0),"",SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405='Input_Meci'!B6)*('Istoric_Nativ'!$C$6:$C$405='Input_Meci'!C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT('Input_Meci'!G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*('Istoric_Nativ'!$Q$6:$Q$405>H12))/AK12)
```

Dependențe directe: `J12`; `'Calibrare_Linii'!U12`; `AK12`; `'Istoric_Nativ'!$B$6:$B$405`; `'Input_Meci'!B6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Input_Meci'!C6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `'Input_Meci'!G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Input_Meci'!E6`; `'Istoric_Nativ'!$Q$6:$Q$405`; `H12`.

Cache original: `0.4444444444444444`. Format afișare: `0.0%`.


### Analiza_Linii!Q12

```excel
=IF(OR(NOT(AND(J12="PASS",'Calibrare_Linii'!U12="VALID")),AL12=0),"",SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405='Input_Meci'!B6)*('Istoric_Nativ'!$C$6:$C$405='Input_Meci'!C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT('Input_Meci'!G6))*((((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6))>0)*('Istoric_Nativ'!$D$6:$D$405>='Motor_Meciuri'!BM6)+((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*('Istoric_Nativ'!$D$6:$D$405>='Motor_Meciuri'!BN6))>0)*('Istoric_Nativ'!$Q$6:$Q$405>H12))/AL12)
```

Dependențe directe: `J12`; `'Calibrare_Linii'!U12`; `AL12`; `'Istoric_Nativ'!$B$6:$B$405`; `'Input_Meci'!B6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Input_Meci'!C6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `'Input_Meci'!G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Motor_Meciuri'!BM6`; `'Input_Meci'!E6`; `'Motor_Meciuri'!BN6`; `'Istoric_Nativ'!$Q$6:$Q$405`; `H12`.

Cache original: `0.55`. Format afișare: `0.0%`.


### Analiza_Linii!R12

```excel
=IF(OR(NOT(AND(J12="PASS",'Calibrare_Linii'!U12="VALID")),AM12=0),"",SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405='Input_Meci'!B6)*('Istoric_Nativ'!$C$6:$C$405='Input_Meci'!C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT('Input_Meci'!G6))*((((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6))>0)*('Istoric_Nativ'!$D$6:$D$405>='Motor_Meciuri'!BO6)+((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*('Istoric_Nativ'!$D$6:$D$405>='Motor_Meciuri'!BP6))>0)*('Istoric_Nativ'!$Q$6:$Q$405>H12))/AM12)
```

Dependențe directe: `J12`; `'Calibrare_Linii'!U12`; `AM12`; `'Istoric_Nativ'!$B$6:$B$405`; `'Input_Meci'!B6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Input_Meci'!C6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `'Input_Meci'!G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Motor_Meciuri'!BO6`; `'Input_Meci'!E6`; `'Motor_Meciuri'!BP6`; `'Istoric_Nativ'!$Q$6:$Q$405`; `H12`.

Cache original: `0.45`. Format afișare: `0.0%`.



## Motor_Meciuri

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
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

### Motor_Meciuri!A6

```excel
=IF('Input_Meci'!A6="","",'Input_Meci'!A6)
```

Dependențe directe: `'Input_Meci'!A6`.

Cache original: `REPLAY_1`. Format afișare: `General`.


### Motor_Meciuri!B6

```excel
=IF(A6="","",'Input_Meci'!B6)
```

Dependențe directe: `A6`; `'Input_Meci'!B6`.

Cache original: `E0`. Format afișare: `General`.


### Motor_Meciuri!C6

```excel
=IF(A6="","",'Input_Meci'!C6)
```

Dependențe directe: `A6`; `'Input_Meci'!C6`.

Cache original: `2025/26`. Format afișare: `General`.


### Motor_Meciuri!D6

```excel
=IF(A6="","",'Input_Meci'!D6&" – "&'Input_Meci'!E6)
```

Dependențe directe: `A6`; `'Input_Meci'!D6`; `'Input_Meci'!E6`.

Cache original: `Brighton – Man United`. Format afișare: `General`.


### Motor_Meciuri!E6

```excel
=IF(A6="","",'Input_Meci'!H6)
```

Dependențe directe: `A6`; `'Input_Meci'!H6`.

Cache original: `REPLAY`. Format afișare: `General`.


### Motor_Meciuri!F6

```excel
=IF(A6="","",'Input_Meci'!F6)
```

Dependențe directe: `A6`; `'Input_Meci'!F6`.

Cache original: `2026-05-24T00:00:00`. Format afișare: `yyyy-mm-dd hh:mm`.


### Motor_Meciuri!G6

```excel
=IF(A6="","",'Input_Meci'!G6)
```

Dependențe directe: `A6`; `'Input_Meci'!G6`.

Cache original: `2026-05-23T23:00:00`. Format afișare: `yyyy-mm-dd hh:mm`.


### Motor_Meciuri!H6

```excel
=IF(A6="","",IF(BQ6<>"VALID","NOT RELEASED",IF(AND(OR('Input_Meci'!I6="NOT AVAILABLE",'Input_Meci'!I6="SOURCE CONFLICT"),'Input_Meci'!J6<>""),"READY",IF(OR(NOT(OR('Input_Meci'!I6="AUTO",'Input_Meci'!I6="")),COUNTIF('Core_Nativ'!R6:R11,"CLOSED")<>6,BJ6>0),"NOT RELEASED","READY"))))
```

Dependențe directe: `A6`; `BQ6`; `'Input_Meci'!I6`; `'Input_Meci'!J6`; `'Core_Nativ'!R6:R11`; `BJ6`.

Cache original: `READY`. Format afișare: `General`.


### Motor_Meciuri!I6

```excel
=IF(A6="","",IF(H6<>"READY","NOT RELEASED",IF(AND(NOT(OR('Input_Meci'!I6="NOT AVAILABLE",'Input_Meci'!I6="SOURCE CONFLICT")),L6=12,AR6>=2,AS6>0,ISNUMBER(AT6),BI6="VALID",BK6="VALID"),"PASS","FAIL")))
```

Dependențe directe: `A6`; `H6`; `'Input_Meci'!I6`; `L6`; `AR6`; `AS6`; `AT6`; `BI6`; `BK6`.

Cache original: `PASS`. Format afișare: `General`.


### Motor_Meciuri!J6

```excel
=IF(A6="","",IF(BQ6<>"VALID","Verifica ID, echipe, mod si cutoff < kickoff",IF(H6<>"READY",IF('Input_Meci'!I6="ACCESS BLOCKED","Acces blocat: reia sursele",IF(BJ6>0,"Istoric invalid sau conflict: verifica randurile native","Surse neinchise / post-cutoff / dovezi incomplete")),IF(OR('Input_Meci'!I6="NOT AVAILABLE",'Input_Meci'!I6="SOURCE CONFLICT"),'Input_Meci'!I6,IF(BK6<>"VALID","Parametri invalizi",IF(L6<>12,"Core / sample / prior insuficient",IF(AR6<2,"N insuficient pentru dispersie",IF(AS6<=0,"Media istorica trebuie sa fie pozitiva",IF(BI6<>"VALID","Context invalid","READY")))))))))
```

Dependențe directe: `A6`; `BQ6`; `H6`; `'Input_Meci'!I6`; `BJ6`; `BK6`; `L6`; `AR6`; `AS6`; `BI6`.

Cache original: `READY`. Format afișare: `General`.


### Motor_Meciuri!K6

```excel
=IF(A6="","",COUNT(T6:AE6))
```

Dependențe directe: `A6`; `T6:AE6`.

Cache original: `12`. Format afișare: `General`.


### Motor_Meciuri!L6

```excel
=IF(A6="","",COUNT(AF6:AQ6))
```

Dependențe directe: `A6`; `AF6:AQ6`.

Cache original: `12`. Format afișare: `General`.


### Motor_Meciuri!M6

```excel
=IF(A6="","",IF(OR('Core_Nativ'!M6<'Core_Nativ'!P6,'Core_Nativ'!M7<'Core_Nativ'!P7,'Core_Nativ'!M8<'Core_Nativ'!P8,'Core_Nativ'!M9<'Core_Nativ'!P9,'Core_Nativ'!M10<'Core_Nativ'!P10,'Core_Nativ'!M11<'Core_Nativ'!P11),"YES","NO"))
```

Dependențe directe: `A6`; `'Core_Nativ'!M6`; `'Core_Nativ'!P6`; `'Core_Nativ'!M7`; `'Core_Nativ'!P7`; `'Core_Nativ'!M8`; `'Core_Nativ'!P8`; `'Core_Nativ'!M9`; `'Core_Nativ'!P9`; `'Core_Nativ'!M10`; `'Core_Nativ'!P10`; `'Core_Nativ'!M11`; `'Core_Nativ'!P11`.

Cache original: `NO`. Format afișare: `General`.


### Motor_Meciuri!N6

```excel
=IF(A6="","",'Core_Nativ'!M6)
```

Dependențe directe: `A6`; `'Core_Nativ'!M6`.

Cache original: `37`. Format afișare: `General`.


### Motor_Meciuri!O6

```excel
=IF(A6="","",'Core_Nativ'!M7)
```

Dependențe directe: `A6`; `'Core_Nativ'!M7`.

Cache original: `18`. Format afișare: `General`.


### Motor_Meciuri!P6

```excel
=IF(A6="","",'Core_Nativ'!M8)
```

Dependențe directe: `A6`; `'Core_Nativ'!M8`.

Cache original: `5`. Format afișare: `General`.


### Motor_Meciuri!Q6

```excel
=IF(A6="","",'Core_Nativ'!M9)
```

Dependențe directe: `A6`; `'Core_Nativ'!M9`.

Cache original: `37`. Format afișare: `General`.


### Motor_Meciuri!R6

```excel
=IF(A6="","",'Core_Nativ'!M10)
```

Dependențe directe: `A6`; `'Core_Nativ'!M10`.

Cache original: `18`. Format afișare: `General`.


### Motor_Meciuri!S6

```excel
=IF(A6="","",'Core_Nativ'!M11)
```

Dependențe directe: `A6`; `'Core_Nativ'!M11`.

Cache original: `5`. Format afișare: `General`.


### Motor_Meciuri!T6

```excel
=IF(OR(A6="",'Core_Nativ'!M6=0),"",'Core_Nativ'!N6)
```

Dependențe directe: `A6`; `'Core_Nativ'!M6`; `'Core_Nativ'!N6`.

Cache original: `5`. Format afișare: `0.00`.


### Motor_Meciuri!U6

```excel
=IF(OR(A6="",'Core_Nativ'!M6=0),"",'Core_Nativ'!O6)
```

Dependențe directe: `A6`; `'Core_Nativ'!M6`; `'Core_Nativ'!O6`.

Cache original: `4.864864864864865`. Format afișare: `0.00`.


### Motor_Meciuri!V6

```excel
=IF(OR(A6="",'Core_Nativ'!M7=0),"",'Core_Nativ'!N7)
```

Dependențe directe: `A6`; `'Core_Nativ'!M7`; `'Core_Nativ'!N7`.

Cache original: `5.222222222222222`. Format afișare: `0.00`.


### Motor_Meciuri!W6

```excel
=IF(OR(A6="",'Core_Nativ'!M7=0),"",'Core_Nativ'!O7)
```

Dependențe directe: `A6`; `'Core_Nativ'!M7`; `'Core_Nativ'!O7`.

Cache original: `4.611111111111111`. Format afișare: `0.00`.


### Motor_Meciuri!X6

```excel
=IF(OR(A6="",'Core_Nativ'!M8=0),"",'Core_Nativ'!N8)
```

Dependențe directe: `A6`; `'Core_Nativ'!M8`; `'Core_Nativ'!N8`.

Cache original: `7.2`. Format afișare: `0.00`.


### Motor_Meciuri!Y6

```excel
=IF(OR(A6="",'Core_Nativ'!M8=0),"",'Core_Nativ'!O8)
```

Dependențe directe: `A6`; `'Core_Nativ'!M8`; `'Core_Nativ'!O8`.

Cache original: `4.4`. Format afișare: `0.00`.


### Motor_Meciuri!Z6

```excel
=IF(OR(A6="",'Core_Nativ'!M9=0),"",'Core_Nativ'!N9)
```

Dependențe directe: `A6`; `'Core_Nativ'!M9`; `'Core_Nativ'!N9`.

Cache original: `4.837837837837838`. Format afișare: `0.00`.


### Motor_Meciuri!AA6

```excel
=IF(OR(A6="",'Core_Nativ'!M9=0),"",'Core_Nativ'!O9)
```

Dependențe directe: `A6`; `'Core_Nativ'!M9`; `'Core_Nativ'!O9`.

Cache original: `5.027027027027027`. Format afișare: `0.00`.


### Motor_Meciuri!AB6

```excel
=IF(OR(A6="",'Core_Nativ'!M10=0),"",'Core_Nativ'!N10)
```

Dependențe directe: `A6`; `'Core_Nativ'!M10`; `'Core_Nativ'!N10`.

Cache original: `4.388888888888889`. Format afișare: `0.00`.


### Motor_Meciuri!AC6

```excel
=IF(OR(A6="",'Core_Nativ'!M10=0),"",'Core_Nativ'!O10)
```

Dependențe directe: `A6`; `'Core_Nativ'!M10`; `'Core_Nativ'!O10`.

Cache original: `5.611111111111111`. Format afișare: `0.00`.


### Motor_Meciuri!AD6

```excel
=IF(OR(A6="",'Core_Nativ'!M11=0),"",'Core_Nativ'!N11)
```

Dependențe directe: `A6`; `'Core_Nativ'!M11`; `'Core_Nativ'!N11`.

Cache original: `5.2`. Format afișare: `0.00`.


### Motor_Meciuri!AE6

```excel
=IF(OR(A6="",'Core_Nativ'!M11=0),"",'Core_Nativ'!O11)
```

Dependențe directe: `A6`; `'Core_Nativ'!M11`; `'Core_Nativ'!O11`.

Cache original: `6`. Format afișare: `0.00`.


### Motor_Meciuri!AF6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R6="CLOSED",'Core_Nativ'!S6=0),IF('Core_Nativ'!M6>='Core_Nativ'!P6,'Core_Nativ'!N6,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T12="DERIVED",'Core_Nativ'!M12>='Core_Nativ'!P6),MIN(1,'Core_Nativ'!M6/'Core_Nativ'!P6)*IF('Core_Nativ'!M6=0,0,'Core_Nativ'!N6)+(1-MIN(1,'Core_Nativ'!M6/'Core_Nativ'!P6))*'Core_Nativ'!N12,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R6`; `'Core_Nativ'!S6`; `'Core_Nativ'!M6`; `'Core_Nativ'!P6`; `'Core_Nativ'!N6`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T12`; `'Core_Nativ'!M12`; `'Core_Nativ'!N12`.

Cache original: `5`. Format afișare: `0.00`.


### Motor_Meciuri!AG6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R6="CLOSED",'Core_Nativ'!S6=0),IF('Core_Nativ'!M6>='Core_Nativ'!P6,'Core_Nativ'!O6,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T12="DERIVED",'Core_Nativ'!M12>='Core_Nativ'!P6),MIN(1,'Core_Nativ'!M6/'Core_Nativ'!P6)*IF('Core_Nativ'!M6=0,0,'Core_Nativ'!O6)+(1-MIN(1,'Core_Nativ'!M6/'Core_Nativ'!P6))*'Core_Nativ'!O12,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R6`; `'Core_Nativ'!S6`; `'Core_Nativ'!M6`; `'Core_Nativ'!P6`; `'Core_Nativ'!O6`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T12`; `'Core_Nativ'!M12`; `'Core_Nativ'!O12`.

Cache original: `4.864864864864865`. Format afișare: `0.00`.


### Motor_Meciuri!AH6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R7="CLOSED",'Core_Nativ'!S7=0),IF('Core_Nativ'!M7>='Core_Nativ'!P7,'Core_Nativ'!N7,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T13="DERIVED",'Core_Nativ'!M13>='Core_Nativ'!P7),MIN(1,'Core_Nativ'!M7/'Core_Nativ'!P7)*IF('Core_Nativ'!M7=0,0,'Core_Nativ'!N7)+(1-MIN(1,'Core_Nativ'!M7/'Core_Nativ'!P7))*'Core_Nativ'!N13,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R7`; `'Core_Nativ'!S7`; `'Core_Nativ'!M7`; `'Core_Nativ'!P7`; `'Core_Nativ'!N7`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T13`; `'Core_Nativ'!M13`; `'Core_Nativ'!N13`.

Cache original: `5.222222222222222`. Format afișare: `0.00`.


### Motor_Meciuri!AI6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R7="CLOSED",'Core_Nativ'!S7=0),IF('Core_Nativ'!M7>='Core_Nativ'!P7,'Core_Nativ'!O7,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T13="DERIVED",'Core_Nativ'!M13>='Core_Nativ'!P7),MIN(1,'Core_Nativ'!M7/'Core_Nativ'!P7)*IF('Core_Nativ'!M7=0,0,'Core_Nativ'!O7)+(1-MIN(1,'Core_Nativ'!M7/'Core_Nativ'!P7))*'Core_Nativ'!O13,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R7`; `'Core_Nativ'!S7`; `'Core_Nativ'!M7`; `'Core_Nativ'!P7`; `'Core_Nativ'!O7`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T13`; `'Core_Nativ'!M13`; `'Core_Nativ'!O13`.

Cache original: `4.611111111111111`. Format afișare: `0.00`.


### Motor_Meciuri!AJ6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R8="CLOSED",'Core_Nativ'!S8=0),IF('Core_Nativ'!M8>='Core_Nativ'!P8,'Core_Nativ'!N8,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T14="DERIVED",'Core_Nativ'!M14>='Core_Nativ'!P8),MIN(1,'Core_Nativ'!M8/'Core_Nativ'!P8)*IF('Core_Nativ'!M8=0,0,'Core_Nativ'!N8)+(1-MIN(1,'Core_Nativ'!M8/'Core_Nativ'!P8))*'Core_Nativ'!N14,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R8`; `'Core_Nativ'!S8`; `'Core_Nativ'!M8`; `'Core_Nativ'!P8`; `'Core_Nativ'!N8`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T14`; `'Core_Nativ'!M14`; `'Core_Nativ'!N14`.

Cache original: `7.2`. Format afișare: `0.00`.


### Motor_Meciuri!AK6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R8="CLOSED",'Core_Nativ'!S8=0),IF('Core_Nativ'!M8>='Core_Nativ'!P8,'Core_Nativ'!O8,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T14="DERIVED",'Core_Nativ'!M14>='Core_Nativ'!P8),MIN(1,'Core_Nativ'!M8/'Core_Nativ'!P8)*IF('Core_Nativ'!M8=0,0,'Core_Nativ'!O8)+(1-MIN(1,'Core_Nativ'!M8/'Core_Nativ'!P8))*'Core_Nativ'!O14,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R8`; `'Core_Nativ'!S8`; `'Core_Nativ'!M8`; `'Core_Nativ'!P8`; `'Core_Nativ'!O8`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T14`; `'Core_Nativ'!M14`; `'Core_Nativ'!O14`.

Cache original: `4.4`. Format afișare: `0.00`.


### Motor_Meciuri!AL6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R9="CLOSED",'Core_Nativ'!S9=0),IF('Core_Nativ'!M9>='Core_Nativ'!P9,'Core_Nativ'!N9,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T15="DERIVED",'Core_Nativ'!M15>='Core_Nativ'!P9),MIN(1,'Core_Nativ'!M9/'Core_Nativ'!P9)*IF('Core_Nativ'!M9=0,0,'Core_Nativ'!N9)+(1-MIN(1,'Core_Nativ'!M9/'Core_Nativ'!P9))*'Core_Nativ'!N15,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R9`; `'Core_Nativ'!S9`; `'Core_Nativ'!M9`; `'Core_Nativ'!P9`; `'Core_Nativ'!N9`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T15`; `'Core_Nativ'!M15`; `'Core_Nativ'!N15`.

Cache original: `4.837837837837838`. Format afișare: `0.00`.


### Motor_Meciuri!AM6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R9="CLOSED",'Core_Nativ'!S9=0),IF('Core_Nativ'!M9>='Core_Nativ'!P9,'Core_Nativ'!O9,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T15="DERIVED",'Core_Nativ'!M15>='Core_Nativ'!P9),MIN(1,'Core_Nativ'!M9/'Core_Nativ'!P9)*IF('Core_Nativ'!M9=0,0,'Core_Nativ'!O9)+(1-MIN(1,'Core_Nativ'!M9/'Core_Nativ'!P9))*'Core_Nativ'!O15,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R9`; `'Core_Nativ'!S9`; `'Core_Nativ'!M9`; `'Core_Nativ'!P9`; `'Core_Nativ'!O9`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T15`; `'Core_Nativ'!M15`; `'Core_Nativ'!O15`.

Cache original: `5.027027027027027`. Format afișare: `0.00`.


### Motor_Meciuri!AN6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R10="CLOSED",'Core_Nativ'!S10=0),IF('Core_Nativ'!M10>='Core_Nativ'!P10,'Core_Nativ'!N10,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T16="DERIVED",'Core_Nativ'!M16>='Core_Nativ'!P10),MIN(1,'Core_Nativ'!M10/'Core_Nativ'!P10)*IF('Core_Nativ'!M10=0,0,'Core_Nativ'!N10)+(1-MIN(1,'Core_Nativ'!M10/'Core_Nativ'!P10))*'Core_Nativ'!N16,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R10`; `'Core_Nativ'!S10`; `'Core_Nativ'!M10`; `'Core_Nativ'!P10`; `'Core_Nativ'!N10`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T16`; `'Core_Nativ'!M16`; `'Core_Nativ'!N16`.

Cache original: `4.388888888888889`. Format afișare: `0.00`.


### Motor_Meciuri!AO6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R10="CLOSED",'Core_Nativ'!S10=0),IF('Core_Nativ'!M10>='Core_Nativ'!P10,'Core_Nativ'!O10,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T16="DERIVED",'Core_Nativ'!M16>='Core_Nativ'!P10),MIN(1,'Core_Nativ'!M10/'Core_Nativ'!P10)*IF('Core_Nativ'!M10=0,0,'Core_Nativ'!O10)+(1-MIN(1,'Core_Nativ'!M10/'Core_Nativ'!P10))*'Core_Nativ'!O16,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R10`; `'Core_Nativ'!S10`; `'Core_Nativ'!M10`; `'Core_Nativ'!P10`; `'Core_Nativ'!O10`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T16`; `'Core_Nativ'!M16`; `'Core_Nativ'!O16`.

Cache original: `5.611111111111111`. Format afișare: `0.00`.


### Motor_Meciuri!AP6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R11="CLOSED",'Core_Nativ'!S11=0),IF('Core_Nativ'!M11>='Core_Nativ'!P11,'Core_Nativ'!N11,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T17="DERIVED",'Core_Nativ'!M17>='Core_Nativ'!P11),MIN(1,'Core_Nativ'!M11/'Core_Nativ'!P11)*IF('Core_Nativ'!M11=0,0,'Core_Nativ'!N11)+(1-MIN(1,'Core_Nativ'!M11/'Core_Nativ'!P11))*'Core_Nativ'!N17,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R11`; `'Core_Nativ'!S11`; `'Core_Nativ'!M11`; `'Core_Nativ'!P11`; `'Core_Nativ'!N11`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T17`; `'Core_Nativ'!M17`; `'Core_Nativ'!N17`.

Cache original: `5.2`. Format afișare: `0.00`.


### Motor_Meciuri!AQ6

```excel
=IF(A6="","",IF(AND('Core_Nativ'!R11="CLOSED",'Core_Nativ'!S11=0),IF('Core_Nativ'!M11>='Core_Nativ'!P11,'Core_Nativ'!O11,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,'Core_Nativ'!T17="DERIVED",'Core_Nativ'!M17>='Core_Nativ'!P11),MIN(1,'Core_Nativ'!M11/'Core_Nativ'!P11)*IF('Core_Nativ'!M11=0,0,'Core_Nativ'!O11)+(1-MIN(1,'Core_Nativ'!M11/'Core_Nativ'!P11))*'Core_Nativ'!O17,"")),""))
```

Dependențe directe: `A6`; `'Core_Nativ'!R11`; `'Core_Nativ'!S11`; `'Core_Nativ'!M11`; `'Core_Nativ'!P11`; `'Core_Nativ'!O11`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `C6`; `'Core_Nativ'!T17`; `'Core_Nativ'!M17`; `'Core_Nativ'!O17`.

Cache original: `6`. Format afișare: `0.00`.


### Motor_Meciuri!AR6

```excel
=IF(A6="","",SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405=B6)*('Istoric_Nativ'!$C$6:$C$405=BL6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT(G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6)+('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)))
```

Dependențe directe: `A6`; `'Istoric_Nativ'!$B$6:$B$405`; `B6`; `'Istoric_Nativ'!$C$6:$C$405`; `BL6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Input_Meci'!E6`.

Cache original: `73`. Format afișare: `0.00`.


### Motor_Meciuri!AS6

```excel
=IF(AR6=0,"",SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405=B6)*('Istoric_Nativ'!$C$6:$C$405=BL6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT(G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6)+('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*'Istoric_Nativ'!$Q$6:$Q$405)/AR6)
```

Dependențe directe: `AR6`; `'Istoric_Nativ'!$B$6:$B$405`; `B6`; `'Istoric_Nativ'!$C$6:$C$405`; `BL6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Input_Meci'!E6`; `'Istoric_Nativ'!$Q$6:$Q$405`.

Cache original: `9.904109589041095`. Format afișare: `0.00`.


### Motor_Meciuri!AT6

```excel
=IF(AR6<2,"",MAX(0,(SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405=B6)*('Istoric_Nativ'!$C$6:$C$405=BL6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT(G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6)+('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*'Istoric_Nativ'!$R$6:$R$405)-AR6*AS6^2)/(AR6-1)))
```

Dependențe directe: `AR6`; `'Istoric_Nativ'!$B$6:$B$405`; `B6`; `'Istoric_Nativ'!$C$6:$C$405`; `BL6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Input_Meci'!E6`; `'Istoric_Nativ'!$R$6:$R$405`; `AS6`.

Cache original: `8.92123287671235`. Format afișare: `0.00`.


### Motor_Meciuri!AU6

```excel
=IF(I6<>"PASS","",AT6/AS6)
```

Dependențe directe: `I6`; `AT6`; `AS6`.

Cache original: `0.9007607192254518`. Format afișare: `0.00`.


### Motor_Meciuri!AV6

```excel
=IF(I6<>"PASS","",IF(AU6<='Config_v6'!$B$10,"POISSON","NEGATIVE BINOMIAL"))
```

Dependențe directe: `I6`; `AU6`; `'Config_v6'!$B$10`.

Cache original: `POISSON`. Format afișare: `0.00`.


### Motor_Meciuri!AW6

```excel
=IF(I6<>"PASS","",IF(AV6="POISSON",9999,AS6/(AU6-1)))
```

Dependențe directe: `I6`; `AV6`; `AS6`; `AU6`.

Cache original: `9999`. Format afișare: `0.00`.


### Motor_Meciuri!AX6

```excel
=IF(A6="","",MAX(1-'Config_v6'!$B$20,MIN(1+'Config_v6'!$B$20,1+0.02*(IF(AND(ISNUMBER('Input_Meci'!N6),'Input_Meci'!N6>=0,'Input_Meci'!N6<=200),'Input_Meci'!N6,12)/12-1)+0.02*(IF(AND(ISNUMBER('Input_Meci'!P6),'Input_Meci'!P6>=0,'Input_Meci'!P6<=200),'Input_Meci'!P6,3.5)/3.5-1)+0.02*(IF(AND(ISNUMBER('Input_Meci'!R6),'Input_Meci'!R6>=0,'Input_Meci'!R6<=200),'Input_Meci'!R6,18)/18-1)+0.02*((IF(AND(ISNUMBER('Input_Meci'!V6),'Input_Meci'!V6>=0,'Input_Meci'!V6<=10),'Input_Meci'!V6,5)-5)/5))))
```

Dependențe directe: `A6`; `'Config_v6'!$B$20`; `'Input_Meci'!N6`; `'Input_Meci'!P6`; `'Input_Meci'!R6`; `'Input_Meci'!V6`.

Cache original: `1`. Format afișare: `0.00`.


### Motor_Meciuri!AY6

```excel
=IF(A6="","",MAX(1-'Config_v6'!$B$20,MIN(1+'Config_v6'!$B$20,1+0.02*(IF(AND(ISNUMBER('Input_Meci'!O6),'Input_Meci'!O6>=0,'Input_Meci'!O6<=200),'Input_Meci'!O6,12)/12-1)+0.02*(IF(AND(ISNUMBER('Input_Meci'!Q6),'Input_Meci'!Q6>=0,'Input_Meci'!Q6<=200),'Input_Meci'!Q6,3.5)/3.5-1)+0.02*(IF(AND(ISNUMBER('Input_Meci'!S6),'Input_Meci'!S6>=0,'Input_Meci'!S6<=200),'Input_Meci'!S6,18)/18-1)+0.02*((IF(AND(ISNUMBER('Input_Meci'!W6),'Input_Meci'!W6>=0,'Input_Meci'!W6<=10),'Input_Meci'!W6,5)-5)/5))))
```

Dependențe directe: `A6`; `'Config_v6'!$B$20`; `'Input_Meci'!O6`; `'Input_Meci'!Q6`; `'Input_Meci'!S6`; `'Input_Meci'!W6`.

Cache original: `1`. Format afișare: `0.00`.


### Motor_Meciuri!AZ6

```excel
=IF(A6="","",MAX(1-'Config_v6'!$B$21,MIN(1+'Config_v6'!$B$21,1+0.012*(IF('Input_Meci'!X6="",5,IF(ISNUMBER('Input_Meci'!X6),'Input_Meci'!X6,5))-5)+0.018*(IF('Input_Meci'!Z6="",5,IF(ISNUMBER('Input_Meci'!Z6),'Input_Meci'!Z6,5))-5)+0.012*(IF('Input_Meci'!AB6="",5,IF(ISNUMBER('Input_Meci'!AB6),'Input_Meci'!AB6,5))-5)+0.015*IF('Input_Meci'!AD6="",0,IF(ISNUMBER('Input_Meci'!AD6),'Input_Meci'!AD6,0))+0.02*IF('Input_Meci'!AF6="",0,IF(ISNUMBER('Input_Meci'!AF6),'Input_Meci'!AF6,0)))))
```

Dependențe directe: `A6`; `'Config_v6'!$B$21`; `'Input_Meci'!X6`; `'Input_Meci'!Z6`; `'Input_Meci'!AB6`; `'Input_Meci'!AD6`; `'Input_Meci'!AF6`.

Cache original: `1`. Format afișare: `0.00`.


### Motor_Meciuri!BA6

```excel
=IF(A6="","",MAX(1-'Config_v6'!$B$21,MIN(1+'Config_v6'!$B$21,1+0.012*(IF('Input_Meci'!Y6="",5,IF(ISNUMBER('Input_Meci'!Y6),'Input_Meci'!Y6,5))-5)+0.018*(IF('Input_Meci'!AA6="",5,IF(ISNUMBER('Input_Meci'!AA6),'Input_Meci'!AA6,5))-5)+0.012*(IF('Input_Meci'!AC6="",5,IF(ISNUMBER('Input_Meci'!AC6),'Input_Meci'!AC6,5))-5)+0.015*IF('Input_Meci'!AE6="",0,IF(ISNUMBER('Input_Meci'!AE6),'Input_Meci'!AE6,0))+0.02*IF('Input_Meci'!AG6="",0,IF(ISNUMBER('Input_Meci'!AG6),'Input_Meci'!AG6,0)))))
```

Dependențe directe: `A6`; `'Config_v6'!$B$21`; `'Input_Meci'!Y6`; `'Input_Meci'!AA6`; `'Input_Meci'!AC6`; `'Input_Meci'!AE6`; `'Input_Meci'!AG6`.

Cache original: `1`. Format afișare: `0.00`.


### Motor_Meciuri!BB6

```excel
=IF(I6<>"PASS","",(AVERAGE(AF6,AM6)*'Config_v6'!$B$4+AVERAGE(AH6,AO6)*'Config_v6'!$B$5+AVERAGE(AJ6,AQ6)*'Config_v6'!$B$6)*AX6*AZ6)
```

Dependențe directe: `I6`; `AF6`; `AM6`; `'Config_v6'!$B$4`; `AH6`; `AO6`; `'Config_v6'!$B$5`; `AJ6`; `AQ6`; `'Config_v6'!$B$6`; `AX6`; `AZ6`.

Cache original: `5.591554054054054`. Format afișare: `0.00`.


### Motor_Meciuri!BC6

```excel
=IF(I6<>"PASS","",(AVERAGE(AL6,AG6)*'Config_v6'!$B$4+AVERAGE(AN6,AI6)*'Config_v6'!$B$5+AVERAGE(AP6,AK6)*'Config_v6'!$B$6)*AY6*BA6)
```

Dependențe directe: `I6`; `AL6`; `AG6`; `'Config_v6'!$B$4`; `AN6`; `AI6`; `'Config_v6'!$B$5`; `AP6`; `AK6`; `'Config_v6'!$B$6`; `AY6`; `BA6`.

Cache original: `4.680405405405406`. Format afișare: `0.00`.


### Motor_Meciuri!BD6

```excel
=IF(I6<>"PASS","",BB6+BC6)
```

Dependențe directe: `I6`; `BB6`; `BC6`.

Cache original: `10.27195945945946`. Format afișare: `0.00`.


### Motor_Meciuri!BE6

```excel
=IF(A6="","",10-SUM(IF(AND(ISNUMBER('Input_Meci'!N6),'Input_Meci'!N6>=0,'Input_Meci'!N6<=200),1,0),IF(AND(ISNUMBER('Input_Meci'!O6),'Input_Meci'!O6>=0,'Input_Meci'!O6<=200),1,0),IF(AND(ISNUMBER('Input_Meci'!P6),'Input_Meci'!P6>=0,'Input_Meci'!P6<=200),1,0),IF(AND(ISNUMBER('Input_Meci'!Q6),'Input_Meci'!Q6>=0,'Input_Meci'!Q6<=200),1,0),IF(AND(ISNUMBER('Input_Meci'!R6),'Input_Meci'!R6>=0,'Input_Meci'!R6<=200),1,0),IF(AND(ISNUMBER('Input_Meci'!S6),'Input_Meci'!S6>=0,'Input_Meci'!S6<=200),1,0),IF(AND(ISNUMBER('Input_Meci'!T6),'Input_Meci'!T6>=0,'Input_Meci'!T6<=100),1,0),IF(AND(ISNUMBER('Input_Meci'!U6),'Input_Meci'!U6>=0,'Input_Meci'!U6<=100),1,0),IF(AND(ISNUMBER('Input_Meci'!V6),'Input_Meci'!V6>=0,'Input_Meci'!V6<=10),1,0),IF(AND(ISNUMBER('Input_Meci'!W6),'Input_Meci'!W6>=0,'Input_Meci'!W6<=10),1,0)))
```

Dependențe directe: `A6`; `'Input_Meci'!N6`; `'Input_Meci'!O6`; `'Input_Meci'!P6`; `'Input_Meci'!Q6`; `'Input_Meci'!R6`; `'Input_Meci'!S6`; `'Input_Meci'!T6`; `'Input_Meci'!U6`; `'Input_Meci'!V6`; `'Input_Meci'!W6`.

Cache original: `10`. Format afișare: `0.00`.


### Motor_Meciuri!BF6

```excel
=IF(I6<>"PASS","",MAX(0,MIN(IF(OR(M6="YES",BL6<>C6),'Config_v6'!$B$34,100),ROUND(40+25*MIN(1,MIN(N6,Q6)/'Config_v6'!$B$7)*MIN(1,MIN(O6,R6)/'Config_v6'!$B$8)*MIN(1,MIN(P6,S6)/'Config_v6'!$B$9)+MAX(0,15-2*ABS(AF6-AJ6)-2*ABS(AL6-AP6))+IF(AU6<='Config_v6'!$B$10,15,IF(AU6<='Config_v6'!$B$11,13,IF(AU6<='Config_v6'!$B$12,10,IF(AU6<='Config_v6'!$B$13,6,0))))+5-BE6/10*'Config_v6'!$B$38,0))))
```

Dependențe directe: `I6`; `M6`; `BL6`; `C6`; `'Config_v6'!$B$34`; `N6`; `Q6`; `'Config_v6'!$B$7`; `O6`; `R6`; `'Config_v6'!$B$8`; `P6`; `S6`; `'Config_v6'!$B$9`; `AF6`; `AJ6`; `AL6`; `AP6`; `AU6`; `'Config_v6'!$B$10`; `'Config_v6'!$B$11`; `'Config_v6'!$B$12`; `'Config_v6'!$B$13`; `BE6`; `'Config_v6'!$B$38`.

Cache original: `90`. Format afișare: `0.00`.


### Motor_Meciuri!BG6

```excel
=IF(I6<>"PASS","",MIN(1,'Config_v6'!$B$14*(0.7+0.3*MIN(1,AR6/'Config_v6'!$B$15))*IF(AU6<='Config_v6'!$B$10,1,IF(AU6<='Config_v6'!$B$11,0.95,IF(AU6<='Config_v6'!$B$12,0.88,0.78)))*(0.75+0.25*BF6/100)))
```

Dependențe directe: `I6`; `'Config_v6'!$B$14`; `AR6`; `'Config_v6'!$B$15`; `AU6`; `'Config_v6'!$B$10`; `'Config_v6'!$B$11`; `'Config_v6'!$B$12`; `BF6`.

Cache original: `0.7995`. Format afișare: `0.00`.


### Motor_Meciuri!BH6

```excel
=IF(I6<>"PASS","",MIN(1,(ABS(AZ6-1)+ABS(BA6-1))*3))
```

Dependențe directe: `I6`; `AZ6`; `BA6`.

Cache original: `0`. Format afișare: `0.00`.


### Motor_Meciuri!BI6

```excel
=IF(A6="","",IF(AND(OR('Input_Meci'!X6="",AND(ISNUMBER('Input_Meci'!X6),'Input_Meci'!X6>=0,'Input_Meci'!X6<=10)),OR('Input_Meci'!Y6="",AND(ISNUMBER('Input_Meci'!Y6),'Input_Meci'!Y6>=0,'Input_Meci'!Y6<=10)),OR('Input_Meci'!Z6="",AND(ISNUMBER('Input_Meci'!Z6),'Input_Meci'!Z6>=0,'Input_Meci'!Z6<=10)),OR('Input_Meci'!AA6="",AND(ISNUMBER('Input_Meci'!AA6),'Input_Meci'!AA6>=0,'Input_Meci'!AA6<=10)),OR('Input_Meci'!AB6="",AND(ISNUMBER('Input_Meci'!AB6),'Input_Meci'!AB6>=0,'Input_Meci'!AB6<=10)),OR('Input_Meci'!AC6="",AND(ISNUMBER('Input_Meci'!AC6),'Input_Meci'!AC6>=0,'Input_Meci'!AC6<=10)),OR('Input_Meci'!AD6="",AND(ISNUMBER('Input_Meci'!AD6),'Input_Meci'!AD6>=-2,'Input_Meci'!AD6<=2)),OR('Input_Meci'!AE6="",AND(ISNUMBER('Input_Meci'!AE6),'Input_Meci'!AE6>=-2,'Input_Meci'!AE6<=2)),OR('Input_Meci'!AF6="",AND(ISNUMBER('Input_Meci'!AF6),'Input_Meci'!AF6>=-2,'Input_Meci'!AF6<=2)),OR('Input_Meci'!AG6="",AND(ISNUMBER('Input_Meci'!AG6),'Input_Meci'!AG6>=-2,'Input_Meci'!AG6<=2))),"VALID","INVALID"))
```

Dependențe directe: `A6`; `'Input_Meci'!X6`; `'Input_Meci'!Y6`; `'Input_Meci'!Z6`; `'Input_Meci'!AA6`; `'Input_Meci'!AB6`; `'Input_Meci'!AC6`; `'Input_Meci'!AD6`; `'Input_Meci'!AE6`; `'Input_Meci'!AF6`; `'Input_Meci'!AG6`.

Cache original: `VALID`. Format afișare: `General`.


### Motor_Meciuri!BJ6

```excel
=IF(A6="",0,SUM('Core_Nativ'!S6:S11))
```

Dependențe directe: `A6`; `'Core_Nativ'!S6:S11`.

Cache original: `0`. Format afișare: `General`.


### Motor_Meciuri!BK6

```excel
='Config_v6'!$B$40
```

Dependențe directe: `'Config_v6'!$B$40`.

Cache original: `VALID`. Format afișare: `General`.


### Motor_Meciuri!BL6

```excel
=IF(A6="","",IF(SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405=B6)*('Istoric_Nativ'!$C$6:$C$405=C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT(G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6)+('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0))>='Config_v6'!$B$41,C6,IF(AND('Input_Meci'!L6="YES",'Input_Meci'!K6<>"",'Input_Meci'!K6<C6,COUNTIF('Core_Nativ'!R12:R17,"CLOSED")=6,SUM('Core_Nativ'!S12:S17)=0),'Input_Meci'!K6,C6)))
```

Dependențe directe: `A6`; `'Istoric_Nativ'!$B$6:$B$405`; `B6`; `'Istoric_Nativ'!$C$6:$C$405`; `C6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Input_Meci'!E6`; `'Config_v6'!$B$41`; `'Input_Meci'!L6`; `'Input_Meci'!K6`; `'Core_Nativ'!R12:R17`; `'Core_Nativ'!S12:S17`.

Cache original: `2025/26`. Format afișare: `General`.


### Motor_Meciuri!BM6

```excel
=IF(OR(A6="",N6=0),0,LARGE(_xlfn._xlws.FILTER('Istoric_Nativ'!$D$6:$D$405,('Istoric_Nativ'!$B$6:$B$405=B6)*('Istoric_Nativ'!$C$6:$C$405=C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT(G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6))>0)),MIN(10,N6)))
```

Dependențe directe: `A6`; `N6`; `'Istoric_Nativ'!$D$6:$D$405`; `'Istoric_Nativ'!$B$6:$B$405`; `B6`; `'Istoric_Nativ'!$C$6:$C$405`; `C6`; `'Istoric_Nativ'!$P$6:$P$405`; `G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`.

Cache original: `2026-03-01T00:00:00`. Format afișare: `yyyy-mm-dd hh:mm`.


### Motor_Meciuri!BN6

```excel
=IF(OR(A6="",Q6=0),0,LARGE(_xlfn._xlws.FILTER('Istoric_Nativ'!$D$6:$D$405,('Istoric_Nativ'!$B$6:$B$405=B6)*('Istoric_Nativ'!$C$6:$C$405=C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT(G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)),MIN(10,Q6)))
```

Dependențe directe: `A6`; `Q6`; `'Istoric_Nativ'!$D$6:$D$405`; `'Istoric_Nativ'!$B$6:$B$405`; `B6`; `'Istoric_Nativ'!$C$6:$C$405`; `C6`; `'Istoric_Nativ'!$P$6:$P$405`; `G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!E6`; `'Istoric_Nativ'!$F$6:$F$405`.

Cache original: `2026-03-01T00:00:00`. Format afișare: `yyyy-mm-dd hh:mm`.


### Motor_Meciuri!BO6

```excel
=IF(OR(A6="",N6=0),0,LARGE(_xlfn._xlws.FILTER('Istoric_Nativ'!$D$6:$D$405,('Istoric_Nativ'!$B$6:$B$405=B6)*('Istoric_Nativ'!$C$6:$C$405=C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT(G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6))>0)),MIN(20,N6)))
```

Dependențe directe: `A6`; `N6`; `'Istoric_Nativ'!$D$6:$D$405`; `'Istoric_Nativ'!$B$6:$B$405`; `B6`; `'Istoric_Nativ'!$C$6:$C$405`; `C6`; `'Istoric_Nativ'!$P$6:$P$405`; `G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`.

Cache original: `2025-12-27T00:00:00`. Format afișare: `yyyy-mm-dd hh:mm`.


### Motor_Meciuri!BP6

```excel
=IF(OR(A6="",Q6=0),0,LARGE(_xlfn._xlws.FILTER('Istoric_Nativ'!$D$6:$D$405,('Istoric_Nativ'!$B$6:$B$405=B6)*('Istoric_Nativ'!$C$6:$C$405=C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT(G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)),MIN(20,Q6)))
```

Dependențe directe: `A6`; `Q6`; `'Istoric_Nativ'!$D$6:$D$405`; `'Istoric_Nativ'!$B$6:$B$405`; `B6`; `'Istoric_Nativ'!$C$6:$C$405`; `C6`; `'Istoric_Nativ'!$P$6:$P$405`; `G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!E6`; `'Istoric_Nativ'!$F$6:$F$405`.

Cache original: `2025-12-26T00:00:00`. Format afișare: `yyyy-mm-dd hh:mm`.


### Motor_Meciuri!BQ6

```excel
=IF(A6="","",IF(AND(COUNTIF(MatchesTable[Match_ID],A6)=1,COUNTIFS(MatchesTable[League],B6,MatchesTable[Season],C6,MatchesTable[Home],'Input_Meci'!D6,MatchesTable[Away],'Input_Meci'!E6,MatchesTable[Kickoff_UTC],F6)=1,B6<>"",C6<>"",'Input_Meci'!D6<>"",'Input_Meci'!E6<>"",'Input_Meci'!D6<>'Input_Meci'!E6,ISNUMBER(F6),ISNUMBER(G6),G6<F6,OR(E6="LIVE",E6="REPLAY"),OR('Input_Meci'!L6="YES",'Input_Meci'!L6="NO",'Input_Meci'!L6="")),"VALID","INVALID"))
```

Dependențe directe: `A6`; `MatchesTable[Match_ID]`; `MatchesTable[League]`; `B6`; `MatchesTable[Season]`; `C6`; `MatchesTable[Home]`; `'Input_Meci'!D6`; `MatchesTable[Away]`; `'Input_Meci'!E6`; `MatchesTable[Kickoff_UTC]`; `F6`; `G6`; `E6`; `'Input_Meci'!L6`.

Cache original: `VALID`. Format afișare: `General`.


### Motor_Meciuri!BR6

```excel
=IF(I6<>"PASS",0,SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405='Input_Meci'!B6)*('Istoric_Nativ'!$C$6:$C$405='Input_Meci'!C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT('Input_Meci'!G6))*((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)))
```

Dependențe directe: `I6`; `'Istoric_Nativ'!$B$6:$B$405`; `'Input_Meci'!B6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Input_Meci'!C6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `'Input_Meci'!G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Input_Meci'!E6`.

Cache original: `36`. Format afișare: `General`.


### Motor_Meciuri!BS6

```excel
=IF(I6<>"PASS",0,SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405='Input_Meci'!B6)*('Istoric_Nativ'!$C$6:$C$405='Input_Meci'!C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT('Input_Meci'!G6))*((((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6))>0)*('Istoric_Nativ'!$D$6:$D$405>=BM6)+((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*('Istoric_Nativ'!$D$6:$D$405>=BN6))>0)))
```

Dependențe directe: `I6`; `'Istoric_Nativ'!$B$6:$B$405`; `'Input_Meci'!B6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Input_Meci'!C6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `'Input_Meci'!G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `BM6`; `'Input_Meci'!E6`; `BN6`.

Cache original: `20`. Format afișare: `General`.


### Motor_Meciuri!BT6

```excel
=IF(I6<>"PASS",0,SUMPRODUCT(('Istoric_Nativ'!$B$6:$B$405='Input_Meci'!B6)*('Istoric_Nativ'!$C$6:$C$405='Input_Meci'!C6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<INT('Input_Meci'!G6))*((((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!D6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!D6))>0)*('Istoric_Nativ'!$D$6:$D$405>=BO6)+((('Istoric_Nativ'!$E$6:$E$405='Input_Meci'!E6)+('Istoric_Nativ'!$F$6:$F$405='Input_Meci'!E6))>0)*('Istoric_Nativ'!$D$6:$D$405>=BP6))>0)))
```

Dependențe directe: `I6`; `'Istoric_Nativ'!$B$6:$B$405`; `'Input_Meci'!B6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Input_Meci'!C6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$D$6:$D$405`; `'Input_Meci'!G6`; `'Istoric_Nativ'!$E$6:$E$405`; `'Input_Meci'!D6`; `'Istoric_Nativ'!$F$6:$F$405`; `BO6`; `'Input_Meci'!E6`; `BP6`.

Cache original: `40`. Format afișare: `General`.



## Core_Nativ

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
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

### Core_Nativ!B6

```excel
=IF('Input_Meci'!A6="","",'Input_Meci'!A6)
```

Dependențe directe: `'Input_Meci'!A6`.

Cache original: `REPLAY_1`. Format afișare: `General`.


### Core_Nativ!E6

```excel
=IF(B6="","",'Input_Meci'!B6)
```

Dependențe directe: `B6`; `'Input_Meci'!B6`.

Cache original: `E0`. Format afișare: `General`.


### Core_Nativ!F6

```excel
=IF(B6="","",IF('Input_Meci'!C6="","",'Input_Meci'!C6))
```

Dependențe directe: `B6`; `'Input_Meci'!C6`.

Cache original: `2025/26`. Format afișare: `General`.


### Core_Nativ!G6

```excel
=IF(B6="","",'Input_Meci'!D6)
```

Dependențe directe: `B6`; `'Input_Meci'!D6`.

Cache original: `Brighton`. Format afișare: `General`.


### Core_Nativ!J6

```excel
=IF(AND(B6<>"",ISNUMBER('Input_Meci'!G6)),INT('Input_Meci'!G6),0)
```

Dependențe directe: `B6`; `'Input_Meci'!G6`.

Cache original: `2026-05-23T00:00:00`. Format afișare: `yyyy-mm-dd hh:mm`.


### Core_Nativ!K6

```excel
=IF(OR(B6="",F6=""),0,IF(H6="HOME",COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1),IF(H6="AWAY",COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1),COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1)+COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1))))
```

Dependențe directe: `B6`; `F6`; `H6`; `'Istoric_Nativ'!$B$6:$B$405`; `E6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Istoric_Nativ'!$E$6:$E$405`; `G6`; `'Istoric_Nativ'!$D$6:$D$405`; `J6`; `'Istoric_Nativ'!$P$6:$P$405`; `'Istoric_Nativ'!$F$6:$F$405`.

Cache original: `37`. Format afișare: `General`.


### Core_Nativ!L6

```excel
=IF(AND(B6<>"",I6="RECENT",K6>0),LARGE(_xlfn._xlws.FILTER('Istoric_Nativ'!$D$6:$D$405,('Istoric_Nativ'!$B$6:$B$405=E6)*('Istoric_Nativ'!$C$6:$C$405=F6)*('Istoric_Nativ'!$P$6:$P$405=1)*('Istoric_Nativ'!$D$6:$D$405<J6)*((('Istoric_Nativ'!$E$6:$E$405=G6)+('Istoric_Nativ'!$F$6:$F$405=G6))>0)),MIN('Config_v6'!$B$54,K6)),0)
```

Dependențe directe: `B6`; `I6`; `K6`; `'Istoric_Nativ'!$D$6:$D$405`; `'Istoric_Nativ'!$B$6:$B$405`; `E6`; `'Istoric_Nativ'!$C$6:$C$405`; `F6`; `'Istoric_Nativ'!$P$6:$P$405`; `J6`; `'Istoric_Nativ'!$E$6:$E$405`; `G6`; `'Istoric_Nativ'!$F$6:$F$405`; `'Config_v6'!$B$54`.

Cache original: `00:00:00`. Format afișare: `yyyy-mm-dd hh:mm;;`.


### Core_Nativ!M6

```excel
=IF(OR(B6="",F6=""),0,IF(H6="HOME",COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6),IF(H6="AWAY",COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6),COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6)+COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6))))
```

Dependențe directe: `B6`; `F6`; `H6`; `'Istoric_Nativ'!$B$6:$B$405`; `E6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Istoric_Nativ'!$E$6:$E$405`; `G6`; `'Istoric_Nativ'!$D$6:$D$405`; `J6`; `'Istoric_Nativ'!$P$6:$P$405`; `L6`; `'Istoric_Nativ'!$F$6:$F$405`.

Cache original: `37`. Format afișare: `General`.


### Core_Nativ!N6

```excel
=IF(M6=0,"",IF(H6="HOME",SUMIFS('Istoric_Nativ'!$G$6:$G$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6),IF(H6="AWAY",SUMIFS('Istoric_Nativ'!$H$6:$H$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6),SUMIFS('Istoric_Nativ'!$G$6:$G$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6)+SUMIFS('Istoric_Nativ'!$H$6:$H$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6)))/M6)
```

Dependențe directe: `M6`; `H6`; `'Istoric_Nativ'!$G$6:$G$405`; `'Istoric_Nativ'!$B$6:$B$405`; `E6`; `'Istoric_Nativ'!$C$6:$C$405`; `F6`; `'Istoric_Nativ'!$E$6:$E$405`; `G6`; `'Istoric_Nativ'!$D$6:$D$405`; `J6`; `'Istoric_Nativ'!$P$6:$P$405`; `L6`; `'Istoric_Nativ'!$H$6:$H$405`; `'Istoric_Nativ'!$F$6:$F$405`.

Cache original: `5`. Format afișare: `0.00`.


### Core_Nativ!O6

```excel
=IF(M6=0,"",IF(H6="HOME",SUMIFS('Istoric_Nativ'!$H$6:$H$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6),IF(H6="AWAY",SUMIFS('Istoric_Nativ'!$G$6:$G$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6),SUMIFS('Istoric_Nativ'!$H$6:$H$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6)+SUMIFS('Istoric_Nativ'!$G$6:$G$405,'Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$P$6:$P$405,1,'Istoric_Nativ'!$D$6:$D$405,">="&L6)))/M6)
```

Dependențe directe: `M6`; `H6`; `'Istoric_Nativ'!$H$6:$H$405`; `'Istoric_Nativ'!$B$6:$B$405`; `E6`; `'Istoric_Nativ'!$C$6:$C$405`; `F6`; `'Istoric_Nativ'!$E$6:$E$405`; `G6`; `'Istoric_Nativ'!$D$6:$D$405`; `J6`; `'Istoric_Nativ'!$P$6:$P$405`; `L6`; `'Istoric_Nativ'!$G$6:$G$405`; `'Istoric_Nativ'!$F$6:$F$405`.

Cache original: `4.864864864864865`. Format afișare: `0.00`.


### Core_Nativ!P6

```excel
='Config_v6'!$B$7
```

Dependențe directe: `'Config_v6'!$B$7`.

Cache original: `10`. Format afișare: `General`.


### Core_Nativ!Q6

```excel
=IF(OR(B6="",F6=""),0,IFERROR(MATCH(E6&"|"&F6,SourceTable[Source_Key],0),0))
```

Dependențe directe: `B6`; `F6`; `E6`; `SourceTable[Source_Key]`.

Cache original: `1`. Format afișare: `General`.


### Core_Nativ!R6

```excel
=IF(B6="","",IF(F6="","UNUSED",IF(Q6=0,"NOT CHECKED",IF(COUNTIF(SourceTable[Source_Key],E6&"|"&F6)<>1,"SOURCE CONFLICT",IF(NOT(OR(INDEX(SourceTable[Status],MAX(1,Q6))="IMPORTED",INDEX(SourceTable[Status],MAX(1,Q6))="PARTIAL",INDEX(SourceTable[Status],MAX(1,Q6))="SOURCE CONFLICT")),"ACCESS BLOCKED",IF(OR(INDEX(SourceTable[Coverage],Q6)<>"FULL SEASON EXPORT",INDEX(SourceTable[URL],Q6)="",INDEX(SourceTable[SHA256],Q6)=""),"EVIDENCE INCOMPLETE",IF(AND('Input_Meci'!H6="LIVE",INDEX(SourceTable[Retrieved_UTC],Q6)>'Input_Meci'!G6),"POST CUTOFF","CLOSED")))))))
```

Dependențe directe: `B6`; `F6`; `Q6`; `SourceTable[Source_Key]`; `E6`; `SourceTable[Status]`; `SourceTable[Coverage]`; `SourceTable[URL]`; `SourceTable[SHA256]`; `'Input_Meci'!H6`; `SourceTable[Retrieved_UTC]`; `'Input_Meci'!G6`.

Cache original: `CLOSED`. Format afișare: `General`.


### Core_Nativ!S6

```excel
=IF(OR(B6="",F6=""),0,COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$O$6:$O$405,"INVALID")+COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$O$6:$O$405,"INVALID",'Istoric_Nativ'!$D$6:$D$405,"*")+COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$E$6:$E$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$O$6:$O$405,"SOURCE CONFLICT")+COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$O$6:$O$405,"INVALID")+COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$O$6:$O$405,"INVALID",'Istoric_Nativ'!$D$6:$D$405,"*")+COUNTIFS('Istoric_Nativ'!$B$6:$B$405,E6,'Istoric_Nativ'!$C$6:$C$405,F6,'Istoric_Nativ'!$F$6:$F$405,G6,'Istoric_Nativ'!$D$6:$D$405,"<"&J6,'Istoric_Nativ'!$O$6:$O$405,"SOURCE CONFLICT"))
```

Dependențe directe: `B6`; `F6`; `'Istoric_Nativ'!$B$6:$B$405`; `E6`; `'Istoric_Nativ'!$C$6:$C$405`; `'Istoric_Nativ'!$E$6:$E$405`; `G6`; `'Istoric_Nativ'!$D$6:$D$405`; `J6`; `'Istoric_Nativ'!$O$6:$O$405`; `'Istoric_Nativ'!$F$6:$F$405`.

Cache original: `0`. Format afișare: `General`.


### Core_Nativ!T6

```excel
=IF(B6="","",IF(R6<>"CLOSED",R6,IF(S6>0,"NATIVE INPUT ISSUE",IF(M6=0,"NO HISTORY",IF(M6<P6,"SMALL SAMPLE","DERIVED")))))
```

Dependențe directe: `B6`; `R6`; `S6`; `M6`; `P6`.

Cache original: `DERIVED`. Format afișare: `General`.


### Core_Nativ!U6

```excel
=IF(B6="","","NativeTable; "&E6&"; "&F6&"; "&G6&"; "&H6&"; before "&TEXT(J6,"yyyy-mm-dd")&IF(I6="RECENT","; from "&TEXT(L6,"yyyy-mm-dd"),""))
```

Dependențe directe: `B6`; `E6`; `F6`; `G6`; `H6`; `J6`; `I6`; `L6`.

Cache original: `NativeTable; E0; 2025/26; Brighton; ANY; before 2026-05-23`. Format afișare: `General`.


### Core_Nativ!F12

```excel
=IF(B12="","",IF('Input_Meci'!K6="","",'Input_Meci'!K6))
```

Dependențe directe: `B12`; `'Input_Meci'!K6`.

Cache original: `None`. Format afișare: `General`.


### Core_Nativ!G15

```excel
=IF(B15="","",'Input_Meci'!E6)
```

Dependențe directe: `B15`; `'Input_Meci'!E6`.

Cache original: `Man United`. Format afișare: `General`.



## Distributie

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
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

### Distributie!A6

```excel
=IF('Motor_Meciuri'!A6="","",'Motor_Meciuri'!A6)
```

Dependențe directe: `'Motor_Meciuri'!A6`.

Cache original: `REPLAY_1`. Format afișare: `General`.


### Distributie!B6

```excel
=IF('Motor_Meciuri'!I6<>"PASS","",'Motor_Meciuri'!BD6)
```

Dependențe directe: `'Motor_Meciuri'!I6`; `'Motor_Meciuri'!BD6`.

Cache original: `10.27195945945946`. Format afișare: `General`.


### Distributie!C6

```excel
=IF(B6="","",'Motor_Meciuri'!AU6)
```

Dependențe directe: `B6`; `'Motor_Meciuri'!AU6`.

Cache original: `0.9007607192254518`. Format afișare: `General`.


### Distributie!D6

```excel
=IF(B6="","",'Motor_Meciuri'!AW6)
```

Dependențe directe: `B6`; `'Motor_Meciuri'!AW6`.

Cache original: `9999`. Format afișare: `General`.


### Distributie!E6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,EXP(-B6),(D6/(D6+B6))^D6))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `D6`.

Cache original: `3.458953219263637e-05`. Format afișare: `General`.


### Distributie!F6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,E6*B6/1,E6*(D6+0)/1*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `E6`; `D6`.

Cache original: `0.0003553022724044287`. Format afișare: `General`.


### Distributie!G6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,F6*B6/2,F6*(D6+1)/2*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `F6`; `D6`.

Cache original: `0.0018248252689960565`. Format afișare: `General`.


### Distributie!H6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,G6*B6/3,G6*(D6+2)/3*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `G6`; `D6`.

Cache original: `0.006248177061241565`. Format afișare: `General`.


### Distributie!I6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,H6*B6/4,H6*(D6+3)/4*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `H6`; `D6`.

Cache original: `0.016045255367149475`. Format afișare: `General`.


### Distributie!J6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,I6*B6/5,I6*(D6+4)/5*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `I6`; `D6`.

Cache original: `0.032963242529606744`. Format afișare: `General`.


### Distributie!K6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,J6*B6/6,J6*(D6+5)/6*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `J6`; `D6`.

Cache original: `0.056432848486075056`. Format afișare: `General`.


### Distributie!L6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,K6*B6/7,K6*(D6+6)/7*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `K6`; `D6`.

Cache original: `0.0828108474043973`. Format afișare: `General`.


### Distributie!M6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,L6*B6/8,L6*(D6+7)/8*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `L6`; `D6`.

Cache original: `0.10632870841768159`. Format afișare: `General`.


### Distributie!N6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,M6*B6/9,M6*(D6+8)/9*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `M6`; `D6`.

Cache original: `0.12135602024923456`. Format afișare: `General`.


### Distributie!O6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,N6*B6/10,N6*(D6+9)/10*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `N6`; `D6`.

Cache original: `0.12465641201614786`. Format afișare: `General`.


### Distributie!P6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,O6*B6/11,O6*(D6+10)/11*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `O6`; `D6`.

Cache original: `0.11640596459923143`. Format afișare: `General`.


### Distributie!Q6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,P6*B6/12,P6*(D6+11)/12*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `P6`; `D6`.

Cache original: `0.09964311243354819`. Format afișare: `General`.


### Distributie!R6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,Q6*B6/13,Q6*(D6+12)/13*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `Q6`; `D6`.

Cache original: `0.07873307779475137`. Format afișare: `General`.


### Distributie!S6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,R6*B6/14,R6*(D6+13)/14*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `R6`; `D6`.

Cache original: `0.05776735594472528`. Format afișare: `General`.


### Distributie!T6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,S6*B6/15,S6*(D6+14)/15*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `S6`; `D6`.

Cache original: `0.039558929222958825`. Format afișare: `General`.


### Distributie!U6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,T6*B6/16,T6*(D6+15)/16*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `T6`; `D6`.

Cache original: `0.0253967323273662`. Format afișare: `General`.


### Distributie!V6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,U6*B6/17,U6*(D6+16)/17*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `U6`; `D6`.

Cache original: `0.01534554146290877`. Format afișare: `General`.


### Distributie!W6

```excel
=IF(B6="","",IF(C6<='Config_v6'!$B$10,V6*B6/18,V6*(D6+17)/18*B6/(D6+B6)))
```

Dependențe directe: `B6`; `C6`; `'Config_v6'!$B$10`; `V6`; `D6`.

Cache original: `0.00875715443280295`. Format afișare: `General`.


### Distributie!X6

```excel
=IF(B6="","",MIN(1,SUM(E6:E6)))
```

Dependențe directe: `B6`; `E6:E6`.

Cache original: `3.458953219263637e-05`. Format afișare: `General`.


### Distributie!Y6

```excel
=IF(B6="","",MIN(1,SUM(E6:F6)))
```

Dependențe directe: `B6`; `E6:F6`.

Cache original: `0.0003898918045970651`. Format afișare: `General`.


### Distributie!Z6

```excel
=IF(B6="","",MIN(1,SUM(E6:G6)))
```

Dependențe directe: `B6`; `E6:G6`.

Cache original: `0.0022147170735931218`. Format afișare: `General`.


### Distributie!AA6

```excel
=IF(B6="","",MIN(1,SUM(E6:H6)))
```

Dependențe directe: `B6`; `E6:H6`.

Cache original: `0.008462894134834687`. Format afișare: `General`.


### Distributie!AB6

```excel
=IF(B6="","",MIN(1,SUM(E6:I6)))
```

Dependențe directe: `B6`; `E6:I6`.

Cache original: `0.024508149501984162`. Format afișare: `General`.


### Distributie!AC6

```excel
=IF(B6="","",MIN(1,SUM(E6:J6)))
```

Dependențe directe: `B6`; `E6:J6`.

Cache original: `0.05747139203159091`. Format afișare: `General`.


### Distributie!AD6

```excel
=IF(B6="","",MIN(1,SUM(E6:K6)))
```

Dependențe directe: `B6`; `E6:K6`.

Cache original: `0.11390424051766596`. Format afișare: `General`.


### Distributie!AE6

```excel
=IF(B6="","",MIN(1,SUM(E6:L6)))
```

Dependențe directe: `B6`; `E6:L6`.

Cache original: `0.19671508792206327`. Format afișare: `General`.


### Distributie!AF6

```excel
=IF(B6="","",MIN(1,SUM(E6:M6)))
```

Dependențe directe: `B6`; `E6:M6`.

Cache original: `0.3030437963397449`. Format afișare: `General`.


### Distributie!AG6

```excel
=IF(B6="","",MIN(1,SUM(E6:N6)))
```

Dependențe directe: `B6`; `E6:N6`.

Cache original: `0.4243998165889794`. Format afișare: `General`.


### Distributie!AH6

```excel
=IF(B6="","",MIN(1,SUM(E6:O6)))
```

Dependențe directe: `B6`; `E6:O6`.

Cache original: `0.5490562286051273`. Format afișare: `General`.


### Distributie!AI6

```excel
=IF(B6="","",MIN(1,SUM(E6:P6)))
```

Dependențe directe: `B6`; `E6:P6`.

Cache original: `0.6654621932043587`. Format afișare: `General`.


### Distributie!AJ6

```excel
=IF(B6="","",MIN(1,SUM(E6:Q6)))
```

Dependențe directe: `B6`; `E6:Q6`.

Cache original: `0.7651053056379069`. Format afișare: `General`.


### Distributie!AK6

```excel
=IF(B6="","",MIN(1,SUM(E6:R6)))
```

Dependențe directe: `B6`; `E6:R6`.

Cache original: `0.8438383834326583`. Format afișare: `General`.


### Distributie!AL6

```excel
=IF(B6="","",MIN(1,SUM(E6:S6)))
```

Dependențe directe: `B6`; `E6:S6`.

Cache original: `0.9016057393773835`. Format afișare: `General`.


### Distributie!AM6

```excel
=IF(B6="","",MIN(1,SUM(E6:T6)))
```

Dependențe directe: `B6`; `E6:T6`.

Cache original: `0.9411646686003423`. Format afișare: `General`.


### Distributie!AN6

```excel
=IF(B6="","",MIN(1,SUM(E6:U6)))
```

Dependențe directe: `B6`; `E6:U6`.

Cache original: `0.9665614009277085`. Format afișare: `General`.


### Distributie!AO6

```excel
=IF(B6="","",MIN(1,SUM(E6:V6)))
```

Dependențe directe: `B6`; `E6:V6`.

Cache original: `0.9819069423906173`. Format afișare: `General`.


### Distributie!AP6

```excel
=IF(B6="","",MIN(1,SUM(E6:W6)))
```

Dependențe directe: `B6`; `E6:W6`.

Cache original: `0.9906640968234202`. Format afișare: `General`.



## Input_Meci

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
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


## Istoric_Nativ

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
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

### Istoric_Nativ!N6

```excel
=IF(AND(A6<>"",ISNUMBER(D6)),B6&"|"&C6&"|"&TEXT(D6,"yyyymmdd")&"|"&E6&"|"&F6,"")
```

Dependențe directe: `A6`; `D6`; `B6`; `C6`; `E6`; `F6`.

Cache original: `E0|2025/26|20250815|Liverpool|Bournemouth`. Format afișare: `General`.


### Istoric_Nativ!O6

```excel
=IF(A6="","",IFERROR(IF(NOT(AND(B6<>"",C6<>"",ISNUMBER(D6),D6>0,E6<>"",F6<>"",E6<>F6,ISNUMBER(G6),ISNUMBER(H6),G6>=0,H6>=0,G6<=100,H6<=100,MOD(G6,1)=0,MOD(H6,1)=0,L6="FT90",S6>0,INDEX(SourceTable[League],MAX(1,S6))=B6,INDEX(SourceTable[Season],MAX(1,S6))=C6,ISNUMBER(K6),K6=INDEX(SourceTable[Retrieved_UTC],MAX(1,S6)),J6<>"",M6<>"")),"INVALID",IF(OR(COUNTIFS('Istoric_Nativ'!$N$6:$N$405,N6,'Istoric_Nativ'!$G$6:$G$405,G6)<>COUNTIF('Istoric_Nativ'!$N$6:$N$405,N6),COUNTIFS('Istoric_Nativ'!$N$6:$N$405,N6,'Istoric_Nativ'!$H$6:$H$405,H6)<>COUNTIF('Istoric_Nativ'!$N$6:$N$405,N6)),"SOURCE CONFLICT",IF(COUNTIF($N$6:N6,N6)>1,"DUPLICATE","VALID"))),"INVALID"))
```

Dependențe directe: `A6`; `B6`; `C6`; `D6`; `E6`; `F6`; `G6`; `H6`; `L6`; `S6`; `SourceTable[League]`; `SourceTable[Season]`; `K6`; `SourceTable[Retrieved_UTC]`; `J6`; `M6`; `'Istoric_Nativ'!$N$6:$N$405`; `N6`; `'Istoric_Nativ'!$G$6:$G$405`; `'Istoric_Nativ'!$H$6:$H$405`; `$N$6:N6`.

Cache original: `VALID`. Format afișare: `General`.


### Istoric_Nativ!P6

```excel
=IF(O6="VALID",1,0)
```

Dependențe directe: `O6`.

Cache original: `1`. Format afișare: `General`.


### Istoric_Nativ!Q6

```excel
=IF(P6=1,G6+H6,0)
```

Dependențe directe: `P6`; `G6`; `H6`.

Cache original: `13`. Format afișare: `General`.


### Istoric_Nativ!R6

```excel
=Q6^2
```

Dependențe directe: `Q6`.

Cache original: `169`. Format afișare: `General`.


### Istoric_Nativ!S6

```excel
=IF(A6="","",IFERROR(MATCH(I6,SourceTable[Source_ID],0),0))
```

Dependențe directe: `A6`; `I6`; `SourceTable[Source_ID]`.

Cache original: `1`. Format afișare: `General`.



## Surse_Import

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
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

### Surse_Import!M6

```excel
=IF(A6="","",B6&"|"&C6)
```

Dependențe directe: `A6`; `B6`; `C6`.

Cache original: `E0|2025/26`. Format afișare: `General`.



## Calibrare_Linii

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
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

### Calibrare_Linii!M6

```excel
=IF(AND(ISNUMBER(I6),ISNUMBER(J6)),COUNTIFS(OOSTable[Line],A6,OOSTable[League],H6,OOSTable[Model_Signature],V6,OOSTable[Record_Valid],1,OOSTable[Settled_UTC],"<="&J6,OOSTable[Snapshot_UTC],">"&I6,OOSTable[Training_End_UTC],I6),0)
```

Dependențe directe: `I6`; `J6`; `OOSTable[Line]`; `A6`; `OOSTable[League]`; `H6`; `OOSTable[Model_Signature]`; `V6`; `OOSTable[Record_Valid]`; `OOSTable[Settled_UTC]`; `OOSTable[Snapshot_UTC]`; `OOSTable[Training_End_UTC]`.

Cache original: `0`. Format afișare: `General`.


### Calibrare_Linii!N6

```excel
=IF(M6=0,0,SUMIFS(OOSTable[Win],OOSTable[Line],A6,OOSTable[League],H6,OOSTable[Model_Signature],V6,OOSTable[Record_Valid],1,OOSTable[Settled_UTC],"<="&J6,OOSTable[Snapshot_UTC],">"&I6,OOSTable[Training_End_UTC],I6))
```

Dependențe directe: `M6`; `OOSTable[Win]`; `OOSTable[Line]`; `A6`; `OOSTable[League]`; `H6`; `OOSTable[Model_Signature]`; `V6`; `OOSTable[Record_Valid]`; `OOSTable[Settled_UTC]`; `J6`; `OOSTable[Snapshot_UTC]`; `I6`; `OOSTable[Training_End_UTC]`.

Cache original: `0`. Format afișare: `General`.


### Calibrare_Linii!O6

```excel
=IF(M6=0,"",N6/M6)
```

Dependențe directe: `M6`; `N6`.

Cache original: `None`. Format afișare: `0.0%`.


### Calibrare_Linii!P6

```excel
=IF(M6=0,"",SUMIFS(OOSTable[P_Final],OOSTable[Line],A6,OOSTable[League],H6,OOSTable[Model_Signature],V6,OOSTable[Record_Valid],1,OOSTable[Settled_UTC],"<="&J6,OOSTable[Snapshot_UTC],">"&I6,OOSTable[Training_End_UTC],I6)/M6)
```

Dependențe directe: `M6`; `OOSTable[P_Final]`; `OOSTable[Line]`; `A6`; `OOSTable[League]`; `H6`; `OOSTable[Model_Signature]`; `V6`; `OOSTable[Record_Valid]`; `OOSTable[Settled_UTC]`; `J6`; `OOSTable[Snapshot_UTC]`; `I6`; `OOSTable[Training_End_UTC]`.

Cache original: `None`. Format afișare: `0.0%`.


### Calibrare_Linii!Q6

```excel
=IF(M6=0,"",(O6+1.96^2/(2*M6)-1.96*SQRT(O6*(1-O6)/M6+1.96^2/(4*M6^2)))/(1+1.96^2/M6))
```

Dependențe directe: `M6`; `O6`.

Cache original: `None`. Format afișare: `0.0%`.


### Calibrare_Linii!R6

```excel
=IF(M6=0,"",MAX(0,P6-O6))
```

Dependențe directe: `M6`; `P6`; `O6`.

Cache original: `None`. Format afișare: `0.0%`.


### Calibrare_Linii!S6

```excel
=IF(AND(G6="APPROVED",ISNUMBER(I6),ISNUMBER(J6),I6<J6,K6<>"",L6<>"",H6<>"",U6="VALID",ISNUMBER(E6),ISNUMBER(F6),M6>='Config_v6'!$B$56),"VALIDATED","PENDING")
```

Dependențe directe: `G6`; `I6`; `J6`; `K6`; `L6`; `H6`; `U6`; `E6`; `F6`; `M6`; `'Config_v6'!$B$56`.

Cache original: `PENDING`. Format afișare: `General`.


### Calibrare_Linii!T6

```excel
=IF(AND(S6="VALIDATED",Q6>='Config_v6'!$B$57,R6<='Config_v6'!$B$58),"VALIDATED","PENDING")
```

Dependențe directe: `S6`; `Q6`; `'Config_v6'!$B$57`; `R6`; `'Config_v6'!$B$58`.

Cache original: `PENDING`. Format afișare: `General`.


### Calibrare_Linii!U6

```excel
=IF(AND(ISNUMBER(D6),D6>0,D6<=1,OR(AND(E6="",F6=""),AND(ISNUMBER(E6),ISNUMBER(F6),E6>=0,E6<F6,F6<=1)),OR(G6="PENDING",G6="PILOT",G6="APPROVED")),"VALID","INVALID")
```

Dependențe directe: `D6`; `E6`; `F6`; `G6`.

Cache original: `VALID`. Format afișare: `General`.


### Calibrare_Linii!V6

```excel
='Config_v6'!$B$60&"|"&A6&"|"&TEXT(D6,"0.000000")&"|"&IF(E6="","NA",TEXT(E6,"0.000000"))&"|"&IF(F6="","NA",TEXT(F6,"0.000000"))
```

Dependențe directe: `'Config_v6'!$B$60`; `A6`; `D6`; `E6`; `F6`.

Cache original: `CORNERS_NATIVE_V14|0.300000|0.450000|0.250000|10.000000|5.000000|3.000000|1.100000|1.350000|1.700000|2.250000|0.820000|20.000000|0.720000|65.000000|0.000000|0.080000|0.120000|0.050000|75.000000|10.000000|5.000000|10.000000|5.000000|2.000000|2.000000|0.550000|0.200000|0.150000|0.100000|0.900000|90.000000|20.000000|1.100000|5.000000|200.000000|0.900000|0.050000|0.080000|O3,5|1.000000|0.050000|0.080000`. Format afișare: `General`.



## OOS_Predictii

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
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

### OOS_Predictii!T6

```excel
=IF(A6="",0,IFERROR(IF(AND(B6<>"",COUNTIF('Calibrare_Linii'!$A$6:$A$19,C6)=1,COUNTIFS(OOSTable[Fixture_ID],A6,OOSTable[Line],C6)=1,ISNUMBER(D6),ISNUMBER(E6),ISNUMBER(F6),F6<D6,D6<E6,ISNUMBER(G6),G6>='Config_v6'!$B$50,G6<=1,ISNUMBER(H6),H6>='Config_v6'!$B$51,H6<=100,ISNUMBER(I6),I6>=0,I6<='Config_v6'!$B$53,ISNUMBER(J6),J6>=0,J6<='Config_v6'!$B$52,K6="NO",L6=12,M6="PASS",ISNUMBER(N6),N6>=0,MOD(N6,1)=0,O6<>"",ISNUMBER(P6),P6>E6,Q6<>"",R6<>"",S6="LIVE"),1,0),0))
```

Dependențe directe: `A6`; `B6`; `'Calibrare_Linii'!$A$6:$A$19`; `C6`; `OOSTable[Fixture_ID]`; `OOSTable[Line]`; `D6`; `E6`; `F6`; `G6`; `'Config_v6'!$B$50`; `H6`; `'Config_v6'!$B$51`; `I6`; `'Config_v6'!$B$53`; `J6`; `'Config_v6'!$B$52`; `K6`; `L6`; `M6`; `N6`; `O6`; `P6`; `Q6`; `R6`; `S6`.

Cache original: `0`. Format afișare: `General`.


### OOS_Predictii!U6

```excel
=IF(T6<>1,0,IF(LEFT(C6,1)="O",IF(N6>INDEX('Calibrare_Linii'!$C$6:$C$19,MATCH(C6,'Calibrare_Linii'!$A$6:$A$19,0)),1,0),IF(N6<=INDEX('Calibrare_Linii'!$C$6:$C$19,MATCH(C6,'Calibrare_Linii'!$A$6:$A$19,0)),1,0)))
```

Dependențe directe: `T6`; `C6`; `N6`; `'Calibrare_Linii'!$C$6:$C$19`; `'Calibrare_Linii'!$A$6:$A$19`.

Cache original: `0`. Format afișare: `General`.



## Verificari

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
| A | Control | A6:A15 | Text | Input sau constantă literală |
| B | Rezultat | B6:B15 | Text sau număr în funcție de control | Rezultat formulă |
| C | Așteptat | C6:C15 | Text sau număr în funcție de control | Input sau constantă literală |
| D | Explicație | D6:D15 | Text | Input sau constantă literală |

### Verificari!B6

```excel
='Config_v6'!$B$40
```

Dependențe directe: `'Config_v6'!$B$40`.

Cache original: `VALID`. Format afișare: `General`.


### Verificari!B7

```excel
=COUNTIF(NativeTable[Row_State],"INVALID")
```

Dependențe directe: `NativeTable[Row_State]`.

Cache original: `0`. Format afișare: `General`.


### Verificari!B8

```excel
=COUNTIF(NativeTable[Row_State],"SOURCE CONFLICT")
```

Dependențe directe: `NativeTable[Row_State]`.

Cache original: `0`. Format afișare: `General`.


### Verificari!B9

```excel
=COUNTIFS(LinesTable[Release],"NOT RELEASED",LinesTable[Risk_Level_FINAL],">0")
```

Dependențe directe: `LinesTable[Release]`; `LinesTable[Risk_Level_FINAL]`.

Cache original: `0`. Format afișare: `General`.


### Verificari!B10

```excel
=COUNTIFS(LinesTable[G0],"<>PASS",LinesTable[P_FINAL],">0")
```

Dependențe directe: `LinesTable[G0]`; `LinesTable[P_FINAL]`.

Cache original: `0`. Format afișare: `General`.


### Verificari!B11

```excel
=COUNTIFS(LinesTable[Risk_Level_FINAL],1,LinesTable[Defensive_Gate],"<>PASS")
```

Dependențe directe: `LinesTable[Risk_Level_FINAL]`; `LinesTable[Defensive_Gate]`.

Cache original: `0`. Format afișare: `General`.


### Verificari!B12

```excel
=COUNTIFS(LinesTable[Mode],"REPLAY",LinesTable[Live_Eligible_Best],1)
```

Dependențe directe: `LinesTable[Mode]`; `LinesTable[Live_Eligible_Best]`.

Cache original: `0`. Format afișare: `General`.


### Verificari!B13

```excel
=ROWS(LinesTable[Line])/ROWS(MatchesTable[Match_ID])
```

Dependențe directe: `LinesTable[Line]`; `MatchesTable[Match_ID]`.

Cache original: `14`. Format afișare: `General`.


### Verificari!B14

```excel
=COUNTIF(NativeTable[Row_State],"DUPLICATE")
```

Dependențe directe: `NativeTable[Row_State]`.

Cache original: `0`. Format afișare: `General`.


### Verificari!B15

```excel
=SUM(OOSTable[Record_Valid])
```

Dependențe directe: `OOSTable[Record_Valid]`.

Cache original: `0`. Format afișare: `General`.



## Documentatie

| Coloană | Nume exact | Interval | Tip semantic | Proveniență |
|---|---|---|---|---|
| A | Subiect | A6:A32 | Text | Input sau constantă literală |
| B | Regulă | B6:B32 | Text | Input sau constantă literală |

