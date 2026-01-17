from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .base import BaseRepository
from sqlalchemy.orm import selectinload
from ..models import Task, User, Tag, task_tags
from ...domain.models.task import TaskCreate, TaskUpdate


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Task, db_session)

    async def get_filtered_tasks(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        completed: Optional[bool] = None,
        priority: Optional[int] = None,
        tag_id_list: Optional[List[int]] = None,
        title_contains: Optional[str] = None,
        estimated_time_min: Optional[int] = None,
        estimated_time_max: Optional[int] = None,
    ) -> List[Task]:
        """Get tasks for a user with comprehensive filtering and eager loading of tags."""
        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .options(selectinload(Task.tags))
        )
        
        if completed is not None:
            stmt = stmt.where(Task.completed == completed)
        
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        
        if title_contains:
            stmt = stmt.where(Task.title.contains(title_contains))
        
        if estimated_time_min is not None:
            stmt = stmt.where(Task.estimated_time >= estimated_time_min)
        
        if estimated_time_max is not None:
            stmt = stmt.where(Task.estimated_time <= estimated_time_max)
        
        if tag_id_list:
            stmt = stmt.join(task_tags).where(task_tags.c.tag_id.in_(tag_id_list))

        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db_session.execute(stmt)
        # Use .unique() to handle potential duplicates from the join
        return result.scalars().unique().all()

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