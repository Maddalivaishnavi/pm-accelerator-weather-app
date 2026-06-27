"""
Full CRUD over persisted WeatherRecord rows, satisfying assessment
requirement 2.1. Each record represents "a location + date range" the
user asked to save, along with the day-by-day temperatures we fetched
for that range at the time it was created (or last refreshed).
"""
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WeatherRecord, DailyTemperature
from app.schemas import WeatherRecordCreate, WeatherRecordUpdate, WeatherRecordOut
from app.services import geocoding, weather
from app.services.export import export_records

router = APIRouter(prefix="/api/records", tags=["records"])

MAX_FUTURE_DAYS = 16  # Open-Meteo's forecast horizon


def _validate_date_range(start_date: date, end_date: date):
    if end_date < start_date:
        raise HTTPException(400, "end_date must be on or after start_date")
    if start_date > date.today() + timedelta(days=MAX_FUTURE_DAYS):
        raise HTTPException(
            400,
            f"start_date can't be more than {MAX_FUTURE_DAYS} days in the future "
            f"— that's beyond what weather forecasts can reliably predict.",
        )


async def _resolve_and_fetch(location: str, start_date: date, end_date: date):
    """Validate the location is real (fuzzy-matched) and fetch daily temps."""
    try:
        match = await geocoding.geocode_best_match(location)
    except Exception:
        raise HTTPException(
            502, "The location lookup service is currently unavailable. Please try again shortly."
        )
    if match is None:
        raise HTTPException(
            404,
            f"Could not find a location matching '{location}'. "
            f"Try a different spelling, a nearby city, or a zip/postal code.",
        )
    try:
        daily = await weather.get_temperature_range(
            match.latitude, match.longitude, start_date, end_date
        )
    except Exception:
        raise HTTPException(502, "The weather service is currently unavailable. Please try again shortly.")
    return match, daily


@router.post("", response_model=WeatherRecordOut, status_code=201)
async def create_record(payload: WeatherRecordCreate, db: Session = Depends(get_db)):
    """CREATE — location + date range -> validated, geocoded, and persisted
    along with the fetched daily temperatures."""
    _validate_date_range(payload.start_date, payload.end_date)
    match, daily = await _resolve_and_fetch(payload.location, payload.start_date, payload.end_date)

    record = WeatherRecord(
        query_location=payload.location,
        resolved_name=match.display_name,
        country=match.country,
        latitude=match.latitude,
        longitude=match.longitude,
        start_date=payload.start_date,
        end_date=payload.end_date,
        notes=payload.notes,
    )
    record.daily_temperatures = [
        DailyTemperature(
            date=d.date, temp_max_c=d.temp_max_c, temp_min_c=d.temp_min_c,
            precipitation_mm=d.precipitation_mm, weather_code=d.weather_code,
        )
        for d in daily
    ]
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[WeatherRecordOut])
def list_records(db: Session = Depends(get_db)):
    """READ — all saved records (no per-user segmentation, per spec)."""
    return db.query(WeatherRecord).order_by(WeatherRecord.created_at.desc()).all()


@router.get("/{record_id}", response_model=WeatherRecordOut)
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, f"No record with id {record_id}")
    return record


@router.put("/{record_id}", response_model=WeatherRecordOut)
async def update_record(
    record_id: int, payload: WeatherRecordUpdate, db: Session = Depends(get_db)
):
    """UPDATE — notes can always be edited freely. Changing location and/or
    dates re-validates and re-fetches the daily temperatures."""
    record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, f"No record with id {record_id}")

    new_location = payload.location if payload.location is not None else record.query_location
    new_start = payload.start_date if payload.start_date is not None else record.start_date
    new_end = payload.end_date if payload.end_date is not None else record.end_date

    location_or_dates_changed = (
        payload.location is not None
        or payload.start_date is not None
        or payload.end_date is not None
    )

    if location_or_dates_changed:
        _validate_date_range(new_start, new_end)
        match, daily = await _resolve_and_fetch(new_location, new_start, new_end)
        record.query_location = new_location
        record.resolved_name = match.display_name
        record.country = match.country
        record.latitude = match.latitude
        record.longitude = match.longitude
        record.start_date = new_start
        record.end_date = new_end
        record.daily_temperatures = [
            DailyTemperature(
                date=d.date, temp_max_c=d.temp_max_c, temp_min_c=d.temp_min_c,
                precipitation_mm=d.precipitation_mm, weather_code=d.weather_code,
            )
            for d in daily
        ]

    if payload.notes is not None:
        record.notes = payload.notes

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, f"No record with id {record_id}")
    db.delete(record)
    db.commit()
    return Response(status_code=204)


@router.get("/{record_id}/export")
def export_one_record(
    record_id: int,
    format: str = Query("json", pattern="^(json|csv|xml|markdown|pdf)$"),
    db: Session = Depends(get_db),
):
    """2.3 Data Export — export a single record."""
    record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, f"No record with id {record_id}")
    content, media_type, ext = export_records([record], format)
    filename = f"weather_record_{record_id}.{ext}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/all")
def export_all_records(
    format: str = Query("json", pattern="^(json|csv|xml|markdown|pdf)$"),
    db: Session = Depends(get_db),
):
    """2.3 Data Export — bulk export of every saved record."""
    records = db.query(WeatherRecord).order_by(WeatherRecord.created_at.desc()).all()
    content, media_type, ext = export_records(records, format)
    filename = f"weather_records_export.{ext}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
