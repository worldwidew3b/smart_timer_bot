from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db_session


async def get_db_session_dependency(session: AsyncSession = Depends(get_db_session)):
    """Dependency to get database session"""
    return session