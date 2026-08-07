"""
Models module exports.
Provides easy imports for all ORM models.
"""

# Phase 1 Models
from app.models.farmer import Farmer
from app.models.field import Field
from app.models.crop import Crop

# Phase 2 Models
from app.models.activity_log import ActivityLog
from app.models.disease_history import DiseaseHistory
from app.models.weather_cache import WeatherCache
from app.models.irrigation import Irrigation
from app.models.fertilizer_application import FertilizerApplication

from .harvest_record import HarvestRecord
from .storage_condition_log import StorageConditionLog

__all__ = [
    # Phase 1
    "Farmer",
    "Field",
    "Crop",
    
    # Phase 2
    "ActivityLog",
    "DiseaseHistory",
    "WeatherCache",
    "Irrigation",
    "FertilizerApplication",

    # Post-Harvest
    "HarvestRecord",
    "StorageConditionLog",
]