from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from ..domain.models.timer import TimerStart, TimerStop, TimerResponse
from ..infrastructure.database.repositories.timer_repository import TimerRepository
from ..infrastructure.database.repositories.task_repository import TaskRepository


class TimerService:
    def __init__(self, db_session: AsyncSession):
        self.timer_repository = TimerRepository(db_session)
        self.task_repository = TaskRepository(db_session)

    async def start_timer(self, timer_data: TimerStart, user_id: int) -> Optional[TimerResponse]:
        """Start a timer for a task"""
        # Verify that the task belongs to the user
        task = await self.task_repository.get(timer_data.task_id)
        if not task or task.user_id != user_id:
            return None

        # Check if there's already an active timer for this user
        active_timer = await self.timer_repository.get_active_timer_for_user(user_id)
        if active_timer:
            # Stop the existing timer first
            await self.timer_repository.stop_timer_session(active_timer.id)

        # Create a new timer session
        timer_session = await self.timer_repository.create_timer_session(timer_data.task_id)
        return TimerResponse.from_orm(timer_session)

    async def stop_timer(self, timer_data: TimerStop, user_id: int) -> Optional[TimerResponse]:
        """Stop a timer session"""
        timer_session = await self.timer_repository.get(timer_data.timer_id)
        if not timer_session:
            return None

        # Verify that the timer belongs to a task owned by the user
        task = await self.task_repository.get(timer_session.task_id)
        if not task or task.user_id != user_id:
            return None

        # Stop the timer
        stopped_timer = await self.timer_repository.stop_timer_session(timer_data.timer_id)
        return TimerResponse.from_orm(stopped_timer)

    async def get_active_timer(self, user_id: int) -> Optional[TimerResponse]:
        """Get the currently active timer for a user"""
        timer_session = await self.timer_repository.get_active_timer_for_user(user_id)
        if timer_session:
            return TimerResponse.from_orm(timer_session)
        return None

    async def pause_timer(self, timer_id: int, user_id: int) -> Optional[TimerResponse]:
        """Pause a timer (not implemented in this version)"""
        # For now, we'll just return the timer as is
        # In a future implementation, we could add a paused field to TimerSession
        timer_session = await self.timer_repository.get(timer_id)
        if not timer_session:
            return None

        task = await self.task_repository.get(timer_session.task_id)
        if not task or task.user_id != user_id:
            return None

        return TimerResponse.from_orm(timer_session)