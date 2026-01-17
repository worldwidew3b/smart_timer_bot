from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Tag(BaseModel):
    id: int
    name: str
    color: Optional[str] = None


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    estimated_time: int
    priority: int
    completed: bool
    tags: List[Tag] = []

class Timer(BaseModel):
    id: int
    task_id: int
    start_time: datetime
    active: bool

class User(BaseModel):
    id: int
    telegram_id: str
    username: Optional[str] = None
    created_at: datetime

# Schemas for creation/update
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    estimated_time: int
    priority: int
    tags: List[int] = []

class TimerStart(BaseModel):
    task_id: int

class TimerStop(BaseModel):
    timer_id: int

# --- Statistics Models ---

class DailyStats(BaseModel):
    date: str
    total_time_spent: int
    completed_tasks: int
    active_tasks: int

class DailyBreakdown(BaseModel):
    date: str
    total_time_spent: int
    completed_tasks: int

class WeeklyStats(BaseModel):
    week_start: str
    week_end: str
    total_time_spent: int
    completed_tasks: int
    daily_breakdown: List[DailyBreakdown] = []

class TagStats(BaseModel):
    tag_id: int
    tag_name: str
    total_time_spent: int
    task_count: int

class ProductivityTrend(BaseModel):
    day: str
    planned_time: int
    actual_time: int
