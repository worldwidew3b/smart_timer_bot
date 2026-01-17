import aiohttp
from typing import Dict, List, Optional
from ..domain.models.task import TaskCreate, TaskUpdate, TaskResponse, TagResponse
from ..domain.models.timer import TimerStart, TimerStop, TimerResponse
from ..domain.models.statistics import DailyStats, WeeklyStats, TagStats


class ApiClient:
    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url
        self.token = token
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None):
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        headers['Content-Type'] = 'application/json'

        url = f"{self.base_url}{endpoint}"
        async with self.session.request(method, url, json=data, params=params, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Request failed with status {response.status}: {await response.text()}")

    # Task methods
    async def create_task(self, task_data: TaskCreate, user_id: int) -> TaskResponse:
        response = await self._request('POST', '/api/tasks/', task_data.dict())
        return TaskResponse(**response)

    async def get_task(self, task_id: int, user_id: int) -> Optional[TaskResponse]:
        try:
            response = await self._request('GET', f'/api/tasks/{task_id}')
            return TaskResponse(**response)
        except Exception:
            return None

    async def get_tasks(self, user_id: int, completed: Optional[bool] = None) -> List[TaskResponse]:
        params = {'completed': completed} if completed is not None else {}
        response = await self._request('GET', '/api/tasks/', params=params)
        return [TaskResponse(**task) for task in response]

    async def update_task(self, task_id: int, task_data: TaskUpdate, user_id: int) -> Optional[TaskResponse]:
        try:
            response = await self._request('PUT', f'/api/tasks/{task_id}', task_data.dict(exclude_unset=True))
            return TaskResponse(**response)
        except Exception:
            return None

    async def delete_task(self, task_id: int, user_id: int) -> bool:
        try:
            await self._request('DELETE', f'/api/tasks/{task_id}')
            return True
        except Exception:
            return False

    # Tag methods
    async def create_tag(self, name: str, color: str = None, user_id: int = 1) -> TagResponse:
        tag_data = {'name': name, 'color': color}
        response = await self._request('POST', '/api/tags/', tag_data)
        return TagResponse(**response)

    async def get_tags(self, user_id: int = 1) -> List[TagResponse]:
        response = await self._request('GET', '/api/tags/')
        return [TagResponse(**tag) for tag in response]

    # Timer methods
    async def start_timer(self, task_id: int, user_id: int) -> Optional[TimerResponse]:
        timer_data = TimerStart(task_id=task_id)
        try:
            response = await self._request('POST', '/api/timer/start', timer_data.dict())
            return TimerResponse(**response)
        except Exception:
            return None

    async def stop_timer(self, timer_id: int, user_id: int) -> Optional[TimerResponse]:
        timer_data = TimerStop(timer_id=timer_id)
        try:
            response = await self._request('POST', '/api/timer/stop', timer_data.dict())
            return TimerResponse(**response)
        except Exception:
            return None

    async def get_active_timer(self, user_id: int) -> Optional[TimerResponse]:
        try:
            response = await self._request('GET', '/api/timer/active')
            return TimerResponse(**response)
        except Exception:
            return None

    # Statistics methods
    async def get_daily_stats(self, date: str = None, user_id: int = 1) -> DailyStats:
        params = {'date': date} if date else {}
        response = await self._request('GET', '/api/stats/daily', params=params)
        return DailyStats(**response)

    async def get_weekly_stats(self, user_id: int = 1) -> WeeklyStats:
        response = await self._request('GET', '/api/stats/weekly')
        return WeeklyStats(**response)

    async def get_tag_stats(self, tag_ids: List[int] = None, period: int = 30, user_id: int = 1) -> List[TagStats]:
        params = {
            'period': period
        }
        if tag_ids:
            params['tag_ids'] = ','.join(map(str, tag_ids))
        response = await self._request('GET', '/api/stats/tags', params=params)
        return [TagStats(**tag_stat) for tag_stat in response]