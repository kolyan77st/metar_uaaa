from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx,os
import google.generativeai as genai

app=FastAPI()

API_KEY=os.getenv("GEMINI_API_KEY")
if API_KEY: genai.configure(api_key=API_KEY)

async def fetch(url):
    async with httpx.AsyncClient() as c:
        r=await c.get(url)
        r.raise_for_status()
        return r.json()

@app.get('/api/forecast')
async def forecast(icao:str='UAAA'):
    if not API_KEY:
        return JSONResponse({'error':'GEMINI_API_KEY missing'},status_code=500)
    metar=(await fetch(f'https://aviationweather.gov/api/data/metar?ids={icao}&format=json'))[0]
    taf=(await fetch(f'https://aviationweather.gov/api/data/taf?ids={icao}&format=json'))[0]
    prompt=f'METAR: {metar.get("rawOb")}\nTAF: {taf.get("rawTAF")}\nСделай краткий прогноз на 6 часов.'
    r=genai.generate_text(model='gemini-1.5-flash',prompt=prompt)
    text=r.text if hasattr(r,'text') else str(r)
    return JSONResponse({'icao':icao,'forecast':text},headers={'Access-Control-Allow-Origin':'*'})
