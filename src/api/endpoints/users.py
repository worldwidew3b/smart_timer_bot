from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.user import UserCreate, UserResponse
from ..domain.services.user_service import UserService
from ..api.dependencies import get_db_session_dependency

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def get_or_create_user(
    user_data: UserCreate,
    db_session: AsyncSession = Depends(get_db_session_dependency),
):
    """
    Get a user by telegram_id, or create them if they don't exist.
    This is the primary way to "log in" or "register" a user from the bot.
    """
    user_service = UserService(db_session)
    user = await user_service.get_or_create_user(
        telegram_id=str(user_data.telegram_id),
        username=user_data.username
    )
    if not user:
        raise HTTPException(status_code=500, detail="Could not create or retrieve user.")
    
    return user
