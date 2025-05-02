import logging
import os
import time
from typing import List, Optional

from datetime import datetime
from todo.models.task_model import Task
from todo.utils.logger import configure_logger
from todo.utils.api_utils import get_random

logger = logging.getLogger(__name__)
configure_logger(logger)


class TaskManager:
    """
    Service layer around Task:
      - in-memory cache with TTL
      - random selection, urgency scoring, and cache management
    """

    def __init__(self):
        """
        Initialize the TaskManager with an empty cache and TTL.

        Args:
            None

        Attributes:
            _cache (dict[int, Task]): Cached Task instances.
            _last_fetched (dict[int, float]): Timestamp of last fetch per ID.
            ttl_seconds (int): Cache time-to-live in seconds.
        """
        self._cache: dict[int, Task] = {}
        self._last_fetched: dict[int, float] = {}

        self.ttl_seconds = int(os.getenv('TASK_CACHE_TTL', 300))


    def get_task(self, task_id: int) -> Task:
        """
        Retrieve a Task by ID, using cache if fresh.

        Args:
            task_id (int): ID of the Task to fetch.

        Returns:
            Task: The fetched Task instance.

        Raises:
            ValueError: If the Task does not exist.
        """
        now = time.time()
        if task_id in self._cache and now - self._last_fetched[task_id] < self.ttl_seconds:
            logger.debug(f"Cache HIT for Task[{task_id}]")
            return self._cache[task_id]

        logger.debug(f"Cache MISS for Task[{task_id}]")
        task = Task.get_task_by_id(task_id)
        self._cache[task_id] = task
        self._last_fetched[task_id] = now
        logger.debug(f"Cached Task[{task_id}] for {self.ttl_seconds}s")
        return task

    def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None
    ) -> Task:
        """
        Create a new Task, persist it, and cache the result.

        Args:
            title (str): Title of the task.
            description (Optional[str]): Description of the task.
            due_date (Optional[datetime]): Due date of the task; must be future datetime if provided.

        Returns:
            Task: The newly created Task instance.

        Raises:
            ValueError: If validation fails.
            SQLAlchemyError: If a DB error occurs.
        """
        task = Task.create_task(title, description, due_date)
        self._cache[task.id] = task
        self._last_fetched[task.id] = time.time()
        logger.info(f"Added & cached Task[{task.id}]")
        return task

    def delete_task(self, task_id: int) -> None:
        """
        Delete a Task by ID and invalidate its cache.

        Args:
            task_id (int): ID of the task to delete.

        Raises:
            ValueError: If the Task does not exist.
            SQLAlchemyError: If a DB error occurs.
        """
        Task.delete(task_id)
        self._cache.pop(task_id, None)
        self._last_fetched.pop(task_id, None)
        logger.info(f"Deleted and cache invalidated for Task[{task_id}]")

    def get_random_task(self) -> dict:
        """
        Return a random Task representation from the catalog.

        Returns:
            dict: A dictionary representing a random task.

        Raises:
            ValueError: If there are no tasks available.
        """
        all_tasks = Task.get_all_tasks()
        if not all_tasks:
            logger.warning("No tasks available for random pick")
            raise ValueError("Task list is empty.")
        idx = get_random(len(all_tasks))
        logger.info(f"Random index: {idx} of {len(all_tasks)}")
        return all_tasks[idx - 1]

    def compute_task_urgency(self, task: Task) -> float:
        """
        Compute an urgency score for a Task based on due date.

        Args:
            task (Task): The task to evaluate.

        Returns:
            float: Urgency score (larger means more urgent).

        Raises:
            None
        """
        now = time.time()
        if not task.due_date:
            return 0.0
        delta = (task.due_date.timestamp() - now) / 86400.0
        urgency = max(0.0, 1 / (1 + delta))
        logger.debug(f"Urgency for Task[{task.id}] ≈ {urgency:.3f}")
        return urgency

    def clear_cache(self):
        """
        Clear the in-memory cache of Task instances.

        Args:
            None

        Returns:
            None
        """
        self._cache.clear()
        self._last_fetched.clear()
        logger.info("Cleared TaskManager cache.")
