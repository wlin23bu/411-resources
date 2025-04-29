from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from datetime import datetime

from config import ProductionConfig
from todo.db import db
from todo.models.task_model import Task
from todo.models.task_manager import TaskManager
from todo.models.user_model import Users
from todo.utils.logger import configure_logger

load_dotenv()


def create_app(config_class=ProductionConfig):
    """
    Application factory for the To-Do API.

    Args:
        config_class: Flask configuration class (defaults to ProductionConfig)

    Returns:
        Flask application instance.
    """
    #Application & logging setup
    app = Flask(__name__)
    configure_logger(app.logger)

    #Configuration
    app.config.from_object(config_class)

    #Database initialization & table creation
    db.init_app(app)
    with app.app_context():
        db.create_all()

    #Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        #here we load by username
        return Users.query.filter_by(username=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401)

    task_manager = TaskManager()

    ####################################################
    #
    # Healthchecks
    #
    ####################################################


    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.

        """
        app.logger.info("Health check endpoint hit")
        return make_response(jsonify({
            'status': 'success',
            'message': 'Service is running'
        }), 200)

    ##################################################
    # User Management
    ##################################################
    @app.route('/api/create-user', methods=['PUT'])
    def create_user() -> Response:
        """
        Register a new user account.

        Expected JSON:
          - username (str)
          - password (str)

        Returns:
            JSON 201 on success.

        Raises:
            400 if username/password missing or validation fails.
            500 on DB error.
        """
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return make_response(jsonify({
                "status": "error",
                "message": "Username and password are required"
            }), 400)

        try:
            Users.create_user(username, password)
            return make_response(jsonify({
                "status": "success",
                "message": f"User '{username}' created successfully"
            }), 201)
        except ValueError as ve:
            return make_response(jsonify({
                "status": "error",
                "message": str(ve)
            }), 400)
        except Exception as e:
            app.logger.error(f"User creation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal error creating user",
                "details": str(e)
            }), 500)

    @app.route('/api/login', methods=['POST'])
    def login() -> Response:
        """
        Authenticate a user.

        Expected JSON:
          - username (str)
          - password (str)

        Returns:
            JSON 200 on success.

        Raises:
            400 if fields missing.
            401 if authentication fails.
            500 on DB error.
        """
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return make_response(jsonify({
                "status": "error",
                "message": "Username and password are required"
            }), 400)

        try:
            if Users.check_password(username, password):
                user = Users.get_by_username(username)
                login_user(user)
                return make_response(jsonify({
                    "status": "success",
                    "message": f"User '{username}' logged in"
                }), 200)
            else:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401)
        except ValueError as ve:
            return make_response(jsonify({
                "status": "error",
                "message": str(ve)
            }), 401)
        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal error during login",
                "details": str(e)
            }), 500)

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout() -> Response:
        """
        Log out the current user.

        Returns:
            JSON 200 on success.
        """
        logout_user()
        return make_response(jsonify({
            "status": "success",
            "message": "User logged out"
        }), 200)

    @app.route('/api/change-password', methods=['POST'])
    @login_required
    def change_password() -> Response:
        """
        Change the password for the logged-in user.

        Expected JSON:
          - new_password (str)

        Returns:
            JSON 200 on success.

        Raises:
            400 if missing or invalid.
            500 on DB error.
        """
        data = request.get_json() or {}
        new_password = data.get("new_password")
        if not new_password:
            return make_response(jsonify({
                "status": "error",
                "message": "New password is required"
            }), 400)

        try:
            Users.update_password(current_user.username, new_password)
            return make_response(jsonify({
                "status": "success",
                "message": "Password updated"
            }), 200)
        except ValueError as ve:
            return make_response(jsonify({
                "status": "error",
                "message": str(ve)
            }), 400)
        except Exception as e:
            app.logger.error(f"Password change failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal error changing password",
                "details": str(e)
            }), 500)

    @app.route('/api/reset-users', methods=['DELETE'])
    def reset_users() -> Response:
        """
        Recreate the users table (drops all users).

        Returns:
            JSON 200 on success.

        Raises:
            500 on DB error.
        """
        try:
            app.logger.info("Recreating Users table")
            with app.app_context():
                Users.__table__.drop(db.engine)
                Users.__table__.create(db.engine)
            return make_response(jsonify({
                "status": "success",
                "message": "Users table reset"
            }), 200)
        except Exception as e:
            app.logger.error(f"Reset users failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal error resetting users",
                "details": str(e)
            }), 500)

    ##################################################
    # To-Do Task Routes
    ##################################################
    @app.route('/api/tasks', methods=['POST'])
    def create_task() -> Response:
        """
        Create a new to-do task.
        """
        data = request.get_json() or {}
        title = data.get("title")
        desc  = data.get("description")
        due   = data.get("due_date")
        due_dt = None
        if due:
            try:
                due_dt = datetime.fromisoformat(due)
            except ValueError:
                return make_response(jsonify({
                    "status": "error",
                    "message": "due_date must be ISO-8601"
                }), 400)

        try:
            task = task_manager.add_task(title, desc, due_dt)
            return make_response(jsonify({
                "status": "success",
                "data": {
                    "id":          task.id,
                    "title":       task.title,
                    "description": task.description,
                    "completed":   task.completed,
                    "created_at":  task.created_at.isoformat(),
                    "due_date":    task.due_date.isoformat() if task.due_date else None,
                }
            }), 201)
        except ValueError as ve:
            return make_response(jsonify({
                "status": "error",
                "message": str(ve)
            }), 400)
        except Exception as e:
            app.logger.error(f"Error creating task: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal server error",
                "details": str(e)
            }), 500)

    @app.route('/api/tasks', methods=['GET'])
    def list_tasks() -> Response:
        """List all to-do tasks."""
        try:
            tasks = Task.get_all_tasks()
            return make_response(jsonify({
                "status": "success",
                "data": tasks
            }), 200)
        except Exception as e:
            app.logger.error(f"Error listing tasks: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal server error",
                "details": str(e)
            }), 500)

    @app.route('/api/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id: int) -> Response:
        """Get one task by ID."""
        try:
            t = Task.get_task_by_id(task_id)
            return make_response(jsonify({
                "status": "success",
                "data": {
                    "id":          t.id,
                    "title":       t.title,
                    "description": t.description,
                    "completed":   t.completed,
                    "created_at":  t.created_at.isoformat(),
                    "due_date":    t.due_date.isoformat() if t.due_date else None,
                }
            }), 200)
        except ValueError as ve:
            return make_response(jsonify({
                "status": "error",
                "message": str(ve)
            }), 404)
        except Exception as e:
            app.logger.error(f"Error fetching task {task_id}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal server error",
                "details": str(e)
            }), 500)

    @app.route('/api/tasks/<int:task_id>', methods=['PUT', 'PATCH'])
    def update_task(task_id: int) -> Response:
        """Update an existing task by ID."""
        data      = request.get_json() or {}
        title     = data.get("title")
        desc      = data.get("description")
        completed = data.get("completed")
        due        = data.get("due_date")
        due_dt    = None
        if "due_date" in data and due:
            try:
                due_dt = datetime.fromisoformat(due)
            except ValueError:
                return make_response(jsonify({
                    "status": "error",
                    "message": "due_date must be ISO-8601"
                }), 400)

        try:
            task = Task.get_task_by_id(task_id)
            updated = task.update(
                title=title,
                description=desc,
                completed=completed,
                due_date=due_dt
            )
            return make_response(jsonify({
                "status": "success",
                "data": {
                    "id":          updated.id,
                    "title":       updated.title,
                    "description": updated.description,
                    "completed":   updated.completed,
                    "created_at":  updated.created_at.isoformat(),
                    "due_date":    updated.due_date.isoformat() if updated.due_date else None,
                }
            }), 200)
        except ValueError as ve:
            return make_response(jsonify({
                "status": "error",
                "message": str(ve)
            }), 400)
        except Exception as e:
            app.logger.error(f"Error updating task {task_id}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal server error",
                "details": str(e)
            }), 500)

    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id: int) -> Response:
        """Delete a task by ID."""
        try:
            Task.delete(task_id)
            return make_response('', 204)
        except ValueError as ve:
            return make_response(jsonify({
                "status": "error",
                "message": str(ve)
            }), 404)
        except Exception as e:
            app.logger.error(f"Error deleting task {task_id}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal server error",
                "details": str(e)
            }), 500)

    return app


if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask app…")
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")
