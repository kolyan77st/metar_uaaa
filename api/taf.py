from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx

app=FastAPI()

@app.get('/api/taf')
async def taf(ids:str='UAAA'):
    url=f'https://aviationweather.gov/api/data/taf?ids={ids}&format=json'
    async with httpx.AsyncClient() as c:
        r=await c.get(url)
        return JSONResponse(content=r.json(),headers={'Access-Control-Allow-Origin':'*'})
