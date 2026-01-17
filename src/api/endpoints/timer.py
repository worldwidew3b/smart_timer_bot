from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..api.dependencies import get_db_session_dependency, get_user_id_dependency
from ..domain.services.timer_service import TimerService
from ..domain.models.timer import TimerStart, TimerStop, TimerResponse


router = APIRouter(prefix="/timer", tags=["timer"])


@router.post("/start", response_model=TimerResponse)
async def start_timer(
    timer_data: TimerStart,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = Depends(get_user_id_dependency)
):
    """Start a timer for a task"""
    timer_service = TimerService(db_session)
    result = await timer_service.start_timer(timer_data, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found or not accessible")
    return result


@router.post("/stop", response_model=TimerResponse)
async def stop_timer(
    timer_data: TimerStop,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = Depends(get_user_id_dependency)
):
    """Stop a timer session"""
    timer_service = TimerService(db_session)
    result = await timer_service.stop_timer(timer_data, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Timer session not found or not accessible")
    return result


@router.get("/active", response_model=TimerResponse)
async def get_active_timer(
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = Depends(get_user_id_dependency)
):
    """Get the currently active timer for a user"""
    timer_service = TimerService(db_session)
    result = await timer_service.get_active_timer(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="No active timer found")
    return result