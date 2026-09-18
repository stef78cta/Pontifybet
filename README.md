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

**Important:** Microsoft Excel recalculează formulele la prima deschidere. Valorile din fișier nu sunt rezultate proaspăt recalculate de aplicație.

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
- `config/model_registry.yaml` — maparea celulelor  
- `templates/` — copii ale șabloanelor (read-only la runtime)  
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
