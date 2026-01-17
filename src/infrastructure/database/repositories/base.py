from typing import TypeVar, Generic, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from ..database.models import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get(self, id: int) -> Optional[ModelType]:
        """Get a record by ID"""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination"""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_data: dict) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_data)
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_data: dict) -> Optional[ModelType]:
        """Update a record by ID"""
        db_obj = await self.get(id)
        if db_obj:
            for key, value in obj_data.items():
                setattr(db_obj, key, value)
            await self.db_session.commit()
            await self.db_session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        """Delete a record by ID"""
        db_obj = await self.get(id)
        if db_obj:
            await self.db_session.delete(db_obj)
            await self.db_session.commit()
            return True
        return False