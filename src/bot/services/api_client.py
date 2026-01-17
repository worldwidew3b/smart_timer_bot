import aiohttp
from typing import Dict, List, Optional
from ..models.api import (
    Task, TaskCreate, Timer, TimerStart, TimerStop, User,
    DailyStats, WeeklyStats, TagStats, ProductivityTrend
)

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        user_id: Optional[int] = None,
        data: Optional[dict] = None, 
        params: Optional[dict] = None,
    ):
        headers = {'Content-Type': 'application/json'}
        if user_id:
            headers['X-User-Id'] = str(user_id)

        url = f"{self.base_url}{endpoint}"
        
        async with self.session.request(method, url, json=data, params=params, headers=headers) as response:
            response.raise_for_status()
            if response.status == 200:
                return await response.json()
            elif response.status == 204:
                return None

    # User method
    async def get_or_create_user(self, telegram_id: int, username: str) -> Optional[User]:
        user_data = {"telegram_id": str(telegram_id), "username": username}
        try:
            response = await self._request('POST', '/users/', data=user_data)
            return User.parse_obj(response)
        except aiohttp.ClientError as e:
            print(f"API call to get/create user failed: {e}")
            return None

    # Task methods
    async def create_task(self, user_id: int, task_data: TaskCreate) -> Task:
        response = await self._request('POST', '/tasks/', user_id=user_id, data=task_data.dict())
        return Task.parse_obj(response)

    async def get_tasks(self, user_id: int, completed: Optional[bool] = None) -> List[Task]:
        params = {}
        if completed is not None:
            params['completed'] = completed
        response = await self._request('GET', '/tasks/', user_id=user_id, params=params)
        return [Task.parse_obj(task) for task in response]

    async def get_task(self, user_id: int, task_id: int) -> Optional[Task]:
        try:
            response = await self._request('GET', f'/tasks/{task_id}', user_id=user_id)
            if response:
                return Task.parse_obj(response)
            return None
        except aiohttp.ClientError:
            return None

    async def delete_task(self, user_id: int, task_id: int) -> bool:
        try:
            await self._request('DELETE', f'/tasks/{task_id}', user_id=user_id)
            return True
        except aiohttp.ClientError:
            return False

    # Timer methods
    async def start_timer(self, user_id: int, task_id: int) -> Optional[Timer]:
        timer_data = TimerStart(task_id=task_id)
        try:
            response = await self._request('POST', '/timer/start', user_id=user_id, data=timer_data.dict())
            return Timer.parse_obj(response)
        except aiohttp.ClientError:
            return None

    async def stop_timer(self, user_id: int, timer_id: int) -> Optional[Timer]:
        timer_data = TimerStop(timer_id=timer_id)
        try:
            response = await self._request('POST', '/timer/stop', user_id=user_id, data=timer_data.dict())
            return Timer.parse_obj(response)
        except aiohttp.ClientError:
            return None

    async def get_active_timer(self, user_id: int) -> Optional[Timer]:
        try:
            response = await self._request('GET', '/timer/active', user_id=user_id)
            if response:
                return Timer.parse_obj(response)
            return None
        except aiohttp.ClientError:
            return None

    # Statistics methods
    async def get_daily_stats(self, user_id: int, date: Optional[str] = None) -> Optional[DailyStats]:
        params = {'date': date} if date else {}
        try:
            response = await self._request('GET', '/stats/daily', user_id=user_id, params=params)
            return DailyStats.parse_obj(response)
        except aiohttp.ClientError:
            return None

    async def get_weekly_stats(self, user_id: int) -> Optional[WeeklyStats]:
        try:
            response = await self._request('GET', '/stats/weekly', user_id=user_id)
            return WeeklyStats.parse_obj(response)
        except aiohttp.ClientError:
            return None

    async def get_tag_stats(self, user_id: int, tag_ids: List[int] = None, period: int = 30) -> List[TagStats]:
        params = {'period': period}
        if tag_ids:
            params['tag_ids'] = ','.join(map(str, tag_ids))
        try:
            response = await self._request('GET', '/stats/tags', user_id=user_id, params=params)
            return [TagStats.parse_obj(stat) for stat in response]
        except aiohttp.ClientError:
            return []

    async def get_productivity_trends(self, user_id: int, days: int = 7) -> List[ProductivityTrend]:
        params = {'days': days}
        try:
            response = await self._request('GET', '/stats/trends', user_id=user_id, params=params)
            return [ProductivityTrend.parse_obj(trend) for trend in response]
        except aiohttp.ClientError:
            return []