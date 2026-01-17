from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, extract, select
from datetime import datetime, timedelta
from ..domain.models.statistics import DailyStats, WeeklyStats, TagStats, ProductivityTrend
from ..infrastructure.database.models import Task, TimerSession, Tag, task_tags
from ..infrastructure.database.repositories.base import BaseRepository


class StatsService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_daily_stats(self, user_id: int, date: str) -> DailyStats:
        """Get statistics for a specific date"""
        # Parse the date string
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        
        # Query for completed tasks on that date
        completed_tasks_query = await self.db_session.execute(
            func.count(Task.id).filter(
                and_(
                    Task.user_id == user_id,
                    func.date(Task.completed_at) == target_date,
                    Task.completed == True
                )
            )
        )
        completed_tasks = completed_tasks_query.scalar() or 0
        
        # Query for active tasks on that date
        active_tasks_query = await self.db_session.execute(
            func.count(Task.id).filter(
                and_(
                    Task.user_id == user_id,
                    func.date(Task.created_at) == target_date,
                    Task.completed == False
                )
            )
        )
        active_tasks = active_tasks_query.scalar() or 0
        
        # Query for total time spent on that date
        time_spent_query = await self.db_session.execute(
            func.sum(TimerSession.duration).filter(
                and_(
                    TimerSession.active == False,  # Only completed sessions
                    func.date(TimerSession.end_time) == target_date,
                    Task.user_id == user_id
                )
            ).select_from(
                TimerSession.__table__.join(Task, TimerSession.task_id == Task.id)
            )
        )
        total_time_spent = time_spent_query.scalar() or 0
        
        return DailyStats(
            date=date,
            total_time_spent=total_time_spent,
            completed_tasks=completed_tasks,
            active_tasks=active_tasks
        )

    async def get_weekly_stats(self, user_id: int) -> WeeklyStats:
        """Get statistics for the current week"""
        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())  # Monday
        week_end = week_start + timedelta(days=6)  # Sunday
        
        # Get daily breakdown for the week
        daily_breakdown = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            daily_stat = await self.get_daily_stats(user_id, day_str)
            daily_breakdown.append(daily_stat)
        
        # Calculate weekly totals
        total_time_spent = sum(day.total_time_spent for day in daily_breakdown)
        completed_tasks = sum(day.completed_tasks for day in daily_breakdown)
        
        return WeeklyStats(
            week_start=week_start.strftime("%Y-%m-%d"),
            week_end=week_end.strftime("%Y-%m-%d"),
            total_time_spent=total_time_spent,
            completed_tasks=completed_tasks,
            daily_breakdown=daily_breakdown
        )

    async def get_tag_stats(self, user_id: int, tag_ids: List[int], period_days: int = 30) -> List[TagStats]:
        """Get statistics for specific tags over a period"""
        from sqlalchemy import and_, or_

        cutoff_date = datetime.now() - timedelta(days=period_days)

        # Build the query using SQLAlchemy's select statement for async
        stmt = (
            select(
                Tag.id.label('tag_id'),
                Tag.name.label('tag_name'),
                func.coalesce(func.sum(TimerSession.duration), 0).label('total_time_spent'),
                func.count(Task.id).label('task_count')
            )
            .select_from(
                Tag.__table__
                .outerjoin(task_tags, Tag.id == task_tags.c.tag_id)
                .outerjoin(Task, task_tags.c.task_id == Task.id)
                .outerjoin(TimerSession, Task.id == TimerSession.task_id)
            )
            .where(Tag.user_id == user_id)
            .where(
                or_(
                    TimerSession.end_time.is_(None),
                    TimerSession.end_time >= cutoff_date
                )
            )
            .group_by(Tag.id, Tag.name)
        )

        # Apply tag filter if specific tags are requested
        if tag_ids:
            stmt = stmt.where(Tag.id.in_(tag_ids))

        results = await self.db_session.execute(stmt)
        rows = results.fetchall()

        tag_stats_list = []
        for row in rows:
            tag_stats_list.append(
                TagStats(
                    tag_id=row.tag_id,
                    tag_name=row.tag_name,
                    total_time_spent=row.total_time_spent or 0,
                    task_count=row.task_count or 0
                )
            )

        return tag_stats_list

    async def get_productivity_trends(self, user_id: int, days: int = 7) -> List[ProductivityTrend]:
        """Get productivity trends over the specified number of days"""
        trends = []
        for i in range(days):
            day = datetime.now() - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            
            # Get daily stats for this day
            daily_stats = await self.get_daily_stats(user_id, day_str)
            
            # For now, we'll use actual time as both planned and actual
            # In a real implementation, we would compare estimated vs actual time
            trends.append(
                ProductivityTrend(
                    day=day_str,
                    planned_time=daily_stats.total_time_spent,  # Placeholder
                    actual_time=daily_stats.total_time_spent,
                    completed_tasks=daily_stats.completed_tasks
                )
            )
        
        return trends