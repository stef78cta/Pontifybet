# Pontifybet MVP

Aplicație **privată** în Python + Streamlit care generează fișiere Excel de analiză a meciurilor, pe baza datelor FootyStats și a șabloanelor Excel existente.

> Utilizarea datelor FootyStats trebuie să respecte licența și termenii abonamentului tău. Nu redistribui datele FootyStats.

## Ce face aplicația

1. Selectezi data, ligile, modelele și fusul orar  
2. Apăși **Listează meciurile**, bifezi unul / mai multe / toate, sortezi după ligă sau oră  
3. Apăși **Generează analiza**  
4. Aplicația colectează datele, le validează, completează **copii** ale șabloanelor  
5. Descarci un ZIP cu fișierele Excel + raportul de validare  

Modele pilot: **Over 0.5**, **Șansă Dublă**, **Cornere Multi-Line V14**.

## Cerințe

- Windows 10/11  
- Python **3.12**  
- (Opțional) Docker Desktop  
- Microsoft Excel pentru recalcularea formulelor la deschiderea fișierelor  

## Instalare pe Windows (pași numerotați)

### 1. Instalează Python 3.12

1. Descarcă de pe https://www.python.org/downloads/release/python-31210/  
2. Rulează installer-ul  
3. Bifează **Add python.exe to PATH**  
4. Deschide un terminal nou PowerShell și verifică:

```powershell
python --version
```

Trebuie să vezi ceva de forma `Python 3.12.x`.

### 2. Deschide proiectul în Cursor IDE

1. Deschide Cursor  
2. File → Open Folder → selectează `C:\_Software\SAAS\Pontifybet`  

### 3. Creează mediul virtual

În terminalul Cursor (folderul proiectului):

```powershell
cd C:\_Software\SAAS\Pontifybet
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Dacă PowerShell blochează scripturile:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

apoi reactivează `.venv`.

### 4. Instalează dependențele

```powershell
pip install -r requirements.txt
```

### 5. Configurează parolele / secretele (fără a le pune în chat)

Copiază exemplul:

```powershell
copy .env.example .env
```

Editează `.env` și setează:

```
APP_PASSWORD=parola-ta-privata
FOOTYSTATS_API_KEY=cheia-ta-din-footystats
```

Cheia API este **obligatorie**. Fără ea, aplicația nu poate lista ligi sau meciuri.

**Alternativă Streamlit (local):** creează fișierul `.streamlit\secrets.toml`:

```toml
APP_PASSWORD = "parola-ta-privata"
FOOTYSTATS_API_KEY = "cheia-ta"
```

### 5b. Test conexiune LIVE (date reale)

1. Ia cheia de la https://footystats.org/api/u/api-settings  
2. Alege ligile pe care le vrei (fără ligi alese, `todays-matches` e gol)  
3. În `.env`: `FOOTYSTATS_API_KEY=...`  
4. Rulează:

```powershell
python scripts/test_footystats_live.py
```

Trebuie să vezi `PASS  test-call` și numărul de ligi/meciuri. Scriptul **nu** afișează cheia.

### 6. Pornește aplicația

```powershell
streamlit run app.py
```

Browserul se deschide de obicei la http://localhost:8501  
Introdu parola din `APP_PASSWORD`.

### 7. Rulează testele

```powershell
pytest -q
```

Toate testele trebuie să treacă (PASS) fără cheie API. Fixture-urile din `mocks/` sunt folosite doar de pytest.

## Folosire rapidă

1. În sidebar: alege data meciurilor  
2. Selectează ligile și cele 3 modele  
3. Apasă **Listează meciurile**, bifează meciurile dorite  
4. Apasă **Generează analiza**  
5. Descarcă ZIP-ul  

**Important:** verdictele apar în aplicație imediat după pasul 4; toate cele trei modele sunt evaluate în Python din formulele originale. Exportul este opțional și nu recalculează nimic — fișierele conțin inputurile și rezultatele deja calculate.

## Istoric și rezultate (SQLite)

Fiecare recomandare pre-match este memorată imuabil în `data/pontifybet.sqlite3`. Directorul `data/` este **persistent** și nu este atins de curățarea `outputs/`.

- **Over 0.5 V4**, **Șansă Dublă V2** și **Cornere Multi-Line V14** sunt înghețate (`FROZEN_PREMATCH`) direct la generarea analizei: verdictul fiecăruia este evaluat din formulele workbook-ului, în Python.
- Cornere persistă toate cele 14 linii per meci (șase Over, opt Under), pe `market` și `line`.
- `PENDING_EXCEL_RECALC` rămâne doar ca stare istorică, pentru înregistrările Cornere salvate înainte de motorul V14. Ele se completează în continuare din secțiunea *Istoric și rezultate → Import verdicte Cornere din Excel recalculat*; un workbook care nu corespunde șablonului este respins cu `IMPORT BLOCAT`. Atenție: recalcularea externă cere un Excel cu funcții de matrice dinamică (Microsoft 365 / Excel 2024), pentru că `Core_Nativ` folosește `FILTER`.

După terminarea meciurilor, butonul **Actualizează rezultate** preia scorul și cornerele oficiale din FootyStats (`/match`), le salvează în `match_results` și calculează settlement-ul HIT / MISS. Recomandarea înghețată nu se modifică niciodată, iar datele lipsă devin `RESULT DATA UNAVAILABLE`, nu MISS.

Inspecție rapidă a bazei:

```powershell
python scripts/show_history_schema.py
```

Baza poate fi redirecționată cu `PONTIFYBET_DB_PATH` (folosit și de teste, ca istoricul real să rămână curat).

## Docker (local)

```powershell
docker build -t pontifybet .
docker run --rm -p 8501:8501 -e APP_PASSWORD=parola-ta -e FOOTYSTATS_API_KEY=cheia-ta pontifybet
```

Deschide http://localhost:8501

## Structura proiectului

- `app.py` — interfața Streamlit  
- `src/api` — conector FootyStats + MOCK  
- `src/models` — schema MatchData  
- `src/validation` — validator  
- `src/adapters` — adaptoarele celor 3 modele  
- `src/excel` — generator + integritate formule  
- `src/history` — istoric SQLite, settlement, backtest  
- `config/model_registry.yaml` — maparea celulelor  
- `templates/` — copii ale șabloanelor (read-only la runtime)  
- `data/` — istoric SQLite persistent (nu se comite)  
- `mocks/` — răspunsuri de test  
- `docs/` — inventar, metodologie, publicare  

## Codex / terminal

Aceleași comenzi ca mai sus, din rădăcina proiectului, cu `.venv` activat.

## Publicare ulterioară

Vezi `docs/publicare_render_railway.md` (instrucțiuni scurte, **fără** publicare în această etapă).

## Securitate

- Nu comite `.env` sau `.streamlit/secrets.toml`  
- Nu pune cheia API în Excel, loguri sau repository  
- Aplicația este privată (parolă unică)
