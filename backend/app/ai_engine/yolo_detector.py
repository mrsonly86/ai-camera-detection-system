"""
YOLOv5 Detection Engine for real-time object detection
"""
import cv2
import torch
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import requests
from ultralytics import YOLO
from loguru import logger
from backend.app.core.config import get_settings

settings = get_settings()


class YOLOv5Detector:
    """YOLOv5 object detection engine"""
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'auto'):
        """
        Initialize YOLOv5 detector
        
        Args:
            model_path: Path to YOLOv5 model file
            device: Device to run inference on ('auto', 'cpu', 'cuda:0', etc.)
        """
        self.model_path = model_path or settings.yolo_model_path
        self.device = self._get_device(device)
        self.model = None
        self.confidence_threshold = 0.25
        self.nms_threshold = 0.45
        self.input_size = 640
        
        # COCO class names
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]
        
        self._load_model()
    
    def _get_device(self, device: str) -> str:
        """Determine the best device for inference"""
        if device == 'auto':
            if torch.cuda.is_available() and settings.gpu_enabled:
                return 'cuda:0'
            else:
                return 'cpu'
        return device
    
    def _load_model(self):
        """Load YOLOv5 model"""
        try:
            # Check if model file exists
            if not Path(self.model_path).exists():
                logger.warning(f"Model file not found at {self.model_path}, downloading default model...")
                self._download_default_model()
            
            # Load model
            self.model = YOLO(self.model_path)
            self.model.to(self.device)
            
            logger.info(f"YOLOv5 model loaded successfully from {self.model_path}")
            logger.info(f"Using device: {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load YOLOv5 model: {e}")
            raise
    
    def _download_default_model(self):
        """Download default YOLOv5 model if not found"""
        try:
            # Create models directory
            model_dir = Path(settings.model_dir)
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Download YOLOv5s model
            model_url = "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt"
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            with open(self.model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded default YOLOv5s model to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to download default model: {e}")
            raise
    
    def detect(self, image: np.ndarray) -> List[Dict]:
        """
        Perform object detection on an image
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of detection dictionaries with bbox, confidence, class info
        """
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            # Run inference
            results = self.model(image, conf=self.confidence_threshold, iou=self.nms_threshold)
            
            detections = []
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf.cpu().numpy())
                        class_id = int(box.cls.cpu().numpy())
                        
                        # Get class name
                        class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}"
                        
                        detection = {
                            'bbox': {
                                'x1': float(x1),
                                'y1': float(y1),
                                'x2': float(x2),
                                'y2': float(y2)
                            },
                            'confidence': confidence,
                            'class_id': class_id,
                            'class_name': class_name
                        }
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []
    
    def detect_persons(self, image: np.ndarray) -> List[Dict]:
        """
        Detect only persons in the image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of person detections
        """
        all_detections = self.detect(image)
        person_detections = [det for det in all_detections if det['class_name'] == 'person']
        return person_detections
    
    def batch_detect(self, images: List[np.ndarray]) -> List[List[Dict]]:
        """
        Perform batch detection on multiple images
        
        Args:
            images: List of input images
            
        Returns:
            List of detection lists for each image
        """
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            # Run batch inference
            results = self.model(images, conf=self.confidence_threshold, iou=self.nms_threshold)
            
            batch_detections = []
            for r in results:
                image_detections = []
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf.cpu().numpy())
                        class_id = int(box.cls.cpu().numpy())
                        class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}"
                        
                        detection = {
                            'bbox': {
                                'x1': float(x1),
                                'y1': float(y1),
                                'x2': float(x2),
                                'y2': float(y2)
                            },
                            'confidence': confidence,
                            'class_id': class_id,
                            'class_name': class_name
                        }
                        image_detections.append(detection)
                
                batch_detections.append(image_detections)
            
            return batch_detections
            
        except Exception as e:
            logger.error(f"Batch detection failed: {e}")
            return [[] for _ in images]
    
    def update_settings(self, confidence_threshold: Optional[float] = None,
                       nms_threshold: Optional[float] = None,
                       input_size: Optional[int] = None):
        """Update detection settings"""
        if confidence_threshold is not None:
            self.confidence_threshold = confidence_threshold
        if nms_threshold is not None:
            self.nms_threshold = nms_threshold
        if input_size is not None:
            self.input_size = input_size
        
        logger.info(f"Updated settings: conf={self.confidence_threshold}, nms={self.nms_threshold}")
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        if self.model is None:
            return {}
        
        return {
            'model_path': self.model_path,
            'device': self.device,
            'confidence_threshold': self.confidence_threshold,
            'nms_threshold': self.nms_threshold,
            'input_size': self.input_size,
            'num_classes': len(self.class_names)
        }


# Global detector instance
_detector_instance = None


def get_detector() -> YOLOv5Detector:
    """Get or create global detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = YOLOv5Detector()
    return _detector_instance


def release_detector():
    """Release global detector instance"""
    global _detector_instance
    if _detector_instance is not None:
        _detector_instance = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Released detector instance")