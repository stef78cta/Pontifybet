# Mesaj pentru Cursor

Implementează în PontifyBet motorul Șansă Dublă din fișierul `11_model_analiza_pariu_sansadubla_optimizat_V2(1).xlsx`, conform manualului și anexelor din acest pachet. Vreau identitate cu formulele Excel pentru aceleași inputuri și metadate, inclusiv sursele, release-ul, cele trei selecții, scorul, nivelul și eligibilitatea.

Această cerere autorizează explicit portarea calculelor acestui model în cod, față de MVP-ul anterior cu Excel ca motor. Păstrează Python 3.12, Streamlit, structura și celelalte modele existente. Nu adăuga infrastructură sau surse de date noi.

Începe prin a verifica repository-ul `C:\_Software\SAAS\Pontifybet`, instrucțiunile locale și implementările reale din `src/pipeline.py`, `src/adapters/double_chance.py`, `src/validation/validator.py`, `config/model_registry.yaml` și `src/excel/`. Aceste căi sunt harta proiectului de verificat, nu dovada că fișierele sau interfețele există în checkout. Alege modulul nou pentru motor după pattern-ul existent și documentează exact fișierele schimbate.

Fixează referința SHA-256 din manifest. Implementează distribuțiile externe și metadatele ca inputuri explicite. Workbook-ul nu definește estimarea Dixon–Coles/Elo din statistici; nu inventa distribuții, coeficienți, endpoint-uri sau câmpuri FootyStats. Dacă furnizarea distribuțiilor nu există în repository, expune lipsa prin stările modelului și permite rularea fixture-urilor sintetice în teste/MOCK. Nu prezenta acest lucru ca analiză LIVE completă.

Tradu formulele și ordinea ramurilor din anexă. Separă validarea Surse_Date, integritatea distribuțiilor/fixture-ului, normalizarea, blend-ul, haircut-ul, gates, fragilitatea, release-ul pe selecție și selectorul. Păstrează `PENDING`, `INVALID`, `CRITICAL MISSING` și contextul `CONDITIONAL` distincte. Nu transforma PENDING în nivel 5. Nu aplica pragurile P_adj de 82/76% selecției 12, unde formula N6 nu le folosește. Nu confunda Pfail_DC fără haircut cu draw_adj din gate. Respectă rotunjirile explicite și nu adăuga epsiloni la praguri.

Nu modifica originalele din `modele_analize/`, formule, praguri, foi sau configurațiile altor modele. Nu reintroduce EV, cotele DC sau confirmarea generică a loturilor ca filtre ale verdictului. Nu considera SMALL SAMPLE hard fail dacă priorul este documentat. Pentru API, −1/−2/null rămân indisponibilitate, niciodată zero inventat. Nu scrie peste formulele D8/G9/H9 din Surse_Date ori B8:D8 din Model_1X2. Dacă exportul nu respectă integritatea: `EXPORT BLOCAT. Motiv: …`.

Integrează rezultatele fără a confunda un output nullable cu 0. Afișează stare date, P_adj, Pfail, gates, scor, nivel, verdict și eligibilitate. Aplică AA pentru clasamentul general și AE pentru DEFENSIV. Nu inventa sortare sau tie-break în motor. Menține o singură sursă de adevăr pentru rezultate; un eventual Excel exportat trebuie să primească aceleași inputuri și să păstreze formulele originale.

Folosește `cazuri_test.json`: 37 de fixture-uri complete, cu rezultate intermediare și finale. Adaugă testele în structura reală de teste a repository-ului. Verifică și frontierele din secțiunea 6.4, cotă invariantă, audit 1X izolat și lipsa unui gate OOS nou. Nu recalcula valorile așteptate cu motorul pe care îl testezi.

Verificări:

1. Din folderul pachetului: `powershell -NoProfile -ExecutionPolicy Bypass -File .\verifica_excel.ps1 -Workbook "CALEA_REALA_A_FISIERULUI_SURSA.xlsx"`. Înlocuiește calea prin fișierul găsit și verificat prin hash. Rezultat cerut: PASS, 37 de cazuri, fără diferențe. Dacă Excel nu este disponibil, marchează explicit verificarea ca neexecutată; nu declara echivalență Excel certificată.
2. Din repository: `pytest -q` — PASS fără cheia API, inclusiv fixture-urile și frontierele.
3. `streamlit run app.py` — pagina `http://localhost:8501` pornește, iar fixture-ul baseline produce 1X: P_adj=0.92, scor16, nivel1, DEFENSIV; X2: P_adj=0.165, scor100, nivel5, NO BET; 12: P_adj=0.885, scor22, nivel2, PRUDENT.

La final prezintă fișierele modificate, rezultatele verificărilor și orice lipsă concretă din furnizarea inputurilor LIVE. Nu schimba pragurile pentru a trece testele.
