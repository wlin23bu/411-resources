import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from todo.db import db
from todo.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class Task(db.Model):
    """Represents a single to-do item."""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)

    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None
    ):
        """
        Initialize a new Task instance with validation.

        Args:
            title (str): The title of the task; must be non-empty.
            description (Optional[str]): Detailed description.
            due_date (Optional[datetime]): When the task is due; if provided, must be a datetime
                and cannot be in the past.

        Raises:
            ValueError: If the title is empty or not a string.
            ValueError: If due_date is not a datetime or is before creation time.
        """
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string.")
        self.title = title.strip()

        self.description = description.strip() if description else None
        self.completed = False
        self.created_at = datetime.utcnow()

        # Validate due_date if provided
        if due_date is not None:
            if not isinstance(due_date, datetime):
                raise ValueError("due_date must be a datetime object.")
            if due_date < self.created_at:
                raise ValueError("due_date cannot be in the past.")
        self.due_date = due_date

    @classmethod
    def create_task(
        cls,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None
    ) -> "Task":
        """
        Construct, validate, and persist a new Task.

        Args:
            title (str): The title of the task.
            description (Optional[str]): Detailed description.
            due_date (Optional[datetime]): When the task is due.

        Returns:
            Task: The newly created Task instance.

        Raises:
            ValueError: If validation fails (title or due_date) or the title already exists.
            SQLAlchemyError: For other database errors.
        """
        logger.info(f"Creating task {title!r}")
        try:
            task = cls(title, description, due_date)
        except ValueError as ve:
            logger.warning(f"Validation failed: {ve}")
            raise

        try:
            db.session.add(task)
            db.session.commit()
            logger.info(f"Task created with id={task.id}")
            return task
        except IntegrityError:
            db.session.rollback()
            logger.error(f"Task with title {title!r} already exists")
            raise ValueError(f"Task with title {title!r} already exists.")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"DB error during task creation: {e}")
            raise

    @classmethod
    def get_task_by_id(cls, task_id: int) -> "Task":
        """
        Retrieve a Task by its primary key.

        Args:
            task_id (int): The ID of the task to retrieve.

        Returns:
            Task: The Task instance.

        Raises:
            ValueError: If no task with the given ID exists.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Fetching task id={task_id}")
        try:
            task = cls.query.get(task_id)
        except SQLAlchemyError as e:
            logger.error(f"DB error fetching task {task_id}: {e}")
            raise
        if not task:
            logger.error(f"Task id={task_id} not found")
            raise ValueError(f"Task with id {task_id} does not exist")
        return task

    @classmethod
    def get_all_tasks(cls) -> List[dict]:
        """
        Return all tasks as a list of dictionaries.

        Returns:
            List[dict]: List of task representations.

        Raises:
            SQLAlchemyError: If a database error occurs.
        """
        logger.info("Fetching all tasks")
        try:
            all_tasks = cls.query.order_by(cls.created_at.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"DB error fetching tasks: {e}")
            raise
        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed,
                "created_at": t.created_at.isoformat(),
                "due_date": t.due_date.isoformat() if t.due_date else None,
            }
            for t in all_tasks
        ]

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None,
        due_date: Optional[datetime] = None
    ) -> "Task":
        """
        Update fields on this Task and persist the changes.

        Args:
            title (Optional[str]): New title, if updating.
            description (Optional[str]): New description.
            completed (Optional[bool]): Completion status.
            due_date (Optional[datetime]): Updated due date (must be datetime and not past).

        Returns:
            Task: The updated Task instance.

        Raises:
            ValueError: If any provided field is invalid.
            SQLAlchemyError: If a database error occurs.
        """

        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty.")
            self.title = title.strip()

        if description is not None:
            self.description = description.strip()

        if completed is not None:
            if not isinstance(completed, bool):
                raise ValueError("Completed must be a boolean.")
            self.completed = completed

        if due_date is not None:
            if not isinstance(due_date, datetime):
                raise ValueError("due_date must be a datetime.")
            if due_date < self.created_at: #make sure that due date is correct 
                raise ValueError("due_date cannot be in the past.")
            self.due_date = due_date
        try:
            db.session.commit()
            logger.info(f"Updated task id={self.id}")
            return self
        except SQLAlchemyError as e:
            db.session.rollback() #if any error are detected rollback
            logger.error(f"DB error updating task id={self.id}: {e}")
            raise

    @classmethod
    def delete(cls, task_id: int) -> None:
        """
        Permanently delete a Task by its ID.

        Args:
            task_id (int): The ID of the task to delete.

        Raises:
            ValueError: If no task with the given ID exists.
            SQLAlchemyError: If a database error occurs.
        """

        logger.info(f"Deleting task id={task_id}")
        try:
            task = cls.query.get(task_id)
        except SQLAlchemyError as e:
            logger.error(f"DB error for delete lookup {task_id}: {e}")
            raise
        if not task:
            logger.error(f"Task id={task_id} not found")
            raise ValueError(f"Task with id {task_id} does not exist")
        try:
            db.session.delete(task)
            db.session.commit()
            logger.info(f"Deleted task id={task_id}")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"DB error deleting task id={task_id}: {e}")
            raise
