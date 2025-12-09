\
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx, os, logging, traceback
import google.generativeai as genai

app = FastAPI()
logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        logging.exception("Failed to configure google.generativeai: %s", e)

async def fetch_json(url: str, timeout: float = 15.0):
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()

def build_prompt(metar_raw: str, taf_raw: str) -> str:
    prompt = (
    "Ты — авиационный метеоролог. "
    "На основе METAR и TAF составь краткий и понятный прогноз для пилота на ближайшие 6 часов.\n"
    "Ответ должен содержать пункты:\n"
    "1) Ветер — изменения и порывы\n"
    "2) Видимость — улучшение/ухудшение\n"
    "3) Облачность/потолок\n"
    "4) Опасные явления\n"
    "И краткий итог (1–2 предложения).\n\n"
    f"METAR: {metar_raw}\n"
    f"TAF: {taf_raw}\n"
)
    return prompt

@app.get("/api/forecast")
async def forecast(icao: str = "UAAA"):
    if not API_KEY:
        logging.error("GEMINI_API_KEY not set in environment")
        return JSONResponse(content={"error": "GEMINI_API_KEY not configured on server"}, status_code=500)

    try:
        metar_url = f"https://aviationweather.gov/api/data/metar?ids={icao}&format=json"
        taf_url = f"https://aviationweather.gov/api/data/taf?ids={icao}&format=json"
        mdata = await fetch_json(metar_url)
        tdata = await fetch_json(taf_url)

        metar = (mdata[0] if isinstance(mdata, list) and len(mdata)>0 else mdata)
        taf = (tdata[0] if isinstance(tdata, list) and len(tdata)>0 else tdata)

        metar_raw = metar.get("rawOb") if isinstance(metar, dict) else str(metar)
        taf_raw = taf.get("rawTAF") if isinstance(taf, dict) else str(taf)

        prompt = build_prompt(metar_raw, taf_raw)
        logging.info("Sending prompt to Gemini; prompt length: %d", len(prompt))

        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(prompt)

# Fallback: получить текст в зависимости от структуры
if hasattr(resp, "text") and resp.text:
    ai_text = resp.text
else:
    try:
        ai_text = str(resp)
    except:
        ai_text = "Модель не вернула текст."



        ai_text = None
        if hasattr(resp, "text") and resp.text:
            ai_text = resp.text
        else:
            try:
                if isinstance(resp, dict):
                    c = resp.get("candidates") or resp.get("outputs") or []
                    if c and isinstance(c, list):
                        first = c[0]
                        ai_text = first.get("content") or first.get("text") or str(first)
                else:
                    ai_text = str(resp)
            except Exception:
                ai_text = str(resp)

        if not ai_text:
            ai_text = "Модель вернула пустой ответ."

        return JSONResponse(content={"icao": icao, "forecast": ai_text}, headers={"Access-Control-Allow-Origin": "*"})
    except httpx.HTTPStatusError as he:
        logging.exception("Upstream HTTP error: %s", he)
        return JSONResponse(content={"error": f"Upstream fetch failed: {str(he)}"}, status_code=502)
    except Exception as e:
        logging.exception("Unhandled exception in /api/forecast: %s", e)
        tb = traceback.format_exc()
        return JSONResponse(content={"error": "Internal server error", "details": str(e), "trace": tb}, status_code=500)
