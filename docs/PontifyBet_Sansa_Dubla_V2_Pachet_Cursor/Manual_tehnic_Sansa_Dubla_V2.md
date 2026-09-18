# Manual tehnic de implementare PontifyBet

Model optimizat V2 pentru Șansă Dublă 1X X2 12

Specificație de portare a formulelor și controalelor în cod. Versiune a manualului 1.0, 18 septembrie 2026.

## Obiectul implementării și referința de conformitate

Implementarea reproduce fișierul `11_model_analiza_pariu_sansadubla_optimizat_V2(1).xlsx`, identificat prin SHA-256 în `manifest.json`. Copia fără sufixul `(1)` furnizată în proiect este identică octet cu octet. Sunt 15 foi și 3.068 de formule, dintre care 2.800 în Backtest. Numele interne cu sufixele v2 și v4 aparțin aceluiași fișier optimizat_V2; nu indică versiuni alternative care trebuie selectate separat.

Obiectivul este identitatea formulelor, a ordinii ramurilor, a stărilor de date și a rezultatelor pentru aceleași intrări. Nu se schimbă praguri pentru a obține o anumită recomandare. Modelele Dixon–Coles/Bivariat Poisson și Elo nu sunt implementate în acest Excel: el primește distribuțiile lor. Reproducerea algoritmului din fișier nu definește automat și un algoritm unic de obținere a acelor distribuții din statistici sportive.

Această cerere definește explicit portarea calculelor în aplicație, o extindere față de fluxul MVP în care Python completează numai inputurile, iar Excel recalculează. Manualul specifică extinderea; nu modifică aplicația, fișierele originale, API-ul sau modelele externe. În Cursor trebuie verificată implementarea existentă înainte de alegerea fișierelor noi. Nu sunt presupuse endpoint-uri sau câmpuri FootyStats pentru probabilitățile externe.

Pentru egalitatea numerică se compară valorile interne cu toleranță absolută 1e-12; statusurile, scorurile întregi, nivelurile și verdicturile se compară exact. Toleranța de test nu se adaugă pragurilor de decizie. Egalitatea binară între limbaje nu este garantată de această toleranță; Microsoft Excel rămâne etalonul final pentru rotunjirile la limită.

### Diferențe esențiale față de o implementare simplificată

- `Double_Chance!N6`, verdictul pentru 12, nu testează pragurile P_adj de 82% și 76%. Acestea sunt utilizate în N4:N5 pentru 1X/X2.
- `Pfail_DC` din Y4:Y6 nu include haircut. Pentru 12, numai Draw Gate folosește `max(min(1, model_draw + haircut), market_draw)`. Scorul pentru 12 folosește separat Pfail_DC și haircut.
- `PENDING` de release blochează clasamentul, dar `PENDING OFFICIAL` pentru context G1, documentat cu `REFRESH PRE-XI`, poate produce `CONDITIONAL` și permite calculul.
- Eșantionul sub 8 impune documentarea priorului, transformă confidence A în B și adaugă 0,02 haircut. Nu există un hard fail doar pentru eticheta SMALL SAMPLE.
- Fragilitatea MATERIAL adaugă un nivel, nu puncte la scor. Verificarea incompletă a acestei fragilități blochează numai 1X.
- Cotele exacte 1X/X2/12 și Edge/EV nu decid verdictul. Probabilitățile de piață 1X2 rămân input critic și influențează blend-ul, controalele și riscul.

## 1 Arhitectura și structura foilor

### 1.1 Inventarul complet

| Foaie exactă | Rol |
| --- | --- |
| Parametri | 45 constante; praguri, ponderi, coeficienți și diagnostice. |
| Input_Meci | Context și inputuri comune; date sportive, piață, sample, flags. |
| Model_1X2 | Validare, normalizare și combinare 50/25/25; release comun. |
| Draw_Risk | Diagnostic și afișarea controlului activ pentru 12. |
| Loss_Risk | Diagnostic și afișarea controalelor 1X/X2. |
| Double_Chance | Selector final, trei rânduri 1X/X2/12, 32 de coloane. |
| Backtest | 200 snapshot-uri, rezultate, Brier, profit și eligibilități. |
| Dashboard | Afișarea rezultatelor finale și interpretării. |
| P0_Gates_v2 | Market Direction, Protected Strength, Draw Gate și P0. |
| Uncertainty_v2 | Haircut unic și surcharge favorit deplasare. |
| WalkForward_Calibration | Monitorizare pe familii; fără gate prematch. |
| Favorite_Fragility_v4 | Audit specific 1X; +1 nivel și închiderea verificării. |
| CHANGELOG_VERSIUNI | Istoric static al corecțiilor V2. |
| DOCUMENTATIE_MODEL | Ghid static actual; fără calcule suplimentare. |
| Surse_Date | Trasabilitate, cronologie și starea datelor. |

Dimensiunile formatate până la rândul 220 și coloana X nu înseamnă că există 220 de meciuri. Modelul prematch analizează un singur meci și produce trei selecții, pe rândurile 4, 5 și 6 din Double_Chance. Backtest are 200 de înregistrări independente, în rândurile 4:203. Nu există named ranges în workbook; coordonatele foaie/celulă sunt identificatorii de referință.

### 1.2 Ordinea dependențelor

1. Se încarcă configurația fixată și inputurile, fără înlocuirea lipsei cu zero.
2. Se evaluează Surse_Date!L5:L11 și L15, integritatea celor trei distribuții F6:F8 și fixture-ul F13 din Model_1X2.
3. Model_1X2!F12 și F14 decid release-ul comun. Normalizările J6:L8 depind numai de validitatea distribuției respective și pot exista înaintea release-ului comun.
4. Dacă F14 este READY, se calculează blend-ul B9:D9 și distribuția finală B10:D10. Uncertainty_v2 poate fi calculat în paralel din sample și confidence, dar rezultatele sale nu acordă release.
5. Se calculează P0_Gates_v2, Surse_Date!L12 și Favorite_Fragility_v4. Nu există ciclu: aceste module nu redefinesc probabilitățile modelului.
6. Double_Chance!AD4:AD6 stabilesc release-ul pe selecție. Se calculează scorurile L, nivelurile M, eligibilitatea AA și verdicturile N, în această ordine logică. AE citește verdictul final.
7. Dashboard afișează rezultatele. Backtest și WalkForward_Calibration sunt fluxuri de monitorizare; nu rescriu probabilitățile, pragurile sau verdictul prematch.

Numai ordinea dependențelor este obligatorie, nu ordinea vizuală a foilor. Evaluarea lazily a ramurilor IF evită calcularea unei împărțiri care nu aparține ramurii selectate. O verificare de dependențe a formulelor extrase nu a identificat cicluri.

### 1.3 Schema inputurilor sportive

În Input_Meci, A este eticheta, B este valoarea pentru gazde sau valoarea comună, C este valoarea pentru oaspeți atunci când are sens, iar D este nota. Nu se scrie automat aceeași valoare în B și C pentru câmpurile comune.

| Celule | Câmp | Tip |
| --- | --- | --- |
| B4:C4 | Echipă | Text |
| B5 | Ligă | Text |
| B6 | Data meci | Dată numerică Excel |
| B7 | Teren neutru? | DA / NU |
| B8:C8 | Poziție clasament | Întreg |
| B9:C9 | Puncte/meci sezon | Float |
| B10:C10 | Puncte/meci H/A | Float |
| B11:C11 | Formă L5 - puncte/meci | Float |
| B12:C12 | Goluri marcate / meci sezon | Float |
| B13:C13 | Goluri primite / meci sezon | Float |
| B14:C14 | Goluri marcate / meci H/A | Float |
| B15:C15 | Goluri primite / meci H/A | Float |
| B16:C16 | xG / meci H/A | Float |
| B17:C17 | xGA / meci H/A | Float |
| B18:C18 | % victorii H/A | Probabilitate [0,1] |
| B19:C19 | % egaluri H/A | Probabilitate [0,1] |
| B20:C20 | % înfrângeri H/A | Probabilitate [0,1] |
| B21:C21 | % meciuri fără gol marcat H/A | Probabilitate [0,1] |
| B22:C22 | % clean sheets H/A | Probabilitate [0,1] |
| B23:C23 | Elo / rating putere | Float |
| B24:C24 | Absențe cheie atac (0-3) | Întreg |
| B25:C25 | Absențe cheie apărare (0-3) | Întreg |
| B26:C26 | Motivație/context (0-3) | Întreg |
| B27:C27 | Zile odihnă | Întreg |
| B28 | Prob. piață 1 de-vig | Probabilitate [0,1] |
| B29 | Prob. piață X de-vig | Probabilitate [0,1] |
| B30 | Prob. piață 2 de-vig | Probabilitate [0,1] |
| B31 | Cotă 1X | Cotă numerică |
| B32 | Cotă X2 | Cotă numerică |
| B33 | Cotă 12 | Cotă numerică |
| B34 | Confidence date | A / B / C |
| B36:C36 | Meciuri sample curent sezon H/A | Întreg ≥0 |
| B37 | Override Protected Strength 1X | DA / NU |
| B38 | Override Protected Strength X2 | DA / NU |
| B39 | Motiv cantitativ override 1X | Text |
| B40 | Motiv cantitativ override X2 | Text |
| C41 | Context negativ favorit deplasare (0-2) | 0 / 1 / 2 numeric |
| B42 | Sursă probabilități 1X2 de-vig | Text |
| B43 | Home favorite foarte scurt? | DA / NU / PENDING |
| B44 | Discrepanțe finishing favorit home? | DA / NU / PENDING |
| B45 | Adversar transition threat / away scoring robust? | DA / NU / PENDING |
| B46 | P1X mare aproape exclusiv din piață? | DA / NU / PENDING |
| B47 | Notă integrare context | Text |

Tipurile din tabel descriu contractul aplicației. Excel nu verifică toate limitele sportive sugerate de etichete. De exemplu, rândurile 24:26 indică 0–3, dar nu au validator numeric în lanțul verdictului. Niciun coeficient ascuns nu transformă xG, Elo, absențele, poziția sau forma din B8:C27 în distribuții. Acestea sunt context pentru producătorii modelelor externe.

O dată validă pentru aplicație se serializează la intrarea motorului în numeric Excel, cu baza 1899-12-30 și fracțiune de zi pentru oră. Formula verifică ISNUMBER, nu formatul vizual al celulei. Excel nu stochează fusul orar; toate momentele se convertesc coerent în același fus înaintea comparației. Nu compara șiruri de date localizate.

### 1.4 Schema celorlalte module

| Modul | Câmpuri și tipuri | Sursa valorilor |
|---|---|---|
| Model_1X2, rândurile 6:8 | B:D probabilități brute, E sumă numerică, F status text, G:H documentare, J:L probabilități normalizate | B6:D7 input extern; B8:D8 din Input_Meci B28:B30; restul formule |
| Model_1X2, rândurile 9:10 | B:D probabilități, E sumă, F status | Blend ponderat, apoi renormalizare |
| Model_1X2, F12:F14 | Statusuri text | Integritate distribuții, fixture și release comun |
| Draw_Risk | B4/B12:B14 probabilități derivate; B5:B6/B8:B9 inputuri probabilistice opționale; B11 flag text; E statusuri | Model, gate, diagnostic manual |
| Loss_Risk | B:C valori pentru 1X/X2; rândurile 5:7 probabilități; 8:9 flag-uri; 10:12 statusuri | Model, piață, diagnostic manual, P0 |
| P0_Gates_v2 | B/D/E/G/I/J numere, C/F/H/K/L texte; A selecție | Probabilități normalizate, override, haircut |
| Uncertainty_v2 | B4 sample numeric; B5 DA/NU/INPUT; B6:B7 confidence; B8:B10 probabilități; B13 probabilitate, C13 context 0–2, D13 puncte | Input_Meci și Parametri |
| Favorite_Fragility_v4 | B5:B9 texte; B11 număr întreg; B12 status; B13 întreg; B14 stare audit | Flag-uri manuale, early season, Surse_Date L12 |
| Surse_Date | C status; D sursă; E/F date numerice; G/H sample; I metodă; J DA/NU; K tratament; L status calculat | Metadate documentate; D8/G9/H9 sunt formule |
| Dashboard | A selecție; B probabilitate; C control; D scor; E nivel; F stare; G verdict; H eligibilitate | Exclusiv Double_Chance |
| DOCUMENTATIE_MODEL | A temă, B regulă, C localizare, toate text | Documentare; fără formulă de decizie |
| CHANGELOG_VERSIUNI | A problemă, B corecție, C efect, toate text | Istoric; fără formulă de decizie |

`schema_celule.json` și CSV furnizează coordonate, variabile, tipuri, roluri, valori inițiale și formule. `formule_integrale.json` cuprinde toate formulele și referințele lor directe. `Anexa_formule_exacte.md` afișează lizibil formulele, reducând numai repetiția celor 200 de rânduri Backtest la rândul reprezentativ 4.

### 1.5 Contractul rezultatelor Double Chance

| Coloană | Câmp exact | Tip |
| --- | --- | --- |
| A | Selecție | Text / status |
| B | P_model | Probabilitate nullable |
| C | Failure mode | Text / status |
| D | P_failure | Probabilitate nullable |
| E | Haircut total | Probabilitate nullable |
| F | P_adj | Probabilitate nullable |
| G | Cotă | Cotă numerică nullable |
| H | P_market | Probabilitate nullable |
| I | Edge | Float nullable, diferență |
| J | EV informativ neutilizat | Șir gol constant |
| K | Control tehnic | Text / status |
| L | Risk Score | Scor întreg nullable |
| M | Risk Level | Nivel întreg nullable |
| N | Verdict | Text / status |
| O | Market Direction | Text / status |
| P | Protected Strength | Text / status |
| Q | Draw Market | Text / status |
| R | Early Season | Text / status |
| S | Confidence efectiv | Text / status |
| T | Away Fav Surcharge | Puncte numeric nullable |
| U | P0 final | Text / status |
| V | Motivație v4 | Text / status |
| W | P1X2 de-vig source | Text / status |
| X | P failure market | Probabilitate nullable |
| Y | Pfail_DC=max(model,market) | Probabilitate nullable |
| Z | Market Direction Gate | Text / status |
| AA | Ranking Eligible | Text / status |
| AB | Favorite Fragility | Text / status |
| AC | Fragility Risk +level | Majorare nivel întreg |
| AD | Stare date | Text / status |
| AE | Eligibil DEFENSIV | Text / status |
| AF | Calibrare familie | Text / status |

Probabilitățile, scorul și nivelul sunt nullable. `null` la interfața JSON reprezintă lipsa valorii numerice; la comparația cu Excel este echivalent cu rezultatul `""`, nu cu zero. Stările textuale nu se substituie între ele. Pentru V se reproduce separat formatul TEXT utilizat în Excel dacă se cere identitate vizuală, inclusiv localizarea separatorului zecimal. W este sursa din Input_Meci B42; AF este numai starea de calibrare.

## 2 Inputuri constante și configurații

### 2.1 Distribuțiile externe și cotele

Model_1X2!B6:D6 primește P(1), P(X), P(2) de la modelul de scor. B7:D7 primește distribuția modelului de forță. Aceste distribuții sunt probabilități externe, nu cote de bookmaker cărora Excel le aplică de-vig. Piața de-vig este introdusă în Input_Meci!B28:B30, în ordinea 1, X, 2.

Workbook-ul nu are trei celule de input pentru cotele simple 1/X/2 și nu conține formula care le elimină marja. Celulele B31:B33 sunt cotele selecțiilor duble 1X/X2/12. Dacă aplicația calculează anterior distribuția de piață din cote 1/X/2, metoda și snapshot-ul trebuie documentate în Surse_Date. Normalizarea proporțională `(1/odds_i)/sum(1/odds_j)` este doar un exemplu de preprocesare posibilă, nu o formulă existentă sau impusă de acest Excel. Identitatea cere aceeași distribuție de-vig introdusă, indiferent de metoda externă.

Nu se construiește automat modelul Elo din Input_Meci!B23:C23 și nu se inventează lambde pentru Dixon–Coles. Pentru aceleași statistici, două modele externe diferite pot genera distribuții diferite; egalitatea cu Excel se cere începând de la distribuțiile și metadatele efectiv introduse.

### 2.2 Constantele complete

| Celulă și parametru | Valoare | Utilizare |
| --- | --- | --- |
| B4 Min_P_DC_Strong | 0.82 | activ; Prag P ajustată pentru DEFENSIV |
| B5 Min_P_DC_Prudent | 0.76 | activ; Prag PRUDENT 1X/X2 |
| B6 Max_Loss_Risk_Strong | 0.18 | istoric; ISTORIC – fără hard gate activ |
| B7 Max_Loss_Risk_Prudent | 0.24 | istoric; ISTORIC – fără hard gate activ |
| B8 Max_Draw_Risk_12_Strong | 0.2 | activ; Prag PASS pentru Draw Gate |
| B9 Max_Draw_Risk_12_Prudent | 0.23 | activ; Max. P_draw_adj pentru 12 PRUDENT |
| B10 Max_DC_Market_Gap | 0.07 | diagnostic; Diagnostic model–piață |
| B11 Min_Edge | 0.025 | istoric neutilizat; ISTORIC – Edge informativ |
| B12 Min_EV_DEPRECATED | 0 | istoric neutilizat; EV neutilizat |
| B13 Uncertainty_Haircut_A | 0.01 | activ; Haircut confidence A |
| B14 Uncertainty_Haircut_B | 0.025 | activ; Haircut confidence B |
| B15 Uncertainty_Haircut_C | 0.05 | activ; Haircut confidence C |
| B16 Draw_00_11_Concentration_Strong | 0.65 | diagnostic; Diagnostic concentrație egal |
| B17 Small_Sample_N | 8 | activ; Prag eșantion mic |
| B18 Recent_Window | 5 | informativ neutilizat; Formă recentă |
| B20 MarketDir_PASS_Max | 0.3 | activ; Market Direction PASS 1X/X2 |
| B21 MarketDir_PRUDENT_Max | 0.35 | activ; Market Direction PRUDENT |
| B22 Protected_Strength_Tolerance | 0.05 | activ; Toleranță protected-side |
| B23 Quant_Override_Min_ModelAdv | 0.07 | activ; Override Protected Strength |
| B24 Draw_WATCH_Max | 0.26 | activ; Limită WATCH pentru 12 |
| B25 EarlySeason_Extra_Haircut | 0.02 | activ; Haircut suplimentar early season |
| B26 AwayFav_Strong_Threshold | 0.55 | activ; Favorit puternic în deplasare |
| B27 AwayFav_Risk_Context1 | 5 | activ; Surcharge risc context negativ=1 |
| B28 AwayFav_Risk_Context2 | 10 | activ; Surcharge risc context negativ=2 |
| B29 WalkForward_MinN_Family | 30 | monitorizare; Minim promovare prag |
| B30 Calibration_Gap_Warn | 0.03 | monitorizare; Avertizare calibrare |
| B31 Probability_Sum_Tolerance | 0.02 | activ; Toleranță sumă 1X2 |
| B32 Weight_Scoreline | 0.5 | activ; Model de scor |
| B33 Weight_Strength | 0.25 | activ; Model de forță |
| B34 Weight_Market | 0.25 | activ; Piață 1X2 de-vig |
| B35 Risk_Failure_1X_X2 | 180 | activ; Risk Score 1X/X2 |
| B36 Risk_Haircut_1X_X2 | 200 | activ; Risk Score 1X/X2 |
| B37 Risk_Failure_12 | 200 | activ; Risk Score 12 |
| B38 Risk_Haircut_12 | 120 | activ; Risk Score 12 |
| B39 Risk_Level1_Max | 20 | activ; Nivel 1 |
| B40 Risk_Level2_Max | 40 | activ; Nivel 2 |
| B41 Risk_Level3_Max | 60 | activ; Nivel 3 |
| B42 Risk_Level4_Max | 80 | activ; Nivel 4 |
| B43 Risk_Score_Max | 100 | activ; Plafon scor |
| B44 Prudent_Gate_Surcharge | 10 | activ; Penalizare gate PRUDENT |
| B45 Draw_Watch_Surcharge | 35 | activ; Penalizare Draw WATCH |
| B46 Gate_Fail_Surcharge | 60 | activ; Penalizare FAIL |
| B47 Risk_Level_Max | 5 | neutilizat direct; formulele folosesc literalul 5; Plafon nivel |
| B48 Fragility_Material_Count | 2 | activ; Prag MATERIAL |
| B49 Fragility_Level_Surcharge | 1 | activ; Majorare MATERIAL |

Există 45 de valori numerice în Parametri. B47, Risk_Level_Max=5, nu este citit de formulele active de nivel: acestea folosesc literalul 5. O portare strictă nu conectează retroactiv acest parametru. B18, Recent_Window=5, nu calculează forma recentă în Excel. Valorile istorice B6:B7 și B11:B12 nu se reactivează ca filtre.

Mai există literali operaționali: 12 zecimale la anumite ROUND de validare/gates, 1e-12 pentru suma ponderilor, 0 zecimale la scor, 1 drept plafon probabilistic, 0 drept limită inferioară P_adj, patru semnale secundare în auditul fragilității, context deplasare 0/1/2, odds >1 pentru profit/ROI și fereastra fixă Backtest 4:203. Pragurile 0,65 și 0,07 afișate ca literali în Draw_Risk/Loss_Risk sunt diagnostice; formulele de status citesc Parametri B16/B10.

### 2.3 Surse și cronologie

Pentru fiecare rând de sursă se păstrează statusul, providerul sau identificatorul sursei, verificarea, cutoff-ul, metoda și confirmarea aceluiași meci. Un șir nevid din I este suficient pentru verificarea formulei; formula nu inspectează semantic metoda sau URL-ul. Aplicația nu trebuie să prezinte acest test de completitudine ca validare științifică a modelului.

Rândurile 5, 6, 7 și 8 reprezintă fixture, model scoreline, model strength și piață. Rândul 9 reprezintă eșantionul curent. Rândul 10 documentează prior/shrinkage când e necesar, 11 contextul, iar 12 auditul fragilității 1X.

```text
META(row):
  dacă D este blank sau COUNT(E:F) != 2
     sau I este blank sau J este blank sau kickoff nu este numeric:
      return PENDING
  dacă J != DA sau E > kickoff sau F > kickoff sau F > E:
      return INVALID
  return READY
```

Comparațiile surselor permit `cutoff <= verified_at <= kickoff`, inclusiv egalitatea cu kickoff. Nu există în aceste formule un prag de vechime în ore sau zile. În Backtest, timestamp-ul predicției are separat condiția strictă `< kickoff`.

Pentru L5:L8: NOT AVAILABLE ori SOURCE CONFLICT → CRITICAL MISSING; VERIFIED, DERIVED ori PRIOR / SHRINKAGE → META; orice alt status → PENDING. Ordinea ramurilor este parte din model. Un status neverificat nu este automat INVALID doar fiindcă alte câmpuri ar fi greșite.

Pentru L9: întâi status critic, apoi lipsa celor două numere → PENDING; valori negative sau fracționare → INVALID. Sunt acceptate statusurile VERIFIED, DERIVED, PRIOR / SHRINKAGE și SMALL SAMPLE, cu META. G9:H9 sunt derivate din Input_Meci B36:C36, nu se suprascriu.

```text
PRIOR = Surse_Date L10:
  dacă L9 != READY: PENDING
  altfel dacă min(G9,H9) >= 8: N/A
  altfel dacă C10 este NOT AVAILABLE sau SOURCE CONFLICT: CRITICAL MISSING
  altfel dacă COUNT(G10:H10) != 2 sau K10 != INTEGRAT IN MODELE: PENDING
  altfel dacă min(G10,H10) <= 0: INVALID
  altfel aplică statusurile admise VERIFIED/DERIVED/PRIOR / SHRINKAGE și META
```

N prior trebuie să fie pozitiv; această formulă nu impune să fie întreg. La N curent ≥8, conținutul rândului 10 este ignorat prin N/A. Nu se inventează o formulă de shrinkage: rândul documentează că aceasta a fost aplicată extern.

### 2.4 Contextul condiționat și release-ul comun

Surse_Date!L11 aplică următoarea ordine:

1. K11=IMPACT NEREZOLVAT sau C11=SOURCE CONFLICT → REVIEW.
2. C11=PENDING OFFICIAL și K11=REFRESH PRE-XI → META; dacă META este READY, rezultatul devine CONDITIONAL.
3. C11 în {NOT AVAILABLE, PROXY ONLY} și K11 în {INTEGRAT IN MODELE, FARA IMPACT MATERIAL} → aceeași conversie READY în CONDITIONAL.
4. Pentru K11 în {INTEGRAT IN MODELE, FARA IMPACT MATERIAL}, statusurile VERIFIED/DERIVED/PRIOR / SHRINKAGE se evaluează prin META. Alte situații rămân PENDING, cu ramurile REVIEW explicite din formula originală.

Nu trebuie impus „lot confirmat” ca filtru nou. În schimb, marcarea unei verificări neînchise ca VERIFIED ar modifica nejustificat release-ul.

```text
Surse_Date L15:
  dacă există CRITICAL MISSING în L5:L10: CRITICAL MISSING
  altfel dacă există INVALID în L5:L11: INVALID
  altfel dacă există PENDING sau REVIEW în L5:L11: PENDING
  altfel dacă L11 == CONDITIONAL: CONDITIONAL
  altfel: READY
```

L12 nu participă la L15. Orice agregare automată peste toate rândurile 5:12 ar produce un motor diferit. F14 din Model_1X2 transformă READY sau CONDITIONAL în READY numai dacă F12 și F13 sunt READY; CRITICAL MISSING are precedență, apoi INVALID, apoi PENDING.

## 3 Calculul probabilităților și incertitudinii

### 3.1 Validarea distribuțiilor

Formula exactă Model_1X2!F6:

```excel
=IF(COUNTBLANK(B6:D6)>0,"INPUT",IF(COUNT(B6:D6)<>3,"INVALID",IF(OR(MIN(B6:D6)<0,MAX(B6:D6)>1,ROUND(ABS(SUM(B6:D6)-1),12)>'Parametri'!B31),"INVALID","OK")))
```

Se aplică identic pe rândurile 6, 7 și 8. COUNTBLANK include celulele goale și formulele care întorc `""`. Textul numeric nu este număr. Pentru piață, B8:D8 folosesc mai întâi ISNUMBER asupra Input_Meci B28:B30; un text numeric se transformă în `""` și produce INPUT. În rândul scoreline/strength, un text prezent fără alte blank-uri produce INVALID.

```text
validate_distribution(p):
  dacă există blank: INPUT
  altfel dacă numărul valorilor numerice != 3: INVALID
  altfel dacă min(p)<0 sau max(p)>1: INVALID
  altfel dacă ROUND_EXCEL(abs(SUM(p)-1),12)>0.02: INVALID
  altfel: OK
```

Limitele 0 și 1 sunt admise. Validarea sumei se face înainte de normalizare; 1,02 și 0,98 sunt acceptate la prag după rotunjirea explicită. 1,20 este invalid. Nu se aplică clamp pe distribuțiile brute pentru a le face valide.

F12 este INVALID dacă oricare dintre F6:F8 este INVALID; este READY dacă toate trei sunt OK; altfel INPUT. F13 verifică întâi completitudinea gazdelor, oaspeților, ligii B5, kickoff-ului numeric B6, terenului B7 și confidence B34. Apoi respinge nume egale, teren în afara DA/NU, confidence în afara A/B/C, sumă a ponderilor diferită de 1 cu mai mult de 1e-12 sau ponderi negative. Nu testează întreaga semantică a parametrilor; configurația se păstrează fixată prin versiune.

### 3.2 Normalizare și blend

Formula exactă Model_1X2!J6:

```excel
=IF(F6<>"OK","",B6/E6)
```

Formula exactă Model_1X2!B9:

```excel
=IF($F$14<>"READY","",'Parametri'!$B$32*J6+'Parametri'!$B$33*J7+'Parametri'!$B$34*J8)
```

Formula exactă Model_1X2!B10:

```excel
=IF(OR(NOT(ISNUMBER(B9)),$F$9<>"OK"),"",B9/$E$9)
```

```text
pentru fiecare model m în scoreline, strength, market:
  sum_m = SUM(raw_m[1],raw_m[X],raw_m[2])
  norm_m[k] = raw_m[k] / sum_m, dacă status_m == OK

dacă release_comun == READY:
  raw_blend[k] = 0.50*scoreline_norm[k]
                 + 0.25*strength_norm[k]
                 + 0.25*market_norm[k]
  blend_sum = SUM(raw_blend[1],raw_blend[X],raw_blend[2])
  dacă ROUND_EXCEL(abs(blend_sum-1),12) <= 0.02:
      final[k] = raw_blend[k] / blend_sum
```

Se păstrează renormalizarea finală, chiar dacă ponderile însumează teoretic 1. Nu se rotunjesc individual probabilitățile la procente afișate. Nu se înlocuiește calculul Excel `P1+PX` cu `1-P2` în implementarea orientată spre egalitate numerică strictă: sunt echivalente matematic, dar pot diferi la ultima cifră în virgulă mobilă.

### 3.3 Calcul unic pentru haircut

Formula exactă Uncertainty_v2!B7:

```excel
=IF(OR(B5="INPUT",AND(B6<>"A",B6<>"B",B6<>"C")),"",IF(AND(B5="DA",B6="A"),"B",B6))
```

Formula exactă Uncertainty_v2!B10:

```excel
=IF(COUNT(B8:B9)<>2,"",B8+B9)
```

```text
n = min(sample_home, sample_away), dacă ambele sunt numerice și nenegative
early = DA dacă n < 8; NU dacă n >= 8; INPUT dacă n lipsește
confidence_effective = B dacă early == DA și confidence_input == A
confidence_effective = confidence_input în celelalte cazuri valide
base = {A:0.01, B:0.025, C:0.05}[confidence_effective]
extra = 0.02 dacă early == DA, altfel 0
haircut = base + extra
```

| Confidence input | N ≥8 | N <8 cu prior valid |
|---|---|---|
| A | A, haircut 0,01 | B, haircut 0,045 |
| B | B, haircut 0,025 | B, haircut 0,045 |
| C | C, haircut 0,05 | C, haircut 0,07 |

Formula locală Uncertainty B4 nu verifică integralitatea sample-ului; Surse_Date L9 o verifică înainte de release. Nu este necesar un nou validator care să schimbe verdictul local. O valoare necunoscută nu se transformă în N=0. Când N=0 este real și documentat, priorul poate permite release-ul.

### 3.4 Probabilitățile selecțiilor și riscul conservator

| Selecție | P_model | Rezultat exclus | P_market selecție | Pfail_DC |
|---|---|---|---|---|
| 1X | final_1 + final_X | 2 | market_1 + market_X | max(final_2, market_2) |
| X2 | final_X + final_2 | 1 | market_X + market_2 | max(final_1, market_1) |
| 12 | final_1 + final_2 | X | market_1 + market_2 | max(final_X, market_X) |

Toate valorile market din acest tabel sunt normalizate, din Model_1X2 J8:L8. Pentru fiecare selecție `P_adj=max(0,P_model-haircut)`. Edge=`P_adj-P_market`, informativ. J4:J6 conțin explicit `=""`; nu există EV prematch calculat în selector.

Formula exactă Double_Chance!F4:

```excel
=IF(OR(NOT(ISNUMBER(B4)),NOT(ISNUMBER(E4))),"",MAX(0,B4-E4))
```

Formula exactă Double_Chance!Y4:

```excel
=IF(OR(NOT(ISNUMBER(D4)),NOT(ISNUMBER(X4))),"",MAX(D4,X4))
```

Haircut-ul este calculat o dată și reutilizat în probabilitate, scor și Draw Gate potrivit formulelor. Faptul că apare și în scor și în draw gate nu autorizează eliminarea unei apariții: acestea sunt utilizări distincte, explicite, în Excel.

## 4 Porți tehnice și fragilitate

### 4.1 Market Direction

Pentru 1X, outcome-ul exclus este 2, iar pentru X2 este 1. Dacă Surse_Date!L8 nu este READY sau probabilitatea de piață exclusă nu este numerică, statusul este INPUT. În rest se compară `ROUND(prob_exclusa,12)` cu pragurile:

| Probabilitate de piață exclusă după ROUND | Status |
|---|---|
| ≤0,30 | PASS |
| >0,30 și ≤0,35 | PRUDENT |
| >0,35 | FAIL |

Formula exactă P0_Gates_v2!C4:

```excel
=IF(OR('Surse_Date'!L8<>"READY",NOT(ISNUMBER(B4))),"INPUT",IF(ROUND(B4,12)<='Parametri'!B20,"PASS",IF(ROUND(B4,12)<='Parametri'!B21,"PRUDENT","FAIL")))
```

### 4.2 Protected Side Strength și override

E4 = market_1 − market_2 pentru 1X; E5 = market_2 − market_1 pentru X2. Echipa protejată înseamnă gazde pentru 1X și oaspeți pentru X2, nu suma probabilității echipă plus egal.

G4 = market_2 − final_2; G5 = market_1 − final_1. Acesta este avantajul modelului combinat în reducerea rezultatului exclus, nu diferența Elo și nici diferența dintre echipe în modelul scoreline.

Formula exactă P0_Gates_v2!H4:

```excel
=IF(OR(NOT(ISNUMBER(E4)),NOT(ISNUMBER(G4))),"INPUT",IF(ROUND(E4,12)>=0,"PASS",IF(ROUND(E4,12)>=-'Parametri'!B22,"PRUDENT",IF(AND('Input_Meci'!B37="DA",ROUND(G4,12)>='Parametri'!B23,'Input_Meci'!B39<>""),"PRUDENT","FAIL"))))
```

```text
dacă E sau G nu sunt numerice: INPUT
altfel dacă ROUND(E,12) >= 0: PASS
altfel dacă ROUND(E,12) >= -0.05: PRUDENT
altfel dacă override == DA și ROUND(G,12) >= 0.07 și motiv != blank:
    PRUDENT
altfel: FAIL
```

Override-ul nu produce PASS, nu reduce probabilitatea de piață și nu modifică haircut-ul. Motivul este testat doar ca text nevid; implementarea nu trebuie să pretindă că formula îi verifică justificarea cantitativă. Verificarea calității explicației este responsabilitatea furnizorului inputului.

### 4.3 Agregarea P0 pentru 1X și X2

```text
dacă MarketDirection==INPUT sau ProtectedStrength==INPUT: INPUT
altfel dacă oricare este FAIL: FAIL
altfel dacă oricare este PRUDENT: PRUDENT
altfel: PASS
```

INPUT este testat înainte de FAIL în această formulă. Nu se înlocuiește ordinea cu o regulă generică „cel mai rău status câștigă”. Când MarketDirection este FAIL, un override valid pe ProtectedStrength nu salvează selecția.

### 4.4 Draw Market Gate pentru 12

Formula exactă P0_Gates_v2!I6:

```excel
=IF(OR(NOT(ISNUMBER('Model_1X2'!C10)),NOT(ISNUMBER('Uncertainty_v2'!B10))),"",MIN(1,'Model_1X2'!C10+'Uncertainty_v2'!B10))
```

Formula exactă P0_Gates_v2!K6:

```excel
=IF(OR('Surse_Date'!L8<>"READY",NOT(ISNUMBER(I6)),NOT(ISNUMBER(J6))),"INPUT",IF(ROUND(MAX(I6,J6),12)<='Parametri'!B8,"PASS",IF(ROUND(MAX(I6,J6),12)<='Parametri'!B9,"PRUDENT",IF(ROUND(MAX(I6,J6),12)<='Parametri'!B24,"WATCH","FAIL"))))
```

```text
model_draw_with_haircut = min(1, final_X + haircut)
draw_adj = max(model_draw_with_haircut, market_X)
dacă sursa pieței != READY sau cele două valori lipsesc: INPUT
altfel compară ROUND(draw_adj,12):
  <=0.20: PASS
  <=0.23: PRUDENT
  <=0.26: WATCH
  altfel: FAIL
P0_12 = DrawMarketGate
```

Plafonarea la 1 este obligatorie. P(0–0), P(1–1), concentrarea lor în remize și mismatch-ul din Draw_Risk sunt diagnostice. Nu adaugă gate-uri sau surcharges ascunse. Draw_Risk E4/E15 reflectă gate-ul ajustat, nu doar P(X) brut.

### 4.5 Favoritul puternic în deplasare

Uncertainty_v2!D13 adaugă puncte numai selecției X2. Dacă Pmarket(2)<0,55, valoarea este 0. Dacă Pmarket(2)≥0,55, contextul negativ 1 adaugă 5, contextul 2 adaugă 10, iar contextul 0 adaugă 0. Această comparație nu conține ROUND la 12 zecimale.

Double_Chance!AD5 cere C41 numeric și egal cu 0, 1 sau 2 chiar și când oaspeții nu ating pragul de 55%. C41 gol ori nevalid produce PENDING doar pentru X2. Nu se interpretează lipsa contextului ca zero implicit la import.

### 4.6 Auditul fragilității 1X

Activatorul B43 este manual: „Home favorite foarte scurt?”. Nu există prag numeric de cotă pentru activare. B6:B9 din Favorite_Fragility conțin patru semnale secundare: early-season, finishing, transition threat și dependența de piață. Activatorul nu intră în numărul semnalelor.

Formula exactă Favorite_Fragility_v4!B12:

```excel
=IF(B5="NU","N/A",IF(B5<>"DA","PENDING",IF(COUNTIF(B6:B9,"DA")+COUNTIF(B6:B9,"NU")<>4,"PENDING",IF(B11>='Parametri'!B48,"MATERIAL",IF(B11=1,"REVIEW","PASS")))))
```

```text
dacă activator == NU: status = N/A
altfel dacă activator != DA: status = PENDING
altfel dacă număr(DA)+număr(NU) în cele 4 semnale != 4: PENDING
altfel dacă număr(DA) >= 2: MATERIAL
altfel dacă număr(DA) == 1: REVIEW
altfel: PASS

extra_level = 1 dacă MATERIAL, altfel 0
closure = N/A dacă activator == NU
closure = CLOSED dacă status != PENDING și Surse_Date L12 == READY
closure = OPEN în rest
```

REVIEW în acest modul înseamnă un semnal verificat și nu este același lucru cu REVIEW din Surse_Date pentru context nerezolvat. Poate avea closure CLOSED și nu adaugă nivel. Două semnale DA plus un PENDING nu produc MATERIAL: auditul rămâne PENDING.

L12 surse este N/A la activator NU; PENDING dacă activatorul nu este DA/NU; REVIEW pentru NOT AVAILABLE/SOURCE CONFLICT când este DA; altfel cere status admis și META. O invaliditate în L12 nu schimbă F14 sau AD5/AD6; 1X rămâne PENDING deoarece closure este OPEN.

## 5 Scor risc nivel verdict și eligibilitate

### 5.1 Release pe selecție

```text
AD4 pentru 1X:
  dacă Model_1X2 F14 != READY: copiază F14
  altfel dacă Favorite_Fragility B14 == OPEN: PENDING
  altfel: READY
AD5 pentru X2:
  dacă F14 != READY: copiază F14
  altfel dacă C41 este număr din {0,1,2}: READY
  altfel: PENDING
AD6 pentru 12:
  dacă F14 != READY: copiază F14
  altfel: READY
```

Dacă doar auditul 1X este deschis, probabilitățile pot exista deja în B/F/Y, dar scorul și nivelul pentru 1X sunt blank și AA este NO. Interfața nu prezintă o probabilitate calculată ca dovadă că selecția este eligibilă.

### 5.2 Scorurile numerice

`indicator(conditie)` este 1 pentru adevărat și 0 pentru fals. R este Pfail_DC, H haircut-ul comun, MD Market Direction, PS Protected Strength, DG Draw Gate, U gate-ul final și A surcharge-ul deplasare.

```text
raw_1X = 180*R + 200*H
         + 10*indicator(MD==PRUDENT)
         + 10*indicator(PS==PRUDENT)
         + 60*indicator(U==FAIL)

raw_X2 = 180*R + 200*H
         + 10*indicator(MD==PRUDENT)
         + 10*indicator(PS==PRUDENT)
         + A + 60*indicator(U==FAIL)

raw_12 = 200*R + 120*H
         + 10*indicator(DG==PRUDENT)
         + 35*indicator(DG==WATCH)
         + 60*indicator(DG==FAIL)

score = min(100, ROUND_EXCEL(raw,0))
```

Formula exactă Double_Chance!L4:

```excel
=IF(OR(AD4<>"READY",NOT(ISNUMBER(B4)),NOT(ISNUMBER(Y4)),NOT(ISNUMBER(E4))),"",MIN('Parametri'!B43,ROUND(Y4*'Parametri'!B35+E4*'Parametri'!B36+IF(O4="PRUDENT",'Parametri'!B44,0)+IF(P4="PRUDENT",'Parametri'!B44,0)+IF(U4="FAIL",'Parametri'!B46,0),0)))
```

Formula exactă Double_Chance!L5:

```excel
=IF(OR(AD5<>"READY",NOT(ISNUMBER(B5)),NOT(ISNUMBER(Y5)),NOT(ISNUMBER(E5))),"",MIN('Parametri'!B43,ROUND(Y5*'Parametri'!B35+E5*'Parametri'!B36+IF(O5="PRUDENT",'Parametri'!B44,0)+IF(P5="PRUDENT",'Parametri'!B44,0)+T5+IF(U5="FAIL",'Parametri'!B46,0),0)))
```

Formula exactă Double_Chance!L6:

```excel
=IF(OR(AD6<>"READY",NOT(ISNUMBER(B6)),NOT(ISNUMBER(Y6)),NOT(ISNUMBER(E6))),"",MIN('Parametri'!B43,ROUND(Y6*'Parametri'!B37+E6*'Parametri'!B38+IF(Q6="PRUDENT",'Parametri'!B44,0)+IF(Q6="WATCH",'Parametri'!B45,0)+IF(Q6="FAIL",'Parametri'!B46,0),0)))
```

Scorul se calculează numai dacă AD este READY și B, Y, E sunt numerice. Două gate-uri PRUDENT la 1X/X2 produc cumulativ +20. Două gate-uri FAIL nu produc +120; se aplică o singură dată +60 pentru U=FAIL. Pentru 12, stările DG sunt exclusive, deci se aplică numai surcharge-ul stării curente. Plafonul se aplică după ROUND. Fragilitatea nu intră în raw sau score.

### 5.3 Nivelurile

| Scor rotunjit | Nivel de bază |
|---|---|
| ≤20 | 1 |
| >20 și ≤40 | 2 |
| >40 și ≤60 | 3 |
| >60 și ≤80 | 4 |
| >80 | 5 |

```text
level(row):
  dacă AD==CRITICAL MISSING: 5
  altfel dacă AD!=READY sau B nu este numeric: blank
  altfel dacă U este FAIL sau WATCH: 5
  altfel dacă U==INPUT: blank
  altfel: min(5, base_level(score) + fragility_extra_level)
```

WATCH pe Draw Gate impune nivel 5 chiar dacă scorul numeric ar indica 4. CRITICAL MISSING produce nivel 5 fără a fabrica un scor 100 sau P_adj=0. Pentru configurația fixată, scorurile sunt nenegative; formula de nivel nu introduce separat un MIN score de zero.

### 5.4 Eligibilitatea

Formula exactă Double_Chance!AA4:

```excel
=IF(AND(AD4="READY",OR(U4="PASS",U4="PRUDENT"),ISNUMBER(M4),M4<5),"YES","NO")
```

`Ranking Eligible=YES` numai dacă AD=READY, U în {PASS,PRUDENT}, M numeric și M<5. Aceeași regulă se aplică celor trei rânduri. RIDICAT poate avea AA=YES; aceasta este eligibilitatea generală, nu eligibilitatea pentru un top defensiv. AE=YES numai dacă AA=YES și N=DEFENSIV.

Excel nu sortează cele trei selecții într-un top și nu definește un tie-break între meciuri. Nu se inventează o ordine de ranking ca parte a motorului. Aplicația păstrează eligibilitatea și utilizează separat regulile de afișare/topuri ale proiectului.

### 5.5 Verdicturile în ordinea exactă

Următorul prefix se aplică înaintea ramurilor specifice:

```text
dacă AD==CRITICAL MISSING: NO BET
altfel dacă AD==INVALID: INPUT INVALID – NO RANK
altfel dacă AD!=READY: VERIFICARE NECESARĂ – NO RANK
altfel dacă U==FAIL: NO BET
altfel dacă U==WATCH: WATCH
altfel dacă U==INPUT sau M nu este numeric: NO RANK
altfel dacă M>=5: WATCH
altfel dacă AA!=YES: NO RANK
altfel dacă M==4: RIDICAT
altfel dacă M==3: MODERAT
altfel: aplică ramura selecției
```

Pentru 1X și X2:

```text
dacă M==1 și U==PASS și P_adj>=0.82: DEFENSIV
altfel dacă P_adj>=0.76: PRUDENT
altfel: MODERAT
```

Pentru 12:

```text
dacă U==PRUDENT sau M==2: PRUDENT
altfel: DEFENSIV
```

Pragurile P_adj nu folosesc ROUND. Se păstrează nivelul separat de verdict: un nivel 1 sau 2 poate primi MODERAT dacă P_adj pentru 1X/X2 nu atinge pragul. În mod similar, Draw PASS nu implică automat DEFENSIV; scorul poate produce nivel 2 sau 3. Nu adăuga testul de 82% în N6.

### 5.6 Monitorizarea și formulele Backtest

| Coloane Backtest | Semnificație și tip |
|---|---|
| A:D | Kickoff dată numerică, ligă text, gazde text, oaspeți text |
| E:I | Selecție; P_model; P_adj; cotă; P_market; probabilități numerice |
| J:K | Edge=G−I; EV=G×H−1 numai cu G numeric și H>1 |
| L:O | Nivel numeric, verdict prematch text, scor final text, rezultat 1/X/2 |
| P:Q | Hit 0/1; profit H−1 la succes sau −1 la eșec, numai dacă H numeric >1 |
| R:V | MD, PS, Draw Gate, early season, surcharge deplasare; snapshot |
| W:X | Brier=(G−P)^2; eligibilitate calibrare YES/NO |
| Y:AB | Timestamp predicție; evaluare recomandare; cotă validă; sursă snapshot |
| AC:AH | Validitate rând; Hit/Brier/P_adj eligibile; profit recomandări; eligibil ROI |

Hit pentru 1X este 1 la rezultat 1 sau X; pentru X2 la X sau 2; pentru 12 la 1 sau 2. Formula acceptă și numerele 1/2 pentru rezultat, respectiv 12 numeric pentru selecție. Un rezultat invalid sau lipsă produce blank. Scorul final N nu este parsat de formulă pentru a deduce rezultatul: O trebuie completat.

X=YES cere A și Y numerice, Y<A, AB nevid, P numeric, G în [0,1] și verdict în {DEFENSIV,PRUDENT,MODERAT,RIDICAT,WATCH,NO BET}. Nu cere cotă. Z=YES restrânge acest set la primele patru verdicturi. AA este MISSING pentru H nenumeric, VALID pentru H>1, INVALID altfel. AH=YES cere Z=YES și AA=VALID. Rândurile incomplete nu devin automat pierderi.

WalkForward_Calibration grupează 1X/X2/12 și folosește exact Backtest 4:203. B este N eligibil, C total hits, D=C/B, E media G eligibil, F=D−E, G media Brier, H profitul recomandărilor cu cote valide, I=H/M, J=PASS la N≥30, K=PASS la abs(F)≤0,03 altfel RECALIBRATE, L numărul recomandărilor, M numărul recomandărilor cu cote valide și N hit-rate-ul recomandărilor. La numitor zero se întoarce blank, nu zero procent.

Calibrarea include WATCH/NO BET cu probabilitate validă. ROI exclude aceste verdicturi și exclude recomandările fără cotă validă. Lipsa unui istoric de 30 de observații nu blochează prematch-ul: Double_Chance AF afișează FĂRĂ ISTORIC, N INSUFICIENT sau starea K. Nici AF, nici calibrarea nu sunt strămoși ai lui N sau AA.

## 6 Validare și teste automate

### 6.1 Separarea verificărilor

Testele de portare verifică trei niveluri: parsarea și maparea inputurilor, calculele pe fiecare modul și comparația end-to-end cu Microsoft Excel recalculat. Un test care compară doar două implementări ale aceleiași formule nu certifică singur echivalența cu Excel.

Pachetul include 37 de cazuri complete, fiecare cu inputuri pe coordonate și 96 de rezultate intermediare/finale așteptate. Aceste rezultate au fost obținute prin evaluarea formulelor extrase; exemplul de bază este verificat și aritmetic independent. Nu sunt prezentate ca rezultate deja executate în Microsoft Excel. Scriptul PowerShell furnizat face această comparație pe un calculator Windows cu Excel instalat.

Au fost parsate și evaluate toate cele 3.068 de formule pentru starea inițială a fișierului. Cache-ul are o diferență locală: Double_Chance!T5 stochează 0, deși formula curentă, cu piața/contextul incomplet, produce `""`. Se folosește recalcularea, nu cache-ul istoric, ca referință. Această diferență nu este motiv pentru modificarea formulei.

### 6.2 Exemplu complet de meci sintetic

Meciul este exclusiv un fixture de test, fără recomandare pentru un eveniment real. Gazde Echipa Alfa, oaspeți Echipa Beta, Liga Test, kickoff 19.09.2026 la 20:00, teren neutru NU. Toate momentele sunt în același fus. Sample gazde=12, oaspeți=10; confidence=A; override-urile=NU; C41=0; activator fragilitate=NU și celelalte trei flag-uri manuale=NU.

| Sursă probabilități | P1 | PX | P2 | Sumă |
|---|---|---|---|---|
| Scoreline | 0,84 | 0,10 | 0,06 | 1 |
| Strength | 0,80 | 0,12 | 0,08 | 1 |
| Piață de-vig | 0,82 | 0,10 | 0,08 | 1 |

Cotele DC informative sunt 1X=1,05, X2=5,00, 12=1,10. Pentru a ilustra proveniența probabilităților de piață, un set ipotetic proporțional de cote simple ar fi 1/(1,05×0,82), 1/(1,05×0,10), 1/(1,05×0,08); acestea sunt circa 1,16144, 9,52381 și 11,90476. Nu se introduc aceste aproximații în motor și nu se folosesc pentru a recalcula piața din fixture: valorile de-vig exacte din tabel sunt inputurile normative.

Surse_Date C5:C12=VERIFIED; D este „Sursa sintetica test”, cu D8 derivat din Input_Meci B42; E=19.09.2026 18:00; F=19.09.2026 17:00; I conține metoda fixture-ului sintetic; J=DA. K11=FARA IMPACT MATERIAL. Rândul 10 include N prior 30/30 și K10=INTEGRAT IN MODELE, dar se evaluează N/A deoarece N curent≥8. Rândul 12 este N/A deoarece activatorul este NU. Statisticile contextuale neutilizate și diagnosticele opționale pot rămâne blank: nu sunt inventate pentru a închide modelul.

Rezultatele de release: L5:L9=READY, L10=N/A, L11=READY, L12=N/A, L15=READY, F12/F13/F14=READY și AD4:AD6=READY. N minim=10, early season=NU, confidence efectiv=A și haircut=0,01.

```text
final_1 = 0.50*0.84 + 0.25*0.80 + 0.25*0.82 = 0.825
final_X = 0.50*0.10 + 0.25*0.12 + 0.25*0.10 = 0.105
final_2 = 0.50*0.06 + 0.25*0.08 + 0.25*0.08 = 0.070
suma finală = 1
```

| Rezultat | 1X | X2 | 12 |
|---|---|---|---|
| P_model | 0,930 | 0,175 | 0,895 |
| Haircut | 0,010 | 0,010 | 0,010 |
| P_adj | 0,920 | 0,165 | 0,885 |
| Failure model | 0,070 | 0,825 | 0,105 |
| Failure market | 0,080 | 0,820 | 0,100 |
| Pfail_DC | 0,080 | 0,825 | 0,105 |
| Market Direction | PASS | FAIL | N/A |
| Protected Strength | PASS | FAIL | N/A |
| Draw ajustat | N/A | N/A | 0,115 |
| P0 final | PASS | FAIL | PASS |
| Scor înainte de ROUND/plafon | 16,4 | 210,5 | 22,2 |
| Scor final | 16 | 100 | 22 |
| Nivel final | 1 | 5 | 2 |
| Verdict | DEFENSIV | NO BET | PRUDENT |
| Ranking Eligible | YES | NO | YES |
| Eligibil DEFENSIV | YES | NO | NO |

Scor 1X: 180×0,08 + 200×0,01=16,4 → ROUND=16. X2: 180×0,825 + 200×0,01 + 60=210,5 → ROUND=211 → plafon=100. 12: 200×0,105 + 120×0,01=22,2 → ROUND=22. 12 rămâne PRUDENT deși draw gate este PASS și P_adj este 88,5%, deoarece nivelul este 2.

În virgulă mobilă, valoarea 1X poate fi serializată 0.9199999999999999. Aceasta reprezintă același rezultat la precizia de comparare declarată; nu se rotunjește la 0,92 înaintea deciziilor.

### 6.3 Teste de stare și de ramură

| Fixture | Comportament verificat |
| --- | --- |
| baseline | Trei distributii distincte; 1X defensiv, 12 prudent desi Draw PASS. |
| price_invariance | Cotele DC nu schimba verdictul, scorul sau eligibilitatea. |
| early_season_A | A devine B; haircut 0.045; prior documentat. |
| early_season_C | N=0 este valid cu prior; haircut 0.07. |
| sample_boundary_8 | N=8 nu este early season. |
| prior_pending | Prior neintegrat: PENDING, fara nivel artificial 5. |
| prior_missing | Lipsa critica conditionala cand N<8. |
| global_pending | Sursa obligatorie neverificata. |
| critical_missing | G0 critic -> nivel 5, NO BET, scor blank. |
| invalid_distribution | Valoare individuala >1 -> INVALID. |
| normalize_sum_102 | Suma 1.02 acceptata dupa ROUND la 12 zecimale; normalizare. |
| invalid_sum | Suma 1.021: INVALID, nu se normalizeaza automat. |
| official_pending_allowed | Stare comuna CONDITIONAL; F14 READY. |
| context_unresolved | REVIEW G1 devine PENDING comun. |
| fragility_open | Numai 1X PENDING; X2 si 12 nu sunt blocate de audit. |
| fragility_material | Doua semnale DA, sursa READY: scor 1X neschimbat, nivel +1. |
| fragility_review | Un singur DA verificat: REVIEW, +0 nivel, audit CLOSED. |
| fragility_source_invalid | Invaliditatea auditului r12 blocheaza numai 1X ca PENDING. |
| away_context_pending | Doar X2 PENDING, chiar daca Pmarket away <55%. |
| away_favorite_surcharge_1 | Surcharge X2=5; scor 21 si nivel 2. |
| away_favorite_surcharge_2 | Surcharge X2=10; scor 26. |
| draw_pass_20 | Draw model + 0.01; comparatie ROUND(...,12). |
| draw_prudent_23 | Draw model + 0.01; comparatie ROUND(...,12). |
| draw_watch_26 | Draw model + 0.01; comparatie ROUND(...,12). |
| draw_fail_above26 | Draw model + 0.01; comparatie ROUND(...,12). |
| market_pass30 | Market Direction 1X la frontiera. |
| market_prudent35 | Market Direction 1X la frontiera. |
| market_fail_above35 | Market Direction 1X la frontiera. |
| strength_minus5 | Protected Strength 1X; restul controalelor se aplica separat. |
| strength_below_minus5 | Protected Strength 1X; restul controalelor se aplica separat. |
| override_valid | Protected FAIL devine PRUDENT; Market Direction ramane PRUDENT. |
| override_no_reason | Motiv blank: override refuzat. |
| override_cannot_bypass_market | Protected poate PRUDENT; Market FAIL mentine NO BET. |
| draw_defensive | 12: scor13, nivel1, DEFENSIV. |
| chronology_invalid | Verificare dupa kickoff: INVALID. |
| sample_fraction_invalid | Sample curent trebuie intreg. |
| numeric_text_market | Textul numeric este ignorat de ISNUMBER, nu convertit automat. |

Pentru `fragility_material`, scorul 1X rămâne 16, nivelul devine 2 și verdictul PRUDENT. Pentru `early_season_A`, haircut=0,045, P_adj 1X=0,885, scor=23 și nivel=2. Pentru `critical_missing`, nivelul este 5 și verdictul NO BET, dar scorul și P_adj nu se umplu cu valori artificiale. Pentru `fragility_open`, numai 1X nu intră în clasament; probabilitatea sa calculată rămâne prezentă.

### 6.4 Teste de frontieră suplimentare în backend

Se testează fiecare prag la valoare exactă și de o parte/de alta: sumă distribuții 0,98/1,02; MD 0,30/0,35; protected delta 0/−0,05; avantaj override 0,07; draw 0,20/0,23/0,26; away threshold 0,55; N=7/8; P_adj 0,76/0,82; scoruri la jumătate înainte de rotunjire și limitele 20/40/60/80. Un delta de 1e-10 este suficient pentru a traversa pragurile rotunjite la 12 zecimale; un delta de 1e-13 poate dispărea prin ROUND.

Exemple unitare pentru ROUND: 20,499999→20; 20,5→21; 40,5→41; 80,5→81. ROUND_EXCEL rotunjește jumătățile în direcția opusă lui zero; funcția `round()` din Python nu se folosește fără adaptare. Nu se introduc epsiloni în comparațiile fără ROUND, precum P_adj≥0,82 sau away≥0,55.

Testele metamorfice trebuie să confirme: modificarea cotelor DC nu schimbă N/L/M/AA; schimbarea diagnosticelor Draw/Loss nu schimbă verdictul; istoric Backtest gol versus populat nu modifică N/AA; auditul 1X nu blochează automat X2/12; reducerea sample-ului aplică exact confidence cap și haircut; un override valid nu anulează MarketDirection FAIL.

### 6.5 Procedura de comparație cu Microsoft Excel

Pachetul include `verifica_excel.ps1`. Se rulează din folderul extras, cu Microsoft Excel desktop instalat și cu fișierul sursă disponibil local:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\verifica_excel.ps1 -Workbook "C:\cale\11_model_analiza_pariu_sansadubla_optimizat_V2(1).xlsx"
```

Scriptul verifică SHA-256, deschide sursa read-only, aplică fiecare fixture într-o instanță separată de workbook, refuză inputuri peste formule, execută CalculateFullRebuild și compară celulele așteptate. Închide fără salvare. Generează raportul JSON și afișează PASS numai dacă toate comparațiile au trecut. Nu rescrie sursa sau pragurile. Raportul de test se păstrează împreună cu versiunea motorului din aplicație.

În backend, aceeași intrare de fixture este adaptată la schema internă și se compară cu aceleași rezultate, incluzând stările intermediare. La eșec se raportează celula, valoarea Excel, valoarea aplicației și primul modul divergent. Nu se ascunde un eșec al verdictului prin toleranță numerică.

```text
pentru fiecare fixture:
    excel_actual = calculate_in_microsoft_excel(fixture.inputs)
    app_actual = app_engine(fixture.inputs)
    pentru fiecare coordonată din fixture.expected:
        compară excel_actual cu expected
        compară app_actual cu excel_actual
        numere: abs(diff) <= 1e-12
        scoruri și niveluri: egalitate exactă
        texte: egalitate exactă
        blank: null sau șir gol, niciodată 0
```

`pytest -q` este verificarea standard a proiectului și trebuie să treacă fără cheie API în modul MOCK. În Cursor se adaugă teste de portare în structura reală găsită, fără a presupune că există deja un modul cu un anumit nume. `streamlit run app.py` trebuie să pornească interfața la http://localhost:8501 și să afișeze separat starea datelor, P_adj, gate, scor, nivel, verdict și eligibilitate.

### 6.6 Limitele compatibilității și acceptanța

Configurația de referință este cea extrasă, cu ponderile 50/25/25. Formula fixture-ului nu verifică toate combinațiile posibile de parametri corupți; portarea nu trebuie să extindă tacit domeniul suportat. Datele API −1/−2/null se mapează la indisponibilitate în adaptor, nu la zero. Dacă se testează inputuri Excel invalide brute, se păstrează statusul pe care formula îl produce, fără a-l confunda cu normalizarea transportului API.

Se păstrează semantica Excel pentru ISNUMBER, COUNT, COUNTBLANK, comparații de text fără sensibilitate la litere mari/mici și diferența dintre celulă goală și formulă cu șir gol. Nu se face automat trim pe motivele override: Excel testează doar nevid. La export și UI pot exista validări distincte, dar acestea nu trebuie ascunse în motorul declarat identic.

Datele introductive din Cadru v5 și Matrice v4 sunt guvernanță. Regulile specifice din workbook stabilesc formula exactă a acestui model, inclusiv haircut-ul în draw gate și separarea stărilor PENDING/INVALID/CRITICAL MISSING. Nu se importă în acest motor structural floors sau praguri ale altor familii de pariuri. Nu se cere validare OOS ca gate prematch suplimentar: calibrarea existentă este informativă.

Acceptanța cere: aceeași sursă identificată prin hash; toate cele 37 de fixtures comparate cu Excel; toate ramurile și frontierele suplimentare testate; zero diferențe în statusuri, niveluri și verdicturi; nicio scriere în originale; nicio regulă de probabilitate introdusă fără suport în formule. Până la executarea etalonului Microsoft Excel, rezultatul este o specificație verificată prin extracție și calcul independent, nu o certificare a unui backend deja implementat.

## Anexa A Instrucțiune de implementare pentru Cursor

Obiectiv unic: portarea motorului Șansă Dublă optimizat_V2, cu identitate față de Excel. Mesajul complet copiabil este în `Mesaj_Cursor.md`. Nu include alte modele, modificări de praguri, recalibrare sau un model nou de generare a probabilităților externe.

## Anexa B Fișierele pachetului

| Fișier | Utilizare |
|---|---|
| Manual_tehnic_Sansa_Dubla_V2.docx | Manual pentru lectură și revizie |
| Manual_tehnic_Sansa_Dubla_V2.md | Aceeași specificație în text pentru Cursor |
| Anexa_formule_exacte.md | Formule lizibile cu dependențe |
| formule_integrale.json | Toate cele 3.068 de formule, fără deduplicare |
| schema_celule.json și CSV | Mapare pe coordonate, tipuri și roluri |
| constante.json | Cele 45 de valori de configurație și utilizarea lor |
| cazuri_test.json | 37 de seturi complete de input și rezultate așteptate |
| rezultate_test.csv | Rezumatul celor 111 rezultate pe selecții |
| verifica_excel.ps1 | Comparația fixture-urilor cu Microsoft Excel |
| Mesaj_Cursor.md | Brief de implementare |
| manifest.json | Identitatea sursei și inventarul foilor |

Originalul Excel se furnizează separat agentului și nu este modificat de pachet. Schema reprezintă specificația celulelor, nu un endpoint API sau schema deja existentă a aplicației. Denumirile interne noi trebuie alese în Cursor după verificarea repository-ului.
