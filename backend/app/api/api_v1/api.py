"""
API router for version 1
"""
from fastapi import APIRouter
from backend.app.api.api_v1.endpoints import (
    auth,
    detection,
    camera,
    face_recognition,
    analytics,
    system
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(detection.router, prefix="/detection", tags=["detection"])
api_router.include_router(camera.router, prefix="/camera", tags=["camera"])
api_router.include_router(face_recognition.router, prefix="/face", tags=["face-recognition"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(system.router, prefix="/system", tags=["system"])