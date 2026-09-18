# Etapa 1 — Inventar verificat

**Data:** 2026-09-17  
**Python:** 3.12.10 (instalat pe Windows)  
**Șabloane runtime:** `templates/` (copii read-only; originalele rămân în `modele_analize/`)

## Fișiere șablon (3 piloți)

| Model | Fișier în templates/ | Dimensiune |
|-------|----------------------|------------|
| Over 0.5 V4 | `1_model_analiza_over0.5_optimizat_V4.xlsx` | ~485 KB |
| Șansă Dublă V2 | `11_model_analiza_pariu_sansadubla_optimizat_V2.xlsx` | ~205 KB |
| Cornere Multi-Line V14 | `6_model_analiza_cornere_multiline_optimizat_V14.xlsx` | ~1.6 MB |

## Documente metodologice

- `modele_analize/Cadru_unificat_analiza_si_risc_pariuri_v5.docx`
- `modele_analize/Matrice_lipsa_date_v4.docx`

## Over 0.5 — structură

- **Foi (20):** Dashboard, Analize meciuri, Setari model, Surse cercetare, Backtest, Risk_Classification, ZeroMass_Gate_v4/v5, Frozen_Predictions, Settlement, DOCUMENTATIE_MODEL, CHANGELOG_VERSIUNI, etc.
- **Input principal:** `Analize meciuri` — 1 rând = 1 meci; header rând 3; date de la rândul 4; coloane A–BI input; BJ+ formule.
- **Nu scrie:** Setari model (praguri/ponderi), foile de output (Dashboard, Risk_*, ZeroMass_*, etc.).
- **VBA / Charts / Pivot / Named ranges:** absente.
- **Data validation:** pe intervale EV/FY/GA (coloane output/derivate).
- **Excel Tables:** 2.

## Șansă Dublă — structură

- **Foi (15):** Parametri, Input_Meci, Model_1X2, Draw_Risk, Loss_Risk, Double_Chance, Backtest, Dashboard, P0_Gates_v2, Uncertainty_v2, Surse_Date, DOCUMENTATIE_MODEL, etc.
- **Input:** `Input_Meci` (vertical B=gazde, C=oaspeți), `Surse_Date` (G0/G1 statusuri), `Model_1X2` rânduri 6–7 (probabilități modele externe).
- **Nu scrie:** Parametri, Double_Chance, Draw_Risk, Loss_Risk, P0_Gates_v2, Dashboard.
- **G-level:** formalizat în Surse_Date coloana B (G0 / G1 / CONDITIONAL).
- **VBA / Charts / Pivot / Named ranges:** absente.

## Cornere V14 — structură

- **Foi (13):** Dashboard, Config_v6, Analiza_Linii, Motor_Meciuri, Core_Nativ, Distributie, Input_Meci, Istoric_Nativ, Surse_Import, Calibrare_Linii, OOS_Predictii, Verificari, Documentatie.
- **Input:** `Input_Meci` A–AG de la rândul 6; opțional Surse_Import.
- **Nu scrie:** Config_v6, Analiza_Linii, Motor_Meciuri, Core_Nativ, Distributie, Dashboard.
- **G0:** 12 valori native cornere (season / home-away / recent × for & against) + sample.
- **Excel Tables:** 11. VBA/Charts/Pivot/Named ranges: absente.
- **Notă sursă:** template menționează Football-Data; MVP folosește doar FootyStats; lipsă G0 → NOT AVAILABLE (fără inventare).

## Decizii implicite confirmate

1. Over 0.5 / Cornere: un workbook pe rulare (mai multe meciuri pe rânduri).
2. Șansă Dublă: un workbook pe meci.
3. LibreOffice recalcul: stub dezactivat.
4. Registry: YAML.

## Checklist Etapa 1

- [x] Python 3.12 disponibil
- [x] 3 șabloane în `templates/`
- [x] Originalele din `modele_analize/` netouchate
- [x] Inventar foi / input / protecție documentat
- [x] Metodologie citită (rezumat în docs/metodologie_rezumat.md)
