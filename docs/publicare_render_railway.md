# Publicare ulterioară (Render / Railway)

Aceste instrucțiuni sunt pentru **după** ce MVP-ul rulează local. Nu publica încă în prima etapă.

## Pregătire comună

1. Creează un repository GitHub privat cu codul (fără `.env`, fără chei).  
2. Asigură-te că `Dockerfile` din rădăcină funcționează local.  
3. Pregătește variabilele de mediu:
   - `APP_PASSWORD`
   - `FOOTYSTATS_API_KEY` (doar dacă vrei mod LIVE)
   - opțional `FORCE_MOCK=true` pentru o demonstrație fără API

## Render

1. Creează un cont pe https://render.com  
2. New → Web Service → conectează repo-ul GitHub  
3. Environment: Docker  
4. Adaugă Environment Variables (`APP_PASSWORD`, etc.)  
5. Port: `8501`  
6. Deploy — verifică URL-ul generat și parola  

## Railway

1. Cont pe https://railway.app  
2. New Project → Deploy from GitHub  
3. Adaugă variabilele de mediu  
4. Expose port `8501`  
5. Deschide domeniul generat  

## Atenții

- Ține serviciul **privat** (parolă + fără indexare publică a datelor).  
- Respectă termenii FootyStats.  
- Nu încărca șabloane Excel cu date reale sensibile în repo public.
