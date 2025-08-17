"""
Detection service for managing detection sessions and results
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.database_models import DetectionSession, Detection
from backend.app.models.schemas import DetectionSessionCreate, DetectionSessionUpdate


class DetectionService:
    """Service class for detection operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user_id: int, session_data: DetectionSessionCreate) -> DetectionSession:
        """Create a new detection session"""
        db_session = DetectionSession(
            user_id=user_id,
            session_name=session_data.session_name,
            camera_settings=session_data.camera_settings,
            start_time=datetime.utcnow()
        )
        
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        
        return db_session
    
    def get_session_by_id(self, session_id: int) -> Optional[DetectionSession]:
        """Get detection session by ID"""
        return self.db.query(DetectionSession).filter(DetectionSession.id == session_id).first()
    
    def get_user_sessions(self, user_id: int) -> List[DetectionSession]:
        """Get all sessions for a user"""
        return self.db.query(DetectionSession)\
                     .filter(DetectionSession.user_id == user_id)\
                     .order_by(desc(DetectionSession.created_at))\
                     .all()
    
    def update_session(self, session_id: int, session_data: DetectionSessionUpdate) -> Optional[DetectionSession]:
        """Update detection session"""
        session = self.get_session_by_id(session_id)
        if not session:
            return None
        
        if session_data.session_name is not None:
            session.session_name = session_data.session_name
        if session_data.status is not None:
            session.status = session_data.status
            if session_data.status in ['completed', 'stopped']:
                session.end_time = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def save_detection(self, session_id: int, detection_data: Dict[str, Any], 
                      image_path: Optional[str] = None) -> Detection:
        """Save a detection result"""
        bbox = detection_data.get('bbox', {})
        
        db_detection = Detection(
            session_id=session_id,
            timestamp=datetime.utcnow(),
            object_class=detection_data.get('object_class', 'unknown'),
            confidence=detection_data.get('confidence', 0.0),
            bbox_x1=bbox.get('x1', 0.0),
            bbox_y1=bbox.get('y1', 0.0),
            bbox_x2=bbox.get('x2', 0.0),
            bbox_y2=bbox.get('y2', 0.0),
            gender=detection_data.get('gender'),
            gender_confidence=detection_data.get('gender_confidence'),
            estimated_age=detection_data.get('estimated_age'),
            age_confidence=detection_data.get('age_confidence'),
            estimated_height=detection_data.get('estimated_height'),
            estimated_weight=detection_data.get('estimated_weight'),
            image_path=image_path
        )
        
        # Check for alerts
        face_match = detection_data.get('face_match', {})
        if face_match.get('matched') and face_match.get('metadata', {}).get('is_wanted'):
            db_detection.is_alert = True
            db_detection.alert_reason = f"Wanted person detected: {face_match.get('name')}"
        
        self.db.add(db_detection)
        
        # Update session detection count
        session = self.get_session_by_id(session_id)
        if session:
            session.total_detections += 1
        
        self.db.commit()
        self.db.refresh(db_detection)
        
        return db_detection
    
    def get_session_detections(self, session_id: int, limit: int = 100) -> List[Detection]:
        """Get detections for a session"""
        return self.db.query(Detection)\
                     .filter(Detection.session_id == session_id)\
                     .order_by(desc(Detection.timestamp))\
                     .limit(limit)\
                     .all()
    
    def get_detection_by_id(self, detection_id: int) -> Optional[Detection]:
        """Get detection by ID"""
        return self.db.query(Detection).filter(Detection.id == detection_id).first()
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a detection session and all its detections"""
        session = self.get_session_by_id(session_id)
        if not session:
            return False
        
        # Delete all detections first
        self.db.query(Detection).filter(Detection.session_id == session_id).delete()
        
        # Delete session
        self.db.delete(session)
        self.db.commit()
        
        return True
    
    def get_recent_detections(self, user_id: int, limit: int = 50) -> List[Detection]:
        """Get recent detections for a user"""
        return self.db.query(Detection)\
                     .join(DetectionSession)\
                     .filter(DetectionSession.user_id == user_id)\
                     .order_by(desc(Detection.timestamp))\
                     .limit(limit)\
                     .all()
    
    def get_alert_detections(self, user_id: int, limit: int = 20) -> List[Detection]:
        """Get alert detections for a user"""
        return self.db.query(Detection)\
                     .join(DetectionSession)\
                     .filter(DetectionSession.user_id == user_id)\
                     .filter(Detection.is_alert == True)\
                     .order_by(desc(Detection.timestamp))\
                     .limit(limit)\
                     .all()