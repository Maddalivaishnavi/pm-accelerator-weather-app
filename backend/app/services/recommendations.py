"""
Rule-based recommendations — no external API, no AI model, just logic over
the weather data we already fetched. Directly answers the assessment's
prompt: "what should a user consider that isn't obvious?"
"""
from typing import List, Optional

from app.schemas import CurrentWeather, DailyForecast, AirQuality

STORM_CODES = {95, 96, 99}
RAIN_CODES = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82}
SNOW_CODES = {71, 73, 75, 77, 85, 86}
FOG_CODES = {45, 48}


def generate_recommendations(
    current: CurrentWeather,
    forecast: List[DailyForecast],
    air_quality: Optional[AirQuality] = None,
) -> List[str]:
    """Returns a short, prioritized list of plain-language tips."""
    tips: List[str] = []
    today = forecast[0] if forecast else None
    code = current.weather_code

    # Severe conditions first
    if code in STORM_CODES:
        tips.append("⚠️ Thunderstorms expected — postpone outdoor plans if you can.")
    elif code in SNOW_CODES:
        tips.append("❄️ Snowfall expected — watch for slippery roads and sidewalks.")
    elif code in RAIN_CODES or (today and (today.precipitation_probability or 0) >= 50):
        tips.append("☔ Rain is likely — bring an umbrella or waterproof jacket.")
    elif code in FOG_CODES:
        tips.append("🌫️ Foggy conditions — drive carefully and allow extra travel time.")

    # Temperature-based
    if current.temperature_c is not None:
        if current.temperature_c >= 35:
            tips.append("🥵 Very hot — stay hydrated and limit time in direct sun.")
        elif current.temperature_c >= 28 and not tips:
            tips.append("🏃 Warm and clear — good conditions for outdoor activity, just bring water.")
        elif current.temperature_c <= 2:
            tips.append("🧥 Freezing temperatures — dress in layers and watch for ice.")
        elif current.temperature_c <= 8:
            tips.append("🧣 Chilly — a warm jacket is a good idea.")

    # Wind
    if current.wind_speed_kmh is not None and current.wind_speed_kmh >= 35:
        tips.append("💨 Strong winds — secure loose outdoor items, and cycling may be difficult.")

    # Air quality
    if air_quality and air_quality.us_aqi is not None:
        if air_quality.us_aqi > 150:
            tips.append("😮‍💨 Air quality is unhealthy — limit prolonged outdoor exertion.")
        elif air_quality.us_aqi > 100:
            tips.append("😮‍💨 Air quality is moderate-to-poor — sensitive groups should take it easy outdoors.")

    # Default, if nothing notable triggered
    if not tips:
        tips.append("🌤️ Conditions look pleasant — a good day to be outside.")

    return tips[:4]
