from fastapi import Depends, Header, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db_session


async def get_db_session_dependency(session: AsyncSession = Depends(get_db_session)):
    """Dependency to get database session"""
    return session

async def get_user_id_dependency(x_user_id: Annotated[int, Header()]) -> int:
    """
    Dependency to get user ID from the 'X-User-Id' header.
    In a real application, this would be replaced with a proper authentication
    system that decodes a JWT token or session cookie.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing 'X-User-Id' header"
        )
    return x_user_id