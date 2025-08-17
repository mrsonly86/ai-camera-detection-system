"""
Face recognition system for identity matching
"""
import cv2
import numpy as np
import pickle
import face_recognition
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from loguru import logger
from backend.app.core.config import get_settings

settings = get_settings()


class FaceRecognitionSystem:
    """Face recognition and identity matching system"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.face_model_path
        self.known_faces = {}  # name -> list of encodings
        self.known_face_metadata = {}  # name -> metadata dict
        self.tolerance = 0.6  # Face matching tolerance
        
        self._load_known_faces()
    
    def _load_known_faces(self):
        """Load known faces from file"""
        try:
            if Path(self.model_path).exists():
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_faces = data.get('faces', {})
                    self.known_face_metadata = data.get('metadata', {})
                logger.info(f"Loaded {len(self.known_faces)} known faces from {self.model_path}")
            else:
                logger.info("No existing face database found, starting with empty database")
                self._create_sample_database()
        except Exception as e:
            logger.error(f"Failed to load known faces: {e}")
            self.known_faces = {}
            self.known_face_metadata = {}
    
    def _create_sample_database(self):
        """Create sample face database for demonstration"""
        # This would normally be populated with real face data
        self.known_faces = {}
        self.known_face_metadata = {}
        self._save_known_faces()
        logger.info("Created empty face database")
    
    def _save_known_faces(self):
        """Save known faces to file"""
        try:
            Path(settings.model_dir).mkdir(parents=True, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                data = {
                    'faces': self.known_faces,
                    'metadata': self.known_face_metadata
                }
                pickle.dump(data, f)
            logger.info(f"Saved face database to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save known faces: {e}")
    
    def encode_face(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face encoding from image
        
        Args:
            face_image: Face image as numpy array
            
        Returns:
            Face encoding array or None if no face found
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Find face locations
            face_locations = face_recognition.face_locations(rgb_image)
            
            if not face_locations:
                return None
            
            # Get face encoding (use the first face if multiple found)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if face_encodings:
                return face_encodings[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Face encoding failed: {e}")
            return None
    
    def add_known_face(self, face_image: np.ndarray, person_name: str, 
                      metadata: Optional[Dict] = None) -> bool:
        """
        Add a new known face to the database
        
        Args:
            face_image: Face image
            person_name: Name/ID of the person
            metadata: Additional metadata about the person
            
        Returns:
            True if face was added successfully
        """
        try:
            encoding = self.encode_face(face_image)
            if encoding is None:
                logger.error(f"Could not extract face encoding for {person_name}")
                return False
            
            # Add to known faces
            if person_name not in self.known_faces:
                self.known_faces[person_name] = []
            
            self.known_faces[person_name].append(encoding)
            
            # Add metadata
            if metadata:
                self.known_face_metadata[person_name] = metadata
            
            # Save to file
            self._save_known_faces()
            
            logger.info(f"Added face for {person_name} to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add known face: {e}")
            return False
    
    def recognize_face(self, face_image: np.ndarray) -> Dict:
        """
        Recognize face and find best match
        
        Args:
            face_image: Face image to recognize
            
        Returns:
            Dictionary with recognition results
        """
        try:
            # Encode the input face
            unknown_encoding = self.encode_face(face_image)
            if unknown_encoding is None:
                return {
                    'matched': False,
                    'name': 'unknown',
                    'confidence': 0.0,
                    'distance': 1.0
                }
            
            best_match_name = 'unknown'
            best_distance = 1.0
            
            # Compare with all known faces
            for person_name, encodings in self.known_faces.items():
                for encoding in encodings:
                    # Calculate face distance
                    distance = face_recognition.face_distance([encoding], unknown_encoding)[0]
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_match_name = person_name
            
            # Check if match is within tolerance
            is_match = best_distance <= self.tolerance
            confidence = max(0.0, 1.0 - best_distance)
            
            result = {
                'matched': is_match,
                'name': best_match_name if is_match else 'unknown',
                'confidence': confidence,
                'distance': best_distance
            }
            
            # Add metadata if available
            if is_match and best_match_name in self.known_face_metadata:
                result['metadata'] = self.known_face_metadata[best_match_name]
            
            return result
            
        except Exception as e:
            logger.error(f"Face recognition failed: {e}")
            return {
                'matched': False,
                'name': 'unknown',
                'confidence': 0.0,
                'distance': 1.0
            }
    
    def batch_recognize(self, face_images: List[np.ndarray]) -> List[Dict]:
        """
        Recognize multiple faces in batch
        
        Args:
            face_images: List of face images
            
        Returns:
            List of recognition results
        """
        results = []
        for face_image in face_images:
            result = self.recognize_face(face_image)
            results.append(result)
        return results
    
    def update_tolerance(self, tolerance: float):
        """Update face matching tolerance"""
        self.tolerance = max(0.0, min(1.0, tolerance))
        logger.info(f"Updated face recognition tolerance to {self.tolerance}")
    
    def remove_known_face(self, person_name: str) -> bool:
        """
        Remove a person from the known faces database
        
        Args:
            person_name: Name of person to remove
            
        Returns:
            True if person was removed
        """
        try:
            if person_name in self.known_faces:
                del self.known_faces[person_name]
                
            if person_name in self.known_face_metadata:
                del self.known_face_metadata[person_name]
            
            self._save_known_faces()
            logger.info(f"Removed {person_name} from face database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove known face: {e}")
            return False
    
    def get_known_faces_list(self) -> List[Dict]:
        """Get list of all known faces with metadata"""
        faces_list = []
        for name, encodings in self.known_faces.items():
            face_info = {
                'name': name,
                'num_encodings': len(encodings),
                'metadata': self.known_face_metadata.get(name, {})
            }
            faces_list.append(face_info)
        return faces_list
    
    def calculate_face_quality(self, face_image: np.ndarray) -> Dict[str, float]:
        """
        Calculate various quality metrics for a face image
        
        Args:
            face_image: Face image
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            # Convert to grayscale for some calculations
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(sharpness / 1000.0, 1.0)
            
            # Brightness
            brightness = np.mean(gray)
            brightness_score = 1.0 - abs(brightness - 128) / 128.0
            
            # Contrast (standard deviation)
            contrast = np.std(gray)
            contrast_score = min(contrast / 50.0, 1.0)
            
            # Face detection confidence
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)
            detection_score = 1.0 if face_locations else 0.0
            
            # Overall quality score
            overall_score = (sharpness_score + brightness_score + contrast_score + detection_score) / 4.0
            
            return {
                'sharpness': sharpness_score,
                'brightness': brightness_score,
                'contrast': contrast_score,
                'detection': detection_score,
                'overall': overall_score
            }
            
        except Exception as e:
            logger.error(f"Face quality calculation failed: {e}")
            return {
                'sharpness': 0.0,
                'brightness': 0.0,
                'contrast': 0.0,
                'detection': 0.0,
                'overall': 0.0
            }
    
    def get_statistics(self) -> Dict:
        """Get face recognition system statistics"""
        total_persons = len(self.known_faces)
        total_encodings = sum(len(encodings) for encodings in self.known_faces.values())
        
        return {
            'total_known_persons': total_persons,
            'total_face_encodings': total_encodings,
            'tolerance': self.tolerance,
            'database_path': self.model_path
        }


# Global face recognition instance
_face_recognition_instance = None


def get_face_recognition() -> FaceRecognitionSystem:
    """Get or create global face recognition instance"""
    global _face_recognition_instance
    if _face_recognition_instance is None:
        _face_recognition_instance = FaceRecognitionSystem()
    return _face_recognition_instance