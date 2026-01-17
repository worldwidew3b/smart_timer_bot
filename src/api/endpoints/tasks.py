from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from ..api.dependencies import get_db_session_dependency
from ..domain.services.task_service import TaskService
from ..domain.models.task import TaskCreate, TaskUpdate, TaskResponse, TagResponse
from ..infrastructure.database.models import Task, Tag, task_tags


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = 1  # In a real app, this would come from authentication
):
    """Create a new task"""
    task_service = TaskService(db_session)
    return await task_service.create_task(task, user_id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = 1  # In a real app, this would come from authentication
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
    user_id: int = 1  # In a real app, this would come from authentication
):
    """Get all tasks for a user with optional filtering"""
    # Parse tag_ids if provided
    tag_id_list = []
    if tag_ids:
        try:
            tag_id_list = [int(tid.strip()) for tid in tag_ids.split(',')]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tag IDs format")
    
    # Build the query with filters
    query = select(Task).where(Task.user_id == user_id)
    
    if completed is not None:
        query = query.where(Task.completed == completed)
    
    if priority is not None:
        query = query.where(Task.priority == priority)
    
    if title_contains:
        query = query.where(Task.title.contains(title_contains))
    
    if estimated_time_min is not None:
        query = query.where(Task.estimated_time >= estimated_time_min)
    
    if estimated_time_max is not None:
        query = query.where(Task.estimated_time <= estimated_time_max)
    
    if tag_id_list:
        # Join with task_tags and filter by tag IDs
        query = query.join(task_tags).where(task_tags.c.tag_id.in_(tag_id_list))
    
    query = query.offset(skip).limit(limit)
    
    result = await db_session.execute(query)
    tasks = result.scalars().all()
    
    # Convert to response objects
    task_responses = []
    for task in tasks:
        # Fetch tags for each task
        tag_query = select(Tag).join(task_tags).where(
            task_tags.c.task_id == task.id,
            Tag.user_id == user_id
        )
        tag_result = await db_session.execute(tag_query)
        tags = [TagResponse.from_orm(tag) for tag in tag_result.scalars().all()]
        
        task_dict = task.__dict__.copy()
        task_dict['tags'] = tags
        task_responses.append(TaskResponse(**task_dict))
    
    return task_responses


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = 1  # In a real app, this would come from authentication
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
    user_id: int = 1  # In a real app, this would come from authentication
):
    """Delete a task"""
    task_service = TaskService(db_session)
    success = await task_service.delete_task(task_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}