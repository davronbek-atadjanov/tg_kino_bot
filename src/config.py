from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Barcha konfiguratsiyalar"""
    
    # Bot sozlamalari
    BOT_TOKEN: str
    
    # Database
    DATABASE_URL: str    

    # Adminlar ro'yxati 
    ADMINS: List[int] = []

    SUBSCRIPTION_CHANNELS: List[int] = []
    # Boshqa
    DEBUG: bool = False

    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()