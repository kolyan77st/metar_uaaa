MONOREPO Variant C — frontend + backend (ready for Vercel)

Structure:
- frontend/index.html  (UI)
- frontend/assets/icons/*.svg
- backend/api/metar.py
- backend/api/taf.py
- backend/api/forecast.py  (Gemini Flash)

Deploy:
1. Push this repo to GitHub.
2. On Vercel, import the repository.
3. In Project Settings -> Environment Variables add:
   GEMINI_API_KEY = <your server API key from Google AI Studio>
4. Redeploy the project.
5. Test endpoints:
   /api/metar?ids=UAAA
   /api/taf?ids=UAAA
   /api/forecast?icao=UAAA
