"""
Camera interface for capturing video from various sources
"""
import cv2
import numpy as np
import threading
import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from loguru import logger
from backend.app.core.config import get_settings

settings = get_settings()


@dataclass
class CameraConfig:
    """Camera configuration settings"""
    index: int = 0
    width: int = 1920
    height: int = 1080
    fps: int = 30
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    saturation: Optional[float] = None
    auto_exposure: bool = True


class CameraInterface:
    """Camera interface for video capture and streaming"""
    
    def __init__(self, config: Optional[CameraConfig] = None):
        """
        Initialize camera interface
        
        Args:
            config: Camera configuration settings
        """
        self.config = config or CameraConfig(
            index=settings.camera_index,
            width=settings.camera_width,
            height=settings.camera_height,
            fps=settings.camera_fps
        )
        
        self.cap = None
        self.is_running = False
        self.capture_thread = None
        self.frame_callback = None
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Initialize camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.config.index)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Cannot open camera with index {self.config.index}")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            # Set additional properties if specified
            if self.config.brightness is not None:
                self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.config.brightness)
            if self.config.contrast is not None:
                self.cap.set(cv2.CAP_PROP_CONTRAST, self.config.contrast)
            if self.config.saturation is not None:
                self.cap.set(cv2.CAP_PROP_SATURATION, self.config.saturation)
            
            # Auto exposure
            if hasattr(cv2, 'CAP_PROP_AUTO_EXPOSURE'):
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 
                           0.25 if self.config.auto_exposure else 0.75)
            
            # Verify settings
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Camera initialized: {actual_width}x{actual_height} @ {actual_fps} FPS")
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            raise
    
    def start_capture(self, frame_callback: Optional[Callable[[np.ndarray], None]] = None):
        """
        Start video capture in a separate thread
        
        Args:
            frame_callback: Callback function to process each frame
        """
        if self.is_running:
            logger.warning("Camera capture is already running")
            return
        
        self.frame_callback = frame_callback
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        logger.info("Camera capture started")
    
    def stop_capture(self):
        """Stop video capture"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        logger.info("Camera capture stopped")
    
    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    logger.error("Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
                
                # Update frame counter and FPS
                self.frame_count += 1
                self.fps_counter += 1
                
                current_time = time.time()
                if current_time - self.last_fps_time >= 1.0:
                    logger.debug(f"Camera FPS: {self.fps_counter}")
                    self.fps_counter = 0
                    self.last_fps_time = current_time
                
                # Store latest frame
                with self.frame_lock:
                    self.latest_frame = frame.copy()
                
                # Call frame callback if provided
                if self.frame_callback:
                    try:
                        self.frame_callback(frame)
                    except Exception as e:
                        logger.error(f"Frame callback error: {e}")
                
                # Control frame rate
                time.sleep(1.0 / self.config.fps)
                
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                time.sleep(0.1)
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get the latest captured frame
        
        Returns:
            Latest frame as numpy array or None if no frame available
        """
        with self.frame_lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None
    
    def capture_single_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame (synchronous)
        
        Returns:
            Captured frame as numpy array or None if failed
        """
        if self.cap is None or not self.cap.isOpened():
            logger.error("Camera not initialized")
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        else:
            logger.error("Failed to capture frame")
            return None
    
    def update_config(self, config: CameraConfig):
        """Update camera configuration"""
        was_running = self.is_running
        
        if was_running:
            self.stop_capture()
        
        self.config = config
        self._reinitialize_camera()
        
        if was_running:
            self.start_capture(self.frame_callback)
        
        logger.info("Camera configuration updated")
    
    def _reinitialize_camera(self):
        """Reinitialize camera with new settings"""
        if self.cap:
            self.cap.release()
        self._initialize_camera()
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Get camera information and current settings"""
        if self.cap is None:
            return {}
        
        return {
            'index': self.config.index,
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'brightness': self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
            'contrast': self.cap.get(cv2.CAP_PROP_CONTRAST),
            'saturation': self.cap.get(cv2.CAP_PROP_SATURATION),
            'is_running': self.is_running,
            'frame_count': self.frame_count
        }
    
    def test_camera(self) -> bool:
        """
        Test if camera is working properly
        
        Returns:
            True if camera test passes, False otherwise
        """
        try:
            frame = self.capture_single_frame()
            return frame is not None and frame.size > 0
        except Exception as e:
            logger.error(f"Camera test failed: {e}")
            return False
    
    def release(self):
        """Release camera resources"""
        self.stop_capture()
        if self.cap:
            self.cap.release()
        logger.info("Camera resources released")
    
    def __del__(self):
        """Destructor to ensure resources are released"""
        self.release()


# Global camera instance
_camera_instance = None


def get_camera() -> CameraInterface:
    """Get or create global camera instance"""
    global _camera_instance
    if _camera_instance is None:
        _camera_instance = CameraInterface()
    return _camera_instance


def release_camera():
    """Release global camera instance"""
    global _camera_instance
    if _camera_instance is not None:
        _camera_instance.release()
        _camera_instance = None
        logger.info("Released camera instance")