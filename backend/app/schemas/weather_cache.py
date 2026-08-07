"""
Pydantic schemas for Weather Cache model.
Handles request/response validation for weather endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


class WeatherCacheCreate(BaseModel):
    """Schema for creating/caching weather data"""
    field_id: UUID = Field(..., description="ID of the field")
    record_date: date = Field(..., description="Date of weather observation")
    temperature_min: Optional[Decimal] = Field(None, ge=-50, le=60, description="Min temp in Celsius")
    temperature_max: Optional[Decimal] = Field(None, ge=-50, le=60, description="Max temp in Celsius")
    temperature_avg: Optional[Decimal] = Field(None, ge=-50, le=60, description="Avg temp in Celsius")
    humidity_min: Optional[Decimal] = Field(None, ge=0, le=100, description="Min humidity %")
    humidity_max: Optional[Decimal] = Field(None, ge=0, le=100, description="Max humidity %")
    humidity_avg: Optional[Decimal] = Field(None, ge=0, le=100, description="Avg humidity %")
    rainfall: Optional[Decimal] = Field(None, ge=0, description="Rainfall in mm")
    wind_speed_avg: Optional[Decimal] = Field(None, ge=0, description="Avg wind speed km/h")
    wind_speed_max: Optional[Decimal] = Field(None, ge=0, description="Max wind speed km/h")
    pressure: Optional[Decimal] = Field(None, description="Pressure in hPa")
    cloud_cover: Optional[Decimal] = Field(None, ge=0, le=100, description="Cloud cover %")
    forecast: Optional[Dict[str, Any]] = Field(None, description="7-day forecast data")
    source: str = Field(..., description="Data source: openweathermap, nasa_power, imd, etc.")


class WeatherCacheUpdate(BaseModel):
    """Schema for updating weather data"""
    temperature_min: Optional[Decimal] = None
    temperature_max: Optional[Decimal] = None
    temperature_avg: Optional[Decimal] = None
    humidity_min: Optional[Decimal] = None
    humidity_max: Optional[Decimal] = None
    humidity_avg: Optional[Decimal] = None
    rainfall: Optional[Decimal] = None
    wind_speed_avg: Optional[Decimal] = None
    wind_speed_max: Optional[Decimal] = None
    pressure: Optional[Decimal] = None
    cloud_cover: Optional[Decimal] = None
    forecast: Optional[Dict[str, Any]] = None


class WeatherCacheResponse(BaseModel):
    """Schema for weather cache response"""
    weather_id: UUID
    field_id: UUID
    record_date: date
    temperature_min: Optional[Decimal] = None
    temperature_max: Optional[Decimal] = None
    temperature_avg: Optional[Decimal] = None
    humidity_min: Optional[Decimal] = None
    humidity_max: Optional[Decimal] = None
    humidity_avg: Optional[Decimal] = None
    rainfall: Optional[Decimal] = None
    wind_speed_avg: Optional[Decimal] = None
    wind_speed_max: Optional[Decimal] = None
    pressure: Optional[Decimal] = None
    cloud_cover: Optional[Decimal] = None
    forecast: Optional[Dict[str, Any]] = None
    source: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WeatherCacheListResponse(BaseModel):
    """Schema for listing weather data"""
    weather_id: UUID
    field_id: UUID
    record_date: date
    temperature_avg: Optional[Decimal] = None
    humidity_avg: Optional[Decimal] = None
    rainfall: Optional[Decimal] = None
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True