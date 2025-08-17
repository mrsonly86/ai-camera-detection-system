"""
System configuration and management endpoints
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.config import get_settings
from backend.app.models.schemas import SystemConfig, SystemConfigUpdate, ResponseMessage
from backend.app.api.api_v1.endpoints.auth import get_current_user
from backend.app.services.system_service import SystemService

router = APIRouter()
settings = get_settings()


@router.get("/config", response_model=List[SystemConfig])
async def get_system_config(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all system configuration settings"""
    system_service = SystemService(db)
    configs = system_service.get_all_configs()
    return configs


@router.get("/config/{config_key}", response_model=SystemConfig)
async def get_config_value(
    config_key: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific configuration value"""
    system_service = SystemService(db)
    config = system_service.get_config(config_key)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/config/{config_key}", response_model=SystemConfig)
async def update_config_value(
    config_key: str,
    config_data: SystemConfigUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a configuration value"""
    system_service = SystemService(db)
    config = system_service.update_config(config_key, config_data)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.get("/info")
async def get_system_info():
    """Get system information (no auth required)"""
    import platform
    import torch
    import cv2
    
    return {
        "application": {
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug
        },
        "system": {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        },
        "ai_libraries": {
            "pytorch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "opencv_version": cv2.__version__
        },
        "gpu_info": {
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() and torch.cuda.device_count() > 0 else None
        }
    }


@router.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {}
        }
        
        # Check database
        try:
            from backend.app.core.database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            health_status["services"]["database"] = "healthy"
        except Exception as e:
            health_status["services"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check AI engines
        try:
            from backend.app.ai_engine.yolo_detector import get_detector
            detector = get_detector()
            if detector.model is not None:
                health_status["services"]["yolo_detector"] = "healthy"
            else:
                health_status["services"]["yolo_detector"] = "unhealthy: model not loaded"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["services"]["yolo_detector"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check camera
        try:
            from backend.app.ai_engine.camera_interface import get_camera
            camera = get_camera()
            if camera.test_camera():
                health_status["services"]["camera"] = "healthy"
            else:
                health_status["services"]["camera"] = "unhealthy: camera test failed"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["services"]["camera"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/restart-services")
async def restart_services(
    service: str,
    current_user = Depends(get_current_user)
):
    """Restart specific services"""
    try:
        if service == "detector":
            from backend.app.ai_engine.yolo_detector import release_detector, get_detector
            release_detector()
            get_detector()  # Reinitialize
            return {"message": "YOLO detector restarted"}
        
        elif service == "camera":
            from backend.app.ai_engine.camera_interface import release_camera, get_camera
            release_camera()
            get_camera()  # Reinitialize
            return {"message": "Camera service restarted"}
        
        elif service == "all":
            from backend.app.ai_engine.yolo_detector import release_detector, get_detector
            from backend.app.ai_engine.camera_interface import release_camera, get_camera
            
            release_detector()
            release_camera()
            get_detector()
            get_camera()
            return {"message": "All services restarted"}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid service name")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart service: {str(e)}")


@router.get("/logs")
async def get_system_logs(
    lines: int = 100,
    current_user = Depends(get_current_user)
):
    """Get system logs"""
    try:
        import os
        from pathlib import Path
        
        log_file = Path(settings.log_file)
        if not log_file.exists():
            return {"logs": [], "message": "Log file not found"}
        
        # Read last N lines
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "logs": [line.strip() for line in recent_lines],
            "total_lines": len(all_lines),
            "returned_lines": len(recent_lines),
            "log_file": str(log_file)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


@router.post("/initialize-defaults")
async def initialize_default_configs(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initialize default system configurations"""
    try:
        system_service = SystemService(db)
        
        default_configs = [
            ("detection_confidence_threshold", "0.25", "float", "Minimum confidence for object detection"),
            ("face_recognition_tolerance", "0.6", "float", "Face recognition matching tolerance"),
            ("max_detection_rate", "30", "integer", "Maximum detections per second"),
            ("auto_save_detections", "true", "boolean", "Automatically save all detections"),
            ("alert_high_confidence", "0.8", "float", "Confidence threshold for high priority alerts"),
            ("camera_auto_adjust", "true", "boolean", "Auto-adjust camera settings"),
            ("batch_processing_size", "8", "integer", "Batch size for AI processing"),
            ("cleanup_old_data_days", "30", "integer", "Days to keep old detection data")
        ]
        
        created_configs = []
        for key, value, config_type, description in default_configs:
            config = system_service.create_or_update_config(key, value, config_type, description)
            created_configs.append(config)
        
        return {
            "message": "Default configurations initialized",
            "configs": created_configs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize configs: {str(e)}")


@router.delete("/config/{config_key}")
async def delete_config(
    config_key: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a configuration setting"""
    system_service = SystemService(db)
    success = system_service.delete_config(config_key)
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {"message": f"Configuration '{config_key}' deleted successfully"}


@router.get("/backup-database")
async def backup_database(current_user = Depends(get_current_user)):
    """Create a backup of the database"""
    try:
        import shutil
        from datetime import datetime
        from pathlib import Path
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"ai_camera_db_backup_{timestamp}.db"
        backup_path = Path(settings.cache_dir) / backup_name
        
        # Copy database file
        db_path = settings.database_url.replace("sqlite:///", "")
        shutil.copy2(db_path, backup_path)
        
        return {
            "message": "Database backup created successfully",
            "backup_file": str(backup_path),
            "timestamp": timestamp
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to backup database: {str(e)}")