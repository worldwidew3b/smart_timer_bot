from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from ..api.dependencies import get_db_session_dependency
from ..domain.services.stats_service import StatsService
from ..domain.models.statistics import DailyStats, WeeklyStats, TagStats, ProductivityTrend


router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/daily", response_model=DailyStats)
async def get_daily_stats(
    date: str = None,  # Format: YYYY-MM-DD
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = 1  # In a real app, this would come from authentication
):
    """Get statistics for a specific date"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    stats_service = StatsService(db_session)
    return await stats_service.get_daily_stats(user_id, date)


@router.get("/weekly", response_model=WeeklyStats)
async def get_weekly_stats(
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = 1  # In a real app, this would come from authentication
):
    """Get statistics for the current week"""
    stats_service = StatsService(db_session)
    return await stats_service.get_weekly_stats(user_id)


@router.get("/tags", response_model=List[TagStats])
async def get_tag_stats(
    tag_ids: str = None,  # Comma-separated list of tag IDs
    period: int = 30,  # Number of days to look back
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = 1  # In a real app, this would come from authentication
):
    """Get statistics for specific tags over a period"""
    # Parse tag_ids if provided
    tag_id_list = []
    if tag_ids:
        try:
            tag_id_list = [int(tid.strip()) for tid in tag_ids.split(',')]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tag IDs format")
    
    stats_service = StatsService(db_session)
    return await stats_service.get_tag_stats(user_id, tag_id_list, period)


@router.get("/trends", response_model=List[ProductivityTrend])
async def get_productivity_trends(
    days: int = 7,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = 1  # In a real app, this would come from authentication
):
    """Get productivity trends over the specified number of days"""
    stats_service = StatsService(db_session)
    return await stats_service.get_productivity_trends(user_id, days)