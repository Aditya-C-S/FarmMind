"""
FarmMind Backend - Main Application Entry Point
FastAPI application initialization and configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.database import Base, engine, test_connection
from app.api import farmer_routes, field_routes, crop_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description="AI-powered farm decision optimization and post-harvest loss reduction platform",
    version=settings.API_VERSION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",  # OpenAPI schema
)

# Add CORS middleware (for frontend communication later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# ===========================
# Startup Events
# ===========================

@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    Creates database tables and tests connection.
    """
    logger.info("=" * 60)
    logger.info("🚀 FarmMind Backend Starting Up")
    logger.info("=" * 60)
    
    # Test database connection
    logger.info("📊 Testing database connection...")
    if test_connection():
        logger.info("✓ Database connection successful")
    else:
        logger.error("✗ Database connection failed!")
        raise Exception("Cannot connect to database")
    
    # Create tables
    logger.info("📋 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created/verified")
    except Exception as e:
        logger.error(f"✗ Failed to create tables: {str(e)}")
        raise
    
    logger.info("=" * 60)
    logger.info(f"✓ FarmMind API {settings.API_VERSION} Ready!")
    logger.info(f"📖 Swagger UI: http://localhost:8000/docs")
    logger.info(f"📚 ReDoc: http://localhost:8000/redoc")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("🛑 FarmMind Backend Shutting Down")


# ===========================
# Health Check Endpoint
# ===========================

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the API is running"
)
async def health_check():
    """
    Health check endpoint.
    Returns the current API status.
    """
    return {
        "status": "healthy",
        "api": settings.API_TITLE,
        "version": settings.API_VERSION,
        "debug": settings.DEBUG,
    }


# ===========================
# Root Endpoint
# ===========================

@app.get(
    "/",
    tags=["Root"],
    summary="API Information",
    description="Get API information"
)
async def root():
    """
    Root endpoint.
    Returns basic API information.
    """
    return {
        "message": "Welcome to FarmMind API",
        "api_title": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": "AI-powered farm decision optimization and post-harvest loss reduction",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health",
    }


# ===========================
# Register API Routes
# ===========================

# Include farmer routes
app.include_router(
    farmer_routes.router,
    prefix="",
    tags=["Farmers"]
)

# Include field routes
app.include_router(
    field_routes.router,
    prefix="",
    tags=["Fields"]
)

# Include crop routes
app.include_router(
    crop_routes.router,
    prefix="",
    tags=["Crops"]
)

logger.info("✓ All API routes registered")


# ===========================
# Error Handlers
# ===========================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "detail": "Internal server error",
        "error": str(exc) if settings.DEBUG else "An error occurred"
    }


# ===========================
# Application Export
# ===========================

if __name__ == "__main__":
    # For running with: python -m uvicorn app.main:app --reload
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )