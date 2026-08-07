"""
FarmMind Backend - Main FastAPI Application
Initializes database, configures middleware, and registers routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.database.database import engine
from app.database.base import Base

# Phase 1 Routers
from app.api.farmer_routes import router as farmer_router
from app.api.field_routes import router as field_router
from app.api.crop_routes import router as crop_router

# Phase 2 Routers
from app.api.activity_routes import router as activity_router
from app.api.disease_routes import router as disease_router
from app.api.weather_routes import router as weather_router
from app.api.irrigation_routes import router as irrigation_router
from app.api.fertilizer_routes import router as fertilizer_router

from app.api.workflow_routes import router as workflow_router
from app.api.context_fusion_routes import router as context_fusion_router

from app.api.decision_optimization_routes import router as decision_optimization_router
from app.api.disease_analysis_routes import router as disease_analysis_router
from app.api.post_harvest_routes import router as post_harvest_router


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description="AI-Powered Farm Intelligence & Workflow Optimization System",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
def startup_event():
    """
    Startup event handler.
    Creates all database tables and logs startup information.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created/verified")
        logger.info(f"✓ API running on {settings.API_TITLE} v{settings.API_VERSION}")
        logger.info(f"✓ Debug mode: {settings.DEBUG}")
    except Exception as e:
        logger.error(f"✗ Startup error: {str(e)}")
        raise


# Health Check Endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api": settings.API_TITLE,
        "version": settings.API_VERSION
    }


# Root Endpoint
@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API information"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": "AI-Powered Farm Intelligence & Workflow Optimization System",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Register Phase 1 Routes
app.include_router(farmer_router)
app.include_router(field_router)
app.include_router(crop_router)

# Register Phase 2 Routes
app.include_router(activity_router)
app.include_router(disease_router)
app.include_router(weather_router)
app.include_router(irrigation_router)
app.include_router(fertilizer_router)

app.include_router(workflow_router)
app.include_router(context_fusion_router)

app.include_router(decision_optimization_router)
app.include_router(disease_analysis_router)
app.include_router(post_harvest_router)

logger.info("✓ All routes registered (Phase 1 + Phase 2 + Disease Analysis)")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)