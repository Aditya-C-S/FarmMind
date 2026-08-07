"""
API routes package initialization.
Exports all API router instances for Phase 1 and Phase 2.
"""

# Phase 1 Routes
from app.api.farmer_routes import router as farmer_router
from app.api.field_routes import router as field_router
from app.api.crop_routes import router as crop_router

# Phase 2 Routes - Farm Memory
from app.api.activity_routes import router as activity_router
from app.api.disease_routes import router as disease_router
from app.api.weather_routes import router as weather_router
from app.api.irrigation_routes import router as irrigation_router
from app.api.fertilizer_routes import router as fertilizer_router

__all__ = [
    # Phase 1
    "farmer_router",
    "field_router",
    "crop_router",
    # Phase 2
    "activity_router",
    "disease_router",
    "weather_router",
    "irrigation_router",
    "fertilizer_router",
]