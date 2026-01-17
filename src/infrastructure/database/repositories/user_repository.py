from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .base import BaseRepository
from ..models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def get_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Get a user by their Telegram ID"""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, telegram_id: str, username: Optional[str] = None) -> User:
        """Create a new user"""
        new_user = User(telegram_id=telegram_id, username=username)
        self.db_session.add(new_user)
        await self.db_session.commit()
        await self.db_session.refresh(new_user)
        return new_user
