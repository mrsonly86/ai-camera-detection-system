"""
Camera control endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from backend.app.models.schemas import CameraConfig
from backend.app.api.api_v1.endpoints.auth import get_current_user
from backend.app.ai_engine.camera_interface import get_camera, CameraConfig as CameraConfigClass

router = APIRouter()


@router.get("/info")
async def get_camera_info(current_user = Depends(get_current_user)):
    """Get camera information and current settings"""
    try:
        camera = get_camera()
        info = camera.get_camera_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get camera info: {str(e)}")


@router.post("/configure")
async def configure_camera(
    config: CameraConfig,
    current_user = Depends(get_current_user)
):
    """Configure camera settings"""
    try:
        camera = get_camera()
        
        # Convert to internal config format
        camera_config = CameraConfigClass(
            index=config.camera_index,
            width=config.width,
            height=config.height,
            fps=config.fps,
            brightness=config.brightness,
            contrast=config.contrast,
            saturation=config.saturation
        )
        
        camera.update_config(camera_config)
        
        return {"message": "Camera configured successfully", "config": config}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure camera: {str(e)}")


@router.post("/test")
async def test_camera(current_user = Depends(get_current_user)):
    """Test camera functionality"""
    try:
        camera = get_camera()
        test_result = camera.test_camera()
        
        return {
            "test_passed": test_result,
            "message": "Camera test passed" if test_result else "Camera test failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Camera test failed: {str(e)}")


@router.post("/start")
async def start_camera(current_user = Depends(get_current_user)):
    """Start camera capture"""
    try:
        camera = get_camera()
        camera.start_capture()
        return {"message": "Camera started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start camera: {str(e)}")


@router.post("/stop")
async def stop_camera(current_user = Depends(get_current_user)):
    """Stop camera capture"""
    try:
        camera = get_camera()
        camera.stop_capture()
        return {"message": "Camera stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop camera: {str(e)}")


@router.get("/status")
async def get_camera_status():
    """Get camera status (no auth required)"""
    try:
        camera = get_camera()
        info = camera.get_camera_info()
        
        return {
            "is_running": info.get('is_running', False),
            "frame_count": info.get('frame_count', 0),
            "resolution": f"{info.get('width', 0)}x{info.get('height', 0)}",
            "fps": info.get('fps', 0)
        }
        
    except Exception as e:
        return {
            "is_running": False,
            "error": str(e)
        }