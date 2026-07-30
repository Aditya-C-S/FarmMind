"""
Services package initialization.
Exports all business logic services for Phase 1 and Phase 2.
"""

# Phase 1 Services
from app.services.farmer_service import FarmerService
from app.services.field_service import FieldService
from app.services.crop_service import CropService

# Phase 2 Services - Farm Memory
from app.services.activity_service import ActivityService
from app.services.disease_service import DiseaseService
from app.services.weather_service import WeatherService
from app.services.irrigation_service import IrrigationService
from app.services.fertilizer_service import FertilizerService

__all__ = [
    # Phase 1
    "FarmerService",
    "FieldService",
    "CropService",
    # Phase 2
    "ActivityService",
    "DiseaseService",
    "WeatherService",
    "IrrigationService",
    "FertilizerService",
]