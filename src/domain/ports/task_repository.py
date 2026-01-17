from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.task import TaskCreate, TaskUpdate, TaskResponse


class ITaskRepository(ABC):
    
    @abstractmethod
    async def get_filtered_tasks(
        self, 
        user_id: int, 
        skip: int, 
        limit: int,
        completed: Optional[bool],
        priority: Optional[int],
        tag_id_list: Optional[List[int]],
        title_contains: Optional[str],
        estimated_time_min: Optional[int],
        estimated_time_max: Optional[int],
    ) -> List[TaskResponse]:
        pass

    @abstractmethod
    async def get_task_with_details(self, task_id: int, user_id: int) -> Optional[TaskResponse]:
        pass

    @abstractmethod
    async def create_task_with_tags(self, task_data: TaskCreate, user_id: int) -> TaskResponse:
        pass

    @abstractmethod
    async def update_task_with_tags(self, task_id: int, task_data: TaskUpdate, user_id: int) -> Optional[TaskResponse]:
        pass

    @abstractmethod
    async def delete(self, task_id: int) -> bool:
        pass
    
    @abstractmethod
    async def get(self, task_id: int) -> Optional[TaskResponse]:
        pass

