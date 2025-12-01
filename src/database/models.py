"""
SQLAlchemy modellar - Users va Movies
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserType:
    """Foydalanuvchi turlari"""     
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"
    

class User(Base):
    """User modeli"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    user_type = Column(String(20), default=UserType.USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, user_type={self.user_type})>"

class Movie(Base):
    """Movie modeli"""      
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True, nullable=False, index=True)
    message_id = Column(String(255), nullable=False)  # Telegram post message identifier (file_id or chat_id:message_id)
    caption = Column(Text, nullable=True)           # Video tavsifi
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Movie(code={self.code}, message_id={self.message_id}, caption={self.caption[:30]}...)>"
