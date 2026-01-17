from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from ..api.dependencies import get_db_session_dependency, get_user_id_dependency
from ..domain.services.task_service import TaskService
from ..domain.models.task import TaskCreate, TaskUpdate, TaskResponse, TagResponse
from ..infrastructure.database.models import Task, Tag, task_tags


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = Depends(get_user_id_dependency)
):
    """Create a new task"""
    task_service = TaskService(db_session)
    return await task_service.create_task(task, user_id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = Depends(get_user_id_dependency)
):
    """Get a specific task by ID"""
    task_service = TaskService(db_session)
    result = await task_service.get_task(task_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    tag_ids: str = Query(None, description="Comma-separated list of tag IDs to filter by"),
    title_contains: str = Query(None, description="Filter tasks by title containing this text"),
    estimated_time_min: Optional[int] = None,
    estimated_time_max: Optional[int] = None,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = Depends(get_user_id_dependency)
):
    """Get all tasks for a user with optional filtering"""
    tag_id_list = []
    if tag_ids:
        try:
            tag_id_list = [int(tid.strip()) for tid in tag_ids.split(',')]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tag IDs format")

    task_service = TaskService(db_session)
    tasks = await task_service.get_tasks(
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
    return tasks


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = Depends(get_user_id_dependency)
):
    """Update a task"""
    task_service = TaskService(db_session)
    result = await task_service.update_task(task_id, task_update, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = Depends(get_user_id_dependency)
):
    """Delete a task"""
    task_service = TaskService(db_session)
    success = await task_service.delete_task(task_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}