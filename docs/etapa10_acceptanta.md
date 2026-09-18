# Etapa 10 — Checklist acceptanță

## Automat (pytest)

- [x] PASS — `pytest -q` (12 teste)
- [x] PASS — modul MOCK fără cheie API
- [x] PASS — `-1` nu devine 0
- [x] PASS — integritate formule Over 0.5 / Șansă Dublă / Cornere
- [x] PASS — G0 critic cornere blochează Real Madrid vs Sevilla
- [x] PASS — pipeline generează ZIP

## Manual / UI (Streamlit local)

- [x] PASS — `streamlit run app.py` pornește pe http://localhost:8501
- [x] PASS — ecran parolă
- [x] PASS — UI: dată, ligi, meciuri, modele, Generează analiza
- [x] PASS — progres + tabel validare + Descarcă fișierele Excel (5 fișiere)
- [x] PASS — mențiune recalcul Microsoft Excel
- [x] PASS — exemplu ZIP în `docs/exemple/pontifybet_mock_example.zip`

## Livrabile

- [x] Cod MVP + requirements.txt
- [x] .env.example + .gitignore
- [x] Dockerfile + README RO
- [x] model_registry.yaml + 3 adaptoare
- [x] mocks + teste
- [x] docs publicare Render/Railway
- [x] git init local (fără push)

## Pași rămași pentru tine

1. Deschide ZIP-ul în Microsoft Excel și lasă formulele să se recalculeze (verificare umană).
2. Când vrei LIVE: pune `FOOTYSTATS_API_KEY` în `.env` și setează `FORCE_MOCK=false`.
3. Schimbă `APP_PASSWORD` din `.env` înainte de orice publicare.
4. Commit pe GitHub la cerere (nu s-a făcut push).
