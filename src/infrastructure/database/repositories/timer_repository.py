from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from .base import BaseRepository
from ..models import TimerSession, Task
from ...domain.models.timer import TimerStart, TimerStop


class TimerRepository(BaseRepository[TimerSession]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(TimerSession, db_session)

    async def get_active_timer_for_user(self, user_id: int) -> Optional[TimerSession]:
        """Get the currently active timer session for a user"""
        stmt = (
            select(TimerSession)
            .join(Task)
            .where(
                TimerSession.active == True,
                Task.user_id == user_id
            )
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_timer_for_task(self, task_id: int) -> Optional[TimerSession]:
        """Get the currently active timer session for a specific task"""
        stmt = select(TimerSession).where(
            TimerSession.task_id == task_id,
            TimerSession.active == True
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_timer_session(self, task_id: int) -> TimerSession:
        """Create a new timer session for a task"""
        timer_session = TimerSession(
            task_id=task_id,
            start_time=datetime.utcnow(),
            active=True
        )
        self.db_session.add(timer_session)
        await self.db_session.commit()
        await self.db_session.refresh(timer_session)
        return timer_session

    async def stop_timer_session(self, timer_id: int) -> Optional[TimerSession]:
        """Stop a timer session and calculate duration"""
        timer_session = await self.get(timer_id)
        if timer_session and timer_session.active:
            timer_session.end_time = datetime.utcnow()
            timer_session.active = False
            # Calculate duration in minutes
            duration = (timer_session.end_time - timer_session.start_time).total_seconds() / 60
            timer_session.duration = round(duration)
            
            await self.db_session.commit()
            await self.db_session.refresh(timer_session)
        return timer_session