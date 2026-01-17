from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TimerStart(BaseModel):
    task_id: int


class TimerStop(BaseModel):
    timer_id: int


class TimerResponse(BaseModel):
    id: int
    task_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    active: bool

    class Config:
        from_attributes = True