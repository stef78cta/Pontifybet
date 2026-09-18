# Pachet tehnic Pontifybet Over 0.5 V4

Manualul este autoritatea explicativă; formula_manifest.json este transcrierea formulelor sursă.
Nu modifica workbook-ul pentru a corespunde documentației istorice contradictorii.

- workbook_inventory.json: toate celulele populate și metadata extrasă din cele 20 foi.
- formula_manifest.json: 14.026 formule literale și referințele lor.
- formula_ast.json: arbori ai expresiilor pentru cele 108 formule ale rândului 4.
- schema.json: coloane, tipuri semantice și roluri de date.
- golden_fixtures.json: 5 DEMO, inputuri și rezultate cache + simulate.
- simulations.json: 13 scenarii modificate în memorie, fără certificare Microsoft Excel.
- verification_report.json: 540 comparații și diferențe numerice.
- audit_formula_evaluator.py: evaluator folosit în audit, nu motor Excel general sau cod de producție.

Pentru reproducerea auditului, creează structura:
<root>/analysis/verify_model.py (copia audit_formula_evaluator.py)
<root>/upload/1_model_analiza_over0.5_optimizat_V4.xlsx (sursa originală)
Rulează python analysis/verify_model.py într-un mediu cu openpyxl.
Evaluatorul implementează numai funcțiile necesare nucleului și convențiile TEXT ale cache-ului;
nu execută toate funcțiile de sumarizare și nu validează locale-ul Microsoft Excel.
Rezultat așteptat: Formula comparisons 540 PASS 540 FAIL 0.

Foaia Excel originală nu este duplicată în acest pachet. Folosește atașamentul cu hash-ul din manual.
Datele sunt DEMO; nu reprezintă recomandări curente sau evaluare predictivă OOS.
