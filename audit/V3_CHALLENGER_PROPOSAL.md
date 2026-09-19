# V3 Challenger – propuneri metodologice pentru Șansă Dublă

**Status: DEZACTIVAT. Nu modifică production V2.**

Documentul nu este o specificație de implementare. Descrie problemele metodologice
identificate în auditul V2 (`audit_sansa_dubla_v2_data_lineage.md`,
`audit_prior_shrinkage.md`, `audit_scoreline_vs_strength.md`) care **nu pot fi reparate ca
bug de paritate**, fiindcă V2 se comportă exact cum a fost proiectat.
Fiecare propunere cere închidere metodologică și backtest înainte de orice cod.

## Ierarhia cauzelor, măsurată

Lot: FootyStats LIVE 2026-09-19, 157 meciuri, 429 selecții cu probabilități complete.
Metrica este raportul de compresie față de piață: cât din semnalul de diferențiere al
pieței păstrează fiecare etapă (1,000 = identic cu piața, 0 = uniform).

| Etapă | raport vs piață | pierdere proprie |
| --- | --- | --- |
| Piață de-vig | 1,000 | — |
| Scoreline brut | 0,952 | −4,8% |
| Scoreline după shrinkage | 0,722 | **−23,0%** |
| Strength brut | 0,749 | −20,3% |
| Strength după shrinkage | 0,337 | **−41,2%** |
| Blend final | 0,620 | — |

Prioritatea intervențiilor rezultă direct din tabel: **§2 (priorul) înainte de orice
altceva**, apoi §1b (agregarea overall), apoi §1a (Dixon-Coles), apoi §3–§5.

---

## 1. Rândurile scoreline și strength nu sunt modele independente

**Problema.** `Model_1X2!J6:L6` (scoreline) și `J7:L7` (strength) sunt generate de aceeași
funcție, `poisson_1x2`, pe două felii ale aceluiași set de goluri: H/A + xG pentru rândul 6,
overall pentru rândul 7.

**Formula V2.** Blend-ul aplică `Parametri!B32:B34` = 0.50 / 0.25 / 0.25:

```
P_blend = 0.50 · P_scoreline + 0.25 · P_strength + 0.25 · P_market
```

**Consecința matematică.** Ponderarea presupune surse cu erori necorelate. Corelația
măsurată între P(1) produs de cele două componente brute este **0,774** pe 157 de meciuri,
în timp ce corelația fiecăreia cu piața este ~0,50. Cele două „modele independente” seamănă
între ele mai mult decât seamănă cu piața. Ponderea efectivă a informației de goluri este
deci ~0,75, nu 0,50. Varianța blend-ului este subestimată, deci intervalele de încredere
sunt prea strânse și haircut-ul de confidence compensează un risc pe care nu îl măsoară.

**Sub-problema 1b, cu impact mai mare decât 1a.** Rândul 7 folosește statistici *overall*
(acasă + deplasare cumulate), ceea ce șterge avantajul de teren. Măsurat, componenta
strength păstrează doar **0,749** din semnalul pieței **chiar fără shrinkage**, față de
0,952 pentru scoreline. Un sfert din capacitatea de diferențiere se pierde numai prin
agregare. Aceasta este o problemă separată de lipsa unui Elo și e mai ieftin de rezolvat:
rândul 7 ar trebui să folosească un rating care păstrează contextul H/A.

**Observație care infirmă o ipoteză anterioară.** `_lambda_from_sides` folosește media
aritmetică dintre atacul unei echipe și apărarea adversarei, în locul formei multiplicative
standard. Analitic, media înjumătățește abaterea față de medie. Măsurat pe lotul real însă,
scoreline-ul brut păstrează 95,2% din semnalul pieței, deci pe intervalele de valori
întâlnite efectiv **nu aceasta este cauza principală**. Rămâne o abatere de la forma
canonică, de rezolvat, dar cu prioritate mică.

**Alternativa propusă.** Două motoare cu adevărat distincte:

- **Scoreline:** Dixon-Coles cu parametrul `tau` de corecție pentru scoruri mici (0-0, 1-0,
  0-1, 1-1), care este exact zona care decide 1X / X2 / 12.
- **Strength:** rating Elo sau Bradley-Terry cu actualizare secvențială și stare persistentă
  între meciuri, plus fereastră de formă (`Parametri!B18` = 5, azi neutilizat).

**Impact estimat.** Nedeterminat fără backtest. Direcția probabilă: `P_draw` mai mare
(Dixon-Coles corectează în sus scorurile mici), deci **mai puține** selecții 12 la Nivel 1,
nu mai multe. Propunerea nu este o relaxare.

**Backtest necesar.** Frozen out-of-sample pe minimum `Parametri!B29` = 30 de meciuri per
familie, cu calibrare comparată la `Parametri!B30` = 0.03 gap maxim. Fără aceasta,
propunerea rămâne închisă.

---

## 2. Puterea priorului nu are sursă metodologică

**Aceasta este cauza dominantă a diferenței față de piață.**

**Problema.** Shrinkage-ul folosește `n_prior` = numărul total de meciuri H/A din ligă.
Măsurat pe cele 393 de selecții cu shrinkage activ din lotul LIVE: `N_current` mediu = 2,8,
`N_prior` mediu = 52,3, deci **ponderea priorului este 94,7%** și a datelor proprii 5,3%.

**Formula V2 (implementată azi).**

```
rate_post = (n_current · rate_current + n_prior · rate_prior) / (n_current + n_prior)
```

**Consecința matematică.** La `N_current < 8` (`Parametri!B17`), estimarea echipei este
practic înlocuită de media ligii. Caz-martor măsurat, Sporting CP – FC Arouca (piață:
78,67% pentru gazde, `N = 3`):

| Parametru | înainte | după | Δ |
| --- | --- | --- | --- |
| Atac Sporting acasă | 2,128 | 1,411 | −0,718 |
| Atac Arouca în deplasare | 0,522 | 1,351 | **+0,830** |
| λ oaspeți | 0,741 | 1,363 | +84% |
| **P(1) scoreline** | **62,68%** | **37,93%** | **−24,75 pp** |

Atacul echipei mai slabe este aproape dublat de prior. Rezultatul final: `P_model(1X)` =
70,58% față de `P_market` = 92,00%, Risk Score 62, Nivel 4, verdict RIDICAT.

Contra-proba: Molde – Aalesund (VERIFIED, `N = 10/9`, pondere proprie 100%) are Δ(1X) =
−7,05 pp. **Bias-ul pe partea de favorit este de trei ori mai mare când shrinkage-ul e
activ.**

Simultan, `Small_Sample_N = 8` își pierde sensul: nu mai marchează „puțină informație
proprie”, ci „aproape numai prior”, iar tranziția de la N=7 la N=8 mută ponderea proprie de
la ~12% la 100% — o treaptă, nu o tranziție.

**Alternativa propusă.** Un `kappa` fix, exprimat în meciuri echivalente, independent de
mărimea ligii:

```
rate_post = (n_current · rate_current + kappa · rate_prior) / (n_current + kappa)
```

cu `kappa` în intervalul 5–10, ales prin validare, nu prin inspecție. La `kappa = 8` și
`N_current = 3`, echipa păstrează 27% din propriul semnal în loc de 5,4% — de cinci ori mai
mult, dar tot conservator. Un `kappa` fix rezolvă și problema de scară: astăzi o ligă cu
300 de meciuri jucate produce un prior de trei ori mai greu decât una cu 100, fără nicio
justificare metodologică.

**Impact estimat.** Probabilități mai dispersate pentru favoriții cu eșantion mic; mai multe
selecții trec de frontiera de Nivel 1. Exact de aceea propunerea **nu** poate fi adoptată
fără backtest: ar arăta ca o relaxare mascată. Ordinul de mărime: pe caz-martor, P(1)
scoreline ar urca de la 37,93% spre banda 50–55%, încă sub cele 62,68% brute.

**Sub-problema 2b.** Priorul este media brută a ligii, identică pentru toate echipele. Un
promovat și un campion primesc același prior. Un prior condiționat pe forța echipei
(clasament, rating de sezon precedent) ar fi mai corect, dar cere o sursă de date pe care
adaptorul nu o furnizează încă.

**Backtest necesar.** Grilă pe `kappa ∈ {3, 5, 8, 10, 15}`, evaluată pe Brier score și
calibrare early-season, out-of-sample, pe sezoane anterioare — nu pe cele 33 de meciuri de
control.

---

## 3. Pragul `Min_P_DC_Strong = 0.82` este inactiv

**Problema.** Pentru 1X / X2, verdictul DEFENSIV cere `M = 1` (Nivel 1):

```
N4 = ... IF(AND(M4=1, U4="PASS", F4>='Parametri'!B4), "DEFENSIV", ...)
```

**Consecința matematică.** Nivel 1 impune `ROUND(180·Pfail_DC + 200·Haircut) <= 20`. Chiar în
regimul cel mai favorabil (confidence A, fără early season), rezultă `Pfail_DC <= 0.1028`,
deci `P_adj >= 0.8872`. Pragul documentat de 0.82 este depășit automat cu 6.7–7.4 pp în toate
regimele de haircut (tabel complet în `risk_coherence_report.md`).

Pragul nu respinge niciodată nimic. Pragul real, nedocumentat, este ~0.89, impus implicit de
coeficientul de risc 180.

**Alternativa propusă.** Una dintre două, nu ambele:

- (a) se documentează explicit că pragul efectiv pentru DEFENSIV este ~0.89 și `B4` rămâne
  ca plasă de siguranță inactivă; **sau**
- (b) se recalibrează `Risk_Failure_1X_X2` astfel încât frontiera de Nivel 1 să coincidă cu
  `B4 = 0.82`, ceea ce ar cere un coeficient de ~113 în loc de 180.

Varianta (b) **ar crește** numărul de pariuri DEFENSIV și de aceea nu poate fi propusă ca
simplă „aliniere semantică”. Este o schimbare de apetit de risc și cere decizie explicită.

**Backtest necesar.** Hit rate observat pentru selecțiile din banda `P_adj ∈ [0.82, 0.89]`,
pe date istorice. Dacă banda performează sub așteptare, pragul actual de facto este corect
și trebuie doar documentat — adică varianta (a).

---

## 4. Haircut-ul este contabilizat de trei ori pentru selecția 12

**Problema.** Pentru rândul 6, `Haircut_Total` intră în trei locuri independente:

| Cale | Formulă |
| --- | --- |
| Probabilitate ajustată | `F6 = B6 - E6` |
| Draw Gate | `P0_Gates_v2!I6 = MIN(1, C10 + E6)` |
| Risk Score | `L6 += 120 · E6` |

**Consecința matematică.** Un haircut de 4.5 pp (confidence B + early season) reduce `P_adj`
cu 4.5 pp, împinge `Pdraw_adj` în sus cu 4.5 pp spre pragul Draw Gate **și** adaugă 5.4
puncte de risc. Aceeași incertitudine este penalizată de trei ori pe trei axe diferite. Pentru
1X / X2 haircut-ul intră doar de două ori (`P_adj` și Risk Score).

**Alternativa propusă.** Haircut-ul rămâne în `P_adj` (este ajustarea de probabilitate) și în
Risk Score (este componenta de incertitudine), dar Draw Gate compară `Pdraw_model_raw` cu
`Pdraw_market`, fără haircut — incertitudinea fiind deja prețuită de celelalte două căi.

**Impact estimat.** Draw Gate mai permisiv pentru meciurile early-season; efect redus,
fiindcă frontiera de Nivel 1 pentru 12 (`Pdraw <= 0.0965`) este oricum de ~2x mai strictă
decât gate-ul (`0.20`). Cu alte cuvinte, gate-ul nu este constrângerea activă, deci
modificarea ar avea impact mic — încă un motiv să nu fie făcută fără dovezi.

**Backtest necesar.** Comparație A/B pe rata de egal realizată în meciurile early-season
respinse azi de Draw Gate.

---

## 5. Asimetrie între `N4`/`N5` și `N6`

**Problema.** `N6` (selecția 12) nu verifică `F6` față de niciun prag de probabilitate:

```
N6 = ... IF(OR(U6="PRUDENT", M6=2), "PRUDENT", "DEFENSIV") ...
```

1X și X2 cer `F >= Parametri!B4`; 12 nu cere nimic. Un 12 cu `P_adj` scăzut, dar `Pdraw` mic
și Nivel 1, poate deveni DEFENSIV fără prag de probabilitate.

**De ce nu s-a modificat.** Este comportamentul workbook-ului de referință. Orice prag adăugat
aici ar fi o regulă nouă fără sursă metodologică — interzis explicit de VERSION LOCK.

**Alternativa propusă.** Se clarifică metodologic dacă absența pragului este intenționată
(fiindcă pentru 12 riscul relevant este `Pdraw`, nu `P_adj`) sau o omisiune. Dacă este
omisiune, se adaugă `F6 >= Parametri!B4` în V3.

**Backtest necesar.** Câte selecții 12 DEFENSIV istorice ar fi fost respinse de un prag pe
`F6` și care a fost rezultatul lor real.

---

## Condiții de activare

Niciuna dintre propunerile de mai sus nu intră în production fără, cumulat:

1. închidere metodologică scrisă (sursa regulii, nu doar valoarea);
2. backtest frozen out-of-sample, în afara celor 33 de meciuri de control;
3. calibrare sub `Calibration_Gap_Warn` = 0.03;
4. minimum `WalkForward_MinN_Family` = 30 de observații per familie;
5. rulare paralelă V2 / V3 cu V2 rămas decizional.
