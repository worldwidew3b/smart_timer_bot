from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..domain.models.task import TaskCreate, TaskUpdate, TaskResponse
from ..infrastructure.database.repositories.task_repository import TaskRepository
from ..infrastructure.database.repositories.tag_repository import TagRepository


class TaskService:
    def __init__(self, db_session: AsyncSession):
        self.task_repository = TaskRepository(db_session)
        self.tag_repository = TagRepository(db_session)

    async def create_task(self, task_data: TaskCreate, user_id: int) -> TaskResponse:
        """Create a new task with associated tags"""
        task = await self.task_repository.create_task_with_tags(task_data, user_id)
        return TaskResponse.from_orm(task)

    async def get_task(self, task_id: int, user_id: int) -> Optional[TaskResponse]:
        """Get a specific task by ID for a user"""
        task = await self.task_repository.get_task_with_details(task_id, user_id)
        if task:
            return TaskResponse.from_orm(task)
        return None

    async def get_tasks(
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
    ) -> List[TaskResponse]:
        """Get all tasks for a user with optional filtering"""
        tasks = await self.task_repository.get_filtered_tasks(
            user_id=user_id,
            skip=skip,
            limit=limit,
            completed=completed,
            priority=priority,
            tag_id_list=tag_id_list,
            title_contains=title_contains,
            estimated_time_min=estimated_time_min,
            estimated_time_max=estimated_time_max,
        )
        return [TaskResponse.from_orm(task) for task in tasks]

    async def update_task(
        self, 
        task_id: int, 
        task_data: TaskUpdate, 
        user_id: int
    ) -> Optional[TaskResponse]:
        """Update a task for a user"""
        task = await self.task_repository.update_task_with_tags(task_id, task_data, user_id)
        if task:
            return TaskResponse.from_orm(task)
        return None

    async def delete_task(self, task_id: int, user_id: int) -> bool:
        """Delete a task for a user"""
        # First get the task to verify ownership
        task = await self.task_repository.get(task_id)
        if task and task.user_id == user_id:
            return await self.task_repository.delete(task_id)
        return False