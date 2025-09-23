from typing import Callable, Any

class IBackgroundTaskService:
    async def enqueue(self, task: Callable, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError