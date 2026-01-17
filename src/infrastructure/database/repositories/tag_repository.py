from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .base import BaseRepository
from ..models import Tag, User


class TagRepository(BaseRepository[Tag]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Tag, db_session)

    async def get_tags_by_user(self, user_id: int) -> List[Tag]:
        """Get all tags for a specific user"""
        stmt = select(Tag).where(Tag.user_id == user_id)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_tag_by_name_and_user(self, name: str, user_id: int) -> Tag:
        """Get a tag by name for a specific user"""
        stmt = select(Tag).where(Tag.name == name, Tag.user_id == user_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_tag_for_user(self, name: str, user_id: int, color: str = None) -> Tag:
        """Create a new tag for a specific user"""
        tag = Tag(name=name, user_id=user_id, color=color)
        self.db_session.add(tag)
        await self.db_session.commit()
        await self.db_session.refresh(tag)
        return tag