from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Bot sozlamalari"""
    
    BOT_TOKEN: str
    DATABASE_URL: str
    DEBUG: bool = False
    
    # Adminlar - vergul bilan ajratilgan raqamlar
    ADMINS: List[int] = []
    
    # Obuna kanallari - vergul bilan ajratilgan raqamlar
    SUBSCRIPTION_CHANNELS: List[int] = []
    
    class Config:
        env_file = ".env"

settings = Settings()