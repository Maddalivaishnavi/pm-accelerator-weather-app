"""
Open-Meteo Air Quality API — used to satisfy the "additional API
integration" stand-apart requirement (2.2). No API key required.

Docs: https://open-meteo.com/en/docs/air-quality-api
"""
import httpx
from app.schemas import AirQuality

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


async def get_air_quality(latitude: float, longitude: float) -> AirQuality:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "us_aqi,pm2_5,pm10",
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(AIR_QUALITY_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    cur = data.get("current", {})
    return AirQuality(
        us_aqi=cur.get("us_aqi"),
        pm2_5=cur.get("pm2_5"),
        pm10=cur.get("pm10"),
    )
