"""
Database models for the AI Camera Detection System
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    detection_sessions = relationship("DetectionSession", back_populates="user")


class DetectionSession(Base):
    """Detection session model to track analysis sessions"""
    __tablename__ = "detection_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_name = Column(String(100))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    total_detections = Column(Integer, default=0)
    camera_settings = Column(JSON)
    status = Column(String(20), default="active")  # active, completed, stopped
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="detection_sessions")
    detections = relationship("Detection", back_populates="session")


class Detection(Base):
    """Individual detection record"""
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("detection_sessions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Object Detection Data
    object_class = Column(String(50))  # person, car, etc.
    confidence = Column(Float)
    bbox_x1 = Column(Float)
    bbox_y1 = Column(Float)
    bbox_x2 = Column(Float)
    bbox_y2 = Column(Float)
    
    # AI Analysis Results
    gender = Column(String(10))  # male, female, unknown
    gender_confidence = Column(Float)
    estimated_age = Column(Integer)
    age_confidence = Column(Float)
    estimated_height = Column(Float)  # in cm
    estimated_weight = Column(Float)  # in kg
    
    # Image Data
    image_path = Column(String(255))
    thumbnail_path = Column(String(255))
    
    # Alert Status
    is_alert = Column(Boolean, default=False)
    alert_reason = Column(String(255))
    
    # Relationships
    session = relationship("DetectionSession", back_populates="detections")
    face_data = relationship("FaceData", back_populates="detection", uselist=False)


class FaceData(Base):
    """Face recognition and analysis data"""
    __tablename__ = "face_data"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detections.id"))
    
    # Face Recognition
    face_encoding = Column(Text)  # JSON string of face encoding
    face_landmarks = Column(Text)  # JSON string of face landmarks
    
    # Face Quality Metrics
    face_quality_score = Column(Float)
    blur_score = Column(Float)
    brightness_score = Column(Float)
    
    # Identity Matching
    matched_person_id = Column(Integer, ForeignKey("known_persons.id"), nullable=True)
    match_confidence = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    detection = relationship("Detection", back_populates="face_data")
    matched_person = relationship("KnownPerson", back_populates="face_matches")


class KnownPerson(Base):
    """Known persons database for face matching"""
    __tablename__ = "known_persons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Identity Information
    national_id = Column(String(50))
    date_of_birth = Column(DateTime)
    nationality = Column(String(50))
    
    # Status Information
    is_wanted = Column(Boolean, default=False)
    risk_level = Column(String(20))  # low, medium, high, critical
    watch_list_category = Column(String(50))
    
    # Reference Images
    reference_face_encoding = Column(Text)  # Primary face encoding
    reference_image_path = Column(String(255))
    
    # External Database IDs
    police_db_id = Column(String(100))
    interpol_db_id = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    face_matches = relationship("FaceData", back_populates="matched_person")


class SystemConfig(Base):
    """System configuration storage"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text)
    config_type = Column(String(20))  # string, integer, float, boolean, json
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    """Alert and notification system"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detections.id"))
    alert_type = Column(String(50))  # face_match, unknown_person, restricted_area
    severity = Column(String(20))  # low, medium, high, critical
    title = Column(String(200))
    message = Column(Text)
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])


class AuditLog(Base):
    """Audit log for security and compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])