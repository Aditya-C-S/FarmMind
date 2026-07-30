"""
Weather Cache model for FarmMind backend.
Caches local weather data for decision making.
"""

from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.base import Base


class WeatherCache(Base):
    """
    Weather Cache ORM model.
    Caches weather data for historical analysis and predictions.
    Stores weather observations and forecasts.
    """
    
    __tablename__ = "weather_cache"
    
    # Primary Key
    weather_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    # Foreign Key
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.field_id", ondelete="CASCADE"), nullable=False)
    
    # Date Information
    record_date = Column(Date, nullable=False)
    
    # Temperature Data (in Celsius)
    temperature_min = Column(Numeric(5, 2), nullable=True)
    temperature_max = Column(Numeric(5, 2), nullable=True)
    temperature_avg = Column(Numeric(5, 2), nullable=True)
    
    # Humidity (0-100%)
    humidity_min = Column(Numeric(5, 2), nullable=True)
    humidity_max = Column(Numeric(5, 2), nullable=True)
    humidity_avg = Column(Numeric(5, 2), nullable=True)
    
    # Rainfall (in mm)
    rainfall = Column(Numeric(8, 2), nullable=True, default=0)
    
    # Wind (km/h)
    wind_speed_avg = Column(Numeric(5, 2), nullable=True)
    wind_speed_max = Column(Numeric(5, 2), nullable=True)
    
    # Pressure and Other Data
    pressure = Column(Numeric(7, 2), nullable=True)  # hPa
    cloud_cover = Column(Numeric(5, 2), nullable=True)  # 0-100%
    
    # Forecast Data (7-day forecast as JSON)
    # Example: {
    #   "forecast": [
    #     {"date": "2024-07-10", "temp_min": 25, "temp_max": 35, "rainfall": 0},
    #     ...
    #   ]
    # }
    forecast = Column(JSONB, nullable=True, default={})
    
    # Source Information
    source = Column(String(50), nullable=False)  # "openweathermap", "nasa_power", "imd", etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    field = relationship("Field", back_populates="weather_cache")
    
    def __repr__(self) -> str:
        return f"<WeatherCache(weather_id={self.weather_id}, field_id={self.field_id}, date='{self.record_date}')>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "weather_id": str(self.weather_id),
            "field_id": str(self.field_id),
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "temperature_min": float(self.temperature_min) if self.temperature_min else None,
            "temperature_max": float(self.temperature_max) if self.temperature_max else None,
            "temperature_avg": float(self.temperature_avg) if self.temperature_avg else None,
            "humidity_min": float(self.humidity_min) if self.humidity_min else None,
            "humidity_max": float(self.humidity_max) if self.humidity_max else None,
            "humidity_avg": float(self.humidity_avg) if self.humidity_avg else None,
            "rainfall": float(self.rainfall) if self.rainfall else 0,
            "wind_speed_avg": float(self.wind_speed_avg) if self.wind_speed_avg else None,
            "wind_speed_max": float(self.wind_speed_max) if self.wind_speed_max else None,
            "pressure": float(self.pressure) if self.pressure else None,
            "cloud_cover": float(self.cloud_cover) if self.cloud_cover else None,
            "forecast": self.forecast,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }