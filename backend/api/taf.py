from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx, logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

API_URL = "https://aviationweather.gov/api/data/taf?format=json"

@app.get("/api/taf")
async def taf(ids: str = "UAAA"):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{API_URL}&ids={ids}")
            r.raise_for_status()
            data = r.json()
        return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})
    except httpx.HTTPStatusError as e:
        logging.exception("HTTP error fetching TAF")
        return JSONResponse(content={"error": f"TAF fetch failed: {str(e)}"}, status_code=502)
    except Exception as e:
        logging.exception("Unexpected error in /api/taf")
        return JSONResponse(content={"error": str(e)}, status_code=500)
