# Pontifybet — Product Specification Document (PSD)

| Câmp | Valoare |
| --- | --- |
| **Produs** | Pontifybet MVP |
| **Tip document** | Product Specification Document |
| **Versiune** | 1.0 |
| **Dată** | 17 septembrie 2026 |
| **Stadiu** | MVP privat, funcțional local (MOCK + LIVE FootyStats) |
| **Audiență** | Proprietar produs, dezvoltatori, viitor operator / publicare |
| **Limbă UI** | Română |
| **Repo local** | `C:\_Software\SAAS\Pontifybet` |

---

## 1. Rezumat executiv

Pontifybet este o **aplicație privată de analiză fotbalistică** care colectează date de meci din FootyStats, le validează după o metodologie internă (Cadru v5 + Matrice v4) și **completează copii** ale unor șabloane Excel existente. Utilizatorul descarcă un ZIP cu fișierele generate și un raport de validare.

Aplicația **nu este un motor de pronostic**. Verdictul, pragurile, ponderile, nivelul de risc și selectorul final rămân **în Excel**. Pontifybet doar alimentează inputurile, protejează formulele și blochează exportul când datele critice lipsesc.

Publicul țintă actual: un operator intern (nu clienți multi-tenant). Accesul se face cu o parolă unică.

---

## 2. Scopul produsului

### 2.1 Problemă

Analizele de pariuri (Over 0.5, Șansă Dublă, Cornere) trăiesc în workbook-uri Excel complexe, calibrate manual. Completarea lor de mână cu statistici FootyStats este lentă, predispusă la erori (valori `-1` tratate ca 0, formule stricate, praguri mutate) și greu de repetat zilnic.

### 2.2 Obiectiv MVP

1. Selecta data, ligile și modelele dintr-o singură pagină web; lista de meciuri se generează la cerere.
2. Aduna datele FootyStats (sau fixture-uri MOCK).
3. Valida inputurile după Matricea de lipsă date v4.
4. Scrie **doar celulele de input** pe copii ale șabloanelor.
5. Oferi descărcare ZIP + raport de validare, fără a atinge originalele.

### 2.3 Non-obiective (explicit)

- Nu calculează recomandarea / verdictul în Python.
- Nu modifică praguri, ponderi, Risk Level, ZeroMass Gate, Config_v6.
- Nu este un SaaS public cu conturi, billing sau multi-user.
- Nu redistribuie date FootyStats.
- Nu adaugă a doua sursă de date (ex. Football-Data) în MVP.
- Nu recalculează formulele pe server (LibreOffice e stub dezactivat).
- Nu include modelele din afara MVP: Handicap, Under 4.5, BTTS, Cartonașe.

---

## 3. Ce face aplicația

Fluxul utilizatorului, pe scurt:

1. Autentificare cu parolă (`APP_PASSWORD`).
2. În sidebar: dată, fus orar, ligi, modele.
3. Buton **Listează meciurile** — tabel cu ligă, oră, echipe; bifă unul / mai multe / toate; sortare ligă sau oră.
4. Buton **Generează analiza** (doar meciurile bifațe).
5. Aplicația afișează progres (meciuri → statistici → validare → Excel → ZIP).
6. Tabel de validare pe combinația meci × model (valid / pending / blocat).
7. Buton **Descarcă fișierele Excel** (arhiva ZIP). După descărcare, fișierele temporare din `outputs/` se șterg.

Meniune vizibilă în UI: *Microsoft Excel va recalcula formulele la prima deschidere. Valorile din fișier nu sunt rezultate proaspăt recalculate.*

### 3.1 Moduri de date

| Mod | Când se activează | Sursă |
| --- | --- | --- |
| **MOCK** | Lipsește `FOOTYSTATS_API_KEY` sau `FORCE_MOCK=true` | Fișiere JSON din `mocks/` |
| **LIVE** | Cheie API prezentă și `FORCE_MOCK=false` | `https://api.football-data-api.com` |

În MOCK, meciurile de demonstrație sunt pe data **2026-03-15**: Arsenal–Chelsea, Liverpool–Everton (Premier League) și Real Madrid–Sevilla (La Liga). Meciul Real Madrid–Sevilla este construit astfel încât modelul Cornere să fie **blocat** pe G0 (lipsă date native), pentru a demonstra validarea.

---

## 4. Ce se introduce (inputuri)

### 4.1 Inputuri de la utilizator (UI)

| Câmp | Unde | Valori / constrângeri | Obligatoriu |
| --- | --- | --- | --- |
| Parolă | Ecran login | Comparată cu `APP_PASSWORD` prin `hmac.compare_digest` | Da (dacă e setată) |
| Data meciurilor | Sidebar | `date_input` Streamlit, format ISO `YYYY-MM-DD` | Da |
| Fus orar | Sidebar | Implicit `Europe/Bucharest`; opțiuni: `UTC`, `Europe/London` | Da |
| Ligi | Sidebar, multiselect | Din `list_leagues` (în LIVE: doar ligile alese pe cheia FootyStats) | Da (cel puțin una pentru listare) |
| Meciuri | Zona principală, tabel | După **Listează meciurile**; filtrate pe dată + ligi; bifă unul / mai multe / toate | Da (cel puțin unul bifat) |
| Modele | Sidebar, multiselect | Over 0.5, Șansă Dublă, Cornere Multi-Line V14 | Da (cel puțin unul) |

Fără listă, fără meci bifat **sau** fără model, generarea este respinsă.

### 4.2 Inputuri de configurare (mediu)

| Variabilă | Rol |
| --- | --- |
| `APP_PASSWORD` | Parola unică a aplicației |
| `FOOTYSTATS_API_KEY` | Cheie API FootyStats (nu se loghează, nu se scrie în Excel, nu se comite) |
| `FORCE_MOCK` | Forțează date de test |
| `FOOTYSTATS_TIMEOUT` | Timeout HTTP, implicit 20 s |
| `FOOTYSTATS_RETRIES` | Retry-uri, implicit 2 |

Surse, în ordine: `.env` → variabile de mediu → `.streamlit/secrets.toml`.

### 4.3 Date preluate din FootyStats (sau MOCK)

Pentru fiecare meci selectat, clientul construiește un obiect canonic `MatchData`:

- Identitate: `match_id`, ligă, sezon, rundă, kickoff UTC + București.
- Echipe: nume, ID, meciuri jucate (overall / home / away).
- Goluri: GF/GA pe sezon și split home/away.
- xG / xGA (dacă există).
- Over 0.5 %, Failed to Score %, Clean Sheet %.
- Formă recentă last 5 / last 10 (inclusiv cornere recente).
- Cote 1X2 și Over/Under 0.5, **doar dacă API-ul le returnează ca valori reale**.
- 12 valori native de cornere (sezon / home-away / recent × for & against).

Fiecare indicator nu este un număr gol, ci un obiect `Indicator`: `value`, `n` (eșantion), `unit`, `endpoint`, `extracted_at`, `cutoff`, `method`, `data_status`, `trace_id`.

### 4.4 Sentineli și regulă de aur

Valorile FootyStats **`-1`, `-2` și `null` se mapează la `NOT AVAILABLE`**, niciodată la `0`. Aplicația nu inventează date lipsă.

---

## 5. Cum funcționează

### 5.1 Arhitectură de pipeline

```
UI Streamlit (app.py)
        │
        ▼
FootyStatsClient  ──sau──  MockFootyStatsClient
        │
        ▼
   MatchData (Pydantic)
        │
        ▼
   Validator (Matrice v4)
        │
        ├── blocat (G0 critic lipsă) → rând roșu, fără Excel pentru acel (meci, model)
        └── permis
                │
                ▼
        Adaptoare (Over05 / DoubleChance / Corners)
                │
                ▼
        Copie șablon + scriere whitelist + fingerprint formule
                │
                ▼
        ZIP (XLSX + validation_report.json + .csv)
```

Orchestrarea este în `src/pipeline.py` → `run_analysis()`.

Etapele de progres afișate:

1. Încarc meciurile
2. Statistici meci N/M
3. Validez datele
4. Generez fișierele Excel
5. Creez arhiva ZIP
6. Gata

### 5.2 Principiu: Excel rămâne motorul

Workbook-ul original (din `modele_analize/`) este arhivă. Runtime-ul copiază din `templates/`. Python scrie **doar input**. Formulele, dashboard-urile, gate-urile de risc și parametrii **nu sunt atinse**.

După scriere se compară o **amprentă** (foi + formule). Orice diferență blochează exportul:

> `EXPORT BLOCAT. Motiv: formula {Sheet}!{Cell} a fost modificată.`

Alte motive de blocare integritate: foi șterse/redenumite, scriere în afara whitelist, încercare de a suprascrie o celulă care conține formulă.

### 5.3 Layout de scriere pe model

| Model | Fișiere generate | Unde scrie | Ce nu scrie |
| --- | --- | --- | --- |
| **Over 0.5 V4** | 1 workbook / rulare (`over05_{dată}.xlsx`) | `Analize meciuri` rânduri de la 4, coloane A–BI | `Setari model`, Dashboard, Risk_*, ZeroMass_* |
| **Cornere Multi-Line V14** | 1 workbook / rulare (`corners_{dată}.xlsx`) | `Input_Meci` de la rândul 6, A–AG | `Config_v6`, `Analiza_Linii`, `Motor_Meciuri`, Dashboard |
| **Șansă Dublă V2** | **1 workbook / meci** (`double_chance_{match_id}.xlsx`) | `Input_Meci` (B/C vertical), `Surse_Date` statusuri G0/G1 | `Parametri`, `Double_Chance`, `P0_Gates_v2`, Dashboard |

Rândurile DEMO din șablon sunt golite/înlocuite, nu se șterge foaia.

Maparea exactă FootyStats → indicator → foaie → celulă → tip → G-level stă în `config/model_registry.yaml`. Un al 4-lea model ulterior se adaugă prin YAML + o clasă adaptor, fără rescrierea generatorului.

### 5.4 Validare (Matrice v4)

Hard fail **doar** dacă lipsește un input **G0 critic** pentru modelul respectiv. Blocarea este pe combinația (meci, model): același meci poate trece la Over 0.5 și eșua la Cornere.

| Status | Blochează? | Comportament |
| --- | --- | --- |
| AVAILABLE - CHECKED | Nu | Folosire integrală |
| AVAILABLE - NOT CHECKED | Nu | Sourcing incomplet; nu e zero |
| DERIVED | Nu | Valoare + N + sursă + metodă |
| PROXY ONLY | Doar dacă G0 cere nativ | Haircut / cap de încredere |
| PENDING OFFICIAL | Nu (de regulă) | Afișează plan de refresh |
| SOURCE CONFLICT | Da dacă afectează G0 | Reconciliere |
| NOT AVAILABLE | Da **doar pe G0 critic** | Nu inventa date |
| SMALL SAMPLE | Nu | Fără downgrade mecanic de risc |

Niveluri G:

- **G0** — hard gate (zero-mass Over 0.5; cote 1X2 de-vig Șansă Dublă; 12 native cornere + sample)
- **G1** — context soft (xG, factori, etc.)
- **G2** — calibrare / incertitudine
- **G3** — piață (cote Over 0.5, unde modelul le cere)

**Over 0.5 — G0 critic:** % Over 0.5 home/away, Failed to Score, Clean Sheet, meciuri jucate home/away, kickoff.

**Șansă Dublă — G0 critic:** cote 1, X, 2; sample home/away; kickoff.

**Cornere — G0 critic:** 12 valori native cornere (sezon / home-away / recent × for & against) + sample overall; kickoff.

Factorii contextuali Over 0.5 (AV–BG, scala -2..2): dacă FootyStats nu îi oferă, rămân goi / `AVAILABLE - NOT CHECKED`, nu se forțează 0. `-1` din demo rămâne sentinel, nu zero.

### 5.5 Ieșiri (output)

Arhiva `pontifybet_export.zip` conține:

- Fișierele `.xlsx` generate (doar pentru combinațiile neblocate)
- `validation_report.json` — lista de `ValidationIssue` (match_id, model_id, indicator, g_level, status, blocking, reason, refresh_plan)
- `validation_report.csv` — aceeași listă, formă scurtă

În UI, tabelul arată: ligă, oră București, echipe, model, Data Status, G0 (OK/FAIL), motiv blocare.

După click pe descărcare, directorul de rulare din `outputs/` este șters.

**Important pentru operator:** prima deschidere în **Microsoft Excel** recalculează formulele. openpyxl nu evaluează formulele; valorile afișate în celulele de output înainte de recalcul nu sunt rezultatul modelului.

---

## 6. Modelele pilot

Originalele rămân în `modele_analize/`. Copiile runtime sunt în `templates/`.

### 6.1 Over 0.5 — `1_model_analiza_over0.5_optimizat_V4.xlsx`

- ~20 foi (Dashboard, Analize meciuri, Setari model, Risk_Classification, ZeroMass_Gate_v4/v5, etc.)
- 1 rând = 1 meci; header pe rândul 3; date de la rândul 4
- Input A–BI; de la BJ încolo sunt formule
- Fără VBA / charts / pivot

### 6.2 Șansă Dublă — `11_model_analiza_pariu_sansadubla_optimizat_V2.xlsx`

- ~15 foi (Parametri, Input_Meci, Model_1X2, Double_Chance, P0_Gates_v2, etc.)
- Layout **vertical**: un meci per fișier (B = gazde, C = oaspeți)
- Cotele 1X2 se transformă în probabilități de-vig (doar dacă toate cele 3 cote sunt > 1); se scriu și cotele aproximative 1X / X2 / 12
- G-level formalizat în `Surse_Date`

### 6.3 Cornere Multi-Line V14 — `6_model_analiza_cornere_multiline_optimizat_V14.xlsx`

- ~13 foi (Dashboard, Config_v6, Analiza_Linii, Motor_Meciuri, Input_Meci, etc.)
- Mai multe meciuri pe rânduri, de la rândul 6
- Template-ul menționează Football-Data; MVP folosește **doar FootyStats**. Dacă cele 12 valori native lipsesc, combinația meci+model este blocată (`NOT AVAILABLE`), fără inventare
- Bundle-ul nativ de cornere este scris în zona de notes a inputului (layout-ul nu are coloane dedicate pentru toate cele 12 valori)

### 6.4 În afara MVP (există ca șabloane, nu sunt generate)

Handicap, Under 4.5, BTTS, Cartonașe — păstrate ca arhivă, neconectate la pipeline.

---

## 7. Conectorul FootyStats

Bază: `https://api.football-data-api.com`  
Autentificare: query `key` din `FOOTYSTATS_API_KEY`  
Envelope JSON: `{success, pager, metadata, data}`

| Metodă | Endpoint | Rol |
| --- | --- | --- |
| `test_call` | `/test-call` | Verificare cheie |
| `list_leagues` | `/league-list?chosen_leagues_only=true` | Ligile alese pe cont |
| `matches_by_date` | `/todays-matches?date=&timezone=` | Meciuri pe zi (max 200/pagină, până la 20 pagini) |
| `league_season` | `/league-season` | Stats ligă |
| `league_matches` | `/league-matches` | Program ligă |
| `league_teams` | `/league-teams?include=stats` | Echipe + stats sezon |
| `team` | `/team?include=stats` | Echipă filtrată pe `competition_id` |
| `last_x` | `/lastx?num=5\|10` | Formă recentă (bloc overall) |
| `match_details` | `/match` | Detalii meci |

Clientul (`src/api/client.py`):

- `httpx`, timeout 20 s, 2 retry-uri
- Cache în memorie pe rulare + fișiere în `.cache/` (gitignored)
- Mesaj UI scurt; log tehnic **fără cheie** și fără dump brut în interfață
- Sezonul ales din `league-list` este **cel mai recent**, nu primul din listă (care e cel mai vechi)

Erori mapate pentru utilizator: cheie invalidă, limită de cereri, ligi nealese, eroare generică FootyStats.

Test LIVE (nu afișează cheia): `python scripts/test_footystats_live.py`

---

## 8. Tech stack

| Strat | Tehnologie | Versiune / notă |
| --- | --- | --- |
| Limbaj | Python | **3.12** (verificat 3.12.10 pe Windows) |
| UI | Streamlit | `>=1.39.0,<2` — o singură pagină, fără React/FastAPI |
| HTTP | httpx | `>=0.27.0,<1` |
| Schema date | Pydantic v2 | `>=2.8.0,<3` |
| Excel | openpyxl | `>=3.1.5,<4` — scrie celule, **nu** evaluează formule |
| Registru modele | YAML (PyYAML) | `config/model_registry.yaml` |
| Config | python-dotenv | `.env` |
| Teste | pytest | `>=8.3.0,<9` — 12 teste, trec fără cheie API |
| Fusuri orare | tzdata | `Europe/Bucharest` |
| Container | Docker | `python:3.12-slim`, port **8501** |
| Recalcul server | LibreOffice | Stub în `src/recalc/libreoffice.py`, **enabled=False** |
| OS țintă | Windows 10/11 | Dezvoltare; Docker pentru publicare ulterioară |

**Nu este folosit:** React, FastAPI, bază de date, ORM, autentificare OAuth/Clerk, Redis.

### 8.1 Structura de fișiere

```
Pontifybet/
├── app.py                      # UI Streamlit
├── requirements.txt
├── Dockerfile
├── config/
│   ├── settings.py             # mediu, căi, mock/live
│   └── model_registry.yaml     # mapare celule
├── src/
│   ├── pipeline.py             # orchestrare
│   ├── api/                    # client + mock + cache
│   ├── models/match_data.py    # Indicator + MatchData
│   ├── validation/validator.py
│   ├── adapters/               # over05, double_chance, corners
│   ├── excel/                  # generator + integritate
│   ├── security/auth.py
│   └── recalc/libreoffice.py   # stub
├── templates/                  # 3 xlsx read-only la runtime
├── modele_analize/             # originale + metodologie (docx)
├── mocks/                      # JSON de test
├── tests/
├── scripts/                    # inspect_template, test_footystats_live
├── docs/                       # inventar, acceptanță, acest PSD
├── outputs/                    # gitignored, temporar
└── .cache/                     # gitignored
```

---

## 9. Interfață

O pagină, layout wide, fără grafice, animații sau meniuri extra.

1. **Login** — titlu Pontifybet, câmp parolă, buton Intră.
2. **Zonă principală** — titlu, instrucțiune scurtă, banner recalcul Excel, caption mod MOCK/LIVE, butoane **Listează meciurile** și **Generează analiza**, tabel meciuri (ligă, oră, echipe, bife, sortare), bară de progres, tabel validare, descărcare ZIP.
3. **Sidebar Filtre** — dată, fus orar, ligi, modele.

Culori semantice în tabel (text): verde = valid, galben = pending, roșu = blocat.

---

## 10. Securitate și conformitate

- Aplicație **privată**, o parolă unică (nu multi-user).
- Comparare parolă timing-safe (`hmac.compare_digest`).
- Cheia API nu apare în Excel, loguri, Git, UI.
- `.env`, `.streamlit/secrets.toml`, `outputs/`, `.cache/` sunt gitignored.
- Datele FootyStats trebuie folosite conform licenței/abonamentului; **fără redistribuire**.
- Dockerfile nu bake-uiește secretele; se trimit cu `-e` la rulare.
- Streamlit: `gatherUsageStats = false`.

Dacă `APP_PASSWORD` lipsește, login-ul trece (convenție de dezvoltare locală). Înainte de orice publicare, parola **trebuie** setată.

---

## 11. Rulare, testare, publicare

### 11.1 Local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

URL implicit: http://localhost:8501

### 11.2 Docker

```powershell
docker build -t pontifybet .
docker run --rm -p 8501:8501 -e APP_PASSWORD=parola-ta -e FORCE_MOCK=true pontifybet
```

### 11.3 Teste

`pytest -q` — toate testele trebuie să treacă fără cheie API. Acoperă: MOCK client, sentinel `-1` ≠ 0, registry, validator (inclusiv blocare G0 Cornere pe Real Madrid vs Sevilla), adaptoare + integritate formule, pipeline ZIP.

Acceptanța Etapa 10 este documentată în `docs/etapa10_acceptanta.md` (PASS automat + UI). Rămâne verificarea umană: deschiderea ZIP-ului în Microsoft Excel pentru recalcul.

### 11.4 Publicare (neexecutată în MVP)

Instrucțiuni scurte în `docs/publicare_render_railway.md` pentru Render sau Railway (Docker, port 8501, env vars). Repo-ul trebuie să rămână **privat**. Nu s-a făcut push/deploy ca parte a MVP-ului.

---

## 12. Constrângeri de produs

1. **Sursă unică:** FootyStats. Lipsă G0 → blocare, nu interpolare.
2. **Integritate Excel:** 0 formule schimbate, 0 praguri mutate, 0 foi șterse/redenumite.
3. **Recalcul:** responsabilitatea operatorului, în Microsoft Excel.
4. **Extensibilitate:** al 4-lea model = YAML + adaptor nou, nu rescriere generator.
5. **Windows-first** pentru operator; Docker pentru gazduire.
6. Git local inițializat; fără push automat.

---

## 13. Riscuri și dependențe

| Risc | Impact | Mitigare actuală |
| --- | --- | --- |
| Limită / cheie FootyStats | Fără date LIVE | Mod MOCK; mesaj 429; cache |
| Ligi nealese pe contul API | `todays-matches` gol | Warning + link API Settings |
| Formule neschimbate dar neevaluate | Output „gol” până la deschiderea în Excel | Banner UI + documentație |
| Șablon Cornere așteaptă Football-Data | G0 poate bloca multe meciuri | Blocaj explicit, fără inventare |
| Parolă unică | Nu scalează la mai mulți utilizatori | Acceptabil pentru MVP privat |
| openpyxl vs Excel real | Diferențe de serial dată / formatare | Verificare umană în Excel |

---

## 14. Glosar

| Termen | Semnificație |
| --- | --- |
| **G0** | Input obligatoriu; lipsa lui blochează (meci, model) |
| **Indicator** | Valoare + metadate de trasabilitate, nu un număr gol |
| **Whitelist** | Celulele pe care adaptorul are voie să le scrie |
| **Fingerprint** | Amprentă foi + formule, comparată înainte/după scriere |
| **MOCK** | Date locale de test, fără API |
| **De-vig** | Transformarea cotelor 1X2 în probabilități fără marja casei |
| **Cadru v5** | Metodologia unificată de analiză și risc (`modele_analize/`) |
| **Matrice v4** | Reguli pentru lipsă date / statusuri de readiness |

---

## 15. Documente conexe

- `README.md` — instalare și folosire
- `docs/etapa1_inventar.md` — foi, input, protecții șabloane
- `docs/metodologie_rezumat.md` — statusuri Data Readiness
- `docs/etapa_footystats_live.md` — endpoint-uri LIVE
- `docs/etapa10_acceptanta.md` — checklist PASS
- `docs/publicare_render_railway.md` — deploy ulterior
- `.cursor/plans/pontifybet_mvp_plan_b6ac23ec.plan.md` — planul de implementare MVP
- `config/model_registry.yaml` — contractul de mapare celule

---

*Sfârșit PSD v1.0 — reflectă starea reală a codului Pontifybet MVP la 17 septembrie 2026.*
