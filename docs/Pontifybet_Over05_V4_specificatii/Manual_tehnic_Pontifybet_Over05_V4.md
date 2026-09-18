# Manual tehnic de implementare Pontifybet Over 0 5

Specificație pentru reproducerea fișierului 1_model_analiza_over0.5_optimizat_V4.xlsx. Nucleu probabilistic cu extensii V2, V3 și V5; selector final metodologia v9.

## Identitatea modelului și contractul de compatibilitate

Fișierul de referință este V4, nu un workbook V2 separat. Denumirea „Model optimizat V2” desemnează numai o etapă istorică din acest fișier. Pentru identitate cu Dashboard trebuie reproduse probabilitatea GP, Confidence GT, Risk Score HE, G0 HG, nivelul HH, clasa HI și recomandarea HK. Portarea exclusivă a coloanelor EA și EL produce alt rezultat.

SHA256 al fișierului analizat:

```text
8068c1f95c8dfa28def846b51b9f152a9e52fd085d8085344a5321b97338c42a
```

Sunt 20 de foi vizibile, 14.026 de celule cu formule și 5 exemple DEMO. Foaia principală are 219 coloane A:HK și 100 de rânduri pregătite pentru meciuri, 4:103. Fiecare rând are 108 formule și 111 poziții fără formule, dintre care FB este retrasă. Nu există named ranges. Proprietatea calcPr nu este prezentă în obiectul workbook citit; aceasta nu certifică faptul că valorile cache sunt rezultatul unei recalculări recente.

Obiectivul acestei specificații este portarea fidelă. Nu se corectează implicit formule considerate discutabile. O corecție de model produce o versiune nouă și un alt set de rezultate de referință. Solicitarea actuală autorizează specificarea unui motor în cod, ceea ce extinde arhitectura MVP anterioară în care Python alimenta numai Excel. Nu implică migrarea celorlalte modele, o a doua sursă de date sau schimbarea interfeței Streamlit.

Verificarea efectuată: evaluator independent al formulelor nucleului, comparat cu cache-ul atașamentului, 540/540 comparații reușite pe cele 5 rânduri DEMO, la toleranță numerică 1e-12. Nu a fost executată o recalculare în Microsoft Excel. Certificarea finală necesită oracle-ul Excel descris în secțiunea 5. Compatibilitatea tehnică nu reprezintă validare a performanței predictive.

## 1 Arhitectura și structura foilor

### 1.1 Cele trei trasee care trebuie separate

Traseul probabilității: inputuri și Setari model → BJ:BS → BT și DZ → FI și FJ → GJ și GK → GL → GO și GP → GQ:GT → Dashboard. DZ folosește BT, nu BV. GL folosește FJ și GK; GP nu este simplul complement neplafonat al lui GL.

Traseul recomandării: inputuri tehnice → GM și GY:HD → HE → HF → HG → HH → HI → HK. Ponderile HE provin din Risk_Classification!E28:E32, care citesc B4:B8. Foaia Risk_Classification afișează și scorul meciului selectat, dar acest circuit nu este circular: ponderile E28:E32 nu depind de scorurile B28:B32.

Traseul auditului: Dashboard și ZeroMass_Gate_v5 citesc meciul selectat; Backtest citește probabilitatea curentă GP și verdictul istoric GV; Settlement alimentează rapoartele de calibrare și distribuție a eșecurilor. Frozen_Predictions nu este conectată automat la Settlement. Foile ZeroMass_Gate_v4 și ZeroMass_WF_v4 au calcule locale, independente de selectorul HK.

Numele unei foi sau eticheta „Gate” nu sunt suficiente pentru a o considera poartă activă. În V4, ZeroMass_Gate_v5!B22:B23 afișează GU/GV istorice, în timp ce Dashboard!C21 citește HK. Nu combina aceste două verdicturi într-un singur câmp.

### 1.2 Structura principală

Analize meciuri!1:2 conține titluri și grupe; rândul 3 conține antetele exacte. Rândurile 4:8 sunt DEMO; 9:103 sunt pregătite pentru inputuri. A este cheia folosită de MATCH. Formulele principale încep de regulă cu IF(A="","",...), deci identificatorul gol suprimă ieșirea rândului. EE și EK sunt formule constante ="".

Blocurile sunt A:H identificare; I:V sezon H/A; W:AF recent; AG:AN H2H și competiție; AO:AU cote și calitate; AV:BG context; BH:BI explicații și URL-uri; BJ:CI calcule inițiale; CJ:DV inputuri V2; DW:EU calcule V2 și live; EV:FA inputuri zero-mass; FB retras; FC:FX calcule V3; FY:GB inputuri recente V5; GC:GX extensia V5; GY:HK clasificarea finală v9.

Whitelist-ul A:BI din MVP nu acoperă modelul complet: sunt necesare și CJ:DV, EV:FA, FY:GB. Aceasta este constatarea structurii sursei, nu permisiunea de a scrie peste formule. Whitelist-ul trebuie construit din rolul fiecărei celule, nu prin autorizarea întregului A:HK. Formula FC, de exemplu, nu este input, chiar dacă vecinătatea EV:FB include inputuri.

### 1.3 Tipuri și convenții

Un procent se stochează ca fracție: 90% = 0.9. GF, GA și xG sunt medii pe meci, nu totaluri de sezon. N, numărul de 0–0 recente și numărul de selecții sunt întregi; indicatorii 0/1 sunt întregi în Excel, nu texte „DA/NU”. Clasa, gate-urile și verdicturile sunt texte distincte.

Excel nu impune o schemă de tipuri rigidă. Tipurile semantice din anexă provin din antete, legendă, formule, formate și exemple. Celulele goale nu justifică inventarea unei valori sau a unei surse. Tipul rezultatului poate fi Float sau text gol; unele formule pot produce o eroare Excel. Un obiect de aplicație trebuie să distingă valoare numerică, blank fizic, șir gol calculat, text de stare și eroare.

C este o dată Excel; exemplul nu conține ora kickoff și nici fusul orar. Pontifybet păstrează separat timestamp-ul cu fus Europe/Bucharest pentru selecție și cutoff. Nu interpreta lipsa orei din Excel ca oră de începere 00:00. Nu adăuga un filtru kickoff în algoritmul numeric sub eticheta „existent în Excel”.

Anexa A inventariază foile și schema câmpurilor. Anexa B conține formulele literale grupate pe familii și adresele dependențelor. workbook_inventory.json păstrează toate celulele populate, inclusiv textele documentare, formatele, valorile cache și comentariile. formula_manifest.json păstrează fiecare dintre cele 14.026 de formule, fără a omite rândurile repetitive.

## 2 Date de intrare și configurații

### 2.1 Datele statistice nu sunt reconstruite în workbook

Fișierul nu conține lista meciurilor istorice din care au fost calculate mediile. I:AN, EV:FA și FY:GB sunt inputuri deja agregate. Nu există un mecanism executabil care să aleagă ultimele 5 meciuri, să excluză amicale sau să filtreze sezonul după dată. Exemplele folosesc frecvent N recent = 5, dar W și AB sunt inputuri și pot fi diferite.

Pentru upstream, mediile sunt definite semantic prin sumă/N pe eșantionul potrivit; O0.5 este numărul meciurilor cu total goluri ≥1/N; FTS este numărul meciurilor în care echipa nu înscrie/N; CS este numărul meciurilor fără gol primit/N; 0–0 FT și HT sunt frecvențe de scor 0–0 la final, respectiv pauză. FY/FZ sunt frecvențe recente FTS, iar GA/GB sunt numere întregi de scoruri 0–0 recente, nu rate. Aceste definiții nu reprezintă formule Excel suplimentare.

Pentru a reproduce rezultatele trebuie folosit același eșantion, aceleași date și același cutoff. Dacă API oferă altă fereastră pentru „recent”, nu declara echivalența. Schema exactă a răspunsurilor FootyStats și corespondentul fiecărui indicator se verifică în Cursor în client și în payload-uri reale. Acest manual nu presupune câmpuri sau endpoint-uri API suplimentare. URL-urile din workbook sunt surse documentare/demo, nu dovada accesului API și nici un mandat pentru o a doua sursă.

### 2.2 G0 real din formule

FK = DA numai dacă COUNT(EV:FA)=6 și COUNT(O,V,FC,FD)=4. FC cere J și L nenule ca blank și L>0; FD cere Q și S și S>0. Prin urmare, xGF de sezon L și S este efectiv critic prin finishing, chiar dacă BK are fallback la goluri.

GM = DA numai dacă FK=DA, COUNT(FY:GB)=4, COUNT(I,P,W,AB,Z,AE,EX,EY,GC,GD)=10 și COUNT(BJ:BN)=5. GC cere X,Z și Z>0; GD cere AC,AE și AE>0. Formula verifică prezența numerică și unele condiții indirecte, nu toate domeniile sau proveniența datelor.

G0 activ este HG = IF(GM="DA","PASS","FAIL – DATE CRITICE ZERO-MASS INCOMPLETE"). Această formulă nu cere explicit N/U, kickoff, identificarea unei surse independente, cote sau lineup. Lipsa lui N/U poate utiliza fallback în DZ și totuși HG poate rămâne PASS. Invers, lipsa L, S, Z sau AE poate închide G0. G0 minimal din brief-ul vechi al aplicației nu este identic cu cel din fișier.

Separă validatorul operațional al aplicației de compatibilitatea formulelor. Ratele trebuie să fie în [0,1], N să fie întreg ne-negativ, cote reale pozitive, medii ne-negative și număr 0–0 recent ≤ N recent. Sunt verificări de calitate recomandate, nu toate sunt impuse de Excel. Nu le prezenta drept formule preexistente. În workbook există validări native numai pentru EV:FA și FY:FZ între 0 și 1, respectiv GA:GB întregi între 0 și 20.

### 2.3 Lipsă versus zero

Sentinelele API -1/-2/null se normalizează în starea NOT AVAILABLE la nivelul aplicației, fără a deveni 0. Celula numerică destinatar rămâne goală. „NOT AVAILABLE” și „NOT CHECKED” sunt stări de metadata/validation_report, nu valori de inserat într-o expresie numerică.

În AV:BG, un blank fizic este tratat de aritmetica Excel ca zero în anumite expresii; textul literal NOT CHECKED produce eroare la înmulțire în BR. Aplicația trebuie să păstreze blank-ul și starea separată pentru identitate cu Excel, fără să pretindă că absența datelor confirmă un context neutru. Un zero explicit înseamnă evaluare numerică neutră sau absența fenomenului, după câmp.

COUNT ignoră textul și blank-urile; AVERAGE din referințe ignoră blank-urile. Dacă lipsește o valoare din CM:CN, DW folosește media celei prezente, nu împarte suma la 2. Dacă ambele lipsesc, IFERROR returnează reperul neutru 1 la raport. Reproducerea exactă necesită aceste diferențe.

### 2.4 Configurații și prioritate

Setari model!A5:I11 definește 7 regimuri. Se selectează rândul prin MATCH(E,A5:A11,0), fără aproximare sau alegerea implicită a primului regim. O denumire incompatibilă produce eroare. B:F sunt ponderile pentru BJ:BN; G este ponderea pieței BP; H multiplică impactul contextual; I multiplică Confidence. J este control ROUND(SUM(B:G),6), nu normalizare automată a ponderilor.

Setari model!B15:B25 conține coeficienții AV:BF, în aceeași ordine. B30=8 și B31=5 sunt puteri de shrinkage, nu numărul obligatoriu de meciuri recente. B44=40 există ca parametru documentat, dar CC folosește ținte hardcodate 10,10,5,5,5,100; nu înlocui aceste constante cu B44.

Valorile operative principale sunt B53=0.75, B54=1.25 pentru context; B58=5 pentru eticheta sample; B64=250 și B65=0.5 pentru priorul 0–0 al ligii; B97=0.75, B98=1.6 pentru FI; B99=0.95, B100=1.15 pentru clasa zero-mass; B101=0.65 pentru P0; B102:B105=0.90/0.91/0.92/0.94 pentru capul raportării. B95 și B96 sunt goale și retrase, împreună cu FB.

B35:B43 și B76 rămân folosite de selectori istorici. Nu sunt pragurile recomandării HK. Pentru HK, pragurile 20,40,60,80 sunt literale în HF. Ponderile active sunt expresii exacte 0.25/0.85, 0.30/0.85, 0.15/0.85, 0.10/0.85, 0.05/0.85, nu procentele rotunjite afișate 29.41% etc.

## 3 Logica de calcul în ordinea dependențelor

### 3.1 Notație și precizie

În pseudocod, S[n] înseamnă Setari model!Bn; c[COL] înseamnă Analize meciuri!COLr pentru rândul curent. wB...wI reprezintă celulele din rândul de regim. clamp(x,lo,hi)=MAX(lo,MIN(hi,x)). Această notație explică formulele; în codul final se păstrează parentetizarea literală din anexa B, în special pentru expresiile cu sume și produse.

Nu se rotunjesc pașii intermediari. Folosește aritmetică double/binary64 și ordinea operațiilor din formulă. ROUND apare în controlul ponderilor J5:J11 cu 6 zecimale. TEXT formatează explicațiile și Dashboard, fără a rotunji valorile folosite ulterior. Python round nu este înlocuitor universal pentru Excel ROUND la egalități; folosește un helper dedicat dacă sunt portate formule ROUND.

Egalitatea bit cu bit nu este garantată între implementările EXP/LN/SQRT ale platformelor. Contractul recomandat este eroare absolută și relativă ≤1e-12 pentru valori numerice, identitate exactă pentru gate/level/verdict și afișare identică după formatare. Toleranța se aplică testului de comparație, niciodată condițiilor de prag. Testele la limită trebuie aprobate de oracle-ul Microsoft Excel.

### 3.2 Shrinkage și intensitățile BJ până la BN

```python
fallback(x, prior) = prior if x is blank else x
shrink(n, x, prior, k) = (n * fallback(x, prior) + k * prior) / (n + k)

BJ = sqrt(shrink(I,J,AJ,S[30]) * shrink(P,R,AJ,S[30])) \
   + sqrt(shrink(P,Q,AK,S[30]) * shrink(I,K,AK,S[30]))
BK = sqrt(shrink(I,fallback(L,fallback(J,AJ)),AJ,S[30]) \
        * shrink(P,fallback(T,fallback(R,AJ)),AJ,S[30])) \
   + sqrt(shrink(P,fallback(S,fallback(Q,AK)),AK,S[30]) \
        * shrink(I,fallback(M,fallback(K,AK)),AK,S[30]))
BL = sqrt(shrink(W,X,AL/2,S[31]) * shrink(AB,AD,AL/2,S[31])) \
   + sqrt(shrink(AB,AC,AL/2,S[31]) * shrink(W,Y,AL/2,S[31]))
BM = aceeași structură ca BL, cu Z→X, AF→AD, AE→AC, AA→Y
     ca lanțuri de fallback xG→goluri→AL/2
BN = (AG * fallback(AH,AL) + 5 * AL) / (AG + 5) if AG > 0 else AL
```

În linia BK, litera S neindexată desemnează coloana xGF oaspeți, iar S[n] parametrul din Setari model; implementarea trebuie să folosească nume distincte pentru a evita ambiguitatea. Media geometrică combină atacul unei echipe cu apărarea adversă. Nu există estimare prin regresie, antrenare ML sau fitting al unei distribuții comune a scorurilor.

### 3.3 Piață și context

BO de-vig: dacă AR>1 și AS>1, BO=(1/AR)/((1/AR)+(1/AS)); dacă numai AR>1, BO=MIN(0.995,(1/AR)/(1+S[32])); fără AR valid, BO=1-EXP(-AL). BP=-LN(1-BO). EC folosește aceeași corecție cu ambele cote, dar cu o singură cotă returnează 1/AR, fără marja S[32]; fără AR>1 returnează text gol. BO și EC nu sunt interschimbabile.

BQ=BJ*wB+BK*wC+BL*wD+BM*wE+BN*wF+BP*wG. Piața are pondere nenulă în toate cele 7 regimuri. BR=clamp(1+(AV*S[15]+...+BF*S[25])*wH,S[53],S[54]); BG nu intră în BR. BS=BQ*BR; BT=EXP(-BS).

Pentru GH, intensitatea este diferită: L_tech=((BJ*wB+BK*wC+BL*wD+BM*wE+BN*wF)/(wB+wC+wD+wE+wF))*BR. Componenta BP este exclusă, iar ponderile tehnice sunt renormalizate. Nu substitui BS pentru această intensitate. ZeroMass_Gate_v5!B9 afișează BS, ceea ce poate induce o interpretare greșită a semnalului GH.

### 3.4 Ramura inițială BV și ramura activă DZ

BU=1+MIN(S[33],AN/100*S[33])*(AM/EXP(-AL)-1), cu fallback 1 dacă AM sau AN este blank. BV combină MIN(0.45,BT*BU) cu empiricul SQRT(MAX(0,1-N)*MAX(0,1-U)), la greutatea S[34]*MIN(1,(I+P)/20), apoi limitează între 0.005 și 0.45. BW=1-BV. Aceasta este ramura veche, folosită de CG și CH, nu baza lui GL.

DW este factorul calității ofensive. Pornește de la 1, adaugă 0.08*(AVERAGE(CM:CN)/S[66]-1), 0.08 pentru CO:CP/S[67], 0.06 pentru CQ:CR/S[68], 0.04 pentru CS:CT/S[69], 0.04 pentru CU:CV/S[70], apoi scade S[73]*AVERAGE(CW:CX). Fiecare raport fără date are fallback 1, iar penalizarea fără date fallback 0. Rezultatul este limitat la [S[71],S[72]]=[0.85,1.15].

DX=1+S[62]*MAX(flag_promovate,flag_etapa_1)+S[63]*flag_etape_2_3. flag_promovate=1 dacă CK sau CL este 1; flag_etapa_1=1 dacă CJ nu este blank și CJ≤1; flag_etape_2_3=1 dacă 1<CJ≤3. O promovată în etapa 2 poate acumula ambii termeni și primi DX=1.35. Nu înlocui cu un IF exclusiv.

DY=1+S[74]*(numărul atacanților indisponibili din CY:CZ)+S[75]*(numărul portarilor indisponibili din DA:DB). Numără doar celulele neblank cu valoarea 0. Parametrii sunt +0.08 și -0.06. Blank-ul nu este considerat indisponibilitate confirmată.

```python
a = S[34] * min(1, (I + P) / 20)
emp = sqrt(max(0,1-N) * max(0,1-U)) if COUNT(N,U)==2 else BT
b = S[65] * min(1, (0 if AN is blank else AN/S[64]))
league_zero = BT if AM is blank else AM
DZ = min(0.6, max(0.002,
     (((1-a)*BT + a*emp)*(1-b) + b*league_zero) * DX * DY / DW))
```

Eticheta „ZIP/regim” din Excel descrie acest amestec și aceste ajustări. Nu implementa automat o distribuție ZIP standard dintr-o bibliotecă statistică și nu introduce un parametru Dixon–Coles rho; asemenea fitting nu există în formulele atașate.

### 3.5 Zero mass V3 și eliminarea FB

FC=clamp(J/L,0.5,1.5) dacă J și L sunt prezente și L>0; altfel gol. FD analog Q/S. FE=SQRT(EV*EW)/S[87], numai cu două valori numerice. FF=AVERAGE(SQRT(O*EY),SQRT(V*EX))/S[88], numai cu toate patru. FG=MAX(0,1-AVERAGE(FC:FD)), cu ambele disponibile. FH=S[94]*AVERAGE(EZ:FA)/S[89], cu ambele numerice.

```python
FI = clamp(1 + S[90]*(FE-1) + S[91]*(FF-1)
             + S[92]*FG + S[93]*(FH-1), S[97], S[98])
     if COUNT(FE:FH)==4 else blank
FJ = min(S[101], max(0.002, DZ*FI)) if FI != blank else blank
```

S[94]=0.75 rămâne activ, iar S[93]=0.20 rămâne activ. Termenul manual FB a fost eliminat, fără redistribuirea ponderii sale. Dacă media EZ/FA=0.35, FH=0.75, nu 1; contribuția S[93]*(FH-1) este -0.05. „Normalizarea” FH la 1 ar schimba modelul. FB și S[95:96] nu trebuie citite de motor.

FL clasifică FI: dacă FK nu este DA, NEDETERMINAT; FI≤0.95 SCĂZUT; FI≤1.15 MEDIU; altfel RIDICAT. Această clasă istorică este folosită de FT. Clasa curentă GN clasifică produsul FI*GK, nu doar FI.

### 3.6 Low conversion V5

GC=clamp(X/Z,0.5,1.5), cu X,Z prezente și Z>0; GD analog AC/AE. GE=AVERAGE(Z,AE) dacă ambele sunt numerice. GF este DA dacă ambele rate FY și FZ sunt ≥S[113]=0.20; GG este DA dacă (FY≥0.20 și EY≥0.30) sau (FZ≥0.20 și EX≥0.30). Lipsa valorilor necesare produce NEDETERMINAT.

GH este DA dacă există numeric BJ:BN, GC:GE și simultan L_tech≥1.6, L_tech≤2.6, AVERAGE(GC:GD)≤0.90 și GE≥0.80. Toate limitele sunt inclusive. GI este DA dacă W și AB sunt fiecare ≥5 și cel puțin unul dintre GA/W și GB/AB este ≥0.20. Raporturile folosesc IFERROR(...,0), conform formulei.

```python
if COUNT(FY:GB) < 4: GJ = blank
elif GH != "DA": GJ = 0
else: GJ = 0.20*(GF=="DA") + 0.20*(GG=="DA") \
         + 0.45 + 0.15*(GI=="DA")
GK = blank if COUNT(GJ)==0 else 1 + 0.20*GJ
GL = FJ if GM!="DA" else min(0.65,max(0.002,FJ*GK))
```

Nucleul GH este obligatoriu pentru un GJ pozitiv. Trei avertizări GF/GG/GI nu declanșează penalizarea dacă GH este NU. În exemplul principal GF=DA, GG=DA și GI=DA, dar GH=NU și GJ=0. GM poate fi NU, iar GL poate totuși păstra FJ numeric; aceasta nu anulează hard fail-ul din HG.

### 3.7 Probabilitate raportată și indicatori auxiliari

GN=NEDETERMINAT dacă GM≠DA; altfel clasifică FI*GK prin 0.95 și 1.15. FM=DA dacă AR>1 și EC≥0.85. FN=DA dacă AU=1 și COUNT(CY:DB)=4; FN nu cere ca fiecare disponibilitate să fie 1, ci doar numerică.

GO=0.90 dacă GM≠DA sau GN=RIDICAT; GO=0.91 dacă GN=MEDIU; pentru GN=SCĂZUT, GO=0.94 dacă FM=FN=DA, altfel 0.92. GP=MIN(1-GL,GO), dacă GL nu este gol. GQ=1/GP pentru GP numeric pozitiv; GR=GP-EC dacă EC există; GS=GP*AR-1 dacă AR>1.

GP nu moștenește plafonul early-season al coloanei EA. Formula GO nu verifică direct sample-ul: cu GN=SCĂZUT și FM=FN=DA poate returna 0.94 și pentru un eșantion mic. Nu importa automat plafonul V2 în formula finală.

Diferența este esențială: pG0 brut este GL, probabilitatea brută Over este 1-GL, probabilitatea raportată este GP. 1-GP include efectul plafonului și nu trebuie etichetat automat drept „P0 recalibrat”. În DEMO-LIGA, GL=0.05643773654116299, deci 1-GL=0.943562263458837, dar GP=0.92.

### 3.8 Confidence nu este scorul care decide recomandarea

CB=MIN(1,COUNT(I:AN,AR:BG)/35). CC=0.25*MIN(1,I/10)+0.25*MIN(1,P/10)+0.15*MIN(1,W/5)+0.15*MIN(1,AB/5)+0.10*MIN(1,AG/5)+0.10*MIN(1,AN/100). CD=MAX(0,1-(MAX(BJ:BN,BP)-MIN(BJ:BN,BP))/(AVERAGE(BJ:BN,BP)*0.6)).

CE=clamp(100*wI*(0.30*CB+0.20*CC+0.20*CD+0.15*AT/5+0.15*AU)-100*0.08*BG,0,100). EG începe cu 0.03; adaugă 0.03 dacă MIN(I,P)<5; 0.03 dacă sunt promovate sau CJ neblank≤1; 0.02 dacă AG=0; 0.03*(1-MIN(1,COUNT(CM:CV)/10)); 0.03*(1-MIN(1,AN/250)) cu AN blank tratat 0; 0.02 dacă AR≤1.

EF=clamp(CE-200*MAX(0,EG-0.03)-10*(AU≠1)-4*(COUNT(CY:DB)<4),0,100). FT=clamp(EF-12*(FK≠DA)-6*(FL=MEDIU)-12*(FL=RIDICAT),0,100). GT=clamp(FT-12*(GM≠DA și FK=DA)-8*(GJ dacă numeric, altfel 0),0,100).

GT este un scor de calitate/încredere 0–100, nu probabilitate calibrată și nu interval statistic de încredere. EG este semilățime euristică, nu interval Wilson. Nu construi HK folosind GT≥75 sau GP≥92%; aceste condiții apar în selectori istorici.

### 3.9 Cele cinci componente de risc

```python
GY = "SOURCING INCOMPLETE – REVIEW REQUIRED" if GM!="DA" else (
     "SMALL SAMPLE + PRIOR / SHRINKAGE" if min(I,P,W,AB)<5 else
     "VERIFIED / PRIOR / SHRINKAGE")
GZ = clamp(100*(1-AVERAGE(1 if GM=="DA" else 0, min(1,AT/5))),0,100)
HA = blank if GM!="DA" else clamp(100*((FI*GK)-0.75)/(1.6-0.75),0,100)
HB = clamp(100*(abs(BR-1)/max(1-0.75,1.25-1)+min(1,BG/2))/2,0,100)
agreement_tech = max(0,1-(max(BJ:BN)-min(BJ:BN))/(AVERAGE(BJ:BN)*0.6))
HC = clamp(100*(1-AVERAGE(CC,agreement_tech)),0,100)
HD = clamp(100*max(0 if GJ==blank else GJ,min(1,BG/2)),0,100)
HE = blank if COUNT(GZ:HD)<5 else (
       GZ*(0.25/0.85)+HA*(0.30/0.85)+HB*(0.15/0.85)
      +HC*(0.10/0.85)+HD*(0.05/0.85))
```

Reproduce expresiile MAX/MIN efective, inclusiv lipsa unor limite inferioare interne. HC exclude BP, spre deosebire de CD. HA poate ajunge la 100 deoarece FI*GK poate depăși 1.6 chiar dacă FI singur este limitat la 1.6. HD ia MAX, nu suma celor două riscuri. HB penalizează valoarea absolută a deviației contextului, deci și un context foarte favorabil golurilor poate crește componenta Context Risk.

### 3.10 Selectorul final

```python
HF = blank if HE==blank else (1 if HE<=20 else 2 if HE<=40
                             else 3 if HE<=60 else 4 if HE<=80 else 5)
HG = "PASS" if GM=="DA" else "FAIL – DATE CRITICE ZERO-MASS INCOMPLETE"
HH = 5 if HG!="PASS" else HF
HI = "N/A" if HH==blank else {
     1:"DEFENSIV",2:"PRUDENT",3:"MODERAT",4:"RIDICAT"}.get(HH,"WATCH / NO BET")
HK = HI
```

Textul de justificare HJ afișează GY, cele cinci riscuri la o zecimală, HE la o zecimală, HF, HG și HH. Păstrează șirul literal din manifest dacă este cerută identitatea textului. În Dashboard!A21 se folosește TEXT(HE,"0.0") și se concatenează nivelul și clasa. Formatarea decimală poate depinde de locale-ul Excel; oracle-ul va fixa locale-ul contractual pentru comparația textelor.

### 3.11 Live și selectori istorici

EA raportează Over V2 prin DZ și capurile early/standard/confirmat B59:B61. EI poate returna WAIT XI – HIGH P sau WAIT DATE CHEIE – HIGH P și consultă EP. EL este verdictul tehnic V6; FU/FV sunt selectori V3, iar GU/GV selectori V5 istorici. Aceștia nu sunt aliasuri ale HK.

EU calculează intensitatea reziduală numai în modul DE="Live 20-30", dacă DF≥ES și DF<90. ES=B82=20, ET=B83=1.5. Formula EU este MAX(0.05,MIN(BS*ET,BS*(90-DF)/90+0.35*(DI+DJ)+0.06*(DK+DL)+0.15*(DM+DN)+0.1*(MAX(DO,DP)-MIN(DO,DP)))). Numele modului nu impune limita superioară 30: formula acceptă până sub 90.

EJ este 1 dacă DG+DH>0; altfel 1-MIN(0.95,MAX(0.001,EXP(-EU)*DX*DY/DW)). EL are mesaje separate pentru live. HK nu citește DE, EJ sau EL și rămâne clasificarea tehnică descrisă mai sus. Un gol deja marcat nu transformă automat HK în EVENIMENT ÎNDEPLINIT. Pentru prima implementare de produs, păstrează fluxul pre-match; nu introduce tacit o interfață live.

EN calculează Kelly fracționat și limita zilnică numai pentru anumite texte EL; EO multiplică EN cu DT. În EN apare textul LIVE – FEZABIL, în timp ce EL returnează LIVE – FEZABIL TEHNIC. Este o neconcordanță istorică de șiruri și nu se repară într-o portare fidelă. EE și EK sunt intenționat goale; FS și GS încă raportează EV.

### 3.12 Backtest și rapoarte

Backtest!J = cotă plasată-1 pentru rezultat 1, altfel -1, cu guard pe A,I,G. K=(E-I)^2. L=-(I*LN(MAX(0.001,E))+(1-I)*LN(MAX(0.001,1-E))). M=G/H-1. Rezumatele folosesc COUNT, AVERAGE, SUM/COUNT și grupe COUNTIFS/AVERAGEIFS. Q11:Q19 numără intervalele de probabilitate cu limita inferioară inclusă și cea superioară exclusă, plus rezultat prezent. T=rată observată-minus-probabilitate medie.

Settlement!R=(I-J)^2, S este log-loss cu probabilități limitate la [0.000001,0.999999]. Aceste limite diferă de Backtest; nu crea un singur helper cu limite implicite comune. Coloanele de rezultat sunt inputuri manuale; nu există colectare automată a scorului final în această foaie.

Risk_Level_Summary numără Settlement!T, însumează J și R. Calibration folosește intervalele A/B și Settlement!I/J; gap-ul este probabilitate medie-minus-rată observată, sens opus față de Backtest!T. Statusul este LOW N pentru N<10, apoi OK la ABS(gap)≤0.03, WATCH la ≤0.06, altfel DRIFT. League_Summary are STABLE la ABS(gap)≤0.05 dacă N≥10. Monthly_Summary folosește [data_start, EDATE(data_start,1)).

Backtest_Summary raportează N, wins, hit rate, Wilson 95% cu z=1.96, probabilitate medie, gap, Brier și log-loss. Wilson folosește formula literală din anexa B. Nu există observații post-match populate care să valideze performanța modelului; cele 5 DEMO nu sunt un backtest OOS.

Rapoartele istorice au nealinieri de numitor: Calibration!C cere rezultat prezent, dar SUMIFS din D nu repetă această condiție; League/Monthly/Risk_Level pot număra rânduri fără rezultat. Nu folosi aceste rezumate ca dovadă de performanță fără verificarea completitudinii datasetului. Pentru paritate exactă se păstrează formulele, iar remedierea necesită versiune separată.

## 4 Criterii de validare și neconcordanțe de implementare

### 4.1 Criteriul efectiv pentru DEFENSIV

Cu A neblank și calcule valide, DEFENSIV înseamnă GM=DA și HE≤20. Nu există condiție suplimentară GP≥92%, GT≥75%, lineup confirmat, două confirmări independente, EV pozitiv sau low-conversion egal cu zero. Nu impune un asemenea filtru în motorul de compatibilitate.

Limitele exacte sunt [0,20] pentru nivelul 1; (20,40] pentru 2; (40,60] pentru 3; (60,80] pentru 4; peste 80 pentru 5. HE=20.1 aparține nivelului 2 chiar dacă un text descriptiv spune „21–40”. Orice G0 FAIL forțează nivelul 5. SMALL SAMPLE influențează CC/HC și alte metrici, dar nu aplică un floor PRUDENT.

Clasa zero-mass și clasa de risc sunt două variabile diferite. GN=RIDICAT nu forțează singur HK=WATCH; DEMO-AMICAL are GN=RIDICAT, HE≈51.719 și HK=MODERAT. Clasa GN controlează capul și contribuie prin FI*GK la HA; clasificarea finală depinde de totalul ponderat.

### 4.2 Cote și lineup

Constatare strictă: HE și HK nu depind de cotele AR/AS, AU sau CY:DB pentru inputuri valide. GH și HC au fost construite fără BP. Dar GL depinde de cote prin BO→BP→BQ→BS→BT→DZ și de disponibilități prin DY→DZ. GT depinde de cote și lineup prin CE/EG/EF și de profilul zero-mass.

Prin urmare, afirmația din documentație „lineup/piață pot afecta numai P_cap” este prea largă. Este corect că nu decid recomandarea finală, dar nu este corect că afectează exclusiv plafonul: unele afectează și probabilitatea brută sau Confidence. Eliminarea influenței din GL pentru a respecta acea propoziție ar încălca identitatea cu Excel.

### 4.3 Confirmări și documentație istorică

Regula a două surse independente este prezentă în ZeroMass_Gate_v4 și ZeroMass_WF_v4, dar aceste foi nu alimentează GO, GP sau HK. GO folosește FM și FN. Nu introduce un prag de două surse în GO fără versiune nouă. Aplicația rămâne cu FootyStats ca sursă unică; simpla prezență a altor URL-uri în workbook nu schimbă scope-ul.

DOCUMENTATIE_MODEL conține atât texte actuale, cât și descrieri vechi: GV este încă descris într-un pasaj ca verdict oficial v5; matricea are și banda 93–94%, în timp ce GO are exact 90/91/92/94%. Anexa de formule și adresele reale prevalează pentru paritate. Cadrul v5 și Matricea v4 oferă reguli metodologice, dar nu adaugă automat formule lipsă în workbook.

### 4.4 Nu confunda date complete cu audit complet

GY sintetizează GM și sample-ul. Nu citește o bază de stări per input și nu verifică URL-uri, timestamp-uri, independența surselor sau SOURCE CONFLICT. O valoare numerică prezentă poate trece COUNT chiar dacă nu este verificată. Aplicația păstrează separat auditul provenienței, refresh-ul PENDING OFFICIAL și conflictele, fără să rescrie GY ca și când Excel ar implementa deja toate aceste stări.

Un G0 PASS nu garantează calcul fără erori: textul NOT CHECKED într-un factor numeric poate strica BR/HE, iar GM poate rămâne DA. O eroare de calcul nu trebuie transformată automat într-un rezultat sănătos sau într-un Risk Score zero. Raportează eroarea tehnică separat de verdictul modelului.

## 5 Validare simulări și teste de acceptanță

### 5.1 Trei niveluri de dovadă

Nivelul 1 este extracția formulelor și a cache-ului existent. Nivelul 2 este evaluarea independentă în Python și comparația cu acel cache. Nivelul 3 este recalcularea actuală în Microsoft Excel și comparația motorului aplicației cu rezultatul salvat după CalculateFullRebuild. Primele două au fost efectuate aici; nivelul 3 rămâne testul obligatoriu de acceptanță în mediul Windows al dezvoltatorului.

S-au verificat toate cele 108 formule/rând pentru fiecare dintre cele 5 DEMO, inclusiv selectori istorici și texte, rezultând 540/540 comparații reușite. Textele au fost comparate exact cu cache-ul, cu tratarea rezultatului ="" ca gol atunci când cache-ul este absent. Valorile numerice au fost comparate prin isclose(rel_tol=1e-12, abs_tol=1e-12). Acest test nu certifică toate cele 14.026 de formule din toate foile și nu înlocuiește Excel.

### 5.2 Exemplul de referință din rândul 4

DEMO-LIGA-001, Gazde Demo A versus Oaspeți Demo B, Liga demonstrativă, Campionat intern, data 2026-09-01. Acesta este un exemplu DEMO din workbook, nu un meci real verificat. Setul complet al inputurilor, inclusiv toate blank-urile, este în golden_fixtures.json; anexa A prezintă schema și valorile rândului 4.

Valori principale: I=P=10; J=1.8, K=1, L=1.7, M=1.05, N=0.9, O=0.1; Q=1.2, R=1.6, S=1.25, T=1.55, U=0.9, V=0.2. W=AB=5; X=1.6, Y=1, Z=1.55, AA=1.1; AC=1.2, AD=1.6, AE=1.3, AF=1.45. AG=4, AH=2.25, AI=1; AJ=1.45, AK=1.15, AL=2.6, AM=0.08, AN=120.

Cotele sunt AO=1.72, AP=3.85, AQ=4.8, AR=1.12, AS=7.2. AT=4, AU=0. AV=1, AW=1, AY=1, BF=1; ceilalți factori AX,AZ:BE,BG sunt 0. CJ=7, CK=CL=0. CM=5.2,CN=4.4,CO=2,CP=1.6,CQ=0.12,CR=0.11,CS=27,CT=23,CU=0.28,CV=0.22,CW=CX=0; CY:CZ și DA:DB sunt 1.

EV=0.05, EW=0.08, EX=0.35, EY=0.25, EZ=0.30, FA=0.35; FY=FZ=0.20, GA=GB=1. FB este blank. DC=1.13; DD blank; DE=Pre-match; DF:DN blank; DO=DP=0; DQ blank; DR=1,DS=0,DT=1000,DU=0.02,DV=0.25. BH/BI sunt textele și URL-urile demo păstrate integral în fixture.

Rezultatul de afișat este P Over 0.5=92%, Confidence≈59.194772288905426, Risk Score≈7.870120560697213, G0=PASS, nivel 1, DEFENSIV. „≈” se referă la afișarea zecimală a unui double; valorile cache integrale sunt în tabelul de rezultate și în JSON. CG=RECOMANDAT CU PRUDENȚĂ și EL/GV=WATCH / NO BET sunt ieșiri istorice, nu recomandarea oficială curentă.

### 5.3 Simulări de comportament

Toate simulările modifică o copie în memorie a rândului 4. Fișierul original nu este modificat. Rezultatele sunt produse de evaluatorul independent; native_excel_verified=false este păstrat în fiecare caz.

Lipsa EV sau L produce G0 FAIL și WATCH / NO BET. Lipsa FY poate păstra GL numeric și GP=0.90, însă HG este FAIL și HH=5. Lipsa N/U nu produce automat G0 FAIL în acest workbook. Reducerea I/P la 4 și W/AB la 3 păstrează în simulare DEFENSIV, demonstrând că SMALL SAMPLE nu impune singur PRUDENT.

Schimbarea cotelor AR/AS modifică GL și GT, dar nu HE/HK. AU=1 ridică GO și GP de la 0.92 la 0.94 în demo și crește GT, fără schimbarea HE/HK. CY=0 crește GL, fără schimbarea riscului final. Modificarea FB nu schimbă ieșirile active.

În scenariul sintetic low-conversion, GJ=1 și GK=1.2, dar HE rămâne sub 20; rezultatul este DEFENSIV chiar cu GP sub 90%. Acesta este comportamentul formulelor, nu o recomandare nouă de produs. Setul exact al modificărilor și toate rezultatele sunt în simulations.json.

### 5.4 Teste obligatorii pentru motorul din aplicație

Teste de referință: fiecare DEMO verificat celulă cu celulă pentru cele 108 rezultate; configurație și SHA256 fixate; verdicturi/gate-uri comparate exact. Teste la limite: HE=20/40/60/80 și valori imediat sub/peste, FI*GK=0.95/1.15, FY/FZ=0.20, CS=0.30, L_tech=1.6/2.6, finishing=0.90, GE=0.80 și rate 0–0=0.20. Injecția HE în testul unitar al selectorului nu este permisă ca modificare a formulei în fișierul original.

Teste de lipsă: null, blank, ="", text, zero numeric, număr stocat ca text; xG zero și lipsă; context blank versus NOT CHECKED; un singur element disponibil la AVERAGE; regresie pentru formula FQ/GQ cu probabilitate blank. Teste de dependență: FB, cote 1X2 AO:AQ, lineup și cote Over/Under; demonstrarea diferenței dintre influența asupra GP/GT și HE/HK. Teste de rutare: Dashboard trebuie să citească HK, nu GV; ID duplicat trebuie raportat operațional deoarece MATCH alege prima apariție.

Teste de protecție: 0 formule modificate, 0 praguri mutate, 0 foi șterse/redenumite, 0 scrieri off-whitelist. Orice abatere oprește exportul cu „EXPORT BLOCAT. Motiv: …”. Nu corecta pragurile ca să treacă testele. Originalele din modele_analize rămân nemodificate.

### 5.5 Oracle Microsoft Excel în Windows

Creează copii temporare ale sursei; scrie exclusiv inputurile fixture-ului, păstrând toate formulele. Deschide fiecare copie în Microsoft Excel instalat local, cu macro-urile dezactivate, update al linkurilor externe dezactivat și calcul automat. Execută CalculateFullRebuild, așteaptă CalculationState=xlDone, verifică erori, salvează și închide. Citește valorile native prin Value2 sau cache-ul fișierului salvat. Nu folosi openpyxl ca motor de recalcul și nu folosi LibreOffice ca oracle al identității Microsoft Excel.

În raportul testului păstrează versiunea Excel, locale-ul, SHA256 al sursei, inputurile, setările și fiecare diferență pe celulă. Un test fără Excel poate fi SKIPPED explicit în CI, dar nu trebuie raportat ca PASS pentru paritate certificată. Runtime-ul aplicației poate rămâne Python; Microsoft Excel este oracle-ul de acceptanță, nu presupune automat instalarea Excel pe server.

Comenzile propuse în Cursor sunt contract de implementat, nu fișiere pretins existente:

```text
python -m pytest tests/test_over05_excel_parity.py -q
python -m pytest tests/test_over05_excel_oracle.py -q
pytest -q
streamlit run app.py
```

Primul test trebuie să treacă fără cheie API, pe fixture-uri locale. Al doilea trebuie să treacă în Windows cu Excel și să declare explicit indisponibilitatea lui în alte medii. Comanda standard pytest -q trebuie să păstreze trecerea testelor MVP fără cheie. Interfața se verifică la http://localhost:8501, cu meciul DEMO și câmpurile GP/GT/HE/HG/HH/HK afișate conform contractului.

### 5.6 Mesaj gata de Cursor

```text
Implementează în Pontifybet un motor Python de compatibilitate pentru Over 0.5,
reproducând fișierul 1_model_analiza_over0.5_optimizat_V4.xlsx și manualul atașat.
Obiectivul este paritatea algoritmului V4, cu selectorul final v9 din GY:HK.

Lucrează în C:\_Software\SAAS\Pontifybet. Începe prin verificarea structurii reale
a repo-ului, a AGENTS.md și a adaptorului existent src/adapters/over05.py.
Verifică src/pipeline.py, src/excel/generator.py, src/excel/integrity.py și registry-ul
înainte de a alege integrarea. Nu presupune că fișierele noi propuse există deja.

Tratează cererea ca autorizare pentru motorul Over 0.5 în cod. Păstrează Streamlit,
Python 3.12, FootyStats ca unică sursă, modelele și fluxul de export existente.
Nu migra alte modele. Nu introduce React, FastAPI, DB, recalcul LibreOffice sau
surse suplimentare. Verifică efectiv câmpurile API; nu inventa mapping-uri.

Folosește SHA256-ul sursei din manual, formula_manifest.json, schema și fixture-urile.
Portează dependențele reale până la GP/GT și GY:HK. Output-ul oficial este HK=HI,
prin HE/HF/HG/HH; nu folosi CG/EL/FV/GV. Păstrează separate probabilitatea brută
1-GL, probabilitatea raportată GP, Confidence GT și Risk Score HE.

Nu adăuga prag GP>=92%, GT>=75%, confirmare lineup, două surse sau EV pozitiv la
selectorul HK. Păstrează influențele actuale ale cotelor/disponibilităților asupra
probabilității și Confidence, fără a le introduce în riscul final. FB este neutilizat.
Păstrează blank, șir gol, zero, eroare și Data Status ca stări distincte.
-1/-2/null din API devin NOT AVAILABLE în audit, niciodată 0 în inputuri.

Înlocuiește whitelist-ul insuficient numai după verificare, cu maparea explicită
a inputurilor A:BI, CJ:DV, EV:FA, FY:GB; FB nu se scrie. Nu scrie în formule.
0 formule schimbate, 0 praguri mutate, 0 foi șterse/redenumite, 0 scrieri off-whitelist.
La abatere: EXPORT BLOCAT. Motiv: ... . Nu schimba praguri ca să treacă testele.

Creează tests/test_over05_excel_parity.py și tests/test_over05_excel_oracle.py.
Verificare: python -m pytest tests/test_over05_excel_parity.py -q — PASS pentru
cele 5 DEMO și cazurile-limită. Adaugă oracle Microsoft Excel pe copii temporare:
python -m pytest tests/test_over05_excel_oracle.py -q — PASS în Windows cu Excel.
Fără Excel marchează oracle-ul SKIPPED, fără a declara paritate certificată.
Compară numeric cu abs/rel 1e-12; clasele/gate-urile exact. Nu rotunji înainte de praguri.
Rulează pytest -q — PASS fără cheie; streamlit run app.py — interfață funcțională.

La final livrează fișierele modificate, rezultatele testelor, diferențele față de
oracle pe celule și limitările rămase. Nu declara identitate certificată numai
din comparația cu cache-ul sau din existența evaluatorului de audit din pachet.
```

## Anexa A Dicționarul complet de foi și câmpuri

Dimensiunile sunt limitele foii, inclusiv zone formatate. Un câmp gol fără formulă este o poziție de input/audit, nu dovada unui input API. Formatele și tipurile efective ale fiecărei celule sunt păstrate în inventarul JSON.

| Foaie | Dimensiune | Formule | Rol |
| --- | --- | --- | --- |
| Dashboard | A1:Q40 | 43 | Afișare a meciului selectat prin B4. Output oficial GP/GT și HE:HK; nu este motorul statistic. |
| Analize meciuri | A1:HK103 | 10800 | Tabelul principal de inputuri și calcul per meci. 100 rânduri; 108 formule/rând. |
| Setari model | A1:J136 | 7 | Configurație numerică activă și parametri istorici. Regimuri B:I; constante B15:B126. |
| Surse cercetare | A1:H73 | 0 | Registru documentar cu 70 surse. Nu colectează date și nu validează automat inputurile. |
| Backtest | A1:Z203 | 2261 | Predicții curente preluate prin ID, rezultate manuale și metrici. Verdictul N citește GV istoric. |
| Risk_Classification | A1:H47 | 21 | Ponderi active și afișaj pentru meciul selectat. E28:E32 alimentează HE. |
| ZeroMass_Gate_v4 | A1:F22 | 4 | Exemplu/gate local cu valori manuale și două confirmări. Nu alimentează HK sau GP. |
| Frozen_Predictions | A1:AZ203 | 0 | Registru manual de snapshoturi pre-match. Fără formule și fără transfer automat către Settlement. |
| Settlement | A1:W203 | 400 | Foaie declarată deprecated pentru analiza pre-match. Brier și log-loss active pentru audit. |
| Risk_Level_Summary | A1:F8 | 25 | Agregări istorice după Settlement!T, nivelurile 1–5. |
| Calibration | A1:G11 | 40 | Benzi de probabilitate și decalaj de calibrare din Settlement. |
| Fail_Distribution | A1:E10 | 14 | Numără eșecurile după codul Settlement!O. |
| League_Summary | A1:H33 | 210 | Agregări pe ligile introduse manual în A4:A33. |
| Monthly_Summary | A1:G27 | 144 | Agregări pe lunile introduse manual în A4:A27. |
| Builder_Marginal_Fails | A1:L4 | 0 | Interfață documentară de audit Builder, fără motor de calcul în această foaie. |
| Backtest_Summary | A1:H15 | 11 | Rezumat post-match, Wilson, Brier, log-loss și stabilitate pe ligi. |
| ZeroMass_WF_v4 | A1:F15 | 2 | Fișă locală walk-forward cu inputuri manuale și cap local. Nu alimentează GP/HK. |
| ZeroMass_Gate_v5 | A1:F23 | 44 | Afișaj de audit al meciului Dashboard. B22/B23 citesc GU/GV istorice. |
| CHANGELOG_VERSIUNI | A1:H64 | 0 | Texte consolidate despre versiunile precedente; nu conține formule. |
| DOCUMENTATIE_MODEL | A1:I464 | 0 | Metodologie, legendă, readiness și matrice de decizie consolidate; nu conține formule. |


### A1 Analize meciuri schema integrală A până la HK

Sursa F înseamnă formulă, I input și R câmp retras. Dependențele exacte sunt în anexa B și manifest. Exemplul este rândul 4, păstrat în JSON fără rotunjire.

#### Identificare și inputuri inițiale

| Col. | Antet exact | Tip semantic | Sursă | Exemplu rând 4 |
| --- | --- | --- | --- | --- |
| A | Match ID | Text | I | DEMO-LIGA-001 |
| B | Tip înregistrare | Text | I | DEMO – înlocuiește |
| C | Data | Dată | I | 2026-09-01 00:00:00 |
| D | Competiție | Text | I | Liga demonstrativă |
| E | Tip competiție | Text | I | Campionat intern |
| F | Etapă/context | Text | I | Etapa 7 |
| G | Gazde | Text | I | Gazde Demo A |
| H | Oaspeți | Text | I | Oaspeți Demo B |
| I | N gazde acasă | Număr întreg | I | 10 |
| J | GF gazde acasă | Float | I | 1.8 |
| K | GA gazde acasă | Float | I | 1 |
| L | xGF gazde acasă | Float | I | 1.7 |
| M | xGA gazde acasă | Float | I | 1.05 |
| N | O0.5 gazde acasă | Procentaj [fracție] | I | 0.9 |
| O | FTS gazde acasă | Procentaj [fracție] | I | 0.1 |
| P | N oaspeți deplasare | Număr întreg | I | 10 |
| Q | GF oaspeți deplasare | Float | I | 1.2 |
| R | GA oaspeți deplasare | Float | I | 1.6 |
| S | xGF oaspeți deplasare | Float | I | 1.25 |
| T | xGA oaspeți deplasare | Float | I | 1.55 |
| U | O0.5 oaspeți deplasare | Procentaj [fracție] | I | 0.9 |
| V | FTS oaspeți deplasare | Procentaj [fracție] | I | 0.2 |
| W | N recent gazde | Număr întreg | I | 5 |
| X | GF recent gazde | Float | I | 1.6 |
| Y | GA recent gazde | Float | I | 1 |
| Z | xGF recent gazde | Float | I | 1.55 |
| AA | xGA recent gazde | Float | I | 1.1 |
| AB | N recent oaspeți | Număr întreg | I | 5 |
| AC | GF recent oaspeți | Float | I | 1.2 |
| AD | GA recent oaspeți | Float | I | 1.6 |
| AE | xGF recent oaspeți | Float | I | 1.3 |
| AF | xGA recent oaspeți | Float | I | 1.45 |
| AG | N H2H | Număr întreg | I | 4 |
| AH | Goluri medii H2H | Float | I | 2.25 |
| AI | O0.5 H2H | Procentaj [fracție] | I | 1 |
| AJ | Medie goluri gazde comp. | Float | I | 1.45 |
| AK | Medie goluri oaspeți comp. | Float | I | 1.15 |
| AL | Medie total goluri comp. | Float | I | 2.6 |
| AM | Rată 0-0 competiție | Procentaj [fracție] | I | 0.08 |
| AN | N meciuri competiție | Număr întreg | I | 120 |
| AO | Cotă 1 | Float | I | 1.72 |
| AP | Cotă X | Float | I | 3.85 |
| AQ | Cotă 2 | Float | I | 4.8 |
| AR | Cotă Over 0.5 | Float | I | 1.12 |
| AS | Cotă Under 0.5 | Float | I | 7.2 |
| AT | Calitate surse (1-5) | Număr întreg | I | 4 |
| AU | Echipe start confirmate (0/1) | Număr întreg | I | 0 |
| AV | Motivație (-2..2) | Număr întreg | I | 1 |
| AW | Deschidere tactică (-2..2) | Număr întreg | I | 1 |
| AX | Atac/absențe (-2..2) | Număr întreg | I | 0 |
| AY | Apărare/absențe (-2..2) | Număr întreg | I | 1 |
| AZ | Rotație (-2..2) | Număr întreg | I | 0 |
| BA | Oboseală (-2..2) | Număr întreg | I | 0 |
| BB | Meteo (-2..2) | Număr întreg | I | 0 |
| BC | Teren (-2..2) | Număr întreg | I | 0 |
| BD | Arbitru/penalty (-2..2) | Număr întreg | I | 0 |
| BE | Context tur/retur (-2..2) | Număr întreg | I | 0 |
| BF | Dezechilibru valoric (-2..2) | Număr întreg | I | 1 |
| BG | Contradicții date (0-2) | Număr întreg | I | 0 |
| BH | Raționament analist | Text | I | Exemplu pentru campionat; confirmați loturile și cotele înainte de utilizare. |
| BI | Surse meci (URL-uri) | Text | I | https://footystats.org/ ; https://understat.com/ |


#### Calcule inițiale

| Col. | Antet exact | Tip semantic | Sursă | Exemplu rând 4 |
| --- | --- | --- | --- | --- |
| BJ | λ sezon goluri | Float sau gol/eroare | F | 2.7087635820327414 |
| BK | λ sezon xG | Float sau gol/eroare | F | 2.695318373689451 |
| BL | λ recent goluri | Float sau gol/eroare | F | 2.6489578808281795 |
| BM | λ recent xG | Float sau gol/eroare | F | 2.6487763675966214 |
| BN | λ H2H | Float sau gol/eroare | F | 2.4444444444444446 |
| BO | Prob. piață O0.5 | Procentaj [fracție] sau gol/eroare | F | 0.8653846153846154 |
| BP | λ piață | Float sau gol/eroare | F | 2.0053335695261145 |
| BQ | λ bază | Float sau gol/eroare | F | 2.568702883845408 |
| BR | Multiplicator context | Float sau gol/eroare | F | 1.07 |
| BS | λ ajustat | Float sau gol/eroare | F | 2.748512085714587 |
| BT | P(0-0) Poisson | Procentaj [fracție] sau gol/eroare | F | 0.06402305118433504 |
| BU | Factor zero ligă | Float sau gol/eroare | F | 1.0385495214000677 |
| BV | P0 calibrat | Procentaj [fracție] sau gol/eroare | F | 0.07486833187454739 |
| BW | P Over 0.5 | Procentaj [fracție] sau gol/eroare | F | 0.9251316681254527 |
| BX | Cotă fair | Float sau gol/eroare | F | 1.0809272176643236 |
| BY | Prob. piață | Procentaj [fracție] sau gol/eroare | F | 0.8653846153846154 |
| BZ | Edge | Procentaj [fracție] sau gol/eroare | F | 0.05974705274083725 |
| CA | EV | Procentaj [fracție] sau gol/eroare | F | 0.03614746830050719 |
| CB | Completitudine | Procentaj [fracție] sau gol/eroare | F | 1 |
| CC | Scor eșantion | Procentaj [fracție] sau gol/eroare | F | 0.9800000000000001 |
| CD | Acord componente | Procentaj [fracție] sau gol/eroare | F | 0.5357386144452715 |
| CE | Confidence Score | Float sau gol/eroare | F | 72.31477228890543 |
| CF | Steag risc | Text sau gol | F | MEDIU |
| CG | Verdict | Text sau gol | F | RECOMANDAT CU PRUDENȚĂ |
| CH | Raționament automat | Text sau gol | F | P(O0,5)=92.5%; λ ajustat=2.75; Confidence=72/100; Edge=6.0%; risc=MEDIU. Exemplu p… |
| CI | Surse consolidate | Text sau gol | F | https://footystats.org/ ; https://understat.com/ |


#### Inputuri V2

| Col. | Antet exact | Tip semantic | Sursă | Exemplu rând 4 |
| --- | --- | --- | --- | --- |
| CJ | Etapa numerică | Număr întreg | I | 7 |
| CK | Gazde promovate (0/1) | Număr întreg | I | 0 |
| CL | Oaspeți promovate (0/1) | Număr întreg | I | 0 |
| CM | SOT gazde/meci | Float | I | 5.2 |
| CN | SOT oaspeți/meci | Float | I | 4.4 |
| CO | Big chances gazde/meci | Float | I | 2 |
| CP | Big chances oaspeți/meci | Float | I | 1.6 |
| CQ | xG/șut gazde | Float | I | 0.12 |
| CR | xG/șut oaspeți | Float | I | 0.11 |
| CS | Touches box gazde/meci | Float | I | 27 |
| CT | Touches box oaspeți/meci | Float | I | 23 |
| CU | Set-piece xG gazde/meci | Float | I | 0.28 |
| CV | Set-piece xG oaspeți/meci | Float | I | 0.22 |
| CW | Cross-heavy gazde (0-2) | Număr întreg | I | 0 |
| CX | Cross-heavy oaspeți (0-2) | Număr întreg | I | 0 |
| CY | Atacant-cheie gazde disponibil | Număr întreg | I | 1 |
| CZ | Atacant-cheie oaspeți disponibil | Număr întreg | I | 1 |
| DA | Portar-cheie gazde disponibil | Număr întreg | I | 1 |
| DB | Portar-cheie oaspeți disponibil | Număr întreg | I | 1 |
| DC | Cotă O0.5 opening | Float | I | 1.13 |
| DD | Cotă O0.5 closing | Float | I | blank |
| DE | Mod analiză | Text | I | Pre-match |
| DF | Minut live | Număr întreg | I | blank |
| DG | Scor gazde live | Număr întreg | I | blank |
| DH | Scor oaspeți live | Număr întreg | I | blank |
| DI | xG gazde live | Float | I | blank |
| DJ | xG oaspeți live | Float | I | blank |
| DK | SOT gazde live | Număr întreg | I | blank |
| DL | SOT oaspeți live | Număr întreg | I | blank |
| DM | Big chances gazde live | Număr întreg | I | blank |
| DN | Big chances oaspeți live | Număr întreg | I | blank |
| DO | Roșu gazde | Număr întreg | I | 0 |
| DP | Roșu oaspeți | Număr întreg | I | 0 |
| DQ | Cotă O0.5 live | Float | I | blank |
| DR | Nr. selecții bilet | Număr întreg | I | 1 |
| DS | Corelație portofoliu | Procentaj [fracție] | I | 0 |
| DT | Bankroll | Float | I | 1000 |
| DU | Limită miză zilnică | Procentaj [fracție] | I | 0.02 |
| DV | Fracție Kelly | Procentaj [fracție] | I | 0.25 |


#### Calcule V2

| Col. | Antet exact | Tip semantic | Sursă | Exemplu rând 4 |
| --- | --- | --- | --- | --- |
| DW | Factor calitate ofensivă | Float sau gol/eroare | F | 1.0357878787878787 |
| DX | Factor regim | Float sau gol/eroare | F | 1 |
| DY | Factor lineup P0 | Float sau gol/eroare | F | 1 |
| DZ | P0 ZIP/regim v2 | Procentaj [fracție] sau gol/eroare | F | 0.0721123897129207 |
| EA | P Over0.5 v2 | Procentaj [fracție] sau gol/eroare | F | 0.9278876102870793 |
| EB | Cotă fair v2 | Float sau gol/eroare | F | 1.0777167287432685 |
| EC | Prob. piață reală v2 | Procentaj [fracție] sau gol/eroare | F | 0.8653846153846154 |
| ED | Edge v2 | Procentaj [fracție] sau gol/eroare | F | 0.06250299490246392 |
| EE | EV – IGNORAT v6 | Text gol | F | blank |
| EF | Confidence v2 | Float sau gol/eroare | F | 59.194772288905426 |
| EG | Incertitudine ± | Procentaj [fracție] sau gol/eroare | F | 0.0456 |
| EH | Cap probabilitate | Text sau gol | F | 93% – standard |
| EI | Gate selecție tehnic v6 | Text sau gol | F | WAIT XI – HIGH P |
| EJ | P Over0.5 live | Procentaj [fracție] sau gol/eroare | F | blank |
| EK | EV live – IGNORAT v6 | Text gol | F | blank |
| EL | Verdict tehnic v6 | Text sau gol | F | WATCH / NO BET |
| EM | Motiv verdict v6 | Text sau gol | F | WAIT XI – HIGH P |
| EN | Miză recomandată % bankroll | Procentaj [fracție] sau gol/eroare | F | 0 |
| EO | Miză recomandată lei | Float sau gol/eroare | F | blank |
| EP | Control portofoliu | Text sau gol | F | DA |
| EQ | CLV | Procentaj [fracție] sau gol/eroare | F | blank |
| ER | Raționament v2 | Text sau gol | F | P v2=92.8% ±4.6%; P0 ZIP=7.2%; Confidence=59/100; piață reală=DA; EV=n/a; gate=WAI… |
| ES | Minut minim live activ | Număr întreg sau gol/eroare | F | 20 |
| ET | Cap intensitate live activ | Float sau gol/eroare | F | 1.5 |
| EU | λ rezidual live v2 | Float sau gol/eroare | F | blank |


#### Zero mass V3

| Col. | Antet exact | Tip semantic | Sursă | Exemplu rând 4 |
| --- | --- | --- | --- | --- |
| EV | Rată 0-0 gazde acasă | Procentaj [fracție] | I | 0.05 |
| EW | Rată 0-0 oaspeți deplasare | Procentaj [fracție] | I | 0.08 |
| EX | Clean sheet gazde acasă | Procentaj [fracție] | I | 0.35 |
| EY | Clean sheet oaspeți deplasare | Procentaj [fracție] | I | 0.25 |
| EZ | Rată 0-0 HT gazde acasă | Procentaj [fracție] | I | 0.3 |
| FA | Rată 0-0 HT oaspeți deplasare | Procentaj [fracție] | I | 0.35 |
| FB | Neutilizat | Neutilizat; blank | R | blank |
| FC | Finishing vs xG gazde | Float sau gol/eroare | F | 1.0588235294117647 |
| FD | Finishing vs xG oaspeți | Float sau gol/eroare | F | 0.96 |
| FE | Risc 0-0 team-specific | Float sau gol/eroare | F | 0.6324555320336758 |
| FF | Risc blank×clean-sheet reciproc | Float sau gol/eroare | F | 0.845378028229756 |
| FG | Risc finishing | Float sau gol/eroare | F | 0 |
| FH | Risc statistic 0–0 HT | Float sau gol/eroare | F | 0.6964285714285714 |
| FI | Factor zero-mass v3 | Float sau gol/eroare | F | 0.7826357823647438 |
| FJ | P0 recalibrat v3 | Procentaj [fracție] sau gol/eroare | F | 0.05643773654116299 |
| FK | Zero-risk complet | Text sau gol | F | DA |
| FL | Clasă zero-risk | Text sau gol | F | SCĂZUT |
| FM | Piață confirmă zero-risk (doar P_cap) | Text sau gol | F | DA |
| FN | Lineup confirmă zero-risk (doar P_cap) | Text sau gol | F | NU |
| FO | Cap probabilitate v3 | Procentaj [fracție] sau gol/eroare | F | 0.92 |
| FP | P Over0.5 v3 | Procentaj [fracție] sau gol/eroare | F | 0.92 |
| FQ | Cotă fair v3 | Float sau gol/eroare | F | 1.0869565217391304 |
| FR | Edge v3 | Procentaj [fracție] sau gol/eroare | F | 0.05461538461538462 |
| FS | EV v3 | Procentaj [fracție] sau gol/eroare | F | 0.030400000000000205 |
| FT | Confidence v3 | Float sau gol/eroare | F | 59.194772288905426 |
| FU | Gate selecție v3 | Text sau gol | F | NU – LINEUP NECONFIRMAT |
| FV | Verdict v3 | Text sau gol | F | WATCH / NO BET |
| FW | Motiv verdict v3 | Text sau gol | F | NU – LINEUP NECONFIRMAT |
| FX | Raționament v3 | Text sau gol | F | P v3=92.0%; P0 v3=5.6%; factor zero=0.78x (SCĂZUT); cap=92.0%; Confidence=59/100; … |


#### Low conversion V5

| Col. | Antet exact | Tip semantic | Sursă | Exemplu rând 4 |
| --- | --- | --- | --- | --- |
| FY | Blank recent gazde | Procentaj [fracție] | I | 0.2 |
| FZ | Blank recent oaspeți | Procentaj [fracție] | I | 0.2 |
| GA | Nr. 0-0 recente gazde | Număr întreg | I | 1 |
| GB | Nr. 0-0 recente oaspeți | Număr întreg | I | 1 |
| GC | Finishing recent gazde | Float sau gol/eroare | F | 1.032258064516129 |
| GD | Finishing recent oaspeți | Float sau gol/eroare | F | 0.923076923076923 |
| GE | Indice chance creation recent | Float sau gol/eroare | F | 1.425 |
| GF | Ambele echipe blank recent | Text sau gol | F | DA |
| GG | Clean-sheet advers relevant | Text sau gol | F | DA |
| GH | λ moderat + finishing slab | Text sau gol | F | NU |
| GI | Acumulare 0-0 recentă | Text sau gol | F | DA |
| GJ | Scor low-conversion v5 | Procentaj [fracție] sau gol/eroare | F | 0 |
| GK | Multiplicator P0 low-conversion | Float sau gol/eroare | F | 1 |
| GL | P0 recalibrat v5 | Procentaj [fracție] sau gol/eroare | F | 0.05643773654116299 |
| GM | Date critice zero-mass complete | Text sau gol | F | DA |
| GN | Clasă zero-mass | Text sau gol | F | SCĂZUT |
| GO | Plafon probabilitate raportată | Procentaj [fracție] sau gol/eroare | F | 0.92 |
| GP | P Over0.5 v5 | Procentaj [fracție] sau gol/eroare | F | 0.92 |
| GQ | Cotă fair v5 | Float sau gol/eroare | F | 1.0869565217391304 |
| GR | Edge v5 | Procentaj [fracție] sau gol/eroare | F | 0.05461538461538462 |
| GS | EV v5 | Procentaj [fracție] sau gol/eroare | F | 0.030400000000000205 |
| GT | Confidence v5 | Float sau gol/eroare | F | 59.194772288905426 |
| GU | Gate selecție v5 (istoric) | Text sau gol | F | NU – LINEUP NECONFIRMAT |
| GV | Verdict v5 (istoric) | Text sau gol | F | WATCH / NO BET |
| GW | Motiv verdict v5 | Text sau gol | F | NU – LINEUP NECONFIRMAT |
| GX | Raționament v5 | Text sau gol | F | P v5=92.0%; P0 v5=5.6%; low-conv=0%; mult.P0=1.00; clasă=SCĂZUT; cap=92.0%; Confid… |


#### Selectorul final v9

| Col. | Antet exact | Tip semantic | Sursă | Exemplu rând 4 |
| --- | --- | --- | --- | --- |
| GY | Data Status | Text sau gol | F | VERIFIED / PRIOR / SHRINKAGE |
| GZ | Data Quality Risk | Float sau gol/eroare | F | 9.999999999999998 |
| HA | Zero-Mass Risk | Float sau gol/eroare | F | 3.839503807616923 |
| HB | Context Risk | Float sau gol/eroare | F | 14.000000000000012 |
| HC | Model Uncertainty | Float sau gol/eroare | F | 9.377513343075528 |
| HD | Compound Risk | Float sau gol/eroare | F | 0 |
| HE | Risk Score | Float sau gol/eroare | F | 7.870120560697213 |
| HF | Risk Level Base | Număr întreg sau gol/eroare | F | 1 |
| HG | G0 / Hard Gate – date critice | Text sau gol | F | PASS |
| HH | Final Risk Level | Număr întreg sau gol/eroare | F | 1 |
| HI | Risk Class | Text sau gol | F | DEFENSIV |
| HJ | Risk Trace | Text sau gol | F | Data=VERIFIED / PRIOR / SHRINKAGE; DQ=10.0; ZM=3.8; Context=14.0; Uncertainty=9.4;… |
| HK | Recomandare finală tehnică | Text sau gol | F | DEFENSIV |


### A2 Configurația exactă din Setari model

| Rând și regim | B sezon GF | C sezon xG | D recent GF | E recent xG | F H2H | G piață | H context | I confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 Campionat intern | 0.25 | 0.25 | 0.15 | 0.15 | 0.05 | 0.15 | 1 | 1 |
| 6 Cupa interna | 0.15 | 0.2 | 0.15 | 0.15 | 0.05 | 0.3 | 1.15 | 0.9 |
| 7 Europa - tur | 0.1 | 0.25 | 0.15 | 0.2 | 0.03 | 0.27 | 1.1 | 0.92 |
| 8 Europa - retur | 0.08 | 0.22 | 0.15 | 0.2 | 0.02 | 0.33 | 1.3 | 0.9 |
| 9 International | 0.1 | 0.2 | 0.15 | 0.2 | 0.05 | 0.3 | 1.15 | 0.9 |
| 10 Turneu neutru | 0.12 | 0.22 | 0.16 | 0.2 | 0.05 | 0.25 | 1.15 | 0.85 |
| 11 Amical | 0.1 | 0.15 | 0.2 | 0.15 | 0.05 | 0.35 | 1.25 | 0.7 |

J5:J11 = ROUND(SUM(B:G),6), control Float. A este Text; B:I sunt Float, B:G ponderi fracționare. Blocurile A14:C25, A29:C54, A57:C83, A86:C109 și A112:C126 au schema Parametru (Text), Valoare (Float/Număr întreg/blank), Rol (Text). A129:C136 este explicație cu valori text, nu sursa numerică a capurilor.

| Celulă | Parametru exact | Valoare | Rol din fișier |
| --- | --- | --- | --- |
| B15 | Motivație | 0.01 | + dacă obiectivul impune marcarea; - dacă remiza/gestionarea este suficientă |
| B16 | Deschidere tactică | 0.025 | + joc vertical/presing; - bloc jos și ritm lent |
| B17 | Atac / absențe | 0.02 | + titulari ofensivi disponibili; - absențe la finalizare/creație |
| B18 | Apărare / absențe | 0.02 | + apărări slăbite; - defensive complete și stabile |
| B19 | Rotație | 0.015 | Efect net estimat; poate crește erorile sau reduce calitatea atacului |
| B20 | Oboseală | 0.01 | Efect net, ținând cont de zile de odihnă, minute și deplasări |
| B21 | Meteo | 0.015 | - pentru vânt/ploaie/căldură severă; 0 pentru condiții normale |
| B22 | Teren | 0.015 | - pentru suprafață slabă; + pentru suprafață rapidă și bună |
| B23 | Arbitru / penalty | 0.01 | Pondere mică: rata brută este puternic influențată de echipele arbitrate |
| B24 | Context tur/retur | 0.025 | + când scorul agregat obligă atacul; - când ambele pot temporiza |
| B25 | Dezechilibru valoric | 0.015 | + când favorita poate produce singură golul; - dacă favorita rotește masiv |
| B30 | k shrinkage sezon | 8 | Eșantioanele mici sunt trase spre media competiției |
| B31 | k shrinkage recent | 5 | Reduce supra-reacția la ultimele rezultate |
| B32 | Marjă implicită când lipsește Under 0,5 | 0.04 | Corecție aproximativă; preferă ambele cote când sunt disponibile |
| B33 | Pondere max. calibrare 0-0 ligă | 0.5 | Corectează abaterea Poisson folosind rata reală de 0-0 |
| B34 | Pondere max. zero empiric echipe | 0.25 | Integrează frecvențele O0,5 home/away |
| B35 | Prag P recomandat | 0.92 | Probabilitate minimă pentru recomandare fermă |
| B36 | Prag Confidence recomandat | 0.75 | Încredere minimă |
| B37 | Prag Edge recomandat | 0.025 | Avantaj minim față de piață |
| B38 | Prag EV recomandat | 0.015 | Randament așteptat minim pe unitate |
| B39 | Prag P cu prudență | 0.88 | Probabilitate minimă pentru recomandare prudentă |
| B40 | Prag Confidence cu prudență | 0.65 | Încredere minimă pentru zona prudentă |
| B41 | Prag Edge cu prudență | 0.01 | Avantaj minim pentru zona prudentă |
| B42 | Prag P neconcludent | 0.82 | Sub acest nivel pariul este evitat |
| B43 | Prag Confidence neconcludent | 0.5 | Sub acest nivel pariul este evitat |
| B44 | Țintă eșantion | 40 | Folosită la scorul de robustețe |
| B45 | Toleranță dispersie componente | 0.6 | Penalizează componentele contradictorii |
| B46 | Țintă completitudine numerică | 35 | Număr orientativ de intrări utile |
| B47 | Pondere completitudine | 0.3 | Confidence Score |
| B48 | Pondere eșantion | 0.2 | Confidence Score |
| B49 | Pondere acord componente | 0.2 | Confidence Score |
| B50 | Pondere calitate surse | 0.15 | Confidence Score |
| B51 | Pondere echipe start | 0.15 | Confidence Score |
| B52 | Penalizare contradicție / nivel | 0.08 | Scădere din Confidence Score |
| B53 | Multiplicator context minim | 0.75 | Limită de robustețe |
| B54 | Multiplicator context maxim | 1.25 | Limită de robustețe |
| B58 | Eșantion minim early season | 5 | Sub acest număr real home/away se aplică plafonul early. |
| B59 | Cap probabilitate early/regim | 0.92 | Plafon pentru eșantion <5, promovate sau etapa 1. |
| B60 | Cap probabilitate standard | 0.93 | Plafon fără confirmarea completă a pieței și loturilor. |
| B61 | Cap probabilitate confirmat | 0.94 | Permis doar cu loturi, disponibilități-cheie și cotă reală. |
| B62 | Majorare P0 regim major | 0.25 | +25% P0 pentru promovate/etapa 1. |
| B63 | Majorare P0 etapele 2-3 | 0.1 | +10% P0 în tranziția de început de sezon. |
| B64 | N minim calibrare ligă | 250 | Factorul zero al ligii ajunge la greutate maximă la 250 meciuri. |
| B65 | Pondere max. zero real ligă v2 | 0.5 | Greutatea maximă a masei empirice 0-0 în ZIP. |
| B66 | SOT bază / echipă | 4.5 | Reper pentru calitatea ofensivă. |
| B67 | Big chances bază / echipă | 1.5 | Reper pentru ocazii mari. |
| B68 | xG/șut bază | 0.1 | Reper pentru calitatea medie a șuturilor. |
| B69 | Touches box bază / echipă | 22 | Reper pentru prezența în careu. |
| B70 | Set-piece xG bază / echipă | 0.25 | Reper pentru faze fixe. |
| B71 | Factor calitate minim | 0.85 | Limită inferioară pentru ajustarea calității ofensive. |
| B72 | Factor calitate maxim | 1.15 | Limită superioară pentru ajustarea calității ofensive. |
| B73 | Penalizare cross-heavy / nivel | 0.03 | Reduce factorul de calitate pentru volum steril de centrări. |
| B74 | Majorare P0 atacant-cheie absent | 0.08 | +8% P0 pentru fiecare atacant-cheie absent. |
| B75 | Ajustare P0 portar-cheie absent | -0.06 | -6% P0 pentru fiecare portar-cheie absent. |
| B76 | Confidence minim selecție finală | 0.75 | Prag separat de probabilitatea statistică. |
| B77 | Interval de incertitudine bază | 0.03 | Semilățime orientativă; crește când informația lipsește. |
| B78 | Nr. maxim selecții portofoliu | 5 | Control: 1–5 selecții independente. |
| B79 | Corelație maximă portofoliu | 0.3 | Peste prag, combinația este blocată. |
| B80 | Fracție Kelly implicită | 0.25 | Kelly fracționat, folosit dacă rândul nu are altă valoare. |
| B81 | Limită miză zilnică implicită | 0.02 | Maximum 2% din bankroll/zi dacă nu se completează altă limită. |
| B82 | Minut minim modul live | 20 | Nu se emite selecție live înainte de minutul 20. |
| B83 | Cap factor intensitate live | 1.5 | Protejează contra extrapolării excesive a ritmului live. |
| B87 | Rată 0-0 echipă de referință | 0.1 | Etalon pentru riscul 0-0 combinat home/away. |
| B88 | Risc blank×CS de referință | 0.25 | Etalon pentru FTS al unei echipe × clean sheet-ul advers. |
| B89 | Rată 0-0 HT de referință | 0.35 | Etalon pentru ritmul fără gol în prima repriză. |
| B90 | Pondere risc 0-0 team-specific | 0.3 | Pondere în factorul zero-mass v3. |
| B91 | Pondere blank×clean-sheet reciproc | 0.3 | Ponderea interacțiunii atac fără gol × apărare fără gol primit. |
| B92 | Pondere finishing vs xG | 0.2 | Penalizează subperformanța comună la finalizare. |
| B93 | Pondere bloc statistic 0–0 HT | 0.2 | Coeficientul exterior 20% rămâne neschimbat. Componenta manuală a fost eliminată. |
| B94 | Coeficient statistic 0–0 HT | 0.75 | 75% păstrat din formula anterioară; ponderea manuală eliminată nu se redistribuie. |
| B95 | Parametru retras – FB eliminat |  | Neutilizat în formule. Nu se completează. |
| B96 | Parametru retras – FB eliminat |  | Neutilizat în formule. Nu se completează. |
| B97 | Factor zero-mass minim | 0.75 | Limită inferioară pentru ajustarea ZIP/DC. |
| B98 | Factor zero-mass maxim | 1.6 | Limită superioară anti-extrapolare. |
| B99 | Prag clasă zero-mass SCĂZUT | 0.95 | Factor ≤ prag: masă la zero controlată. |
| B100 | Prag clasă zero-mass RIDICAT | 1.15 | Factor > prag: risc 0-0 ridicat. |
| B101 | P0 maxim recalibrat v3 | 0.65 | Plafon tehnic al probabilității 0-0. |
| B102 | Cap probabilitate risc ridicat / date incomplete | 0.9 | Peste 90% nu este permis cu date zero-risk incomplete sau risc ridicat. |
| B103 | Cap probabilitate risc mediu | 0.91 | Plafon pentru clasa MEDIU. |
| B104 | Cap probabilitate risc scăzut fără confirmări complete | 0.92 | Plafon de raportare; nu influențează recomandarea finală. |
| B105 | Cap probabilitate risc scăzut cu confirmări complete | 0.94 | Permis numai cu confirmări complete; nu influențează recomandarea finală. |
| B106 | Prag confirmare piață zero-risk | 0.85 | Probabilitatea implicită reală minimă a pieței. |
| B107 | Penalizare confidence zero-risk incomplet | 12 | Puncte scăzute când setul P0 v3 nu este complet. |
| B108 | Penalizare confidence risc mediu | 6 | Puncte scăzute pentru clasa MEDIU. |
| B109 | Penalizare confidence risc ridicat | 12 | Puncte scăzute pentru clasa RIDICAT. |
| B113 | Prag blank recent / echipă | 0.2 | Semnal activ când fiecare echipă are blank rate recent ≥20%. |
| B114 | Prag clean-sheet advers relevant | 0.3 | Semnal activ când blank-ul unei echipe întâlnește CS advers ≥30%. |
| B115 | λ moderat minim | 1.6 | Limita inferioară a ferestrei λ moderate. |
| B116 | λ moderat maxim | 2.6 | Limita superioară a ferestrei λ moderate. |
| B117 | Prag finishing recent slab | 0.9 | Media GF/xGF recent ≤0,90 indică conversie slabă. |
| B118 | xGF recent minim – chance creation | 0.8 | Necesită ocazii create; evită confundarea atacului inert cu subfinalizarea. |
| B119 | Prag rată 0-0 recent acumulată | 0.2 | Semnal când cel puțin o echipă are ≥20% rezultate 0-0 în fereastra recentă. |
| B120 | N minim recent pentru 0-0 | 5 | Eșantion minim pentru semnalul de acumulare 0-0. |
| B121 | Pondere blank bilateral | 0.2 | Pondere în scorul low-conversion. |
| B122 | Pondere clean-sheet advers | 0.2 | Pondere în scorul low-conversion. |
| B123 | Pondere nucleu low-conversion | 0.45 | Cea mai mare pondere: λ moderat + finishing slab + xGF relevant. |
| B124 | Pondere acumulare 0-0 recentă | 0.15 | Pondere în scorul low-conversion. |
| B125 | Majorare P0 maximă low-conversion | 0.2 | Majorare incrementală maximă a P0; nu modifică plafoanele 90/91/92/94%. |
| B126 | Penalizare Confidence maximă | 8 | Penalizare maximă, proporțională cu scorul low-conversion. |


### A3 Celelalte foi tabelare

#### Surse cercetare

Registru documentar cu 70 surse. Nu colectează date și nu validează automat inputurile.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | Nr. | Număr întreg | Valoare fixă / input manual |
| B | Website / instituție | Text | Valoare fixă / input manual |
| C | Categorie | Text | Valoare fixă / input manual |
| D | URL | Text | Valoare fixă / input manual |
| E | Utilizare în model | Text | Valoare fixă / input manual |
| F | Observație extrasă | Text | Valoare fixă / input manual |
| G | Nivel evidență | Text | Valoare fixă / input manual |
| H | Data consultării | Dată | Valoare fixă / input manual |


#### Backtest

Predicții curente preluate prin ID, rezultate manuale și metrici. Verdictul N citește GV istoric.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | Match ID | Text | Valoare fixă / input manual |
| B | Data | Dată sau gol | Formulă B4 |
| C | Gazde | Text sau gol | Formulă C4 |
| D | Oaspeți | Text sau gol | Formulă D4 |
| E | P model v5 O0.5 | Procentaj [fracție] sau gol | Formulă E4 |
| F | Confidence v5 | Float 0–100 sau gol | Formulă F4 |
| G | Cotă plasată | Float | Valoare fixă / input manual |
| H | Cotă închidere | Float | Valoare fixă / input manual |
| I | Rezultat O0.5 (1/0) | Număr întreg 0/1 | Valoare fixă / input manual |
| J | Profit 1u | Float sau gol | Formulă J4 |
| K | Brier Score | Float sau gol | Formulă K4 |
| L | Log-loss | Float sau gol | Formulă L4 |
| M | CLV | Procentaj [fracție] sau gol | Formulă M4 |
| N | Verdict v5 | Text sau gol | Formulă N4 |
| O | Clasă zero-risk v5 | Text sau gol | Formulă O4 |
| P | Indicator | Text | Valoare fixă / input manual |
| Q | Valoare | Mixt după rând | Formulă Q4; alte rânduri au etichete/valori fixe |
| U | Clasă zero-risk | Text | Valoare fixă / input manual |
| V | Nr. | Număr întreg | Formulă V4 |
| W | Brier mediu | Float sau gol | Formulă W4 |
| X | Log-loss mediu | Float sau gol | Formulă X4 |
| Y | P medie | Procentaj [fracție] sau gol | Formulă Y4 |
| Z | Rată reală | Procentaj [fracție] sau gol | Formulă Z4 |

A4:A203 și G:I sunt inputuri manuale; B:F și J:O formule. P3:T19 este rezumat lateral cu etichete și formule; U3:Z7 este rezumat pe clase. Q/R/S/T nu formează o schemă uniformă de rând-meci. Adresele complete se află în manifest.

#### Frozen Predictions

Registru manual de snapshoturi pre-match. Fără formule și fără transfer automat către Settlement.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | Snapshot_ID | Text | Valoare fixă / input manual |
| B | Snapshot_TS | Dată/timestamp | Valoare fixă / input manual |
| C | Match_Date | Dată/timestamp | Valoare fixă / input manual |
| D | Country | Text | Valoare fixă / input manual |
| E | League | Text | Valoare fixă / input manual |
| F | Home | Text | Valoare fixă / input manual |
| G | Away | Text | Valoare fixă / input manual |
| H | Market | Text | Valoare fixă / input manual |
| I | Line | Float | Valoare fixă / input manual |
| J | Model_Version | Text | Valoare fixă / input manual |
| K | P_Model | Float procentaj | Valoare fixă / input manual |
| L | P_Final | Float procentaj | Valoare fixă / input manual |
| M | Verdict | Text | Valoare fixă / input manual |
| N | Risk_Level | Număr întreg | Valoare fixă / input manual |
| O | Hard_Gates | Text | Valoare fixă / input manual |
| P | Data_Grade | Text | Valoare fixă / input manual |
| Q | PreMatch_Frozen | Text | Valoare fixă / input manual |
| R | P0_model | Float procentaj | Valoare fixă / input manual |
| S | P0_empirical_HA | Float procentaj | Valoare fixă / input manual |
| T | P0_league | Float procentaj | Valoare fixă / input manual |
| U | P0_calibrated | Float procentaj | Valoare fixă / input manual |
| V | BlankRate_H | Float procentaj | Valoare fixă / input manual |
| W | BlankRate_A | Float procentaj | Valoare fixă / input manual |
| X | Opponent_CS_HA | Float procentaj | Valoare fixă / input manual |
| Y | ZeroMassConfirmationCount | Număr întreg | Valoare fixă / input manual |
| Z | Lineup_Status | Text | Valoare fixă / input manual |
| AA | P_Cap | Float procentaj | Valoare fixă / input manual |
| AB | ZeroMass_Status | Text | Valoare fixă / input manual |
| AC | Candidate_Threshold_ID | Text | Valoare fixă / input manual |
| AD | Notes | Text | Valoare fixă / input manual |
| AE | BlankRecent_H | Float procentaj | Valoare fixă / input manual |
| AF | BlankRecent_A | Float procentaj | Valoare fixă / input manual |
| AG | Recent00_Count_H | Număr întreg | Valoare fixă / input manual |
| AH | Recent00_Count_A | Număr întreg | Valoare fixă / input manual |
| AI | RecentFinishing_H | Float | Valoare fixă / input manual |
| AJ | RecentFinishing_A | Float | Valoare fixă / input manual |
| AK | ChanceCreation_Index | Float | Valoare fixă / input manual |
| AL | BothBlank_Flag | Text | Valoare fixă / input manual |
| AM | OpponentCS_Flag | Text | Valoare fixă / input manual |
| AN | ModerateLambdaWeakFinishing_Flag | Text | Valoare fixă / input manual |
| AO | Recent00_Accumulation_Flag | Text | Valoare fixă / input manual |
| AP | LowConversion_Score | Float procentaj | Valoare fixă / input manual |
| AQ | LowConversion_P0_Multiplier | Float | Valoare fixă / input manual |
| AR | P0_v5 | Float procentaj | Valoare fixă / input manual |
| AS | ZeroRisk_v5 | Text | Valoare fixă / input manual |
| AT | P_Cap_v5 | Float procentaj | Valoare fixă / input manual |
| AU | P_Final_v5 | Float procentaj | Valoare fixă / input manual |

A:AU sunt câmpurile cu antet; AV:AZ sunt doar în limita formatată, fără câmpuri denumite. Toate valorile se îngheață înainte de kickoff. Nu există formule care să copieze automat predicțiile.

#### Settlement

Foaie declarată deprecated pentru analiza pre-match. Brier și log-loss active pentru audit.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | Snapshot_ID | Text | Valoare fixă / input manual |
| B | Match_Date | Dată/timestamp | Valoare fixă / input manual |
| C | League | Text | Valoare fixă / input manual |
| D | Home | Text | Valoare fixă / input manual |
| E | Away | Text | Valoare fixă / input manual |
| F | Market | Text | Valoare fixă / input manual |
| G | Line | Float | Valoare fixă / input manual |
| H | Model_Version | Text | Valoare fixă / input manual |
| I | P_Final_Frozen | Float | Valoare fixă / input manual |
| J | Outcome_1_0 | Număr întreg | Valoare fixă / input manual |
| K | Profit_1u | Float | Valoare fixă / input manual |
| L | Score_H | Număr întreg | Valoare fixă / input manual |
| M | Score_A | Număr întreg | Valoare fixă / input manual |
| N | Total | Număr întreg | Valoare fixă / input manual |
| O | Fail_Mode | Text | Valoare fixă / input manual |
| P | Settlement_Source | Text | Valoare fixă / input manual |
| Q | Settled_TS | Dată/timestamp | Valoare fixă / input manual |
| R | Brier | Float | Formulă R4 |
| S | LogLoss | Float | Formulă S4 |
| T | Risk_Level | Număr întreg | Valoare fixă / input manual |
| U | Hard_Gates_Frozen | Text | Valoare fixă / input manual |
| V | Verdict_Frozen | Text | Valoare fixă / input manual |
| W | Notes | Text | Valoare fixă / input manual |


#### Risk Level Summary

Agregări istorice după Settlement!T, nivelurile 1–5.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | Risk Level | Număr întreg | Valoare fixă / input manual |
| B | N | Număr întreg | Formulă B4 |
| C | Wins | Număr întreg | Formulă C4 |
| D | Hit Rate | Procentaj [fracție] sau gol | Formulă D4 |
| E | Brier | Float sau gol | Formulă E4 |
| F | Fail Rate | Procentaj [fracție] sau gol | Formulă F4 |


#### Calibration

Benzi de probabilitate și decalaj de calibrare din Settlement.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | P low | Procentaj [fracție] | Valoare fixă / input manual |
| B | P high | Procentaj [fracție] | Valoare fixă / input manual |
| C | N | Număr întreg | Formulă C4 |
| D | Mean P | Procentaj [fracție] sau gol | Formulă D4 |
| E | Observed Rate | Procentaj [fracție] sau gol | Formulă E4 |
| F | Calibration Gap | Float diferență fracții | Formulă F4 |
| G | Status | Text | Formulă G4 |


#### Fail Distribution

Numără eșecurile după codul Settlement!O.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | Fail Mode | Text | Valoare fixă / input manual |
| B | Fails | Număr întreg | Formulă B4 |
| C | Share of Fails | Procentaj [fracție] sau gol | Formulă C4 |
| D | Model relevance | Text | Valoare fixă / input manual |
| E | Notes | Text | Valoare fixă / input manual |


#### League Summary

Agregări pe ligile introduse manual în A4:A33.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | League | Text | Valoare fixă / input manual |
| B | N | Număr întreg sau gol | Formulă B4 |
| C | Wins | Număr întreg sau gol | Formulă C4 |
| D | Hit Rate | Procentaj [fracție] sau gol | Formulă D4 |
| E | Mean P | Procentaj [fracție] sau gol | Formulă E4 |
| F | Calibration Gap | Float diferență fracții | Formulă F4 |
| G | Brier | Float sau gol | Formulă G4 |
| H | Stability | Text | Formulă H4 |


#### Monthly Summary

Agregări pe lunile introduse manual în A4:A27.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | Month Start | Dată (serial Excel) | Valoare fixă / input manual |
| B | N | Număr întreg sau gol | Formulă B4 |
| C | Wins | Număr întreg sau gol | Formulă C4 |
| D | Hit Rate | Procentaj [fracție] sau gol | Formulă D4 |
| E | Mean P | Procentaj [fracție] sau gol | Formulă E4 |
| F | Calibration Gap | Float diferență fracții | Formulă F4 |
| G | Brier | Float sau gol | Formulă G4 |

A4 este serialul Excel 46235 (2026-08-01 în sistemul de date al fișierului). Următoarele luni nu sunt generate automat; A5:A27 sunt goale.

#### Builder Marginal Fails

Interfață documentară de audit Builder, fără motor de calcul în această foaie.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | Builder_ID | Text | Valoare fixă / input manual |
| B | Builder_Type | Text | Valoare fixă / input manual |
| C | Match | Text | Valoare fixă / input manual |
| D | Failed_Leg | Text | Valoare fixă / input manual |
| E | Source_Model | Text | Valoare fixă / input manual |
| F | Leg_P | Procentaj [fracție] | Valoare fixă / input manual |
| G | Leg_Risk | Float/nivel; convenție nefixată | Valoare fixă / input manual |
| H | Source_Gates | Text | Valoare fixă / input manual |
| I | Correlation | Float | Valoare fixă / input manual |
| J | Uncertainty | Float | Valoare fixă / input manual |
| K | Marginal_Fail_Contribution | Float | Valoare fixă / input manual |
| L | Notes | Text | Valoare fixă / input manual |


#### Backtest Summary

Rezumat post-match, Wilson, Brier, log-loss și stabilitate pe ligi.

| Col. | Antet exact | Tip | Sursă |
| --- | --- | --- | --- |
| A | Metric | Text | Valoare fixă / input manual |
| B | Walk-forward value | Număr întreg/Float după rând | Formulă B4; alte rânduri au etichete/valori fixe |
| C | Meaning | Text | Valoare fixă / input manual |
| D | Threshold-change role | Text | Valoare fixă / input manual |
| E | Reference evidence | Text | Valoare fixă / input manual |
| F | Reference N / value | Mixt numeric/text | Valoare fixă / input manual |
| G | Reference Wilson / metric | Mixt numeric/text | Valoare fixă / input manual |
| H | Status | Text | Valoare fixă / input manual |


### A4 Foi cu structură verticală și blocuri documentare

#### Dashboard

Afișare a meciului selectat prin B4. Output oficial GP/GT și HE:HK; nu este motorul statistic.

| Zonă | Câmpuri exacte sau outputuri | Tip | Sursă |
| --- | --- | --- | --- |
| B4 | Match ID selectat | Text | Input manual |
| B7,D7,F7,H7,B8,D8,F8,H8 | Identitate, context și surse | Text/Dată/Număr | INDEX/MATCH după B4 |
| K4:K9 | Componente lambda BJ:BN și BP | Float | INDEX/MATCH |
| A12,C12,E12,G12 | GL, GP, GQ, GT | Float/procentaj | INDEX/MATCH |
| A16,C16,E16,G16 | AR, EC, GR, GS | Float/procentaj | INDEX/MATCH |
| A21,C21 | Scor și recomandare HK | Text | TEXT/INDEX/MATCH |
| E26:E33,G26:G33 | Control tehnic și stări | Mixt | Formule; antete A25/E25/G25 |
| A36,A39 | HJ și CI | Text | INDEX/MATCH |
| K31 | Număr website-uri | Întreg | COUNTA(Surse cercetare!A4:A100) |
| K32:K34 | Versiune, dată, metodologie | Text/Dată | Constante documentare |


#### Risk Classification

Ponderi active și afișaj pentru meciul selectat. E28:E32 alimentează HE.

| Zonă | Câmpuri exacte sau outputuri | Tip | Sursă |
| --- | --- | --- | --- |
| A3:E9 | Componentă; Pondere activă; Scor 0–100; Definiție operațională; Sursă în Analize meciuri | Text, Float, Float, Text, Text | A/D/E texte; B4:B9 formule; C4:C8 nepopulate |
| A12:D17 | Risk Score; Nivel; Interpretare; Acțiune | Text, Întreg, Text, Text | Constante documentare |
| A19:D25 | Regulă comună; Valoare; Rol; Observație | Text/Număr | Constante |
| A28:E32 | Componente ale meciului și ponderi | Text/Float | B28:B32 INDEX/MATCH; E28:E32 formule B4:B8 |
| B35:B39 | Risk Score; Risk Level Base; G0; Final Risk Level; Risk Class | Float/Întreg/Text | Formule |
| A41:E47 | Definiții finale | Text | Documentație |


#### ZeroMass Gate v4

Exemplu/gate local cu valori manuale și două confirmări. Nu alimentează HK sau GP.

| Zonă | Câmpuri exacte sau outputuri | Tip | Sursă |
| --- | --- | --- | --- |
| A3:F10 | Componentă; Valoare / Status; Prag / sens; Sursa 1; Sursa 2; Rol | Text/Mixt/Text/Text/Text/Text | B4:B10 inputuri manuale; D/E surse text |
| A12:D18 | Calcul / Gate; Valoare; Regulă; Rezultat | Text/Mixt/Text/Text | B13:B16 input; B17:B18 și D17:D18 formule |


#### ZeroMass WF v4

Fișă locală walk-forward cu inputuri manuale și cap local. Nu alimentează GP/HK.

| Zonă | Câmpuri exacte sau outputuri | Tip | Sursă |
| --- | --- | --- | --- |
| A3:F15 | Field; Value; Role; Rule; OOS status; Builder | Text/Mixt/Text/Text/Text/Text | B4:B13 input manual; B14/B15 formule |


#### ZeroMass Gate v5

Afișaj de audit al meciului Dashboard. B22/B23 citesc GU/GV istorice.

| Zonă | Câmpuri exacte sau outputuri | Tip | Sursă |
| --- | --- | --- | --- |
| B2 | Match ID | Text | Dashboard!B4 |
| A4:F23 | Indicator; Valoare; Prag / referință; Status; Rol; Interpretare | Text/Mixt/Mixt/Text/Text/Text | A/E/F texte; B și D formule; C mixt; detalii în manifest |


#### CHANGELOG VERSIUNI

Texte consolidate despre versiunile precedente; nu conține formule. Nu au un antet unic pentru toate rândurile. Coloanele se interpretează pe bloc, nu ca tabel de inputuri.

| Început bloc | Conținut |
| --- | --- |
| A4 | Update_v4 |
| A13 | WF_Update_v4 |
| A21 | Update_v5 |
| A31 | Update_v6 |
| A42 | Update_v7 |

Antetele exacte ale blocurilor sunt prezentate mai jos. Toate coloanele sunt Text documentar; valorile numerice sunt menționate în texte, fără formule executabile.

| Rând antet | Coloane și denumiri exacte |
| --- | --- |
| 7 | A: Prioritate; B: Update; C: Problemă / motiv; D: Regulă operațională; E: Implementare; F: Impact risc |
| 16 | A: Priority; B: Change; C: Evidence status; D: Operational rule; E: Threshold action; F: Builder impact; G: Audit note |
| 24 | A: Prioritate; B: Modificare; C: Problemă tratată; D: Regulă operațională; E: Implementare; F: Praguri |
| 34 | A: Prioritate; B: Modificare; C: Implementare; D: Impact; E: Praguri vechi; F: Observație |
| 44 | A: Prioritate; B: Clarificare; C: Regulă nouă / explicitată; D: Ce NU se schimbă; E: Impact; F: Motiv |
| 52 | A: Prioritate; B: Modificare; C: Regulă activă; D: Ce NU se schimbă; E: Impact; F: Trasabilitate |
| 60 | A: Prioritate; B: Modificare; C: Regulă activă; D: Parametri; E: Impact; F: Trasabilitate |


#### DOCUMENTATIE MODEL

Metodologie, legendă, readiness și matrice de decizie consolidate; nu conține formule. Nu au un antet unic pentru toate rândurile. Coloanele se interpretează pe bloc, nu ca tabel de inputuri.

| Început bloc | Conținut |
| --- | --- |
| A4 | Metodologie |
| A70 | Legendă câmpuri |
| A297 | Metodologie v1.1 |
| A317 | Metodologie v3 |
| A342 | Metodologie v5 |
| A368 | Data_Readiness_v6 |
| A399 | Metodologie_v7 |
| A428 | Decision_Matrix_v7 |

Legenda la A74:H280: A index, B Grup, C Câmp, D Ce înseamnă, E Cum se citește / interpretează, F Format / unitate, G Tip câmp, H Rol / observație. Readiness la A371:F380: Status, Definiție, Efect în model, Hard fail?, Utilizare recomandată, Observație. A383:F387: Componentă model, Clasă, Status input, Tratament, Sursă sugerată, Notă. A430:G437: Gate, Zero-Mass, Data Readiness, P_cap orientativ, Risk Score, Verdict posibil, Interpretare. A439:G446: Câmp, Regulă, Sursă, Efect SMALL SAMPLE, Output, Gate, Observație. A449:I464 este actualizarea v9; principalele texte sunt în A și C. Toate sunt valori documentare fixe, de regulă Text, cu index/valori numerice unde apar.

## Anexa B Formulele exacte și dependențele

Formulele de mai jos sunt copiate din fișier, cu separator invariant virgulă și nume de funcții în engleză. Fiecare familie arată celula reprezentativă, numărul de apariții și intervalul adreselor. Manifestul JSON enumeră fiecare adresă exactă, inclusiv ancorele absolute. Referințele fără nume de foaie sunt în foaia curentă. Copierea formulei pe alt rând trebuie să respecte ancorele $, nu înlocuirea brută a cifrei 4.

### Dashboard

**K4** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$BJ$4:$BJ$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$BJ$4:$BJ$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**K5** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$BK$4:$BK$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$BK$4:$BK$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**K6** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$BL$4:$BL$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$BL$4:$BL$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**B7** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$G$4:$G$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$G$4:$G$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**D7** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$H$4:$H$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$H$4:$H$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**F7** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$D$4:$D$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$D$4:$D$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**H7** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$E$4:$E$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$E$4:$E$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**K7** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$BM$4:$BM$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$BM$4:$BM$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**B8** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$C$4:$C$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$C$4:$C$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**D8** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$F$4:$F$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$F$4:$F$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**F8** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$AT$4:$AT$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$AT$4:$AT$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**H8** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$AU$4:$AU$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$AU$4:$AU$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**K8** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$BN$4:$BN$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$BN$4:$BN$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**K9** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$BP$4:$BP$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$BP$4:$BP$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**A12** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GL$4:$GL$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GL$4:$GL$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**C12** — 2 apariții; prima C12, ultima E26; lista completă în manifest.

```excel
=IFERROR(INDEX('Analize meciuri'!$GP$4:$GP$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GP$4:$GP$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**E12** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GQ$4:$GQ$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GQ$4:$GQ$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**G12** — 2 apariții; prima G12, ultima E27; lista completă în manifest.

```excel
=IFERROR(INDEX('Analize meciuri'!$GT$4:$GT$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GT$4:$GT$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**A16** — 2 apariții; prima A16, ultima E28; lista completă în manifest.

```excel
=IFERROR(INDEX('Analize meciuri'!$AR$4:$AR$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$AR$4:$AR$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**C16** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$EC$4:$EC$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$EC$4:$EC$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**E16** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GR$4:$GR$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GR$4:$GR$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**G16** — 2 apariții; prima G16, ultima E29; lista completă în manifest.

```excel
=IFERROR(INDEX('Analize meciuri'!$GS$4:$GS$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GS$4:$GS$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**A21** — 1 apariții; adresă unică.

```excel
=IFERROR(TEXT(INDEX('Analize meciuri'!$HE$4:$HE$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"0.0")&" / Nivel "&INDEX('Analize meciuri'!$HH$4:$HH$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0))&" / "&INDEX('Analize meciuri'!$HI$4:$HI$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"N/A")
```

Dependențe: 'Analize meciuri'!$HE$4:$HE$103, $B$4, 'Analize meciuri'!$A$4:$A$103, 'Analize meciuri'!$HH$4:$HH$103, 'Analize meciuri'!$HI$4:$HI$103.

**C21** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$HK$4:$HK$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$HK$4:$HK$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**G26** — 4 apariții; prima G26, ultima G29; lista completă în manifest.

```excel
=IF(E26="","N/A","INFORMATIV")
```

Dependențe: E26.

**E30** — 1 apariții; adresă unică.

```excel
=IFERROR(IFERROR(INDEX('Analize meciuri'!$GM$4:$GM$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")&" / "&IFERROR(INDEX('Analize meciuri'!$GN$4:$GN$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),""),"")
```

Dependențe: 'Analize meciuri'!$GM$4:$GM$103, $B$4, 'Analize meciuri'!$A$4:$A$103, 'Analize meciuri'!$GN$4:$GN$103.

**G30** — 1 apariții; adresă unică.

```excel
=IF(LEFT(E30,2)="DA","OK","VERIFICĂ")
```

Dependențe: E30.

**E31** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$FN$4:$FN$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$FN$4:$FN$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**G31** — 2 apariții; prima G31, ultima G32; lista completă în manifest.

```excel
="INFORMATIV – DOAR P_CAP"
```

Dependențe: niciuna; formulă constantă.

**K31** — 1 apariții; adresă unică.

```excel
=COUNTA('Surse cercetare'!$A$4:$A$100)
```

Dependențe: 'Surse cercetare'!$A$4:$A$100.

**E32** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$FM$4:$FM$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$FM$4:$FM$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**E33** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$HG$4:$HG$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0))&" / Nivel "&INDEX('Analize meciuri'!$HH$4:$HH$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$HG$4:$HG$103, $B$4, 'Analize meciuri'!$A$4:$A$103, 'Analize meciuri'!$HH$4:$HH$103.

**G33** — 1 apariții; adresă unică.

```excel
=IF(LEFT(E33,4)="PASS","DA","NU")
```

Dependențe: E33.

**A36** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$HJ$4:$HJ$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$HJ$4:$HJ$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

**A39** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$CI$4:$CI$103,MATCH($B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$CI$4:$CI$103, $B$4, 'Analize meciuri'!$A$4:$A$103.

### Analize meciuri

**BJ4** — 100 apariții; prima BJ4, ultima BJ103; lista completă în manifest.

```excel
=IF($A4="","",SQRT((($I4*IF($J4="",$AJ4,$J4)+'Setari model'!$B$30*$AJ4)/($I4+'Setari model'!$B$30))*(($P4*IF($R4="",$AJ4,$R4)+'Setari model'!$B$30*$AJ4)/($P4+'Setari model'!$B$30)))+SQRT((($P4*IF($Q4="",$AK4,$Q4)+'Setari model'!$B$30*$AK4)/($P4+'Setari model'!$B$30))*(($I4*IF($K4="",$AK4,$K4)+'Setari model'!$B$30*$AK4)/($I4+'Setari model'!$B$30))))
```

Dependențe: $A4, $I4, $J4, $AJ4, 'Setari model'!$B$30, $P4, $R4, $Q4, $AK4, $K4.

**BK4** — 100 apariții; prima BK4, ultima BK103; lista completă în manifest.

```excel
=IF($A4="","",SQRT((($I4*IF($L4="",IF($J4="",$AJ4,$J4),$L4)+'Setari model'!$B$30*$AJ4)/($I4+'Setari model'!$B$30))*(($P4*IF($T4="",IF($R4="",$AJ4,$R4),$T4)+'Setari model'!$B$30*$AJ4)/($P4+'Setari model'!$B$30)))+SQRT((($P4*IF($S4="",IF($Q4="",$AK4,$Q4),$S4)+'Setari model'!$B$30*$AK4)/($P4+'Setari model'!$B$30))*(($I4*IF($M4="",IF($K4="",$AK4,$K4),$M4)+'Setari model'!$B$30*$AK4)/($I4+'Setari model'!$B$30))))
```

Dependențe: $A4, $I4, $L4, $J4, $AJ4, 'Setari model'!$B$30, $P4, $T4, $R4, $S4, $Q4, $AK4, $M4, $K4.

**BL4** — 100 apariții; prima BL4, ultima BL103; lista completă în manifest.

```excel
=IF($A4="","",SQRT((($W4*IF($X4="",$AL4/2,$X4)+'Setari model'!$B$31*$AL4/2)/($W4+'Setari model'!$B$31))*(($AB4*IF($AD4="",$AL4/2,$AD4)+'Setari model'!$B$31*$AL4/2)/($AB4+'Setari model'!$B$31)))+SQRT((($AB4*IF($AC4="",$AL4/2,$AC4)+'Setari model'!$B$31*$AL4/2)/($AB4+'Setari model'!$B$31))*(($W4*IF($Y4="",$AL4/2,$Y4)+'Setari model'!$B$31*$AL4/2)/($W4+'Setari model'!$B$31))))
```

Dependențe: $A4, $W4, $X4, $AL4, 'Setari model'!$B$31, $AB4, $AD4, $AC4, $Y4.

**BM4** — 100 apariții; prima BM4, ultima BM103; lista completă în manifest.

```excel
=IF($A4="","",SQRT((($W4*IF($Z4="",IF($X4="",$AL4/2,$X4),$Z4)+'Setari model'!$B$31*$AL4/2)/($W4+'Setari model'!$B$31))*(($AB4*IF($AF4="",IF($AD4="",$AL4/2,$AD4),$AF4)+'Setari model'!$B$31*$AL4/2)/($AB4+'Setari model'!$B$31)))+SQRT((($AB4*IF($AE4="",IF($AC4="",$AL4/2,$AC4),$AE4)+'Setari model'!$B$31*$AL4/2)/($AB4+'Setari model'!$B$31))*(($W4*IF($AA4="",IF($Y4="",$AL4/2,$Y4),$AA4)+'Setari model'!$B$31*$AL4/2)/($W4+'Setari model'!$B$31))))
```

Dependențe: $A4, $W4, $Z4, $X4, $AL4, 'Setari model'!$B$31, $AB4, $AF4, $AD4, $AE4, $AC4, $AA4, $Y4.

**BN4** — 100 apariții; prima BN4, ultima BN103; lista completă în manifest.

```excel
=IF($A4="","",IF($AG4>0,($AG4*IF($AH4="",$AL4,$AH4)+5*$AL4)/($AG4+5),$AL4))
```

Dependențe: $A4, $AG4, $AH4, $AL4.

**BO4** — 100 apariții; prima BO4, ultima BO103; lista completă în manifest.

```excel
=IF($A4="","",IF($AR4>1,IF($AS4>1,(1/$AR4)/((1/$AR4+1/$AS4)),MIN(0.995,(1/$AR4)/(1+'Setari model'!$B$32))),1-EXP(-$AL4)))
```

Dependențe: $A4, $AR4, $AS4, 'Setari model'!$B$32, $AL4.

**BP4** — 100 apariții; prima BP4, ultima BP103; lista completă în manifest.

```excel
=IF($A4="","",-LN(1-$BO4))
```

Dependențe: $A4, $BO4.

**BQ4** — 100 apariții; prima BQ4, ultima BQ103; lista completă în manifest.

```excel
=IF($A4="","",$BJ4*INDEX('Setari model'!$B$5:$B$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BK4*INDEX('Setari model'!$C$5:$C$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BL4*INDEX('Setari model'!$D$5:$D$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BM4*INDEX('Setari model'!$E$5:$E$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BN4*INDEX('Setari model'!$F$5:$F$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BP4*INDEX('Setari model'!$G$5:$G$11,MATCH($E4,'Setari model'!$A$5:$A$11,0)))
```

Dependențe: $A4, $BJ4, 'Setari model'!$B$5:$B$11, $E4, 'Setari model'!$A$5:$A$11, $BK4, 'Setari model'!$C$5:$C$11, $BL4, 'Setari model'!$D$5:$D$11, $BM4, 'Setari model'!$E$5:$E$11, $BN4, 'Setari model'!$F$5:$F$11, $BP4, 'Setari model'!$G$5:$G$11.

**BR4** — 100 apariții; prima BR4, ultima BR103; lista completă în manifest.

```excel
=IF($A4="","",MAX('Setari model'!$B$53,MIN('Setari model'!$B$54,1+($AV4*'Setari model'!$B$15+$AW4*'Setari model'!$B$16+$AX4*'Setari model'!$B$17+$AY4*'Setari model'!$B$18+$AZ4*'Setari model'!$B$19+$BA4*'Setari model'!$B$20+$BB4*'Setari model'!$B$21+$BC4*'Setari model'!$B$22+$BD4*'Setari model'!$B$23+$BE4*'Setari model'!$B$24+$BF4*'Setari model'!$B$25)*INDEX('Setari model'!$H$5:$H$11,MATCH($E4,'Setari model'!$A$5:$A$11,0)))))
```

Dependențe: $A4, 'Setari model'!$B$53, 'Setari model'!$B$54, $AV4, 'Setari model'!$B$15, $AW4, 'Setari model'!$B$16, $AX4, 'Setari model'!$B$17, $AY4, 'Setari model'!$B$18, $AZ4, 'Setari model'!$B$19, $BA4, 'Setari model'!$B$20, $BB4, 'Setari model'!$B$21, $BC4, 'Setari model'!$B$22, $BD4, 'Setari model'!$B$23, $BE4, 'Setari model'!$B$24, $BF4, 'Setari model'!$B$25, 'Setari model'!$H$5:$H$11, $E4, 'Setari model'!$A$5:$A$11.

**BS4** — 100 apariții; prima BS4, ultima BS103; lista completă în manifest.

```excel
=IF($A4="","",$BQ4*$BR4)
```

Dependențe: $A4, $BQ4, $BR4.

**BT4** — 100 apariții; prima BT4, ultima BT103; lista completă în manifest.

```excel
=IF($A4="","",EXP(-$BS4))
```

Dependențe: $A4, $BS4.

**BU4** — 100 apariții; prima BU4, ultima BU103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR($AM4="",$AN4=""),1,1+MIN('Setari model'!$B$33,$AN4/100*'Setari model'!$B$33)*($AM4/EXP(-$AL4)-1)))
```

Dependențe: $A4, $AM4, $AN4, 'Setari model'!$B$33, $AL4.

**BV4** — 100 apariții; prima BV4, ultima BV103; lista completă în manifest.

```excel
=IF($A4="","",MIN(0.45,MAX(0.005,(1-'Setari model'!$B$34*MIN(1,($I4+$P4)/20))*MIN(0.45,$BT4*$BU4)+'Setari model'!$B$34*MIN(1,($I4+$P4)/20)*IF(COUNT($N4,$U4)=2,SQRT(MAX(0,1-$N4)*MAX(0,1-$U4)),IF($AM4="",EXP(-$AL4),$AM4)))))
```

Dependențe: $A4, 'Setari model'!$B$34, $I4, $P4, $BT4, $BU4, $N4, $U4, $AM4, $AL4.

**BW4** — 100 apariții; prima BW4, ultima BW103; lista completă în manifest.

```excel
=IF($A4="","",1-$BV4)
```

Dependențe: $A4, $BV4.

**BX4** — 100 apariții; prima BX4, ultima BX103; lista completă în manifest.

```excel
=IF($A4="","",1/$BW4)
```

Dependențe: $A4, $BW4.

**BY4** — 100 apariții; prima BY4, ultima BY103; lista completă în manifest.

```excel
=IF($A4="","",$BO4)
```

Dependențe: $A4, $BO4.

**BZ4** — 100 apariții; prima BZ4, ultima BZ103; lista completă în manifest.

```excel
=IF($A4="","",$BW4-$BY4)
```

Dependențe: $A4, $BW4, $BY4.

**CA4** — 100 apariții; prima CA4, ultima CA103; lista completă în manifest.

```excel
=IF($A4="","",IF($AR4>1,$BW4*$AR4-1,""))
```

Dependențe: $A4, $AR4, $BW4.

**CB4** — 100 apariții; prima CB4, ultima CB103; lista completă în manifest.

```excel
=IF($A4="","",MIN(1,COUNT($I4:$AN4,$AR4:$BG4)/'Setari model'!$B$46))
```

Dependențe: $A4, $I4:$AN4, $AR4:$BG4, 'Setari model'!$B$46.

**CC4** — 100 apariții; prima CC4, ultima CC103; lista completă în manifest.

```excel
=IF($A4="","",0.25*MIN(1,$I4/10)+0.25*MIN(1,$P4/10)+0.15*MIN(1,$W4/5)+0.15*MIN(1,$AB4/5)+0.1*MIN(1,$AG4/5)+0.1*MIN(1,$AN4/100))
```

Dependențe: $A4, $I4, $P4, $W4, $AB4, $AG4, $AN4.

**CD4** — 100 apariții; prima CD4, ultima CD103; lista completă în manifest.

```excel
=IF($A4="","",MAX(0,1-(MAX($BJ4:$BN4,$BP4)-MIN($BJ4:$BN4,$BP4))/(AVERAGE($BJ4:$BN4,$BP4)*'Setari model'!$B$45)))
```

Dependențe: $A4, $BJ4:$BN4, $BP4, 'Setari model'!$B$45.

**CE4** — 100 apariții; prima CE4, ultima CE103; lista completă în manifest.

```excel
=IF($A4="","",MAX(0,MIN(100,100*INDEX('Setari model'!$I$5:$I$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))*('Setari model'!$B$47*$CB4+'Setari model'!$B$48*$CC4+'Setari model'!$B$49*$CD4+'Setari model'!$B$50*$AT4/5+'Setari model'!$B$51*$AU4)-100*'Setari model'!$B$52*$BG4)))
```

Dependențe: $A4, 'Setari model'!$I$5:$I$11, $E4, 'Setari model'!$A$5:$A$11, 'Setari model'!$B$47, $CB4, 'Setari model'!$B$48, $CC4, 'Setari model'!$B$49, $CD4, 'Setari model'!$B$50, $AT4, 'Setari model'!$B$51, $AU4, 'Setari model'!$B$52, $BG4.

**CF4** — 100 apariții; prima CF4, ultima CF103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR($AT4<3,$BG4>=2,$CB4<0.55,$CC4<0.4),"RIDICAT",IF(OR($AU4=0,$CD4<0.45,$BR4<0.9),"MEDIU","SCĂZUT")))
```

Dependențe: $A4, $AT4, $BG4, $CB4, $CC4, $AU4, $CD4, $BR4.

**CG4** — 100 apariții; prima CG4, ultima CG103; lista completă în manifest.

```excel
=IF($A4="","",IF($AR4>1,IF(AND($BW4>= 'Setari model'!$B$35,$CE4>=100*'Setari model'!$B$36,$BZ4>= 'Setari model'!$B$37,$CA4>= 'Setari model'!$B$38,$CF4<>"RIDICAT"),"PARIU RECOMANDAT",IF(AND($BW4>= 'Setari model'!$B$39,$CE4>=100*'Setari model'!$B$40,$BZ4>= 'Setari model'!$B$41,$CA4>=0,$CF4<>"RIDICAT"),"RECOMANDAT CU PRUDENȚĂ",IF(AND($BW4>= 'Setari model'!$B$42,$CE4>=100*'Setari model'!$B$43),"ANALIZĂ NECONCLUDENTĂ","PARIU EVITAT"))),IF(AND($BW4>= 'Setari model'!$B$35,$CE4>=100*'Setari model'!$B$36,$CF4<>"RIDICAT"),"FAVORABIL STATISTIC – VERIFICĂ COTA",IF(AND($BW4>= 'Setari model'!$B$42,$CE4>=100*'Setari model'!$B$43),"ANALIZĂ NECONCLUDENTĂ","PARIU EVITAT"))))
```

Dependențe: $A4, $AR4, $BW4, 'Setari model'!$B$35, $CE4, 'Setari model'!$B$36, $BZ4, 'Setari model'!$B$37, $CA4, 'Setari model'!$B$38, $CF4, 'Setari model'!$B$39, 'Setari model'!$B$40, 'Setari model'!$B$41, 'Setari model'!$B$42, 'Setari model'!$B$43.

**CH4** — 100 apariții; prima CH4, ultima CH103; lista completă în manifest.

```excel
=IF($A4="","","P(O0,5)="&TEXT($BW4,"0.0%")&"; λ ajustat="&TEXT($BS4,"0.00")&"; Confidence="&TEXT($CE4,"0")&"/100; Edge="&TEXT($BZ4,"0.0%")&"; risc="&$CF4&". "&$BH4)
```

Dependențe: $A4, $BW4, $BS4, $CE4, $BZ4, $CF4, $BH4.

**CI4** — 100 apariții; prima CI4, ultima CI103; lista completă în manifest.

```excel
=IF($A4="","",$BI4)
```

Dependențe: $A4, $BI4.

**DW4** — 100 apariții; prima DW4, ultima DW103; lista completă în manifest.

```excel
=IF($A4="","",MAX('Setari model'!$B$71,MIN('Setari model'!$B$72,1+0.08*(IFERROR(AVERAGE($CM4:$CN4)/'Setari model'!$B$66,1)-1)+0.08*(IFERROR(AVERAGE($CO4:$CP4)/'Setari model'!$B$67,1)-1)+0.06*(IFERROR(AVERAGE($CQ4:$CR4)/'Setari model'!$B$68,1)-1)+0.04*(IFERROR(AVERAGE($CS4:$CT4)/'Setari model'!$B$69,1)-1)+0.04*(IFERROR(AVERAGE($CU4:$CV4)/'Setari model'!$B$70,1)-1)-'Setari model'!$B$73*IFERROR(AVERAGE($CW4:$CX4),0))))
```

Dependențe: $A4, 'Setari model'!$B$71, 'Setari model'!$B$72, $CM4:$CN4, 'Setari model'!$B$66, $CO4:$CP4, 'Setari model'!$B$67, $CQ4:$CR4, 'Setari model'!$B$68, $CS4:$CT4, 'Setari model'!$B$69, $CU4:$CV4, 'Setari model'!$B$70, 'Setari model'!$B$73, $CW4:$CX4.

**DX4** — 100 apariții; prima DX4, ultima DX103; lista completă în manifest.

```excel
=IF($A4="","",1+'Setari model'!$B$62*MAX(IF(OR($CK4=1,$CL4=1),1,0),IF(AND($CJ4<>"",$CJ4<=1),1,0))+'Setari model'!$B$63*IF(AND($CJ4>1,$CJ4<=3),1,0))
```

Dependențe: $A4, 'Setari model'!$B$62, $CK4, $CL4, $CJ4, 'Setari model'!$B$63.

**DY4** — 100 apariții; prima DY4, ultima DY103; lista completă în manifest.

```excel
=IF($A4="","",1+'Setari model'!$B$74*(IF($CY4="",0,IF($CY4=0,1,0))+IF($CZ4="",0,IF($CZ4=0,1,0)))+'Setari model'!$B$75*(IF($DA4="",0,IF($DA4=0,1,0))+IF($DB4="",0,IF($DB4=0,1,0))))
```

Dependențe: $A4, 'Setari model'!$B$74, $CY4, $CZ4, 'Setari model'!$B$75, $DA4, $DB4.

**DZ4** — 100 apariții; prima DZ4, ultima DZ103; lista completă în manifest.

```excel
=IF($A4="","",MIN(0.6,MAX(0.002,(((1-'Setari model'!$B$34*MIN(1,($I4+$P4)/20))*$BT4+'Setari model'!$B$34*MIN(1,($I4+$P4)/20)*IF(COUNT($N4,$U4)=2,SQRT(MAX(0,1-$N4)*MAX(0,1-$U4)),$BT4))*(1-'Setari model'!$B$65*MIN(1,IF($AN4="",0,$AN4/'Setari model'!$B$64)))+'Setari model'!$B$65*MIN(1,IF($AN4="",0,$AN4/'Setari model'!$B$64))*IF($AM4="",$BT4,$AM4))*$DX4*$DY4/$DW4)))
```

Dependențe: $A4, 'Setari model'!$B$34, $I4, $P4, $BT4, $N4, $U4, 'Setari model'!$B$65, $AN4, 'Setari model'!$B$64, $AM4, $DX4, $DY4, $DW4.

**EA4** — 100 apariții; prima EA4, ultima EA103; lista completă în manifest.

```excel
=IF($A4="","",MIN(1-$DZ4,IF(OR(MIN($I4,$P4)<'Setari model'!$B$58,$CK4=1,$CL4=1,AND($CJ4<>"",$CJ4<=1)),'Setari model'!$B$59,IF(AND($AU4=1,$AR4>1,COUNT($CY4:$DB4)=4),'Setari model'!$B$61,'Setari model'!$B$60))))
```

Dependențe: $A4, $DZ4, $I4, $P4, 'Setari model'!$B$58, $CK4, $CL4, $CJ4, 'Setari model'!$B$59, $AU4, $AR4, $CY4:$DB4, 'Setari model'!$B$61, 'Setari model'!$B$60.

**EB4** — 100 apariții; prima EB4, ultima EB103; lista completă în manifest.

```excel
=IF($A4="","",1/$EA4)
```

Dependențe: $A4, $EA4.

**EC4** — 100 apariții; prima EC4, ultima EC103; lista completă în manifest.

```excel
=IF($A4="","",IF($AR4>1,IF($AS4>1,(1/$AR4)/((1/$AR4)+(1/$AS4)),1/$AR4),""))
```

Dependențe: $A4, $AR4, $AS4.

**ED4** — 100 apariții; prima ED4, ultima ED103; lista completă în manifest.

```excel
=IF($A4="","",IF($EC4="","",$EA4-$EC4))
```

Dependențe: $A4, $EC4, $EA4.

**EE4** — 200 apariții; prima EE4, ultima EK103; lista completă în manifest.

```excel
=""
```

Dependențe: niciuna; formulă constantă.

**EF4** — 100 apariții; prima EF4, ultima EF103; lista completă în manifest.

```excel
=IF($A4="","",MAX(0,MIN(100,$CE4-200*MAX(0,$EG4-'Setari model'!$B$77)-IF($AU4<>1,10,0)-IF(COUNT($CY4:$DB4)<4,4,0))))
```

Dependențe: $A4, $CE4, $EG4, 'Setari model'!$B$77, $AU4, $CY4:$DB4.

**EG4** — 100 apariții; prima EG4, ultima EG103; lista completă în manifest.

```excel
=IF($A4="","",'Setari model'!$B$77+IF(MIN($I4,$P4)<'Setari model'!$B$58,0.03,0)+IF(OR($CK4=1,$CL4=1,AND($CJ4<>"",$CJ4<=1)),0.03,0)+IF($AG4=0,0.02,0)+0.03*(1-MIN(1,COUNT($CM4:$CV4)/10))+0.03*(1-MIN(1,IF($AN4="",0,$AN4/'Setari model'!$B$64)))+IF($AR4<=1,0.02,0))
```

Dependențe: $A4, 'Setari model'!$B$77, $I4, $P4, 'Setari model'!$B$58, $CK4, $CL4, $CJ4, $AG4, $CM4:$CV4, $AN4, 'Setari model'!$B$64, $AR4.

**EH4** — 100 apariții; prima EH4, ultima EH103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR(MIN($I4,$P4)<'Setari model'!$B$58,$CK4=1,$CL4=1,AND($CJ4<>"",$CJ4<=1)),"92% – early/regim",IF(AND($AU4=1,$AR4>1,COUNT($CY4:$DB4)=4),"94% – confirmat","93% – standard")))
```

Dependențe: $A4, $I4, $P4, 'Setari model'!$B$58, $CK4, $CL4, $CJ4, $AU4, $AR4, $CY4:$DB4.

**EI4** — 100 apariții; prima EI4, ultima EI103; lista completă în manifest.

```excel
=IF($A4="","",IF(AND($EA4>0.9,$AU4<>1),"WAIT XI – HIGH P",IF(AND($EA4>0.9,COUNT($CY4:$DB4)<4),"WAIT DATE CHEIE – HIGH P",IF($EP4<>"DA","NU – PORTOFOLIU","DA"))))
```

Dependențe: $A4, $EA4, $AU4, $CY4:$DB4, $EP4.

**EJ4** — 100 apariții; prima EJ4, ultima EJ103; lista completă în manifest.

```excel
=IF($A4="","",IF($DE4<>"Live 20-30","",IF(SUM($DG4:$DH4)>0,1,IF($EU4="","",1-MIN(0.95,MAX(0.001,EXP(-$EU4)*$DX4*$DY4/$DW4))))))
```

Dependențe: $A4, $DE4, $DG4:$DH4, $EU4, $DX4, $DY4, $DW4.

**EL4** — 100 apariții; prima EL4, ultima EL103; lista completă în manifest.

```excel
=IF($A4="","",IF($DE4="Live 20-30",IF(SUM($DG4:$DH4)>0,"EVENIMENT ÎNDEPLINIT",IF(OR($DF4="",COUNT($DI4:$DN4)<4),"LIVE – WATCH",IF($EJ4>=0.75,"LIVE – FEZABIL TEHNIC","LIVE – NO BET"))),IF($EI4<>"DA","WATCH / NO BET",IF(AND($EA4>=INDEX('Setari model'!$B$35:$B$40,1),$EF4>=100*'Setari model'!$B$76),"PARIU RECOMANDAT",IF(AND($EA4>=INDEX('Setari model'!$B$35:$B$40,5),$EF4>=100*'Setari model'!$B$40),"WATCH – APROAPE DE PRAG","PARIU EVITAT")))))
```

Dependențe: $A4, $DE4, $DG4:$DH4, $DF4, $DI4:$DN4, $EJ4, $EI4, $EA4, 'Setari model'!$B$35:$B$40, $EF4, 'Setari model'!$B$76, 'Setari model'!$B$40.

**EM4** — 100 apariții; prima EM4, ultima EM103; lista completă în manifest.

```excel
=IF($A4="","",IF($DE4="Live 20-30",IF(SUM($DG4:$DH4)>0,"Gol deja marcat.",IF($DF4="","Minut live lipsă.",IF(COUNT($DI4:$DN4)<4,"Lipsesc xG/SOT/big chances live.",IF($EJ4<0.75,"P live sub prag.","Semnal live tehnic complet; EV ignorat.")))),IF($EI4<>"DA",$EI4,IF($EF4<75,"Confidence sub 75.",IF($EA4<0.92,"P sub 92%.","G0/Zero-Mass + confidence trecute; EV ignorat.")))))
```

Dependențe: $A4, $DE4, $DG4:$DH4, $DF4, $DI4:$DN4, $EJ4, $EI4, $EF4, $EA4.

**EN4** — 100 apariții; prima EN4, ultima EN103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR($EL4="PARIU RECOMANDAT",$EL4="LIVE – FEZABIL"),MIN(IF($DU4>0,$DU4,'Setari model'!$B$81)/MAX(1,$DR4),IF($DV4>0,$DV4,'Setari model'!$B$80)*MAX(0,((IF($DE4="Live 20-30",$EJ4,$EA4)*IF($DE4="Live 20-30",$DQ4,$AR4)-1)/(IF($DE4="Live 20-30",$DQ4,$AR4)-1)))),0))
```

Dependențe: $A4, $EL4, $DU4, 'Setari model'!$B$81, $DR4, $DV4, 'Setari model'!$B$80, $DE4, $EJ4, $EA4, $DQ4, $AR4.

**EO4** — 100 apariții; prima EO4, ultima EO103; lista completă în manifest.

```excel
=IF($A4="","",IF(AND($EN4>0,$DT4>0),$EN4*$DT4,""))
```

Dependențe: $A4, $EN4, $DT4.

**EP4** — 100 apariții; prima EP4, ultima EP103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR($DR4<1,$DR4>'Setari model'!$B$78),"NU – 1–5 selecții",IF($DS4>'Setari model'!$B$79,"NU – corelație", "DA")))
```

Dependențe: $A4, $DR4, 'Setari model'!$B$78, $DS4, 'Setari model'!$B$79.

**EQ4** — 100 apariții; prima EQ4, ultima EQ103; lista completă în manifest.

```excel
=IF($A4="","",IF(AND($DC4>1,$DD4>1),$DC4/$DD4-1,""))
```

Dependențe: $A4, $DC4, $DD4.

**ER4** — 100 apariții; prima ER4, ultima ER103; lista completă în manifest.

```excel
=IF($A4="","","P v2="&TEXT($EA4,"0.0%")&" ±"&TEXT($EG4,"0.0%")&"; P0 ZIP="&TEXT($DZ4,"0.0%")&"; Confidence="&TEXT($EF4,"0")&"/100; piață reală="&IF($EC4="","NU","DA")&"; EV="&IF($EE4="","n/a",TEXT($EE4,"0.0%"))&"; gate="&$EI4&"; verdict="&$EL4&". "&$EM4)
```

Dependențe: $A4, $EA4, $EG4, $DZ4, $EF4, $EC4, $EE4, $EI4, $EL4, $EM4.

**ES4** — 100 apariții; prima ES4, ultima ES103; lista completă în manifest.

```excel
=IF($A4="","",'Setari model'!$B$82)
```

Dependențe: $A4, 'Setari model'!$B$82.

**ET4** — 100 apariții; prima ET4, ultima ET103; lista completă în manifest.

```excel
=IF($A4="","",'Setari model'!$B$83)
```

Dependențe: $A4, 'Setari model'!$B$83.

**EU4** — 100 apariții; prima EU4, ultima EU103; lista completă în manifest.

```excel
=IF(OR($A4="",$DE4<>"Live 20-30",$DF4="",$DF4<$ES4,$DF4>=90),"",MAX(0.05,MIN($BS4*$ET4,$BS4*(90-$DF4)/90+0.35*($DI4+$DJ4)+0.06*($DK4+$DL4)+0.15*($DM4+$DN4)+0.1*(MAX($DO4,$DP4)-MIN($DO4,$DP4)))))
```

Dependențe: $A4, $DE4, $DF4, $ES4, $BS4, $ET4, $DI4, $DJ4, $DK4, $DL4, $DM4, $DN4, $DO4, $DP4.

**FC4** — 100 apariții; prima FC4, ultima FC103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR($J4="",$L4="",$L4<=0),"",MAX(0.5,MIN(1.5,$J4/$L4))))
```

Dependențe: $A4, $J4, $L4.

**FD4** — 100 apariții; prima FD4, ultima FD103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR($Q4="",$S4="",$S4<=0),"",MAX(0.5,MIN(1.5,$Q4/$S4))))
```

Dependențe: $A4, $Q4, $S4.

**FE4** — 100 apariții; prima FE4, ultima FE103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($EV4:$EW4)<2,"",SQRT($EV4*$EW4)/'Setari model'!$B$87))
```

Dependențe: $A4, $EV4:$EW4, $EV4, $EW4, 'Setari model'!$B$87.

**FF4** — 100 apariții; prima FF4, ultima FF103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($O4,$V4,$EX4,$EY4)<4,"",AVERAGE(SQRT($O4*$EY4),SQRT($V4*$EX4))/'Setari model'!$B$88))
```

Dependențe: $A4, $O4, $V4, $EX4, $EY4, 'Setari model'!$B$88.

**FG4** — 100 apariții; prima FG4, ultima FG103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($FC4:$FD4)<2,"",MAX(0,1-AVERAGE($FC4:$FD4))))
```

Dependențe: $A4, $FC4:$FD4.

**FH4** — 100 apariții; prima FH4, ultima FH103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($EZ4:$FA4)<2,"",'Setari model'!$B$94*AVERAGE($EZ4:$FA4)/'Setari model'!$B$89))
```

Dependențe: $A4, $EZ4:$FA4, 'Setari model'!$B$94, 'Setari model'!$B$89.

**FI4** — 100 apariții; prima FI4, ultima FI103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($FE4:$FH4)<4,"",MAX('Setari model'!$B$97,MIN('Setari model'!$B$98,1+'Setari model'!$B$90*($FE4-1)+'Setari model'!$B$91*($FF4-1)+'Setari model'!$B$92*$FG4+'Setari model'!$B$93*($FH4-1)))))
```

Dependențe: $A4, $FE4:$FH4, 'Setari model'!$B$97, 'Setari model'!$B$98, 'Setari model'!$B$90, $FE4, 'Setari model'!$B$91, $FF4, 'Setari model'!$B$92, $FG4, 'Setari model'!$B$93, $FH4.

**FJ4** — 100 apariții; prima FJ4, ultima FJ103; lista completă în manifest.

```excel
=IF($A4="","",IF($FI4="","",MIN('Setari model'!$B$101,MAX(0.002,$DZ4*$FI4))))
```

Dependențe: $A4, $FI4, 'Setari model'!$B$101, $DZ4.

**FK4** — 100 apariții; prima FK4, ultima FK103; lista completă în manifest.

```excel
=IF($A4="","",IF(AND(COUNT($EV4:$FA4)=6,COUNT($O4,$V4,$FC4,$FD4)=4),"DA","NU"))
```

Dependențe: $A4, $EV4:$FA4, $O4, $V4, $FC4, $FD4.

**FL4** — 100 apariții; prima FL4, ultima FL103; lista completă în manifest.

```excel
=IF($A4="","",IF($FK4<>"DA","NEDETERMINAT",IF($FI4<='Setari model'!$B$99,"SCĂZUT",IF($FI4<='Setari model'!$B$100,"MEDIU","RIDICAT"))))
```

Dependențe: $A4, $FK4, $FI4, 'Setari model'!$B$99, 'Setari model'!$B$100.

**FM4** — 100 apariții; prima FM4, ultima FM103; lista completă în manifest.

```excel
=IF($A4="","",IF(AND($AR4>1,$EC4>='Setari model'!$B$106),"DA","NU"))
```

Dependențe: $A4, $AR4, $EC4, 'Setari model'!$B$106.

**FN4** — 100 apariții; prima FN4, ultima FN103; lista completă în manifest.

```excel
=IF($A4="","",IF(AND($AU4=1,COUNT($CY4:$DB4)=4),"DA","NU"))
```

Dependențe: $A4, $AU4, $CY4:$DB4.

**FO4** — 100 apariții; prima FO4, ultima FO103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR($FK4<>"DA",$FL4="RIDICAT"),'Setari model'!$B$102,IF($FL4="MEDIU",'Setari model'!$B$103,IF(AND($FM4="DA",$FN4="DA"),'Setari model'!$B$105,'Setari model'!$B$104))))
```

Dependențe: $A4, $FK4, $FL4, 'Setari model'!$B$102, 'Setari model'!$B$103, $FM4, $FN4, 'Setari model'!$B$105, 'Setari model'!$B$104.

**FP4** — 100 apariții; prima FP4, ultima FP103; lista completă în manifest.

```excel
=IF($A4="","",IF($FJ4="","",MIN(1-$FJ4,$FO4)))
```

Dependențe: $A4, $FJ4, $FO4.

**FQ4** — 100 apariții; prima FQ4, ultima FQ103; lista completă în manifest.

```excel
=IF($A4="","",IF($FP4="","",IF($FP4>0,1/$FP4,"")))
```

Dependențe: $A4, $FP4.

**FR4** — 100 apariții; prima FR4, ultima FR103; lista completă în manifest.

```excel
=IF($A4="","",IF($EC4="","",$FP4-$EC4))
```

Dependențe: $A4, $EC4, $FP4.

**FS4** — 100 apariții; prima FS4, ultima FS103; lista completă în manifest.

```excel
=IF($A4="","",IF($AR4>1,$FP4*$AR4-1,""))
```

Dependențe: $A4, $AR4, $FP4.

**FT4** — 100 apariții; prima FT4, ultima FT103; lista completă în manifest.

```excel
=IF($A4="","",MAX(0,MIN(100,$EF4-IF($FK4<>"DA",'Setari model'!$B$107,0)-IF($FL4="MEDIU",'Setari model'!$B$108,0)-IF($FL4="RIDICAT",'Setari model'!$B$109,0))))
```

Dependențe: $A4, $EF4, $FK4, 'Setari model'!$B$107, $FL4, 'Setari model'!$B$108, 'Setari model'!$B$109.

**FU4** — 100 apariții; prima FU4, ultima FU103; lista completă în manifest.

```excel
=IF($A4="","",IF($AR4<=1,"NU – LIPSEȘTE COTA REALĂ",IF($FK4<>"DA","NU – ZERO-RISK INCOMPLET",IF($FL4<>"SCĂZUT","NU – RISC 0-0 "&$FL4,IF($FN4<>"DA","NU – LINEUP NECONFIRMAT",IF($FM4<>"DA","NU – PIAȚĂ NECONFIRMATĂ",IF($EP4<>"DA","NU – PORTOFOLIU","DA")))))))
```

Dependențe: $A4, $AR4, $FK4, $FL4, $FN4, $FM4, $EP4.

**FV4** — 100 apariții; prima FV4, ultima FV103; lista completă în manifest.

```excel
=IF($A4="","",IF($FU4<>"DA","WATCH / NO BET",IF(AND($FP4>='Setari model'!$B$35,$FT4>=100*'Setari model'!$B$76,$FS4>0),"PARIU RECOMANDAT",IF(AND($FP4>='Setari model'!$B$39,$FT4>=100*'Setari model'!$B$40,$FS4>0),"WATCH – APROAPE DE PRAG","PARIU EVITAT"))))
```

Dependențe: $A4, $FU4, $FP4, 'Setari model'!$B$35, $FT4, 'Setari model'!$B$76, $FS4, 'Setari model'!$B$39, 'Setari model'!$B$40.

**FW4** — 100 apariții; prima FW4, ultima FW103; lista completă în manifest.

```excel
=IF($A4="","",IF($FU4<>"DA",$FU4,IF($FT4<75,"Confidence v3 sub 75.",IF($FP4<0.92,"P v3 sub 92%.",IF($FS4<=0,"EV v3 nepozitiv.","P0 v3, lineup și piață confirmate.")))))
```

Dependențe: $A4, $FU4, $FT4, $FP4, $FS4.

**FX4** — 100 apariții; prima FX4, ultima FX103; lista completă în manifest.

```excel
=IF($A4="","","P v3="&TEXT($FP4,"0.0%")&"; P0 v3="&TEXT($FJ4,"0.0%")&"; factor zero="&IF($FI4="","n/a",TEXT($FI4,"0.00x"))&" ("&$FL4&"); cap="&TEXT($FO4,"0.0%")&"; Confidence="&TEXT($FT4,"0")&"/100; lineup="&$FN4&"; piață="&$FM4&"; EV="&IF($FS4="","n/a",TEXT($FS4,"0.0%"))&"; gate="&$FU4&"; verdict="&$FV4&". "&$FW4)
```

Dependențe: $A4, $FP4, $FJ4, $FI4, $FL4, $FO4, $FT4, $FN4, $FM4, $FS4, $FU4, $FV4, $FW4.

**GC4** — 100 apariții; prima GC4, ultima GC103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR($X4="",$Z4="",$Z4<=0),"",MAX(0.5,MIN(1.5,$X4/$Z4))))
```

Dependențe: $A4, $X4, $Z4.

**GD4** — 100 apariții; prima GD4, ultima GD103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR($AC4="",$AE4="",$AE4<=0),"",MAX(0.5,MIN(1.5,$AC4/$AE4))))
```

Dependențe: $A4, $AC4, $AE4.

**GE4** — 100 apariții; prima GE4, ultima GE103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($Z4,$AE4)<2,"",AVERAGE($Z4,$AE4)))
```

Dependențe: $A4, $Z4, $AE4.

**GF4** — 100 apariții; prima GF4, ultima GF103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($FY4:$FZ4)<2,"NEDETERMINAT",IF(AND($FY4>='Setari model'!$B$113,$FZ4>='Setari model'!$B$113),"DA","NU")))
```

Dependențe: $A4, $FY4:$FZ4, $FY4, 'Setari model'!$B$113, $FZ4.

**GG4** — 100 apariții; prima GG4, ultima GG103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($FY4:$FZ4,$EX4:$EY4)<4,"NEDETERMINAT",IF(OR(AND($FY4>='Setari model'!$B$113,$EY4>='Setari model'!$B$114),AND($FZ4>='Setari model'!$B$113,$EX4>='Setari model'!$B$114)),"DA","NU")))
```

Dependențe: $A4, $FY4:$FZ4, $EX4:$EY4, $FY4, 'Setari model'!$B$113, $EY4, 'Setari model'!$B$114, $FZ4, $EX4.

**GH4** — 100 apariții; prima GH4, ultima GH103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($BJ4:$BN4,$GC4:$GE4)<8,"NEDETERMINAT",IF(AND((($BJ4*INDEX('Setari model'!$B$5:$B$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BK4*INDEX('Setari model'!$C$5:$C$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BL4*INDEX('Setari model'!$D$5:$D$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BM4*INDEX('Setari model'!$E$5:$E$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BN4*INDEX('Setari model'!$F$5:$F$11,MATCH($E4,'Setari model'!$A$5:$A$11,0)))/(INDEX('Setari model'!$B$5:$B$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+INDEX('Setari model'!$C$5:$C$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+INDEX('Setari model'!$D$5:$D$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+INDEX('Setari model'!$E$5:$E$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+INDEX('Setari model'!$F$5:$F$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))))*$BR4>='Setari model'!$B$115,(($BJ4*INDEX('Setari model'!$B$5:$B$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BK4*INDEX('Setari model'!$C$5:$C$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BL4*INDEX('Setari model'!$D$5:$D$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BM4*INDEX('Setari model'!$E$5:$E$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+$BN4*INDEX('Setari model'!$F$5:$F$11,MATCH($E4,'Setari model'!$A$5:$A$11,0)))/(INDEX('Setari model'!$B$5:$B$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+INDEX('Setari model'!$C$5:$C$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+INDEX('Setari model'!$D$5:$D$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+INDEX('Setari model'!$E$5:$E$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))+INDEX('Setari model'!$F$5:$F$11,MATCH($E4,'Setari model'!$A$5:$A$11,0))))*$BR4<='Setari model'!$B$116,AVERAGE($GC4:$GD4)<='Setari model'!$B$117,$GE4>='Setari model'!$B$118),"DA","NU")))
```

Dependențe: $A4, $BJ4:$BN4, $GC4:$GE4, $BJ4, 'Setari model'!$B$5:$B$11, $E4, 'Setari model'!$A$5:$A$11, $BK4, 'Setari model'!$C$5:$C$11, $BL4, 'Setari model'!$D$5:$D$11, $BM4, 'Setari model'!$E$5:$E$11, $BN4, 'Setari model'!$F$5:$F$11, $BR4, 'Setari model'!$B$115, 'Setari model'!$B$116, $GC4:$GD4, 'Setari model'!$B$117, $GE4, 'Setari model'!$B$118.

**GI4** — 100 apariții; prima GI4, ultima GI103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($W4,$AB4,$GA4:$GB4)<4,"NEDETERMINAT",IF(AND($W4>='Setari model'!$B$120,$AB4>='Setari model'!$B$120,OR(IFERROR($GA4/$W4,0)>='Setari model'!$B$119,IFERROR($GB4/$AB4,0)>='Setari model'!$B$119)),"DA","NU")))
```

Dependențe: $A4, $W4, $AB4, $GA4:$GB4, 'Setari model'!$B$120, $GA4, 'Setari model'!$B$119, $GB4.

**GJ4** — 100 apariții; prima GJ4, ultima GJ103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($FY4:$GB4)<4,"",IF($GH4<>"DA",0,'Setari model'!$B$121*IF($GF4="DA",1,0)+'Setari model'!$B$122*IF($GG4="DA",1,0)+'Setari model'!$B$123+'Setari model'!$B$124*IF($GI4="DA",1,0))))
```

Dependențe: $A4, $FY4:$GB4, $GH4, 'Setari model'!$B$121, $GF4, 'Setari model'!$B$122, $GG4, 'Setari model'!$B$123, 'Setari model'!$B$124, $GI4.

**GK4** — 100 apariții; prima GK4, ultima GK103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($GJ4)=0,"",1+'Setari model'!$B$125*$GJ4))
```

Dependențe: $A4, $GJ4, 'Setari model'!$B$125.

**GL4** — 100 apariții; prima GL4, ultima GL103; lista completă în manifest.

```excel
=IF($A4="","",IF($GM4<>"DA",$FJ4,MIN('Setari model'!$B$101,MAX(0.002,$FJ4*$GK4))))
```

Dependențe: $A4, $GM4, $FJ4, 'Setari model'!$B$101, $GK4.

**GM4** — 100 apariții; prima GM4, ultima GM103; lista completă în manifest.

```excel
=IF($A4="","",IF(AND($FK4="DA",COUNT($FY4:$GB4)=4,COUNT($I4,$P4,$W4,$AB4,$Z4,$AE4,$EX4,$EY4,$GC4,$GD4)=10,COUNT($BJ4:$BN4)=5),"DA","NU"))
```

Dependențe: $A4, $FK4, $FY4:$GB4, $I4, $P4, $W4, $AB4, $Z4, $AE4, $EX4, $EY4, $GC4, $GD4, $BJ4:$BN4.

**GN4** — 100 apariții; prima GN4, ultima GN103; lista completă în manifest.

```excel
=IF($A4="","",IF($GM4<>"DA","NEDETERMINAT",IF($FI4*$GK4<='Setari model'!$B$99,"SCĂZUT",IF($FI4*$GK4<='Setari model'!$B$100,"MEDIU","RIDICAT"))))
```

Dependențe: $A4, $GM4, $FI4, $GK4, 'Setari model'!$B$99, 'Setari model'!$B$100.

**GO4** — 100 apariții; prima GO4, ultima GO103; lista completă în manifest.

```excel
=IF($A4="","",IF(OR($GM4<>"DA",$GN4="RIDICAT"),'Setari model'!$B$102,IF($GN4="MEDIU",'Setari model'!$B$103,IF(AND($FM4="DA",$FN4="DA"),'Setari model'!$B$105,'Setari model'!$B$104))))
```

Dependențe: $A4, $GM4, $GN4, 'Setari model'!$B$102, 'Setari model'!$B$103, $FM4, $FN4, 'Setari model'!$B$105, 'Setari model'!$B$104.

**GP4** — 100 apariții; prima GP4, ultima GP103; lista completă în manifest.

```excel
=IF($A4="","",IF($GL4="","",MIN(1-$GL4,$GO4)))
```

Dependențe: $A4, $GL4, $GO4.

**GQ4** — 100 apariții; prima GQ4, ultima GQ103; lista completă în manifest.

```excel
=IF($A4="","",IF($GP4="","",IF($GP4>0,1/$GP4,"")))
```

Dependențe: $A4, $GP4.

**GR4** — 100 apariții; prima GR4, ultima GR103; lista completă în manifest.

```excel
=IF($A4="","",IF($EC4="","",$GP4-$EC4))
```

Dependențe: $A4, $EC4, $GP4.

**GS4** — 100 apariții; prima GS4, ultima GS103; lista completă în manifest.

```excel
=IF($A4="","",IF($AR4>1,$GP4*$AR4-1,""))
```

Dependențe: $A4, $AR4, $GP4.

**GT4** — 100 apariții; prima GT4, ultima GT103; lista completă în manifest.

```excel
=IF($A4="","",MAX(0,MIN(100,$FT4-IF(AND($GM4<>"DA",$FK4="DA"),'Setari model'!$B$107,0)-'Setari model'!$B$126*IF($GJ4="",0,$GJ4))))
```

Dependențe: $A4, $FT4, $GM4, $FK4, 'Setari model'!$B$107, 'Setari model'!$B$126, $GJ4.

**GU4** — 100 apariții; prima GU4, ultima GU103; lista completă în manifest.

```excel
=IF($A4="","",IF($AR4<=1,"NU – LIPSEȘTE COTA REALĂ",IF($GM4<>"DA","NU – DATE LOW-CONVERSION INCOMPLETE",IF($GN4<>"SCĂZUT","NU – RISC 0-0 "&$GN4,IF($FN4<>"DA","NU – LINEUP NECONFIRMAT",IF($FM4<>"DA","NU – PIAȚĂ NECONFIRMATĂ",IF($EP4<>"DA","NU – PORTOFOLIU","DA")))))))
```

Dependențe: $A4, $AR4, $GM4, $GN4, $FN4, $FM4, $EP4.

**GV4** — 100 apariții; prima GV4, ultima GV103; lista completă în manifest.

```excel
=IF($A4="","",IF($GU4<>"DA","WATCH / NO BET",IF(AND($GP4>='Setari model'!$B$35,$GT4>=100*'Setari model'!$B$76,$GS4>0),"PARIU RECOMANDAT",IF(AND($GP4>='Setari model'!$B$39,$GT4>=100*'Setari model'!$B$40,$GS4>0),"WATCH – APROAPE DE PRAG","PARIU EVITAT"))))
```

Dependențe: $A4, $GU4, $GP4, 'Setari model'!$B$35, $GT4, 'Setari model'!$B$76, $GS4, 'Setari model'!$B$39, 'Setari model'!$B$40.

**GW4** — 100 apariții; prima GW4, ultima GW103; lista completă în manifest.

```excel
=IF($A4="","",IF($GU4<>"DA",$GU4,IF($GT4<75,"Confidence v5 sub 75.",IF($GP4<0.92,"P v5 sub 92%.",IF($GS4<=0,"EV v5 nepozitiv.",IF($GJ4>0,"Low-conversion absorbit în P0; toate porțile rămân trecute.","Toate porțile v5 sunt trecute."))))))
```

Dependențe: $A4, $GU4, $GT4, $GP4, $GS4, $GJ4.

**GX4** — 100 apariții; prima GX4, ultima GX103; lista completă în manifest.

```excel
=IF($A4="","","P v5="&TEXT($GP4,"0.0%")&"; P0 v5="&TEXT($GL4,"0.0%")&"; low-conv="&IF(COUNT($GJ4)=0,"n/a",TEXT($GJ4,"0%"))&"; mult.P0="&IF(COUNT($GK4)=0,"n/a",TEXT($GK4,"0.00"))&"; clasă="&$GN4&"; cap="&TEXT($GO4,"0.0%")&"; Confidence="&TEXT($GT4,"0")&"/100; lineup="&$FN4&"; piață="&$FM4&"; EV="&IF($GS4="","n/a",TEXT($GS4,"0.0%"))&"; gate="&$GU4&"; verdict="&$GV4&". "&$GW4)
```

Dependențe: $A4, $GP4, $GL4, $GJ4, $GK4, $GN4, $GO4, $GT4, $FN4, $FM4, $GS4, $GU4, $GV4, $GW4.

**GY4** — 100 apariții; prima GY4, ultima GY103; lista completă în manifest.

```excel
=IF($A4="","",IF($GM4<>"DA","SOURCING INCOMPLETE – REVIEW REQUIRED",IF(MIN($I4,$P4,$W4,$AB4)<'Setari model'!$B$58,"SMALL SAMPLE + PRIOR / SHRINKAGE","VERIFIED / PRIOR / SHRINKAGE")))
```

Dependențe: $A4, $GM4, $I4, $P4, $W4, $AB4, 'Setari model'!$B$58.

**GZ4** — 100 apariții; prima GZ4, ultima GZ103; lista completă în manifest.

```excel
=IF($A4="","",MAX(0,MIN(100,100*(1-AVERAGE(IF($GM4="DA",1,0),MIN(1,$AT4/5))))))
```

Dependențe: $A4, $GM4, $AT4.

**HA4** — 100 apariții; prima HA4, ultima HA103; lista completă în manifest.

```excel
=IF($A4="","",IF($GM4<>"DA","",MAX(0,MIN(100,100*(($FI4*$GK4)-'Setari model'!$B$97)/('Setari model'!$B$98-'Setari model'!$B$97)))))
```

Dependențe: $A4, $GM4, $FI4, $GK4, 'Setari model'!$B$97, 'Setari model'!$B$98.

**HB4** — 100 apariții; prima HB4, ultima HB103; lista completă în manifest.

```excel
=IF($A4="","",MAX(0,MIN(100,100*(ABS($BR4-1)/MAX(1-'Setari model'!$B$53,'Setari model'!$B$54-1)+MIN(1,$BG4/2))/2)))
```

Dependențe: $A4, $BR4, 'Setari model'!$B$53, 'Setari model'!$B$54, $BG4.

**HC4** — 100 apariții; prima HC4, ultima HC103; lista completă în manifest.

```excel
=IF($A4="","",MAX(0,MIN(100,100*(1-AVERAGE($CC4,MAX(0,1-(MAX($BJ4:$BN4)-MIN($BJ4:$BN4))/(AVERAGE($BJ4:$BN4)*'Setari model'!$B$45)))))))
```

Dependențe: $A4, $CC4, $BJ4:$BN4, 'Setari model'!$B$45.

**HD4** — 100 apariții; prima HD4, ultima HD103; lista completă în manifest.

```excel
=IF($A4="","",MAX(0,MIN(100,100*MAX(IF($GJ4="",0,$GJ4),MIN(1,$BG4/2)))))
```

Dependențe: $A4, $GJ4, $BG4.

**HE4** — 100 apariții; prima HE4, ultima HE103; lista completă în manifest.

```excel
=IF($A4="","",IF(COUNT($GZ4:$HD4)<5,"",$GZ4*Risk_Classification!$E$28+$HA4*Risk_Classification!$E$29+$HB4*Risk_Classification!$E$30+$HC4*Risk_Classification!$E$31+$HD4*Risk_Classification!$E$32))
```

Dependențe: $A4, $GZ4:$HD4, $GZ4, Risk_Classification!$E$28, $HA4, Risk_Classification!$E$29, $HB4, Risk_Classification!$E$30, $HC4, Risk_Classification!$E$31, $HD4, Risk_Classification!$E$32.

**HF4** — 100 apariții; prima HF4, ultima HF103; lista completă în manifest.

```excel
=IF($A4="","",IF($HE4="","",IF($HE4<=20,1,IF($HE4<=40,2,IF($HE4<=60,3,IF($HE4<=80,4,5))))))
```

Dependențe: $A4, $HE4.

**HG4** — 100 apariții; prima HG4, ultima HG103; lista completă în manifest.

```excel
=IF($A4="","",IF($GM4="DA","PASS","FAIL – DATE CRITICE ZERO-MASS INCOMPLETE"))
```

Dependențe: $A4, $GM4.

**HH4** — 100 apariții; prima HH4, ultima HH103; lista completă în manifest.

```excel
=IF($A4="","",IF($HG4<>"PASS",5,$HF4))
```

Dependențe: $A4, $HG4, $HF4.

**HI4** — 100 apariții; prima HI4, ultima HI103; lista completă în manifest.

```excel
=IF($A4="","",IF($HH4="","N/A",IF($HH4=1,"DEFENSIV",IF($HH4=2,"PRUDENT",IF($HH4=3,"MODERAT",IF($HH4=4,"RIDICAT","WATCH / NO BET"))))))
```

Dependențe: $A4, $HH4.

**HJ4** — 100 apariții; prima HJ4, ultima HJ103; lista completă în manifest.

```excel
=IF($A4="","","Data="&$GY4&"; DQ="&TEXT($GZ4,"0.0")&"; ZM="&IF($HA4="","n/a",TEXT($HA4,"0.0"))&"; Context="&TEXT($HB4,"0.0")&"; Uncertainty="&TEXT($HC4,"0.0")&"; Compound="&TEXT($HD4,"0.0")&"; Risk Score="&IF($HE4="","n/a",TEXT($HE4,"0.0"))&"; Base="&IF($HF4="","n/a",$HF4)&"; G0="&$HG4&"; Final="&$HH4&". Cota, EV si lineup sunt informative si nu intra in recomandare.")
```

Dependențe: $A4, $GY4, $GZ4, $HA4, $HB4, $HC4, $HD4, $HE4, $HF4, $HG4, $HH4.

**HK4** — 100 apariții; prima HK4, ultima HK103; lista completă în manifest.

```excel
=IF($A4="","",$HI4)
```

Dependențe: $A4, $HI4.

### Setari model

**J5** — 7 apariții; prima J5, ultima J11; lista completă în manifest.

```excel
=ROUND(SUM(B5:G5),6)
```

Dependențe: B5:G5.

### Backtest

**B4** — 200 apariții; prima B4, ultima B203; lista completă în manifest.

```excel
=IF($A4="","",IFERROR(INDEX('Analize meciuri'!$C$4:$C$103,MATCH($A4,'Analize meciuri'!$A$4:$A$103,0)),""))
```

Dependențe: $A4, 'Analize meciuri'!$C$4:$C$103, 'Analize meciuri'!$A$4:$A$103.

**C4** — 200 apariții; prima C4, ultima C203; lista completă în manifest.

```excel
=IF($A4="","",IFERROR(INDEX('Analize meciuri'!$G$4:$G$103,MATCH($A4,'Analize meciuri'!$A$4:$A$103,0)),""))
```

Dependențe: $A4, 'Analize meciuri'!$G$4:$G$103, 'Analize meciuri'!$A$4:$A$103.

**D4** — 200 apariții; prima D4, ultima D203; lista completă în manifest.

```excel
=IF($A4="","",IFERROR(INDEX('Analize meciuri'!$H$4:$H$103,MATCH($A4,'Analize meciuri'!$A$4:$A$103,0)),""))
```

Dependențe: $A4, 'Analize meciuri'!$H$4:$H$103, 'Analize meciuri'!$A$4:$A$103.

**E4** — 200 apariții; prima E4, ultima E203; lista completă în manifest.

```excel
=IF($A4="","",IFERROR(INDEX('Analize meciuri'!$GP$4:$GP$103,MATCH($A4,'Analize meciuri'!$A$4:$A$103,0)),""))
```

Dependențe: $A4, 'Analize meciuri'!$GP$4:$GP$103, 'Analize meciuri'!$A$4:$A$103.

**F4** — 200 apariții; prima F4, ultima F203; lista completă în manifest.

```excel
=IF($A4="","",IFERROR(INDEX('Analize meciuri'!$GT$4:$GT$103,MATCH($A4,'Analize meciuri'!$A$4:$A$103,0)),""))
```

Dependențe: $A4, 'Analize meciuri'!$GT$4:$GT$103, 'Analize meciuri'!$A$4:$A$103.

**J4** — 200 apariții; prima J4, ultima J203; lista completă în manifest.

```excel
=IF(OR($A4="",I4="",G4=""),"",IF(I4=1,G4-1,-1))
```

Dependențe: $A4, I4, G4.

**K4** — 200 apariții; prima K4, ultima K203; lista completă în manifest.

```excel
=IF(OR($A4="",I4=""),"",(E4-I4)^2)
```

Dependențe: $A4, I4, E4.

**L4** — 200 apariții; prima L4, ultima L203; lista completă în manifest.

```excel
=IF(OR($A4="",I4=""),"",-(I4*LN(MAX(0.001,E4))+(1-I4)*LN(MAX(0.001,1-E4))))
```

Dependențe: $A4, I4, E4.

**M4** — 200 apariții; prima M4, ultima M203; lista completă în manifest.

```excel
=IF(OR($A4="",G4="",H4=""),"",G4/H4-1)
```

Dependențe: $A4, G4, H4.

**N4** — 200 apariții; prima N4, ultima N203; lista completă în manifest.

```excel
=IF($A4="","",IFERROR(INDEX('Analize meciuri'!$GV$4:$GV$103,MATCH($A4,'Analize meciuri'!$A$4:$A$103,0)),""))
```

Dependențe: $A4, 'Analize meciuri'!$GV$4:$GV$103, 'Analize meciuri'!$A$4:$A$103.

**O4** — 200 apariții; prima O4, ultima O203; lista completă în manifest.

```excel
=IF($A4="","",IFERROR(INDEX('Analize meciuri'!$GN$4:$GN$103,MATCH($A4,'Analize meciuri'!$A$4:$A$103,0)),""))
```

Dependențe: $A4, 'Analize meciuri'!$GN$4:$GN$103, 'Analize meciuri'!$A$4:$A$103.

**Q4** — 1 apariții; adresă unică.

```excel
=COUNT(I4:I203)
```

Dependențe: I4:I203.

**V4** — 4 apariții; prima V4, ultima V7; lista completă în manifest.

```excel
=COUNTIF($O$4:$O$203,$U4)
```

Dependențe: $O$4:$O$203, $U4.

**W4** — 4 apariții; prima W4, ultima W7; lista completă în manifest.

```excel
=IFERROR(AVERAGEIF($O$4:$O$203,$U4,$K$4:$K$203),"")
```

Dependențe: $O$4:$O$203, $U4, $K$4:$K$203.

**X4** — 4 apariții; prima X4, ultima X7; lista completă în manifest.

```excel
=IFERROR(AVERAGEIF($O$4:$O$203,$U4,$L$4:$L$203),"")
```

Dependențe: $O$4:$O$203, $U4, $L$4:$L$203.

**Y4** — 4 apariții; prima Y4, ultima Y7; lista completă în manifest.

```excel
=IFERROR(AVERAGEIF($O$4:$O$203,$U4,$E$4:$E$203),"")
```

Dependențe: $O$4:$O$203, $U4, $E$4:$E$203.

**Z4** — 4 apariții; prima Z4, ultima Z7; lista completă în manifest.

```excel
=IFERROR(AVERAGEIF($O$4:$O$203,$U4,$I$4:$I$203),"")
```

Dependențe: $O$4:$O$203, $U4, $I$4:$I$203.

**Q5** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGE(I4:I203),"")
```

Dependențe: I4:I203.

**Q6** — 1 apariții; adresă unică.

```excel
=IFERROR(SUM(J4:J203)/COUNT(J4:J203),"")
```

Dependențe: J4:J203.

**Q7** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGE(K4:K203),"")
```

Dependențe: K4:K203.

**Q8** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGE(M4:M203),"")
```

Dependențe: M4:M203.

**Q11** — 1 apariții; adresă unică.

```excel
=COUNTIFS($E$4:$E$203,">="&0.75,$E$4:$E$203,"<"&0.8,$I$4:$I$203,"<>")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**R11** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($E$4:$E$203,$E$4:$E$203,">="&0.75,$E$4:$E$203,"<"&0.8,$I$4:$I$203,"<>"),"")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**S11** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($I$4:$I$203,$E$4:$E$203,">="&0.75,$E$4:$E$203,"<"&0.8),"")
```

Dependențe: $I$4:$I$203, $E$4:$E$203.

**T11** — 9 apariții; prima T11, ultima T19; lista completă în manifest.

```excel
=IF(Q11=0,"",S11-R11)
```

Dependențe: Q11, S11, R11.

**Q12** — 1 apariții; adresă unică.

```excel
=COUNTIFS($E$4:$E$203,">="&0.8,$E$4:$E$203,"<"&0.85,$I$4:$I$203,"<>")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**R12** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($E$4:$E$203,$E$4:$E$203,">="&0.8,$E$4:$E$203,"<"&0.85,$I$4:$I$203,"<>"),"")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**S12** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($I$4:$I$203,$E$4:$E$203,">="&0.8,$E$4:$E$203,"<"&0.85),"")
```

Dependențe: $I$4:$I$203, $E$4:$E$203.

**Q13** — 1 apariții; adresă unică.

```excel
=COUNTIFS($E$4:$E$203,">="&0.85,$E$4:$E$203,"<"&0.88,$I$4:$I$203,"<>")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**R13** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($E$4:$E$203,$E$4:$E$203,">="&0.85,$E$4:$E$203,"<"&0.88,$I$4:$I$203,"<>"),"")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**S13** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($I$4:$I$203,$E$4:$E$203,">="&0.85,$E$4:$E$203,"<"&0.88),"")
```

Dependențe: $I$4:$I$203, $E$4:$E$203.

**Q14** — 1 apariții; adresă unică.

```excel
=COUNTIFS($E$4:$E$203,">="&0.88,$E$4:$E$203,"<"&0.9,$I$4:$I$203,"<>")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**R14** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($E$4:$E$203,$E$4:$E$203,">="&0.88,$E$4:$E$203,"<"&0.9,$I$4:$I$203,"<>"),"")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**S14** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($I$4:$I$203,$E$4:$E$203,">="&0.88,$E$4:$E$203,"<"&0.9),"")
```

Dependențe: $I$4:$I$203, $E$4:$E$203.

**Q15** — 1 apariții; adresă unică.

```excel
=COUNTIFS($E$4:$E$203,">="&0.9,$E$4:$E$203,"<"&0.92,$I$4:$I$203,"<>")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**R15** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($E$4:$E$203,$E$4:$E$203,">="&0.9,$E$4:$E$203,"<"&0.92,$I$4:$I$203,"<>"),"")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**S15** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($I$4:$I$203,$E$4:$E$203,">="&0.9,$E$4:$E$203,"<"&0.92),"")
```

Dependențe: $I$4:$I$203, $E$4:$E$203.

**Q16** — 1 apariții; adresă unică.

```excel
=COUNTIFS($E$4:$E$203,">="&0.92,$E$4:$E$203,"<"&0.94,$I$4:$I$203,"<>")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**R16** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($E$4:$E$203,$E$4:$E$203,">="&0.92,$E$4:$E$203,"<"&0.94,$I$4:$I$203,"<>"),"")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**S16** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($I$4:$I$203,$E$4:$E$203,">="&0.92,$E$4:$E$203,"<"&0.94),"")
```

Dependențe: $I$4:$I$203, $E$4:$E$203.

**Q17** — 1 apariții; adresă unică.

```excel
=COUNTIFS($E$4:$E$203,">="&0.94,$E$4:$E$203,"<"&0.96,$I$4:$I$203,"<>")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**R17** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($E$4:$E$203,$E$4:$E$203,">="&0.94,$E$4:$E$203,"<"&0.96,$I$4:$I$203,"<>"),"")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**S17** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($I$4:$I$203,$E$4:$E$203,">="&0.94,$E$4:$E$203,"<"&0.96),"")
```

Dependențe: $I$4:$I$203, $E$4:$E$203.

**Q18** — 1 apariții; adresă unică.

```excel
=COUNTIFS($E$4:$E$203,">="&0.96,$E$4:$E$203,"<"&0.98,$I$4:$I$203,"<>")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**R18** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($E$4:$E$203,$E$4:$E$203,">="&0.96,$E$4:$E$203,"<"&0.98,$I$4:$I$203,"<>"),"")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**S18** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($I$4:$I$203,$E$4:$E$203,">="&0.96,$E$4:$E$203,"<"&0.98),"")
```

Dependențe: $I$4:$I$203, $E$4:$E$203.

**Q19** — 1 apariții; adresă unică.

```excel
=COUNTIFS($E$4:$E$203,">="&0.98,$E$4:$E$203,"<"&1.001,$I$4:$I$203,"<>")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**R19** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($E$4:$E$203,$E$4:$E$203,">="&0.98,$E$4:$E$203,"<"&1.001,$I$4:$I$203,"<>"),"")
```

Dependențe: $E$4:$E$203, $I$4:$I$203.

**S19** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGEIFS($I$4:$I$203,$E$4:$E$203,">="&0.98,$E$4:$E$203,"<"&1.001),"")
```

Dependențe: $I$4:$I$203, $E$4:$E$203.

### Risk Classification

**B4** — 1 apariții; adresă unică.

```excel
=0.25/0.85
```

Dependențe: niciuna; formulă constantă.

**B5** — 1 apariții; adresă unică.

```excel
=0.3/0.85
```

Dependențe: niciuna; formulă constantă.

**B6** — 1 apariții; adresă unică.

```excel
=0.15/0.85
```

Dependențe: niciuna; formulă constantă.

**B7** — 1 apariții; adresă unică.

```excel
=0.1/0.85
```

Dependențe: niciuna; formulă constantă.

**B8** — 1 apariții; adresă unică.

```excel
=0.05/0.85
```

Dependențe: niciuna; formulă constantă.

**B9** — 1 apariții; adresă unică.

```excel
=SUM(B4:B8)
```

Dependențe: B4:B8.

**B28** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GZ$4:$GZ$103,MATCH(Dashboard!$B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GZ$4:$GZ$103, Dashboard!$B$4, 'Analize meciuri'!$A$4:$A$103.

**E28** — 1 apariții; adresă unică.

```excel
=$B$4
```

Dependențe: $B$4.

**B29** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$HA$4:$HA$103,MATCH(Dashboard!$B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$HA$4:$HA$103, Dashboard!$B$4, 'Analize meciuri'!$A$4:$A$103.

**E29** — 1 apariții; adresă unică.

```excel
=$B$5
```

Dependențe: $B$5.

**B30** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$HB$4:$HB$103,MATCH(Dashboard!$B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$HB$4:$HB$103, Dashboard!$B$4, 'Analize meciuri'!$A$4:$A$103.

**E30** — 1 apariții; adresă unică.

```excel
=$B$6
```

Dependențe: $B$6.

**B31** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$HC$4:$HC$103,MATCH(Dashboard!$B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$HC$4:$HC$103, Dashboard!$B$4, 'Analize meciuri'!$A$4:$A$103.

**E31** — 1 apariții; adresă unică.

```excel
=$B$7
```

Dependențe: $B$7.

**B32** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$HD$4:$HD$103,MATCH(Dashboard!$B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$HD$4:$HD$103, Dashboard!$B$4, 'Analize meciuri'!$A$4:$A$103.

**E32** — 1 apariții; adresă unică.

```excel
=$B$8
```

Dependențe: $B$8.

**B35** — 1 apariții; adresă unică.

```excel
=IF(COUNT(B28:B32)<5,"",SUMPRODUCT(B28:B32,E28:E32))
```

Dependențe: B28:B32, E28:E32.

**B36** — 1 apariții; adresă unică.

```excel
=IF(B35="","",IF(B35<=20,1,IF(B35<=40,2,IF(B35<=60,3,IF(B35<=80,4,5)))))
```

Dependențe: B35.

**B37** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$HG$4:$HG$103,MATCH(Dashboard!$B$4,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$HG$4:$HG$103, Dashboard!$B$4, 'Analize meciuri'!$A$4:$A$103.

**B38** — 1 apariții; adresă unică.

```excel
=IF(B37="","",IF(B37<>"PASS",5,B36))
```

Dependențe: B37, B36.

**B39** — 1 apariții; adresă unică.

```excel
=IF(B38="","",IF(B38=1,"DEFENSIV",IF(B38=2,"PRUDENT",IF(B38=3,"MODERAT",IF(B38=4,"RIDICAT","WATCH / NO BET")))))
```

Dependențe: B38.

### ZeroMass Gate v4

**B17** — 1 apariții; adresă unică.

```excel
=IF(AND(B14>=2,UPPER(B15)="PASS",UPPER(B16)="SCĂZUT"),0.94,0.9)
```

Dependențe: B14, B15, B16.

**D17** — 1 apariții; adresă unică.

```excel
=IF(B17>0.9,"CONFIRMAT 2 SURSE","CAP 90%")
```

Dependențe: B17.

**B18** — 1 apariții; adresă unică.

```excel
=MIN(B13,B17)
```

Dependențe: B13, B17.

**D18** — 1 apariții; adresă unică.

```excel
=IF(B18>0.9,"ELIGIBIL P>90%","FĂRĂ P>90%")
```

Dependențe: B18.

### Settlement

**R4** — 200 apariții; prima R4, ultima R203; lista completă în manifest.

```excel
=IF(OR(I4="",J4=""),"",POWER(I4-J4,2))
```

Dependențe: I4, J4.

**S4** — 200 apariții; prima S4, ultima S203; lista completă în manifest.

```excel
=IF(OR(I4="",J4=""),"",-((J4*LN(MAX(MIN(I4,0.999999),0.000001)))+((1-J4)*LN(MAX(MIN(1-I4,0.999999),0.000001)))))
```

Dependențe: I4, J4.

### Risk Level Summary

**B4** — 5 apariții; prima B4, ultima B8; lista completă în manifest.

```excel
=COUNTIF(Settlement!$T$4:$T$203,A4)
```

Dependențe: Settlement!$T$4:$T$203, A4.

**C4** — 5 apariții; prima C4, ultima C8; lista completă în manifest.

```excel
=SUMIF(Settlement!$T$4:$T$203,A4,Settlement!$J$4:$J$203)
```

Dependențe: Settlement!$T$4:$T$203, A4, Settlement!$J$4:$J$203.

**D4** — 5 apariții; prima D4, ultima D8; lista completă în manifest.

```excel
=IFERROR(C4/B4,"")
```

Dependențe: C4, B4.

**E4** — 5 apariții; prima E4, ultima E8; lista completă în manifest.

```excel
=IFERROR(SUMIF(Settlement!$T$4:$T$203,A4,Settlement!$R$4:$R$203)/B4,"")
```

Dependențe: Settlement!$T$4:$T$203, A4, Settlement!$R$4:$R$203, B4.

**F4** — 5 apariții; prima F4, ultima F8; lista completă în manifest.

```excel
=IF(D4="","",1-D4)
```

Dependențe: D4.

### Calibration

**C4** — 8 apariții; prima C4, ultima C11; lista completă în manifest.

```excel
=COUNTIFS(Settlement!$I$4:$I$203,">="&A4,Settlement!$I$4:$I$203,"<"&B4,Settlement!$J$4:$J$203,"<>")
```

Dependențe: Settlement!$I$4:$I$203, A4, B4, Settlement!$J$4:$J$203.

**D4** — 8 apariții; prima D4, ultima D11; lista completă în manifest.

```excel
=IFERROR(SUMIFS(Settlement!$I$4:$I$203,Settlement!$I$4:$I$203,">="&A4,Settlement!$I$4:$I$203,"<"&B4)/C4,"")
```

Dependențe: Settlement!$I$4:$I$203, A4, B4, C4.

**E4** — 8 apariții; prima E4, ultima E11; lista completă în manifest.

```excel
=IFERROR(SUMIFS(Settlement!$J$4:$J$203,Settlement!$I$4:$I$203,">="&A4,Settlement!$I$4:$I$203,"<"&B4)/C4,"")
```

Dependențe: Settlement!$J$4:$J$203, Settlement!$I$4:$I$203, A4, B4, C4.

**F4** — 8 apariții; prima F4, ultima F11; lista completă în manifest.

```excel
=IF(OR(D4="",E4=""),"",D4-E4)
```

Dependențe: D4, E4.

**G4** — 8 apariții; prima G4, ultima G11; lista completă în manifest.

```excel
=IF(C4<10,"LOW N",IF(ABS(F4)<=0.03,"OK",IF(ABS(F4)<=0.06,"WATCH","DRIFT")))
```

Dependențe: C4, F4.

### Fail Distribution

**B4** — 7 apariții; prima B4, ultima B10; lista completă în manifest.

```excel
=COUNTIFS(Settlement!$J$4:$J$203,0,Settlement!$O$4:$O$203,A4)
```

Dependențe: Settlement!$J$4:$J$203, Settlement!$O$4:$O$203, A4.

**C4** — 7 apariții; prima C4, ultima C10; lista completă în manifest.

```excel
=IFERROR(B4/COUNTIF(Settlement!$J$4:$J$203,0),"")
```

Dependențe: B4, Settlement!$J$4:$J$203.

### League Summary

**B4** — 30 apariții; prima B4, ultima B33; lista completă în manifest.

```excel
=IF(A4="","",COUNTIF(Settlement!$C$4:$C$203,A4))
```

Dependențe: A4, Settlement!$C$4:$C$203.

**C4** — 30 apariții; prima C4, ultima C33; lista completă în manifest.

```excel
=IF(A4="","",SUMIF(Settlement!$C$4:$C$203,A4,Settlement!$J$4:$J$203))
```

Dependențe: A4, Settlement!$C$4:$C$203, Settlement!$J$4:$J$203.

**D4** — 30 apariții; prima D4, ultima D33; lista completă în manifest.

```excel
=IFERROR(C4/B4,"")
```

Dependențe: C4, B4.

**E4** — 30 apariții; prima E4, ultima E33; lista completă în manifest.

```excel
=IFERROR(SUMIF(Settlement!$C$4:$C$203,A4,Settlement!$I$4:$I$203)/B4,"")
```

Dependențe: Settlement!$C$4:$C$203, A4, Settlement!$I$4:$I$203, B4.

**F4** — 30 apariții; prima F4, ultima F33; lista completă în manifest.

```excel
=IF(OR(D4="",E4=""),"",E4-D4)
```

Dependențe: D4, E4.

**G4** — 30 apariții; prima G4, ultima G33; lista completă în manifest.

```excel
=IFERROR(SUMIF(Settlement!$C$4:$C$203,A4,Settlement!$R$4:$R$203)/B4,"")
```

Dependențe: Settlement!$C$4:$C$203, A4, Settlement!$R$4:$R$203, B4.

**H4** — 30 apariții; prima H4, ultima H33; lista completă în manifest.

```excel
=IF(A4="","",IF(B4<10,"LOW N",IF(ABS(F4)<=0.05,"STABLE","WATCH")))
```

Dependențe: A4, B4, F4.

### Monthly Summary

**B4** — 24 apariții; prima B4, ultima B27; lista completă în manifest.

```excel
=IF(A4="","",COUNTIFS(Settlement!$B$4:$B$203,">="&A4,Settlement!$B$4:$B$203,"<"&EDATE(A4,1)))
```

Dependențe: A4, Settlement!$B$4:$B$203.

**C4** — 24 apariții; prima C4, ultima C27; lista completă în manifest.

```excel
=IF(A4="","",SUMIFS(Settlement!$J$4:$J$203,Settlement!$B$4:$B$203,">="&A4,Settlement!$B$4:$B$203,"<"&EDATE(A4,1)))
```

Dependențe: A4, Settlement!$J$4:$J$203, Settlement!$B$4:$B$203.

**D4** — 24 apariții; prima D4, ultima D27; lista completă în manifest.

```excel
=IFERROR(C4/B4,"")
```

Dependențe: C4, B4.

**E4** — 24 apariții; prima E4, ultima E27; lista completă în manifest.

```excel
=IF(A4="","",IFERROR(SUMIFS(Settlement!$I$4:$I$203,Settlement!$B$4:$B$203,">="&A4,Settlement!$B$4:$B$203,"<"&EDATE(A4,1))/B4,""))
```

Dependențe: A4, Settlement!$I$4:$I$203, Settlement!$B$4:$B$203, B4.

**F4** — 24 apariții; prima F4, ultima F27; lista completă în manifest.

```excel
=IF(OR(D4="",E4=""),"",E4-D4)
```

Dependențe: D4, E4.

**G4** — 24 apariții; prima G4, ultima G27; lista completă în manifest.

```excel
=IF(A4="","",IFERROR(SUMIFS(Settlement!$R$4:$R$203,Settlement!$B$4:$B$203,">="&A4,Settlement!$B$4:$B$203,"<"&EDATE(A4,1))/B4,""))
```

Dependențe: A4, Settlement!$R$4:$R$203, Settlement!$B$4:$B$203, B4.

### Backtest Summary

**B4** — 1 apariții; adresă unică.

```excel
=COUNT(Settlement!$J$4:$J$203)
```

Dependențe: Settlement!$J$4:$J$203.

**B5** — 1 apariții; adresă unică.

```excel
=SUM(Settlement!$J$4:$J$203)
```

Dependențe: Settlement!$J$4:$J$203.

**B6** — 1 apariții; adresă unică.

```excel
=IFERROR(B5/B4,"")
```

Dependențe: B5, B4.

**B7** — 1 apariții; adresă unică.

```excel
=IF(B4=0,"",((B5/B4)+(1.96^2)/(2*B4)-1.96*SQRT((B5/B4)*(1-B5/B4)/B4+(1.96^2)/(4*B4^2)))/(1+(1.96^2)/B4))
```

Dependențe: B4, B5.

**B8** — 1 apariții; adresă unică.

```excel
=IF(B4=0,"",((B5/B4)+(1.96^2)/(2*B4)+1.96*SQRT((B5/B4)*(1-B5/B4)/B4+(1.96^2)/(4*B4^2)))/(1+(1.96^2)/B4))
```

Dependențe: B4, B5.

**B9** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGE(Settlement!$I$4:$I$203),"")
```

Dependențe: Settlement!$I$4:$I$203.

**B10** — 1 apariții; adresă unică.

```excel
=IF(OR(B9="",B6=""),"",B9-B6)
```

Dependențe: B9, B6.

**B11** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGE(Settlement!$R$4:$R$203),"")
```

Dependențe: Settlement!$R$4:$R$203.

**B12** — 1 apariții; adresă unică.

```excel
=IFERROR(AVERAGE(Settlement!$S$4:$S$203),"")
```

Dependențe: Settlement!$S$4:$S$203.

**B13** — 1 apariții; adresă unică.

```excel
=COUNTIF(League_Summary!$B$4:$B$33,">0")
```

Dependențe: League_Summary!$B$4:$B$33.

**B14** — 1 apariții; adresă unică.

```excel
=COUNTIF(League_Summary!$H$4:$H$33,"STABLE")
```

Dependențe: League_Summary!$H$4:$H$33.

### ZeroMass WF v4

**B14** — 1 apariții; adresă unică.

```excel
=IF(AND(B11>=2,B12="CONFIRMED",B13="SCĂZUT"),0.94,IF(B13="SCĂZUT",0.92,IF(B13="MEDIU",0.91,0.9)))
```

Dependențe: B11, B12, B13.

**B15** — 1 apariții; adresă unică.

```excel
=IF(B7="","",MIN(1-B7,B14))
```

Dependențe: B7, B14.

### ZeroMass Gate v5

**B2** — 1 apariții; adresă unică.

```excel
=Dashboard!B4
```

Dependențe: Dashboard!B4.

**B5** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$FY$4:$FY$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$FY$4:$FY$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**C5** — 2 apariții; prima C5, ultima C6; lista completă în manifest.

```excel
='Setari model'!$B$113
```

Dependențe: 'Setari model'!$B$113.

**D5** — 19 apariții; prima D5, ultima D23; lista completă în manifest.

```excel
=IF(B5="","",IF(OR(B5="DA",B5="SCĂZUT"),"PASS",IF(OR(B5="NU",B5="MEDIU",B5="RIDICAT",B5="NEDETERMINAT"),"FLAG","INFO")))
```

Dependențe: B5.

**B6** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$FZ$4:$FZ$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$FZ$4:$FZ$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B7** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GF$4:$GF$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GF$4:$GF$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B8** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GG$4:$GG$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GG$4:$GG$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B9** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$BS$4:$BS$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$BS$4:$BS$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B10** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GC$4:$GC$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GC$4:$GC$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**C10** — 2 apariții; prima C10, ultima C11; lista completă în manifest.

```excel
='Setari model'!$B$117
```

Dependențe: 'Setari model'!$B$117.

**B11** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GD$4:$GD$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GD$4:$GD$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B12** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GE$4:$GE$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GE$4:$GE$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**C12** — 1 apariții; adresă unică.

```excel
='Setari model'!$B$118
```

Dependențe: 'Setari model'!$B$118.

**B13** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GH$4:$GH$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GH$4:$GH$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B14** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GI$4:$GI$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GI$4:$GI$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B15** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GJ$4:$GJ$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GJ$4:$GJ$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B16** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GK$4:$GK$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GK$4:$GK$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B17** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GL$4:$GL$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GL$4:$GL$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B18** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GM$4:$GM$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GM$4:$GM$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B19** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GN$4:$GN$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GN$4:$GN$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B20** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GO$4:$GO$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GO$4:$GO$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B21** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GP$4:$GP$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GP$4:$GP$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B22** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GU$4:$GU$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GU$4:$GU$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

**B23** — 1 apariții; adresă unică.

```excel
=IFERROR(INDEX('Analize meciuri'!$GV$4:$GV$103,MATCH($B$2,'Analize meciuri'!$A$4:$A$103,0)),"")
```

Dependențe: 'Analize meciuri'!$GV$4:$GV$103, $B$2, 'Analize meciuri'!$A$4:$A$103.

## Anexa C Rezultate numerice și simulări

### C1 Rândul 4 valori cache de referință

| Celulă | Indicator | Valoare cache |
| --- | --- | --- |
| BJ4 | λ sezon goluri | 2.7087635820327414 |
| BK4 | λ sezon xG | 2.695318373689451 |
| BL4 | λ recent goluri | 2.6489578808281795 |
| BM4 | λ recent xG | 2.6487763675966214 |
| BN4 | λ H2H | 2.4444444444444446 |
| BO4 | Prob. piață O0.5 | 0.8653846153846154 |
| BP4 | λ piață | 2.0053335695261145 |
| BQ4 | λ bază | 2.568702883845408 |
| BR4 | Multiplicator context | 1.07 |
| BS4 | λ ajustat | 2.748512085714587 |
| BT4 | P(0-0) Poisson | 0.06402305118433504 |
| DZ4 | P0 ZIP/regim v2 | 0.0721123897129207 |
| FC4 | Finishing vs xG gazde | 1.0588235294117647 |
| FD4 | Finishing vs xG oaspeți | 0.96 |
| FE4 | Risc 0-0 team-specific | 0.6324555320336758 |
| FF4 | Risc blank×clean-sheet reciproc | 0.845378028229756 |
| FG4 | Risc finishing | 0 |
| FH4 | Risc statistic 0–0 HT | 0.6964285714285714 |
| FI4 | Factor zero-mass v3 | 0.7826357823647438 |
| FJ4 | P0 recalibrat v3 | 0.05643773654116299 |
| GC4 | Finishing recent gazde | 1.032258064516129 |
| GD4 | Finishing recent oaspeți | 0.923076923076923 |
| GE4 | Indice chance creation recent | 1.425 |
| GF4 | Ambele echipe blank recent | DA |
| GG4 | Clean-sheet advers relevant | DA |
| GH4 | λ moderat + finishing slab | NU |
| GI4 | Acumulare 0-0 recentă | DA |
| GJ4 | Scor low-conversion v5 | 0 |
| GK4 | Multiplicator P0 low-conversion | 1 |
| GL4 | P0 recalibrat v5 | 0.05643773654116299 |
| GM4 | Date critice zero-mass complete | DA |
| GN4 | Clasă zero-mass | SCĂZUT |
| GO4 | Plafon probabilitate raportată | 0.92 |
| GP4 | P Over0.5 v5 | 0.92 |
| GQ4 | Cotă fair v5 | 1.0869565217391304 |
| GR4 | Edge v5 | 0.05461538461538462 |
| GS4 | EV v5 | 0.030400000000000205 |
| GT4 | Confidence v5 | 59.194772288905426 |
| GZ4 | Data Quality Risk | 9.999999999999998 |
| HA4 | Zero-Mass Risk | 3.839503807616923 |
| HB4 | Context Risk | 14.000000000000012 |
| HC4 | Model Uncertainty | 9.377513343075528 |
| HD4 | Compound Risk | 0 |
| HE4 | Risk Score | 7.870120560697213 |
| HF4 | Risk Level Base | 1 |
| HG4 | G0 / Hard Gate – date critice | PASS |
| HH4 | Final Risk Level | 1 |
| HI4 | Risk Class | DEFENSIV |
| HK4 | Recomandare finală tehnică | DEFENSIV |


### C2 Toate exemplele existente

| Match ID | GP | GT | HE | HG | HH și HK |
| --- | --- | --- | --- | --- | --- |
| DEMO-LIGA-001 | 0.92 | 59.194772288905426 | 7.870120560697213 | PASS | 1 DEFENSIV |
| DEMO-CUPA-002 | 0.92 | 32.070156010341734 | 24.908034164456684 | PASS | 2 PRUDENT |
| DEMO-EURO-TUR-003 | 0.9117521424002618 | 71.32636861164305 | 3.886353641167856 | PASS | 1 DEFENSIV |
| DEMO-EURO-RET-004 | 0.94 | 77.03030347448944 | 12.964645200107853 | PASS | 1 DEFENSIV |
| DEMO-AMICAL-005 | 0.7113519435181987 | 0 | 51.7192363277411 | PASS | 3 MODERAT |


### C3 Simulări independente fără certificare Excel nativă

| Scenariu | GL | GP | HE | HG | HK |
| --- | --- | --- | --- | --- | --- |
| missing_EV |  |  |  | FAIL – DATE CRITICE ZERO-MASS INCOMPLETE | WATCH / NO BET |
| missing_xG_L |  |  |  | FAIL – DATE CRITICE ZERO-MASS INCOMPLETE | WATCH / NO BET |
| missing_recent_blank_FY | 0.05643773654116299 | 0.9 |  | FAIL – DATE CRITICE ZERO-MASS INCOMPLETE | WATCH / NO BET |
| small_sample | 0.054190597177293194 | 0.92 | 10.187180523477762 | PASS | DEFENSIV |
| no_odds | 0.053927654040911946 | 0.92 | 7.870120560697213 | PASS | DEFENSIV |
| confirmed_lineup | 0.05643773654116299 | 0.94 | 7.870120560697213 | PASS | DEFENSIV |
| striker_absent | 0.060952755464456033 | 0.92 | 7.870120560697213 | PASS | DEFENSIV |
| unused_FB | 0.05643773654116299 | 0.92 | 7.870120560697213 | PASS | DEFENSIV |
| odds_changed | 0.06136589031182642 | 0.92 | 7.870120560697213 | PASS | DEFENSIV |
| missing_O05 | 0.0512727784146835 | 0.92 | 7.870120560697213 | PASS | DEFENSIV |
| low_conversion | 0.1056096823840552 | 0.8943903176159448 | 17.304014964934687 | PASS | DEFENSIV |
| context_text | ERROR:XLException | ERROR:XLException | ERROR:XLException | PASS | ERROR:XLException |
| context_blank | 0.05715520659615344 | 0.92 | 7.517179384226624 | PASS | DEFENSIV |


Setul complet de modificări este în simulations.json. `missing_EV` se referă la coloana EV (rata 0–0 a gazdelor), nu la Expected Value. Numele câmpurilor Excel au prioritate asupra abrevierilor economice.
