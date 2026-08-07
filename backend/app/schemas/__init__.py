"""
Schemas module exports.
Provides easy imports for all Pydantic schemas (Phase 1 + Phase 2).
"""

# Phase 1 schemas
from app.schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse, FarmerDetailResponse
from app.schemas.field import FieldCreate, FieldUpdate, FieldResponse, FieldDetailResponse
from app.schemas.crop import CropCreate, CropUpdate, CropResponse, CropDetailResponse

# Phase 2 schemas
from app.schemas.activity_log import (
    ActivityLogCreate,
    ActivityLogUpdate,
    ActivityLogResponse,
    ActivityLogListResponse,
)
from app.schemas.disease_history import (
    DiseaseHistoryCreate,
    DiseaseHistoryUpdate,
    DiseaseHistoryResponse,
    DiseaseHistoryListResponse,
)
from app.schemas.weather_cache import (
    WeatherCacheCreate,
    WeatherCacheUpdate,
    WeatherCacheResponse,
    WeatherCacheListResponse,
)
from app.schemas.irrigation import (
    IrrigationCreate,
    IrrigationUpdate,
    IrrigationResponse,
    IrrigationListResponse,
    IrrigationStatsResponse,
)
from app.schemas.fertilizer_application import (
    FertilizerApplicationCreate,
    FertilizerApplicationUpdate,
    FertilizerApplicationResponse,
    FertilizerApplicationListResponse,
    FertilizerStatsResponse,
)

__all__ = [
    # Phase 1
    "FarmerCreate",
    "FarmerUpdate",
    "FarmerResponse",
    "FarmerDetailResponse",
    "FieldCreate",
    "FieldUpdate",
    "FieldResponse",
    "FieldDetailResponse",
    "CropCreate",
    "CropUpdate",
    "CropResponse",
    "CropDetailResponse",
    
    # Phase 2
    "ActivityLogCreate",
    "ActivityLogUpdate",
    "ActivityLogResponse",
    "ActivityLogListResponse",
    "DiseaseHistoryCreate",
    "DiseaseHistoryUpdate",
    "DiseaseHistoryResponse",
    "DiseaseHistoryListResponse",
    "WeatherCacheCreate",
    "WeatherCacheUpdate",
    "WeatherCacheResponse",
    "WeatherCacheListResponse",
    "IrrigationCreate",
    "IrrigationUpdate",
    "IrrigationResponse",
    "IrrigationListResponse",
    "IrrigationStatsResponse",
    "FertilizerApplicationCreate",
    "FertilizerApplicationUpdate",
    "FertilizerApplicationResponse",
    "FertilizerApplicationListResponse",
    "FertilizerStatsResponse",
]