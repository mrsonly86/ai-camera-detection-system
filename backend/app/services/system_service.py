"""
System service for managing system configuration and settings
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.database_models import SystemConfig
from backend.app.models.schemas import SystemConfigUpdate


class SystemService:
    """Service class for system configuration operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_config(self, config_key: str) -> Optional[SystemConfig]:
        """Get a configuration value by key"""
        return self.db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    
    def get_all_configs(self) -> List[SystemConfig]:
        """Get all configuration settings"""
        return self.db.query(SystemConfig).order_by(SystemConfig.config_key).all()
    
    def create_config(self, config_key: str, config_value: str, 
                     config_type: str = "string", description: str = "") -> SystemConfig:
        """Create a new configuration setting"""
        db_config = SystemConfig(
            config_key=config_key,
            config_value=config_value,
            config_type=config_type,
            description=description
        )
        
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        
        return db_config
    
    def update_config(self, config_key: str, config_data: SystemConfigUpdate) -> Optional[SystemConfig]:
        """Update a configuration setting"""
        config = self.get_config(config_key)
        if not config:
            return None
        
        config.config_value = config_data.config_value
        if config_data.description is not None:
            config.description = config_data.description
        
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    def create_or_update_config(self, config_key: str, config_value: str,
                               config_type: str = "string", description: str = "") -> SystemConfig:
        """Create or update a configuration setting"""
        existing_config = self.get_config(config_key)
        
        if existing_config:
            existing_config.config_value = config_value
            if description:
                existing_config.description = description
            self.db.commit()
            self.db.refresh(existing_config)
            return existing_config
        else:
            return self.create_config(config_key, config_value, config_type, description)
    
    def delete_config(self, config_key: str) -> bool:
        """Delete a configuration setting"""
        config = self.get_config(config_key)
        if not config:
            return False
        
        self.db.delete(config)
        self.db.commit()
        
        return True
    
    def get_config_value(self, config_key: str, default_value: str = "") -> str:
        """Get configuration value with default fallback"""
        config = self.get_config(config_key)
        return config.config_value if config else default_value
    
    def get_config_as_bool(self, config_key: str, default_value: bool = False) -> bool:
        """Get configuration value as boolean"""
        config = self.get_config(config_key)
        if not config:
            return default_value
        
        return config.config_value.lower() in ('true', '1', 'yes', 'on')
    
    def get_config_as_int(self, config_key: str, default_value: int = 0) -> int:
        """Get configuration value as integer"""
        config = self.get_config(config_key)
        if not config:
            return default_value
        
        try:
            return int(config.config_value)
        except ValueError:
            return default_value
    
    def get_config_as_float(self, config_key: str, default_value: float = 0.0) -> float:
        """Get configuration value as float"""
        config = self.get_config(config_key)
        if not config:
            return default_value
        
        try:
            return float(config.config_value)
        except ValueError:
            return default_value