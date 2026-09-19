# Pachet tehnic Cornere Multiline V14

Începe cu Manual_tehnic_Cornere_Multiline_V14.md. Anexa_schema_si_formule.md descrie schema și formulele reprezentative. Formulele complete sunt în formule_integrale.csv; celule_integrale.json include și inputuri, cache și dependențe.

Pentru verificarea fixture-urilor rulează `python verifica_replay.py`. Nu este un motor de producție. Scope-ul este limitat explicit la cele trei exemple REPLAY originale. Originalul XLSX nu este modificat și nu este inclus în acest pachet; folosește fișierul atașat cu SHA-256 din manifest_sursa.json.

Rezultatele din expected_42_selectii_cache.json sunt valori SALVATE în XLSX, confirmate numeric prin LibreOffice și harness. Rezultatele Python sunt separate în rezultate_replay_recalculate.json. Limitele și diferențele auxiliare sunt documentate în manual și raport_recalculare.json.

Tipuri: JSON null în cache înseamnă celulă goală/rezultat gol, nu zero. Probabilitățile sunt fracții 0–1. Toate CSV-urile sunt UTF-8 cu BOM și separator virgulă; pentru formule folosește un cititor CSV care păstrează textul, fără executarea lor ca formule într-un spreadsheet. Coloanele sunt citate corect de formatul CSV.

Workbook-ul are 85.647 formule și 13 foi. Baza GitHub este main la bda2a1c632d916f1dfaf4d94eba22d085bb6a2f4. Pachetul nu este un audit exhaustiv al aplicației și nu conține modificări de cod ale repository-ului.
