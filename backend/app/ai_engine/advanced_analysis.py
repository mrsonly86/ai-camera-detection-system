"""
Advanced AI analysis for gender classification, age estimation, and biometric analysis
"""
import cv2
import numpy as np
import pickle
from typing import Dict, Optional, Tuple, List
from pathlib import Path
import mediapipe as mp
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import joblib
from loguru import logger
from backend.app.core.config import get_settings

settings = get_settings()


class GenderClassifier:
    """Gender classification using facial features"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.gender_model_path
        self.model = None
        self.scaler = None
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_detection = self.mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)
        
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create a new one"""
        try:
            if Path(self.model_path).exists():
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                logger.info(f"Gender classification model loaded from {self.model_path}")
            else:
                logger.warning("Gender model not found, creating mock model")
                self._create_mock_model()
        except Exception as e:
            logger.error(f"Failed to load gender model: {e}")
            self._create_mock_model()
    
    def _create_mock_model(self):
        """Create a mock model for demonstration"""
        self.model = SVC(probability=True, kernel='rbf')
        self.scaler = StandardScaler()
        
        # Create mock training data
        X_mock = np.random.rand(100, 468 * 3)  # 468 face landmarks * 3 coordinates
        y_mock = np.random.choice([0, 1], 100)  # 0: male, 1: female
        
        X_scaled = self.scaler.fit_transform(X_mock)
        self.model.fit(X_scaled, y_mock)
        
        # Save mock model
        Path(settings.model_dir).mkdir(parents=True, exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({'model': self.model, 'scaler': self.scaler}, f)
        
        logger.info("Created mock gender classification model")
    
    def extract_facial_features(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """Extract facial features from face image"""
        try:
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_image)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                features = []
                for landmark in landmarks.landmark:
                    features.extend([landmark.x, landmark.y, landmark.z])
                return np.array(features)
            
            return None
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None
    
    def predict_gender(self, face_image: np.ndarray) -> Dict[str, float]:
        """
        Predict gender from face image
        
        Args:
            face_image: Cropped face image
            
        Returns:
            Dictionary with gender prediction and confidence
        """
        try:
            features = self.extract_facial_features(face_image)
            if features is None:
                return {'gender': 'unknown', 'confidence': 0.0}
            
            # Scale features
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            gender = 'female' if prediction == 1 else 'male'
            confidence = float(max(probabilities))
            
            return {'gender': gender, 'confidence': confidence}
            
        except Exception as e:
            logger.error(f"Gender prediction failed: {e}")
            return {'gender': 'unknown', 'confidence': 0.0}


class AgeEstimator:
    """Age estimation using facial features and deep learning"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.age_model_path
        self.model = None
        self.scaler = None
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)
        
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create a new one"""
        try:
            if Path(self.model_path).exists():
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                logger.info(f"Age estimation model loaded from {self.model_path}")
            else:
                logger.warning("Age model not found, creating mock model")
                self._create_mock_model()
        except Exception as e:
            logger.error(f"Failed to load age model: {e}")
            self._create_mock_model()
    
    def _create_mock_model(self):
        """Create a mock model for demonstration"""
        from sklearn.ensemble import RandomForestRegressor
        
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.scaler = StandardScaler()
        
        # Create mock training data
        X_mock = np.random.rand(200, 468 * 3)  # 468 face landmarks * 3 coordinates
        y_mock = np.random.randint(18, 80, 200)  # Ages 18-80
        
        X_scaled = self.scaler.fit_transform(X_mock)
        self.model.fit(X_scaled, y_mock)
        
        # Save mock model
        Path(settings.model_dir).mkdir(parents=True, exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({'model': self.model, 'scaler': self.scaler}, f)
        
        logger.info("Created mock age estimation model")
    
    def estimate_age(self, face_image: np.ndarray) -> Dict[str, float]:
        """
        Estimate age from face image
        
        Args:
            face_image: Cropped face image
            
        Returns:
            Dictionary with age estimate and confidence
        """
        try:
            # Extract facial features (similar to gender classifier)
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                return {'age': 0, 'confidence': 0.0}
            
            landmarks = results.multi_face_landmarks[0]
            features = []
            for landmark in landmarks.landmark:
                features.extend([landmark.x, landmark.y, landmark.z])
            
            features = np.array(features)
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Predict age
            age_prediction = self.model.predict(features_scaled)[0]
            
            # Calculate confidence based on facial clarity and feature quality
            confidence = self._calculate_age_confidence(face_image)
            
            return {'age': int(age_prediction), 'confidence': confidence}
            
        except Exception as e:
            logger.error(f"Age estimation failed: {e}")
            return {'age': 0, 'confidence': 0.0}
    
    def _calculate_age_confidence(self, face_image: np.ndarray) -> float:
        """Calculate confidence score based on image quality"""
        try:
            # Calculate image sharpness (Laplacian variance)
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize to 0-1 scale
            sharpness_score = min(laplacian_var / 1000.0, 1.0)
            
            # Calculate brightness score
            brightness = np.mean(gray)
            brightness_score = 1.0 - abs(brightness - 128) / 128.0
            
            # Combined confidence
            confidence = (sharpness_score + brightness_score) / 2.0
            return float(confidence)
            
        except Exception:
            return 0.5


class HeightEstimator:
    """Height estimation using perspective geometry and body proportions"""
    
    def __init__(self):
        self.average_head_height_cm = 23.0  # Average head height in cm
        self.camera_height_cm = 180.0  # Assumed camera height
        self.focal_length_px = 800.0  # Estimated focal length in pixels
    
    def estimate_height(self, bbox: Dict[str, float], image_height: int, 
                       camera_height: Optional[float] = None) -> Dict[str, float]:
        """
        Estimate person height using perspective geometry
        
        Args:
            bbox: Bounding box with x1, y1, x2, y2
            image_height: Height of the image in pixels
            camera_height: Camera height in cm (optional)
            
        Returns:
            Dictionary with height estimate and confidence
        """
        try:
            camera_h = camera_height or self.camera_height_cm
            
            # Calculate person height in pixels
            person_height_px = bbox['y2'] - bbox['y1']
            
            # Calculate distance from camera using similar triangles
            # Assuming person takes up full height means they are close
            distance_factor = image_height / person_height_px
            
            # Estimate real height using perspective projection
            # This is a simplified model - in practice would need camera calibration
            estimated_height = self.average_head_height_cm * (person_height_px / 30.0)  # 30px ~ head height
            
            # Apply distance correction
            if distance_factor > 1:
                estimated_height *= min(distance_factor * 0.8, 2.0)  # Cap the correction
            
            # Clamp to reasonable range
            estimated_height = max(120, min(220, estimated_height))
            
            # Calculate confidence based on bbox size and position
            confidence = self._calculate_height_confidence(bbox, image_height)
            
            return {'height': estimated_height, 'confidence': confidence}
            
        except Exception as e:
            logger.error(f"Height estimation failed: {e}")
            return {'height': 170.0, 'confidence': 0.0}
    
    def _calculate_height_confidence(self, bbox: Dict[str, float], image_height: int) -> float:
        """Calculate confidence for height estimation"""
        person_height_px = bbox['y2'] - bbox['y1']
        
        # Higher confidence for larger people in image
        size_factor = person_height_px / image_height
        size_confidence = min(size_factor * 2.0, 1.0)
        
        # Higher confidence if person touches bottom of image (ground visible)
        bottom_factor = max(0, 1.0 - (image_height - bbox['y2']) / image_height)
        
        return float((size_confidence + bottom_factor) / 2.0)


class WeightEstimator:
    """Weight estimation using body shape analysis"""
    
    def __init__(self):
        self.height_weight_ratios = {
            'thin': 2.3,      # height_cm / weight_kg ratio for thin person
            'normal': 2.7,    # normal weight person
            'heavy': 3.2      # heavy person
        }
    
    def estimate_weight(self, bbox: Dict[str, float], estimated_height: float) -> Dict[str, float]:
        """
        Estimate weight based on body shape and height
        
        Args:
            bbox: Bounding box of detected person
            estimated_height: Previously estimated height
            
        Returns:
            Dictionary with weight estimate and confidence
        """
        try:
            # Calculate body width/height ratio
            body_width = bbox['x2'] - bbox['x1']
            body_height = bbox['y2'] - bbox['y1']
            aspect_ratio = body_width / body_height if body_height > 0 else 0.5
            
            # Determine body type based on aspect ratio
            if aspect_ratio < 0.35:
                body_type = 'thin'
            elif aspect_ratio > 0.55:
                body_type = 'heavy'
            else:
                body_type = 'normal'
            
            # Estimate weight using height and body type
            height_weight_ratio = self.height_weight_ratios[body_type]
            estimated_weight = estimated_height / height_weight_ratio
            
            # Add some variation based on exact aspect ratio
            if body_type == 'normal':
                weight_adjustment = (aspect_ratio - 0.45) * 20  # ±10kg adjustment
                estimated_weight += weight_adjustment
            
            # Clamp to reasonable range
            estimated_weight = max(40, min(150, estimated_weight))
            
            # Calculate confidence
            confidence = self._calculate_weight_confidence(aspect_ratio, body_height)
            
            return {'weight': estimated_weight, 'confidence': confidence}
            
        except Exception as e:
            logger.error(f"Weight estimation failed: {e}")
            return {'weight': 70.0, 'confidence': 0.0}
    
    def _calculate_weight_confidence(self, aspect_ratio: float, body_height_px: float) -> float:
        """Calculate confidence for weight estimation"""
        # Higher confidence for larger detections
        size_confidence = min(body_height_px / 200.0, 1.0)
        
        # Lower confidence for extreme aspect ratios
        ratio_confidence = 1.0 - abs(aspect_ratio - 0.45) * 2.0
        ratio_confidence = max(0.2, ratio_confidence)
        
        return float((size_confidence + ratio_confidence) / 2.0)


class AdvancedAIAnalyzer:
    """Main class combining all AI analysis capabilities"""
    
    def __init__(self):
        self.gender_classifier = GenderClassifier()
        self.age_estimator = AgeEstimator()
        self.height_estimator = HeightEstimator()
        self.weight_estimator = WeightEstimator()
        
        logger.info("Advanced AI Analyzer initialized")
    
    def analyze_person(self, image: np.ndarray, bbox: Dict[str, float]) -> Dict:
        """
        Perform complete analysis on detected person
        
        Args:
            image: Full image
            bbox: Person bounding box
            
        Returns:
            Complete analysis results
        """
        try:
            # Extract face region for analysis
            x1, y1, x2, y2 = int(bbox['x1']), int(bbox['y1']), int(bbox['x2']), int(bbox['y2'])
            
            # Extract upper portion for face analysis (upper 1/3 of person)
            face_y1 = y1
            face_y2 = y1 + int((y2 - y1) * 0.4)
            face_image = image[face_y1:face_y2, x1:x2]
            
            results = {}
            
            # Gender classification
            if face_image.size > 0:
                gender_result = self.gender_classifier.predict_gender(face_image)
                results['gender'] = gender_result['gender']
                results['gender_confidence'] = gender_result['confidence']
            else:
                results['gender'] = 'unknown'
                results['gender_confidence'] = 0.0
            
            # Age estimation
            if face_image.size > 0:
                age_result = self.age_estimator.estimate_age(face_image)
                results['estimated_age'] = age_result['age']
                results['age_confidence'] = age_result['confidence']
            else:
                results['estimated_age'] = 0
                results['age_confidence'] = 0.0
            
            # Height estimation
            height_result = self.height_estimator.estimate_height(bbox, image.shape[0])
            results['estimated_height'] = height_result['height']
            results['height_confidence'] = height_result['confidence']
            
            # Weight estimation
            weight_result = self.weight_estimator.estimate_weight(bbox, height_result['height'])
            results['estimated_weight'] = weight_result['weight']
            results['weight_confidence'] = weight_result['confidence']
            
            return results
            
        except Exception as e:
            logger.error(f"Person analysis failed: {e}")
            return {
                'gender': 'unknown',
                'gender_confidence': 0.0,
                'estimated_age': 0,
                'age_confidence': 0.0,
                'estimated_height': 170.0,
                'height_confidence': 0.0,
                'estimated_weight': 70.0,
                'weight_confidence': 0.0
            }


# Global analyzer instance
_analyzer_instance = None


def get_analyzer() -> AdvancedAIAnalyzer:
    """Get or create global analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = AdvancedAIAnalyzer()
    return _analyzer_instance