from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx, logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

API_URL = "https://aviationweather.gov/api/data/metar?format=json"

@app.get("/api/metar")
async def metar(ids: str = "UAAA"):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{API_URL}&ids={ids}")
            r.raise_for_status()
            data = r.json()
        return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})
    except httpx.HTTPStatusError as e:
        logging.exception("HTTP error fetching METAR")
        return JSONResponse(content={"error": f"METAR fetch failed: {str(e)}"}, status_code=502)
    except Exception as e:
        logging.exception("Unexpected error in /api/metar")
        return JSONResponse(content={"error": str(e)}, status_code=500)
