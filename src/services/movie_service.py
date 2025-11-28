"""
Movie CRUD operations
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Movie


class MovieService:
    """Kinolar bilan ishlash servisi"""
    
    @staticmethod
    async def get_by_code(session: AsyncSession, code: int) -> Movie | None:
        """Kod bo'yicha kino qidirish"""
        stmt = select(Movie).where(Movie.code == code)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(session: AsyncSession) -> list[Movie]:
        """Barcha kinolarni olish"""
        stmt = select(Movie).order_by(Movie.created_at.desc())
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(session: AsyncSession, code: int, url: str) -> Movie:
        """Yangi kino qo'shish"""
        movie = Movie(code=code, url=url)
        session.add(movie)
        await session.flush()
        return movie
    
    @staticmethod
    async def delete(session: AsyncSession, code: int) -> bool:
        """Kino o'chirish"""
        movie = await MovieService.get_by_code(session, code)
        if movie:
            await session.delete(movie)
            await session.flush()
            return True
        return False
    
    @staticmethod
    async def exists(session: AsyncSession, code: int) -> bool:
        """Kod mavjud yoki yo'qligini tekshirish"""
        result = await session.execute(
            select(Movie).where(Movie.code == code)
        )
        return result.scalar_one_or_none() is not None
