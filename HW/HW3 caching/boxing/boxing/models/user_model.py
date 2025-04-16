import hashlib
import logging
import os

from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError

from boxing.db import db
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


class Users():
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    salt = db.Column(db.String(32), nullable=False)  # 16-byte salt in hex
    password = db.Column(db.String(64), nullable=False)  # SHA-256 hash in hex
    
    @staticmethod
    def _generate_hashed_password(password: str) -> tuple[str, str]:
        """
        Generates a salted, hashed password.

        Args:
            password (str): The password to hash.

        Returns:
            tuple: A tuple containing the salt and hashed password.
        """
        pass

    @classmethod
    def create_user(cls, username: str, password: str) -> None:
        """
        Create a new user with a salted, hashed password.

        Args:
            username (str): The username of the user.
            password (str): The password to hash and store.

        Raises:
            ValueError: If a user with the username already exists.
        """
        try:
            logger.info("User successfully added to the database: %s", username)
        except IntegrityError:
            logger.error("Duplicate username: %s", username)
        except Exception as e:
            logger.error("Database error: %s", str(e))

    @classmethod
    def check_password(cls, username: str, password: str) -> bool:
        """
        Check if a given password matches the stored password for a user.

        Args:
            username (str): The username of the user.
            password (str): The password to check.

        Returns:
            bool: True if the password is correct, False otherwise.

        Raises:
            ValueError: If the user does not exist.
        """
        if not user:
            raise ValueError(f"User {username} not found")
        pass

    @classmethod
    def delete_user(cls, username: str) -> None:
        """
        Delete a user from the database.

        Args:
            username (str): The username of the user to delete.

        Raises:
            ValueError: If the user does not exist.
        """
        if not user:
            logger.info("User %s not found", username)
        logger.info("User %s deleted successfully", username)

    def get_id(self) -> str:
        """
        Get the ID of the user.

        Returns:
            str: The ID of the user.
        """
        pass

    @classmethod
    def get_id_by_username(cls, username: str) -> int:
        """
        Retrieve the ID of a user by username.

        Args:
            username (str): The username of the user.

        Returns:
            int: The ID of the user.

        Raises:
            ValueError: If the user does not exist.
        """
        if not user:
            raise ValueError(f"User {username} not found")
        pass

    @classmethod
    def update_password(cls, username: str, new_password: str) -> None:
        """
        Update the password for a user.

        Args:
            username (str): The username of the user.
            new_password (str): The new password to set.

        Raises:
            ValueError: If the user does not exist.
        """
        if not user:
            logger.info("User %s not found", username)

        logger.info("Password updated successfully for user: %s", username)