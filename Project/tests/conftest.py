import pytest

import os, sys
# insert project root (one level up from tests/) onto sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from app import create_app
from config import TestConfig
from todo.db import db
from todo.models.task_model import Task 
from todo.models.user_model import Users

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def session(app):
    with app.app_context():
        db.session.query(Task).delete()
        db.session.query(Users).delete() 
        db.session.commit()
        
        yield db.session
        #  db.session.commit()
        db.session.rollback()
        db.session.query(Task).delete()
        db.session.query(Users).delete()
        db.session.commit()
        db.session.remove()

@pytest.fixture(autouse=True)
def app_context(app):
    """Ensure all tests run within an application context"""
    with app.app_context():
        yield