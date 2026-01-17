from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# User Models
class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Tag Models
class TagBase(BaseModel):
    name: str
    color: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(TagBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# Task Models
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    estimated_time: int  # in minutes
    priority: int = 1  # 1-5 scale
    completed: bool = False


class TaskCreate(TaskBase):
    tags: List[int] = []  # List of tag IDs


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_time: Optional[int] = None
    priority: Optional[int] = None
    completed: Optional[bool] = None
    tags: Optional[List[int]] = None


class TaskResponse(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    actual_time_spent: int = 0
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


# Timer Models
class TimerBase(BaseModel):
    task_id: int
    active: bool = True


class TimerStart(BaseModel):
    task_id: int


class TimerStop(BaseModel):
    timer_id: int


class TimerResponse(TimerBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None

    class Config:
        from_attributes = True


# Statistics Models
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