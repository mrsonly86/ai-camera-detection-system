"""
FastAPI application main entry point
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from pathlib import Path

from backend.app.core.config import get_settings
from backend.app.core.logging import setup_logging
from backend.app.core.database import create_tables
from backend.app.api.api_v1.api import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    setup_logging()
    create_tables()
    
    # Ensure directories exist
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.model_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.cache_dir).mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Shutdown
    from backend.app.ai_engine.yolo_detector import release_detector
    from backend.app.ai_engine.camera_interface import release_camera
    
    release_detector()
    release_camera()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Camera Detection System with YOLOv5 and Advanced Analysis",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static files
static_dir = Path("frontend/build")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Upload directory
upload_dir = Path(settings.upload_dir)
if upload_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Camera Detection System",
        "version": settings.app_version,
        "status": "running",
        "docs": "/api/v1/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": "2024-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )