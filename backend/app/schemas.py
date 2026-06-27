"""
Pydantic schemas: request/response shapes for the API.
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# ---------- Shared / lookup (non-persisted) schemas ----------

class GeocodeMatch(BaseModel):
    name: str
    country: Optional[str] = None
    admin1: Optional[str] = None
    latitude: float
    longitude: float
    display_name: str


class DailyForecast(BaseModel):
    date: date
    temp_max_c: Optional[float] = None
    temp_min_c: Optional[float] = None
    precipitation_mm: Optional[float] = None
    precipitation_probability: Optional[float] = None
    weather_code: Optional[int] = None
    description: Optional[str] = None


class CurrentWeather(BaseModel):
    temperature_c: Optional[float] = None
    feels_like_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    weather_code: Optional[int] = None
    description: Optional[str] = None
    is_day: Optional[bool] = None


class AirQuality(BaseModel):
    us_aqi: Optional[float] = None
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None


class WeatherLookupResponse(BaseModel):
    resolved_location: GeocodeMatch
    alternatives: List[GeocodeMatch] = []
    current: CurrentWeather
    forecast: List[DailyForecast]
    air_quality: Optional[AirQuality] = None
    recommendations: List[str] = []
    ai_insight: Optional[str] = None


# ---------- Persisted record (CRUD) schemas ----------

class WeatherRecordCreate(BaseModel):
    location: str = Field(..., min_length=1, description="Free-text location entered by the user")
    start_date: date
    end_date: date
    notes: Optional[str] = None

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, end_date, info):
        start_date = info.data.get("start_date")
        if start_date and end_date < start_date:
            raise ValueError("end_date must be on or after start_date")
        return end_date


class WeatherRecordUpdate(BaseModel):
    """All fields optional — user picks what to change.
    Changing location/dates triggers a re-fetch of weather data."""
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class DailyTemperatureOut(BaseModel):
    date: date
    temp_max_c: Optional[float] = None
    temp_min_c: Optional[float] = None
    precipitation_mm: Optional[float] = None
    weather_code: Optional[int] = None

    class Config:
        from_attributes = True


class WeatherRecordOut(BaseModel):
    id: int
    query_location: str
    resolved_name: str
    country: Optional[str] = None
    latitude: float
    longitude: float
    start_date: date
    end_date: date
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    daily_temperatures: List[DailyTemperatureOut] = []

    class Config:
        from_attributes = True
