import pytest
import time
from datetime import datetime, timedelta

from todo.models.task_model import Task
from todo.models.task_manager import TaskManager
from todo.utils.api_utils import get_random


@pytest.fixture
def task_manager():
    """Provides a fresh TaskManager instance."""
    return TaskManager()


@pytest.fixture
def sample_task(session):
    """Creates and returns a persisted sample task."""
    return Task.create_task("Sample", "desc", None)


def test_get_task_caches_value(task_manager, sample_task):
    """get_task should cache the Task instance."""
    tid = sample_task.id
    t1 = task_manager.get_task(tid)
    assert tid in task_manager._cache
    t2 = task_manager.get_task(tid)
    assert t1 is t2


def test_add_and_delete_task(task_manager):
    """add_task should persist then delete_task should remove and invalidate cache."""
    task = task_manager.add_task("Manage", None, None)
    assert task.id in task_manager._cache
    task_manager.delete_task(task.id)
    assert task.id not in task_manager._cache
    with pytest.raises(ValueError):
        Task.get_task_by_id(task.id)


def test_get_random_task(monkeypatch, session, task_manager):
    """get_random_task should return the mocked index element."""
    titles = ["A", "B", "C"]
    for t in titles:
        Task.create_task(t, None, None)
    monkeypatch.setattr(get_random, '__call__', lambda *args, **kwargs: 2)
    # or monkeypatch the function path directly:
    # monkeypatch.setattr('todo.models.task_manager.get_random', lambda n: 2)
    rand = task_manager.get_random_task()
    assert rand['title'] == "B"


def test_get_random_empty_raises(task_manager):
    """get_random_task on empty list should raise ValueError."""
    with pytest.raises(ValueError):
        task_manager.get_random_task()


def test_compute_task_urgency(task_manager):
    """compute_task_urgency should be 0 for no due_date and >0 for future due_date."""
    future = datetime.utcnow() + timedelta(days=1)
    t = Task.create_task("Urgent", None, future)
    zero = task_manager.compute_task_urgency(Task.get_task_by_id(t.id))
    assert zero == 0.0  # no due_date stored on instance so default 0
    t_with_due = Task.create_task("Urgent2", None, future)
    urg = task_manager.compute_task_urgency(Task.get_task_by_id(t_with_due.id))
    assert isinstance(urg, float)
    assert urg > 0


def test_clear_cache(task_manager, sample_task):
    """clear_cache should empty both cache dicts."""
    task_manager.get_task(sample_task.id)
    assert task_manager._cache
    task_manager.clear_cache()
    assert task_manager._cache == {}
    assert task_manager._last_fetched == {}
