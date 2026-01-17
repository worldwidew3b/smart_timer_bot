from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..infrastructure.database.repositories.user_repository import UserRepository
from ..infrastructure.database.models import User


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.user_repository = UserRepository(db_session)

    async def get_or_create_user(self, telegram_id: str, username: Optional[str] = None) -> User:
        """
        Get a user by telegram_id, or create a new one if they don't exist.
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.user_repository.create_user(telegram_id=str(telegram_id), username=username)
        return user
