"""
Weather Service module.
Contains business logic for weather cache operations.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
import logging
import requests
from datetime import datetime

from app.models.weather_cache import WeatherCache
from app.models.field import Field
from app.schemas.weather_cache import WeatherCacheCreate, WeatherCacheUpdate

logger = logging.getLogger(__name__)


class WeatherService:
    """Service class for weather cache operations"""
    
    @staticmethod
    def create_weather(db: Session, weather_data: WeatherCacheCreate) -> WeatherCache:
        """Create weather cache entry"""
        field = db.query(Field).filter(Field.field_id == weather_data.field_id).first()
        if not field:
            raise ValueError(f"Field with ID {weather_data.field_id} not found")
        
        try:
            db_weather = WeatherCache(
                field_id=weather_data.field_id,
                record_date=weather_data.record_date,
                temperature_min=weather_data.temperature_min,
                temperature_max=weather_data.temperature_max,
                temperature_avg=weather_data.temperature_avg,
                humidity_min=weather_data.humidity_min,
                humidity_max=weather_data.humidity_max,
                humidity_avg=weather_data.humidity_avg,
                rainfall=weather_data.rainfall,
                wind_speed_avg=weather_data.wind_speed_avg,
                wind_speed_max=weather_data.wind_speed_max,
                pressure=weather_data.pressure,
                cloud_cover=weather_data.cloud_cover,
                forecast=weather_data.forecast,
                source=weather_data.source,
            )
            db.add(db_weather)
            db.commit()
            db.refresh(db_weather)
            logger.info(f"✓ Weather cached: {db_weather.weather_id}")
            return db_weather
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error caching weather: {str(e)}")
            raise
    
    @staticmethod
    def get_weather_by_id(db: Session, weather_id: UUID) -> WeatherCache | None:
        """Get weather by ID"""
        return db.query(WeatherCache).filter(WeatherCache.weather_id == weather_id).first()
    
    @staticmethod
    def get_weather_by_field(db: Session, field_id: UUID, skip: int = 0, limit: int = 100) -> list[WeatherCache]:
        """Get weather history for a field"""
        return db.query(WeatherCache).filter(WeatherCache.field_id == field_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_latest_weather(db: Session, field_id: UUID) -> WeatherCache | None:
        """Get latest weather record for a field"""
        return db.query(WeatherCache).filter(WeatherCache.field_id == field_id).order_by(WeatherCache.record_date.desc()).first()
    
    @staticmethod
    def get_weather_range(db: Session, field_id: UUID, start_date: date, end_date: date) -> list[WeatherCache]:
        """Get weather data for date range"""
        return db.query(WeatherCache).filter(
            WeatherCache.field_id == field_id,
            WeatherCache.record_date >= start_date,
            WeatherCache.record_date <= end_date
        ).all()
    
    @staticmethod
    def update_weather(db: Session, weather_id: UUID, weather_data: WeatherCacheUpdate) -> WeatherCache | None:
        """Update weather record"""
        db_weather = db.query(WeatherCache).filter(WeatherCache.weather_id == weather_id).first()
        
        if not db_weather:
            return None
        
        try:
            update_data = weather_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_weather, field, value)
            
            db.commit()
            db.refresh(db_weather)
            logger.info(f"✓ Weather updated: {weather_id}")
            return db_weather
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error updating weather: {str(e)}")
            raise
    
    @staticmethod
    def delete_weather(db: Session, weather_id: UUID) -> bool:
        """Delete weather record"""
        db_weather = db.query(WeatherCache).filter(WeatherCache.weather_id == weather_id).first()
        
        if not db_weather:
            return False
        
        try:
            db.delete(db_weather)
            db.commit()
            logger.info(f"✓ Weather deleted: {weather_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error deleting weather: {str(e)}")
            raise
    
    @staticmethod
    def count_weather_records(db: Session, field_id: UUID) -> int:
        """Count weather records for field"""
        return db.query(WeatherCache).filter(WeatherCache.field_id == field_id).count()

    import requests

    @staticmethod
    def fetch_5_day_forecast(latitude: float, longitude: float):
        """
        Fetch a 5-day weather forecast from Open-Meteo.
        Returns None if the API is unavailable.
        """

        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,

            "daily": ",".join([
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "wind_speed_10m_max",
            ]),

            "hourly": ",".join([
                "relative_humidity_2m",
            ]),

            "forecast_days": 5,
            "timezone": "auto",
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            from collections import defaultdict

            humidity_by_day = defaultdict(list)

            times = data["hourly"]["time"]
            humidities = data["hourly"]["relative_humidity_2m"]

            for t, h in zip(times, humidities):
                day = t.split("T")[0]
                humidity_by_day[day].append(h)

            forecast = []

            for i in range(min(5, len(data["daily"]["time"]))):

                day = data["daily"]["time"][i]

                daily_humidity = humidity_by_day.get(day, [])

                avg_humidity = (
                    round(sum(daily_humidity) / len(daily_humidity), 1)
                    if daily_humidity
                    else None
                )

                forecast.append({
                    "date": day,
                    "temperature_max": data["daily"]["temperature_2m_max"][i],
                    "temperature_min": data["daily"]["temperature_2m_min"][i],
                    "humidity": avg_humidity,
                    "rainfall": data["daily"]["precipitation_sum"][i],
                    "wind_speed": data["daily"]["wind_speed_10m_max"][i],
                })

            return forecast

        except requests.exceptions.RequestException as e:
            print(f"[Weather Service] Open-Meteo unavailable: {e}")
            return None