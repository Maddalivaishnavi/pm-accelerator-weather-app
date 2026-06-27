"""
Wraps Open-Meteo's Forecast API (current + future) and Archive API
(historical). No API key required for either.

Forecast docs: https://open-meteo.com/en/docs
Archive docs:  https://open-meteo.com/en/docs/historical-weather-api
"""
from datetime import date, datetime, timedelta
from typing import List, Optional

import httpx

from app.schemas import CurrentWeather, DailyForecast
from app.services.weather_codes import describe_weather_code

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Open-Meteo's forecast endpoint can also serve recent past days (via the
# past_days param) and up to 16 days ahead. Anything older than this we
# route to the archive endpoint instead.
MAX_PAST_DAYS_VIA_FORECAST = 92
MAX_FORECAST_DAYS_AHEAD = 16


async def get_current_and_forecast(
    latitude: float, longitude: float, forecast_days: int = 5
) -> tuple[CurrentWeather, List[DailyForecast]]:
    """Current conditions + the next `forecast_days` days."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                   "wind_speed_10m,weather_code,is_day",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                 "precipitation_probability_max,weather_code",
        "timezone": "auto",
        "forecast_days": forecast_days,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    cur = data.get("current", {})
    current = CurrentWeather(
        temperature_c=cur.get("temperature_2m"),
        feels_like_c=cur.get("apparent_temperature"),
        humidity_pct=cur.get("relative_humidity_2m"),
        wind_speed_kmh=cur.get("wind_speed_10m"),
        weather_code=cur.get("weather_code"),
        description=describe_weather_code(cur.get("weather_code")),
        is_day=bool(cur.get("is_day")) if cur.get("is_day") is not None else None,
    )

    daily = data.get("daily", {})
    forecast = _zip_daily(daily)
    return current, forecast


def _zip_daily(daily: dict) -> List[DailyForecast]:
    dates = daily.get("time", [])
    out = []
    for i, d in enumerate(dates):
        code = _at(daily.get("weather_code"), i)
        out.append(
            DailyForecast(
                date=date.fromisoformat(d),
                temp_max_c=_at(daily.get("temperature_2m_max"), i),
                temp_min_c=_at(daily.get("temperature_2m_min"), i),
                precipitation_mm=_at(daily.get("precipitation_sum"), i),
                precipitation_probability=_at(daily.get("precipitation_probability_max"), i),
                weather_code=code,
                description=describe_weather_code(code),
            )
        )
    return out


def _at(lst: Optional[list], i: int):
    if not lst or i >= len(lst):
        return None
    return lst[i]


async def get_temperature_range(
    latitude: float, longitude: float, start_date: date, end_date: date
) -> List[DailyForecast]:
    """
    Returns one DailyForecast row per day in [start_date, end_date].

    Open-Meteo splits "recent past + future" (forecast endpoint, via the
    past_days/forecast_days params) from "deep history" (archive endpoint).
    We pick whichever endpoint(s) the requested range actually needs and
    merge the results, so the caller doesn't have to think about it.
    """
    today = date.today()
    cutoff = today - timedelta(days=MAX_PAST_DAYS_VIA_FORECAST)

    results: List[DailyForecast] = []

    # Portion of the range older than the forecast endpoint's lookback window
    # -> archive API
    if start_date < cutoff:
        archive_end = min(end_date, cutoff - timedelta(days=1))
        if start_date <= archive_end:
            results.extend(
                await _fetch_archive_range(latitude, longitude, start_date, archive_end)
            )
        range_start_for_forecast = cutoff
    else:
        range_start_for_forecast = start_date

    # Portion within the forecast endpoint's range (recent past -> future)
    if range_start_for_forecast <= end_date:
        results.extend(
            await _fetch_forecast_range(
                latitude, longitude, range_start_for_forecast, end_date
            )
        )

    results.sort(key=lambda r: r.date)
    return results


async def _fetch_archive_range(
    latitude: float, longitude: float, start_date: date, end_date: date
) -> List[DailyForecast]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(ARCHIVE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
    return _zip_daily(data.get("daily", {}))


async def _fetch_forecast_range(
    latitude: float, longitude: float, start_date: date, end_date: date
) -> List[DailyForecast]:
    today = date.today()
    past_days = max(0, (today - start_date).days)
    forecast_days_ahead = max(0, (end_date - today).days) + 1
    forecast_days_ahead = min(forecast_days_ahead, MAX_FORECAST_DAYS_AHEAD)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
        "timezone": "auto",
        "past_days": past_days,
        "forecast_days": forecast_days_ahead,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    all_days = _zip_daily(data.get("daily", {}))
    return [d for d in all_days if start_date <= d.date <= end_date]
