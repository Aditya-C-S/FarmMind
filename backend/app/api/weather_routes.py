"""
Weather Routes module.
API endpoints for weather cache operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date

from app.database.session import get_db
from app.schemas.weather_cache import WeatherCacheCreate, WeatherCacheUpdate, WeatherCacheResponse, WeatherCacheListResponse
from app.services.weather_service import WeatherService
from app.services.weather_intelligence_service import WeatherIntelligenceService

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.post("", response_model=WeatherCacheResponse, status_code=status.HTTP_201_CREATED)
def create_weather(weather_data: WeatherCacheCreate, db: Session = Depends(get_db)):
    """Create a new weather cache entry"""
    try:
        weather = WeatherService.create_weather(db, weather_data)
        return weather
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error caching weather")


@router.get("", response_model=list[WeatherCacheListResponse])
def list_weather(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """List all weather records (paginated)"""
    # Note: This gets all weather without field filter - consider filtering in production
    return []

@router.get("/intelligence")
def get_weather_intelligence(
    lat: float,
    lon: float,
    crop_type: str,
):
    try:
        forecast = WeatherService.fetch_5_day_forecast(lat, lon)

        if forecast is None:
            return {
                "forecast": [],
                "irrigation": {},
                "prevention": [],
                "message": "Weather service unavailable."
            }

        irrigation = WeatherIntelligenceService.irrigation_advice(
            crop_type,
            forecast
        )

        prevention = WeatherIntelligenceService.disease_prevention(
            crop_type,
            forecast
        )

        return {
            "forecast": forecast,
            "irrigation": irrigation,
            "prevention": prevention
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/{weather_id}", response_model=WeatherCacheResponse)
def get_weather(weather_id: UUID, db: Session = Depends(get_db)):
    """Get a specific weather record by ID"""
    weather = WeatherService.get_weather_by_id(db, weather_id)
    if not weather:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weather record not found")
    return weather


@router.get("/field/{field_id}", response_model=list[WeatherCacheListResponse])
def get_weather_by_field(field_id: UUID, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """Get all weather records for a specific field"""
    weather_records = WeatherService.get_weather_by_field(db, field_id, skip, limit)
    return weather_records


@router.get("/field/{field_id}/latest", response_model=WeatherCacheResponse)
def get_latest_weather(field_id: UUID, db: Session = Depends(get_db)):
    """Get latest weather record for a field"""
    weather = WeatherService.get_latest_weather(db, field_id)
    if not weather:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No weather records found for this field")
    return weather


@router.get("/field/{field_id}/range", response_model=list[WeatherCacheListResponse])
def get_weather_range(field_id: UUID, start_date: date, end_date: date, db: Session = Depends(get_db)):
    """Get weather data for a date range"""
    weather_records = WeatherService.get_weather_range(db, field_id, start_date, end_date)
    return weather_records


@router.put("/{weather_id}", response_model=WeatherCacheResponse)
def update_weather(weather_id: UUID, weather_data: WeatherCacheUpdate, db: Session = Depends(get_db)):
    """Update a weather record"""
    weather = WeatherService.update_weather(db, weather_id, weather_data)
    if not weather:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weather record not found")
    return weather


@router.delete("/{weather_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weather(weather_id: UUID, db: Session = Depends(get_db)):
    """Delete a weather record"""
    success = WeatherService.delete_weather(db, weather_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weather record not found")
    return None


@router.get("/field/{field_id}/count", response_model=dict)
def count_weather_records(field_id: UUID, db: Session = Depends(get_db)):
    """Count weather records for a field"""
    count = WeatherService.count_weather_records(db, field_id)
    return {"field_id": field_id, "total_records": count}