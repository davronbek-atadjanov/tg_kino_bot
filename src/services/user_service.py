"""
User operations
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User


class UserService:
    """Foydalanuvchilar bilan ishlash servisi"""
    
    @staticmethod
    async def get_or_create(session: AsyncSession, telegram_id: int) -> User:
        """User olish yoki yaratish"""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(telegram_id=telegram_id)
            session.add(user)
            await session.flush()
        
        return user
    
    @staticmethod
    async def is_admin(session: AsyncSession, telegram_id: int) -> bool:
        """Admin yoki yo'qligini tekshirish"""
        user = await UserService.get_or_create(session, telegram_id)
        return user.is_admin
    
    @staticmethod
    async def set_admin(session: AsyncSession, telegram_id: int, is_admin: bool):
        """Admin statusini o'zgartirish"""
        user = await UserService.get_or_create(session, telegram_id)
        user.is_admin = is_admin
        await session.flush()