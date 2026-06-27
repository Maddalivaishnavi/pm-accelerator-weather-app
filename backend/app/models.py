"""
ORM models.

WeatherRecord  -> one saved "lookup" a user created (location + date range)
DailyTemperature -> one row per day within that record's date range (one-to-many)
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)

    # What the user actually typed in, e.g. "tuni andhra pradesh"
    query_location = Column(String, nullable=False)

    # What we resolved it to via geocoding, e.g. "Tuni, Andhra Pradesh, India"
    resolved_name = Column(String, nullable=False)
    country = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    daily_temperatures = relationship(
        "DailyTemperature",
        back_populates="record",
        cascade="all, delete-orphan",
        order_by="DailyTemperature.date",
    )


class DailyTemperature(Base):
    __tablename__ = "daily_temperatures"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("weather_records.id"), nullable=False)

    date = Column(Date, nullable=False)
    temp_max_c = Column(Float, nullable=True)
    temp_min_c = Column(Float, nullable=True)
    precipitation_mm = Column(Float, nullable=True)
    weather_code = Column(Integer, nullable=True)

    record = relationship("WeatherRecord", back_populates="daily_temperatures")
