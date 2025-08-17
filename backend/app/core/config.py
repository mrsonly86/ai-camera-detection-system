"""
Core configuration settings for the AI Camera Detection System
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Configuration
    app_name: str = Field(default="AI Camera Detection System", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./ai_camera_detection.db", env="DATABASE_URL")
    postgres_url: Optional[str] = Field(default=None, env="POSTGRES_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # AI Model Configuration
    yolo_model_path: str = Field(default="./models/yolov5s.pt", env="YOLO_MODEL_PATH")
    face_model_path: str = Field(default="./models/face_recognition_model.pkl", env="FACE_MODEL_PATH")
    gender_model_path: str = Field(default="./models/gender_model.pkl", env="GENDER_MODEL_PATH")
    age_model_path: str = Field(default="./models/age_model.pkl", env="AGE_MODEL_PATH")
    
    # Camera Configuration
    camera_index: int = Field(default=0, env="CAMERA_INDEX")
    camera_width: int = Field(default=1920, env="CAMERA_WIDTH")
    camera_height: int = Field(default=1080, env="CAMERA_HEIGHT")
    camera_fps: int = Field(default=30, env="CAMERA_FPS")
    
    # Security Settings
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    encryption_key: str = Field(default="your-encryption-key-change-in-production", env="ENCRYPTION_KEY")
    
    # External API Configuration (Mock)
    police_api_url: str = Field(default="http://localhost:8001/api/v1", env="POLICE_API_URL")
    interpol_api_url: str = Field(default="http://localhost:8002/api/v1", env="INTERPOL_API_URL")
    police_api_key: str = Field(default="mock-police-api-key", env="POLICE_API_KEY")
    interpol_api_key: str = Field(default="mock-interpol-api-key", env="INTERPOL_API_KEY")
    
    # Performance Settings
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    batch_size: int = Field(default=8, env="BATCH_SIZE")
    gpu_enabled: bool = Field(default=True, env="GPU_ENABLED")
    tensorrt_enabled: bool = Field(default=False, env="TENSORRT_ENABLED")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    # Storage Configuration
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    model_dir: str = Field(default="./models", env="MODEL_DIR")
    cache_dir: str = Field(default="./cache", env="CACHE_DIR")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings