"""
Wraps Open-Meteo's free Geocoding API.
No API key required. Handles turning free-text ("tuni", "10001", "near the
eiffel tower") into resolvable lat/lon, and supports fuzzy matching by
returning the top N candidates.

Docs: https://open-meteo.com/en/docs/geocoding-api
"""
import httpx
from typing import List
from app.schemas import GeocodeMatch

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


def _to_match(item: dict) -> GeocodeMatch:
    parts = [item.get("name")]
    if item.get("admin1"):
        parts.append(item["admin1"])
    if item.get("country"):
        parts.append(item["country"])
    display_name = ", ".join(p for p in parts if p)

    return GeocodeMatch(
        name=item.get("name"),
        country=item.get("country"),
        admin1=item.get("admin1"),
        latitude=item["latitude"],
        longitude=item["longitude"],
        display_name=display_name,
    )


async def geocode_location(query: str, count: int = 5) -> List[GeocodeMatch]:
    """
    Resolve free-text location into one or more candidate matches.
    Returns an empty list if nothing is found (caller decides how to error).

    Supports zip/postal codes and city/town/landmark names — Open-Meteo's
    geocoder indexes the GeoNames database which includes postal codes.
    """
    params = {"name": query.strip(), "count": count, "language": "en", "format": "json"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(GEOCODE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results") or []
    return [_to_match(r) for r in results]


async def geocode_best_match(query: str) -> GeocodeMatch | None:
    matches = await geocode_location(query, count=5)
    return matches[0] if matches else None
