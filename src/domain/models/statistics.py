from pydantic import BaseModel
from typing import List, Optional


class DailyStats(BaseModel):
    date: str
    total_time_spent: int  # in minutes
    completed_tasks: int
    active_tasks: int


class WeeklyStats(BaseModel):
    week_start: str
    week_end: str
    total_time_spent: int  # in minutes
    completed_tasks: int
    daily_breakdown: List[DailyStats]


class TagStats(BaseModel):
    tag_id: int
    tag_name: str
    total_time_spent: int  # in minutes
    task_count: int


class ProductivityTrend(BaseModel):
    day: str
    planned_time: int  # in minutes
    actual_time: int  # in minutes
    completed_tasks: int