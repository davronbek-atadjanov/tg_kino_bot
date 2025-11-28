"""
Session manager - dependency injection uchun
"""
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import async_session
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_session() -> AsyncSession:
    """Async session manager"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

