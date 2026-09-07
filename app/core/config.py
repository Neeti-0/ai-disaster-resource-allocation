import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./disaster_allocation.db"
    
    # API
    API_TITLE: str = "AI Disaster Resource Allocation Backend"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Backend for AI-powered disaster resource allocation with constraint optimization"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Optimization
    OPTIMIZATION_TIMEOUT_SECONDS: int = 300
    MAX_ZONES: int = 10000
    MAX_RESOURCES: int = 10000
    MAX_FACILITIES: int = 1000
    
    # Priority Weights
    PRIORITY_WEIGHTS: dict = {
        "population": 0.2,
        "medical_need": 0.25,
        "vulnerability": 0.15,
        "damage": 0.2,
        "shortage": 0.12,
        "accessibility": 0.08
    }
    
    # Demand Estimation Defaults
    WATER_PER_PERSON_LITERS: float = 7.5
    FOOD_PER_PERSON_PACKETS: float = 0.5
    MEDICINE_PER_100_PEOPLE: float = 5.0
    BLANKET_PER_PERSON: float = 0.3
    TENT_PER_PERSON: float = 0.1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # ML Model
    ML_MODEL_PATH: str = "./app/ml/models/priority_model.pkl"
    USE_ML_MODEL: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
