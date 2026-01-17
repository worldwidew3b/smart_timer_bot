from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .base import BaseRepository
from ..models import Task, User, Tag
from ...domain.models.task import TaskCreate, TaskUpdate


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Task, db_session)

    async def get_tasks_by_user(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        completed: Optional[bool] = None
    ) -> List[Task]:
        """Get tasks for a specific user with optional filtering"""
        stmt = select(Task).where(Task.user_id == user_id)
        
        if completed is not None:
            stmt = stmt.where(Task.completed == completed)
            
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_task_with_details(self, task_id: int, user_id: int) -> Optional[Task]:
        """Get a task with its tags and user info"""
        stmt = select(Task).join(User).outerjoin(Task.tags).where(
            Task.id == task_id, 
            Task.user_id == user_id
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_task_with_tags(self, task_data: TaskCreate, user_id: int) -> Task:
        """Create a task and associate it with tags"""
        # Prepare task data excluding tags
        task_dict = task_data.dict(exclude={'tags'})
        task_dict['user_id'] = user_id
        
        # Create the task
        task = Task(**task_dict)
        self.db_session.add(task)
        await self.db_session.flush()  # Get the task ID without committing
        
        # Associate tags if provided
        if task_data.tags:
            # Get existing tags by IDs
            tag_stmt = select(Tag).where(Tag.id.in_(task_data.tags), Tag.user_id == user_id)
            tags_result = await self.db_session.execute(tag_stmt)
            tags = tags_result.scalars().all()
            task.tags.extend(tags)
        
        await self.db_session.commit()
        await self.db_session.refresh(task)
        return task

    async def update_task_with_tags(self, task_id: int, task_data: TaskUpdate, user_id: int) -> Optional[Task]:
        """Update a task and its associated tags"""
        task = await self.get(task_id)
        if not task or task.user_id != user_id:
            return None
            
        # Update task fields
        update_data = task_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field != 'tags':  # Handle tags separately
                setattr(task, field, value)
        
        # Update tags if provided
        if 'tags' in update_data and task_data.tags is not None:
            # Clear existing tags
            task.tags.clear()
            
            # Add new tags if any
            if task_data.tags:
                tag_stmt = select(Tag).where(Tag.id.in_(task_data.tags), Tag.user_id == user_id)
                tags_result = await self.db_session.execute(tag_stmt)
                tags = tags_result.scalars().all()
                task.tags.extend(tags)
        
        await self.db_session.commit()
        await self.db_session.refresh(task)
        return task