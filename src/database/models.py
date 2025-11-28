"""
SQLAlchemy modellar - Users va Movies
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User modeli"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, is_admin={self.is_admin})>"


class Movie(Base):
    """Movie modeli"""
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True, nullable=False, index=True)
    url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Movie(code={self.code}, url={self.url})>"
