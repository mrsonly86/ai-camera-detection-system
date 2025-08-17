"""
Pydantic models for API request/response schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# Detection Schemas
class BoundingBox(BaseModel):
    x1: float = Field(..., ge=0)
    y1: float = Field(..., ge=0)
    x2: float = Field(..., ge=0)
    y2: float = Field(..., ge=0)


class DetectionResult(BaseModel):
    object_class: str
    confidence: float = Field(..., ge=0, le=1)
    bbox: BoundingBox
    
    # AI Analysis Results
    gender: Optional[str] = None
    gender_confidence: Optional[float] = None
    estimated_age: Optional[int] = None
    age_confidence: Optional[float] = None
    estimated_height: Optional[float] = None
    estimated_weight: Optional[float] = None
    
    # Face Recognition
    face_match: Optional[Dict[str, Any]] = None
    face_quality_score: Optional[float] = None


class DetectionSessionCreate(BaseModel):
    session_name: str = Field(..., max_length=100)
    camera_settings: Optional[Dict[str, Any]] = None


class DetectionSessionUpdate(BaseModel):
    session_name: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r'^(active|completed|stopped)$')


class DetectionSession(BaseModel):
    id: int
    session_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_detections: int
    camera_settings: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Detection(BaseModel):
    id: int
    session_id: int
    timestamp: datetime
    object_class: str
    confidence: float
    bbox_x1: float
    bbox_y1: float
    bbox_x2: float
    bbox_y2: float
    gender: Optional[str] = None
    gender_confidence: Optional[float] = None
    estimated_age: Optional[int] = None
    age_confidence: Optional[float] = None
    estimated_height: Optional[float] = None
    estimated_weight: Optional[float] = None
    image_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    is_alert: bool = False
    alert_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


# Known Person Schemas
class KnownPersonCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    national_id: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    is_wanted: bool = False
    risk_level: Optional[str] = Field(None, pattern=r'^(low|medium|high|critical)$')
    watch_list_category: Optional[str] = None


class KnownPersonUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_wanted: Optional[bool] = None
    risk_level: Optional[str] = None
    watch_list_category: Optional[str] = None


class KnownPerson(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    national_id: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    is_wanted: bool
    risk_level: Optional[str] = None
    watch_list_category: Optional[str] = None
    reference_image_path: Optional[str] = None
    police_db_id: Optional[str] = None
    interpol_db_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Alert Schemas
class AlertCreate(BaseModel):
    detection_id: int
    alert_type: str = Field(..., max_length=50)
    severity: str = Field(..., pattern=r'^(low|medium|high|critical)$')
    title: str = Field(..., max_length=200)
    message: str


class Alert(BaseModel):
    id: int
    detection_id: int
    alert_type: str
    severity: str
    title: str
    message: str
    is_acknowledged: bool
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Camera Configuration Schemas
class CameraConfig(BaseModel):
    camera_index: int = Field(default=0, ge=0)
    width: int = Field(default=1920, ge=640)
    height: int = Field(default=1080, ge=480)
    fps: int = Field(default=30, ge=1, le=60)
    brightness: Optional[float] = Field(None, ge=0, le=1)
    contrast: Optional[float] = Field(None, ge=0, le=2)
    saturation: Optional[float] = Field(None, ge=0, le=2)


# AI Model Configuration Schemas
class ModelConfig(BaseModel):
    model_type: str = Field(..., pattern=r'^(yolo|face_recognition|gender|age)$')
    model_path: str
    confidence_threshold: float = Field(default=0.5, ge=0, le=1)
    nms_threshold: float = Field(default=0.4, ge=0, le=1)
    input_size: Optional[List[int]] = None
    batch_size: int = Field(default=1, ge=1)
    gpu_enabled: bool = True


# Statistics Schemas
class DetectionStats(BaseModel):
    total_detections: int
    total_persons: int
    male_count: int
    female_count: int
    unknown_gender_count: int
    average_age: Optional[float] = None
    age_distribution: Dict[str, int]  # age ranges
    alerts_count: int
    critical_alerts_count: int


class SessionStats(BaseModel):
    session_id: int
    session_name: str
    duration_minutes: Optional[float] = None
    detections_per_minute: Optional[float] = None
    detection_stats: DetectionStats


# System Configuration Schemas
class SystemConfigUpdate(BaseModel):
    config_value: str
    description: Optional[str] = None


class SystemConfig(BaseModel):
    id: int
    config_key: str
    config_value: str
    config_type: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Response Schemas
class ResponseMessage(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int