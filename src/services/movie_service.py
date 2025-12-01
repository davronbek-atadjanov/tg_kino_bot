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
    async def create(session: AsyncSession, code: int, message_id: str, caption: str = None) -> Movie:
        """
        Yangi kino qo'shish - message identifier + caption bilan

        Args:
            session: Database session
            code: Kino kodi (unique)
            message_id: Telegram message identifier or file_id (string)
            caption: Video tavsifi (optional)
        """
        movie = Movie(code=code, message_id=message_id, caption=caption)
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

    @staticmethod
    async def update(session: AsyncSession, code: int, message_id: str = None, caption: str = None) -> bool:
        """Kino update qilish"""
        movie = await MovieService.get_by_code(session, code)
        if movie:
            if message_id:
                movie.message_id = message_id
            if caption is not None:
                movie.caption = caption
            await session.flush()
            return True
        return False
