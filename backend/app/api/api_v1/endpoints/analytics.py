"""
Analytics and statistics endpoints
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.schemas import DetectionStats, SessionStats
from backend.app.api.api_v1.endpoints.auth import get_current_user
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    days: int = Query(7, ge=1, le=365),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for the last N days"""
    try:
        analytics_service = AnalyticsService(db)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get various statistics
        stats = analytics_service.get_dashboard_stats(current_user.id, start_date, end_date)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")


@router.get("/detection-stats")
async def get_detection_statistics(
    session_id: Optional[int] = None,
    days: int = Query(7, ge=1, le=365),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detection statistics"""
    try:
        analytics_service = AnalyticsService(db)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if session_id:
            stats = analytics_service.get_session_detection_stats(session_id)
        else:
            stats = analytics_service.get_user_detection_stats(current_user.id, start_date, end_date)
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detection stats: {str(e)}")


@router.get("/gender-distribution")
async def get_gender_distribution(
    days: int = Query(7, ge=1, le=365),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get gender distribution statistics"""
    try:
        analytics_service = AnalyticsService(db)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        distribution = analytics_service.get_gender_distribution(current_user.id, start_date, end_date)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "distribution": distribution
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get gender distribution: {str(e)}")


@router.get("/age-distribution")
async def get_age_distribution(
    days: int = Query(7, ge=1, le=365),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get age distribution statistics"""
    try:
        analytics_service = AnalyticsService(db)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        distribution = analytics_service.get_age_distribution(current_user.id, start_date, end_date)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "distribution": distribution
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get age distribution: {str(e)}")


@router.get("/detection-timeline")
async def get_detection_timeline(
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detection timeline (hourly breakdown)"""
    try:
        analytics_service = AnalyticsService(db)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)
        
        timeline = analytics_service.get_detection_timeline(current_user.id, start_date, end_date)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "hours": hours
            },
            "timeline": timeline
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detection timeline: {str(e)}")


@router.get("/alerts-summary")
async def get_alerts_summary(
    days: int = Query(7, ge=1, le=365),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alerts summary"""
    try:
        analytics_service = AnalyticsService(db)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        summary = analytics_service.get_alerts_summary(current_user.id, start_date, end_date)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "alerts": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts summary: {str(e)}")


@router.get("/session-performance")
async def get_session_performance(
    session_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance metrics for a specific session"""
    try:
        analytics_service = AnalyticsService(db)
        performance = analytics_service.get_session_performance(session_id)
        
        if not performance:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return performance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session performance: {str(e)}")


@router.get("/export-data")
async def export_analytics_data(
    format: str = Query("json", pattern="^(json|csv)$"),
    days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export analytics data in JSON or CSV format"""
    try:
        analytics_service = AnalyticsService(db)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        data = analytics_service.export_user_data(current_user.id, start_date, end_date, format)
        
        return {
            "format": format,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


@router.get("/system-metrics")
async def get_system_metrics(current_user = Depends(get_current_user)):
    """Get system performance metrics"""
    try:
        from backend.app.ai_engine.yolo_detector import get_detector
        from backend.app.ai_engine.camera_interface import get_camera
        from backend.app.ai_engine.face_recognition import get_face_recognition
        
        # Get AI engine metrics
        detector = get_detector()
        camera = get_camera()
        face_recognition = get_face_recognition()
        
        detector_info = detector.get_model_info()
        camera_info = camera.get_camera_info()
        face_stats = face_recognition.get_statistics()
        
        # System resource usage
        import psutil
        
        metrics = {
            "ai_engines": {
                "detector": detector_info,
                "camera": camera_info,
                "face_recognition": face_stats
            },
            "system_resources": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")