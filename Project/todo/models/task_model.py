import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from todo.db import db
from todo.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class Task(db.Model):
    __tablename__ = "tasks"

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
        Args:
            title: non-empty string
            description: optional text
            due_date: optional datetime in the future
        Raises:
            ValueError: on invalid title or due_date type
        """
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string.")
        self.title = title.strip()
        self.description = description.strip() if description else None
        self.completed = False
        self.created_at = datetime.utcnow()
        self.due_date = due_date

    @classmethod
    def create_task(
        cls,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None
    ) -> "Task":
        """
        Args:
            title: non-empty
            description: optional
            due_date: optional datetime
        Returns:
            The newly-created Task
        Raises:
            ValueError: duplicate title or invalid input
            SQLAlchemyError: DB issues
        """
        task = cls(title, description, due_date)
        db.session.add(task)
        try:
            db.session.commit()
            return task
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Task with title '{title}' already exists.")
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def get_task_by_id(cls, task_id: int) -> "Task":
        """
        Args:
            task_id: primary key
        Returns:
            Task instance
        Raises:
            ValueError: if not found
        """
        task = cls.query.get(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} does not exist")
        return task

    @classmethod
    def get_all_tasks(cls) -> List[dict]:
        """
        Returns:
            A list of dicts, one per Task
        """
        rows = cls.query.order_by(cls.created_at.desc()).all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed,
                "created_at": t.created_at.isoformat(),
                "due_date": t.due_date.isoformat() if t.due_date else None,
            }
            for t in rows
        ]

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None,
        due_date: Optional[datetime] = None
    ) -> "Task":
        """
        Args:
            Any of the fields to change
        Returns:
            self
        Raises:
            ValueError: on invalid inputs
            SQLAlchemyError: DB issues
        """
        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty.")
            self.title = title.strip()
        if description is not None:
            self.description = description.strip()
        if completed is not None:
            if not isinstance(completed, bool):
                raise ValueError("Completed must be boolean.")
            self.completed = completed
        if due_date is not None:
            if not isinstance(due_date, datetime):
                raise ValueError("due_date must be a datetime.")
            self.due_date = due_date

        try:
            db.session.commit()
            return self
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def delete(cls, task_id: int) -> None:
        """
        Args:
            task_id: primary key
        Raises:
            ValueError: if not found
            SQLAlchemyError: DB issues
        """
        task = cls.query.get(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} does not exist")
        db.session.delete(task)
        db.session.commit()
