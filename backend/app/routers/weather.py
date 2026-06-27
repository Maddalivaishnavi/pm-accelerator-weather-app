"""
Stateless "look up the weather right now" endpoints. These don't touch the
database — they back the main search box on the frontend. Saving a lookup
into the persisted log happens via the /api/records endpoints (records.py).
"""
from fastapi import APIRouter, HTTPException, Query

from app.schemas import WeatherLookupResponse, GeocodeMatch
from app.services import geocoding, weather, air_quality, recommendations, ai_insights

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/lookup", response_model=WeatherLookupResponse)
async def lookup_weather(
    location: str = Query(..., min_length=1, description="City, zip code, landmark, etc."),
    forecast_days: int = Query(5, ge=1, le=16),
):
    """Resolve a free-text location, then return current weather + forecast."""
    try:
        matches = await geocoding.geocode_location(location)
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="The location lookup service is currently unavailable. Please try again shortly.",
        )
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find a location matching '{location}'. "
                   f"Try a different spelling, a nearby city, or a zip/postal code.",
        )

    best = matches[0]
    try:
        current, forecast = await weather.get_current_and_forecast(
            best.latitude, best.longitude, forecast_days=forecast_days
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="The weather service is currently unavailable. Please try again shortly.",
        )

    try:
        aq = await air_quality.get_air_quality(best.latitude, best.longitude)
    except Exception:
        aq = None  # air quality is a nice-to-have; don't fail the whole request

    tips = recommendations.generate_recommendations(current, forecast, aq)
    insight = await ai_insights.generate_insight(best.display_name, current, forecast, aq)

    return WeatherLookupResponse(
        resolved_location=best,
        alternatives=matches[1:],
        current=current,
        forecast=forecast,
        air_quality=aq,
        recommendations=tips,
        ai_insight=insight,
    )


@router.get("/by-coordinates", response_model=WeatherLookupResponse)
async def lookup_weather_by_coordinates(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    forecast_days: int = Query(5, ge=1, le=16),
):
    """Used by the 'use my current location' button (browser geolocation)."""
    try:
        current, forecast = await weather.get_current_and_forecast(
            latitude, longitude, forecast_days=forecast_days
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="The weather service is currently unavailable. Please try again shortly.",
        )

    try:
        aq = await air_quality.get_air_quality(latitude, longitude)
    except Exception:
        aq = None

    here = GeocodeMatch(
        name="Current location",
        country=None,
        admin1=None,
        latitude=latitude,
        longitude=longitude,
        display_name=f"Current location ({latitude:.3f}, {longitude:.3f})",
    )

    tips = recommendations.generate_recommendations(current, forecast, aq)
    insight = await ai_insights.generate_insight(here.display_name, current, forecast, aq)

    return WeatherLookupResponse(
        resolved_location=here, alternatives=[], current=current,
        forecast=forecast, air_quality=aq,
        recommendations=tips, ai_insight=insight,
    )
