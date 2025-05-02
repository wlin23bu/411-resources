# To-Do API Application

This Flask application provides a RESTful API for managing to-do tasks. It includes user authentication and task management functionality.

## Application Overview

The To-Do API allows users to:
- Create and manage user accounts
- Authenticate via login/logout
- Create, read, update, and delete to-do tasks
- Get random tasks
- Check the health of the service

## API Routes

### Health Check

Route: `/api/health`
- Request Type: GET
- Purpose: Verifies the service is running properly.
- Request Format: No parameters required
- Response Format: JSON
  - `status` (String): Success status
  - `message` (String): Service status message
- Response Example:
  ```json
  {
    "status": "success",
    "message": "Service is running"
  }
  ```

### User Management

Route: `/api/create-user`
- Request Type: PUT
- Purpose: Registers a new user account.
- Request Body:
  - `username` (String): User's chosen username
  - `password` (String): User's chosen password
- Response Format: JSON
  - `status` (String): Success or error
  - `message` (String): Result message
  - `details` (String, optional): Error details if applicable
- Response Status Codes:
  - 201: Created successfully
  - 400: Invalid request or validation error
  - 500: Server error
- Example Request:
  ```json
  {
    "username": "newuser123",
    "password": "securepassword"
  }
  ```
- Example Success Response:
  ```json
  {
    "status": "success",
    "message": "User 'newuser123' created successfully"
  }
  ```
- Example Error Response:
  ```json
  {
    "status": "error",
    "message": "Username and password are required"
  }
  ```

Route: `/api/login`
- Request Type: POST
- Purpose: Authenticates a user and initiates a session.
- Request Body:
  - `username` (String): User's username
  - `password` (String): User's password
- Response Format: JSON
  - `status` (String): Success or error
  - `message` (String): Authentication result
  - `details` (String, optional): Error details if applicable
- Response Status Codes:
  - 200: Login successful
  - 400: Missing credentials
  - 401: Authentication failed
  - 500: Server error
- Example Request:
  ```json
  {
    "username": "newuser123",
    "password": "securepassword"
  }
  ```
- Example Success Response:
  ```json
  {
    "status": "success",
    "message": "User 'newuser123' logged in"
  }
  ```
- Example Error Response:
  ```json
  {
    "status": "error",
    "message": "Invalid username or password"
  }
  ```

Route: `/api/logout`
- Request Type: POST
- Purpose: Logs out the current user.
- Request Format: No parameters required (requires authentication)
- Response Format: JSON
  - `status` (String): Success or error
  - `message` (String): Logout confirmation
- Response Status Codes:
  - 200: Logout successful
  - 401: Not authenticated
- Example Success Response:
  ```json
  {
    "status": "success",
    "message": "User logged out"
  }
  ```
- Example Error Response (Unauthenticated):
  ```json
  {
    "status": "error",
    "message": "Authentication required"
  }
  ```

Route: `/api/change-password`
- Request Type: POST
- Purpose: Changes the password for the logged-in user.
- Request Body:
  - `new_password` (String): User's new password
- Response Format: JSON
  - `status` (String): Success or error
  - `message` (String): Password update result
  - `details` (String, optional): Error details if applicable
- Response Status Codes:
  - 200: Password updated successfully
  - 400: Invalid request
  - 401: Not authenticated
  - 500: Server error
- Example Request:
  ```json
  {
    "new_password": "newSecurePassword"
  }
  ```
- Example Success Response:
  ```json
  {
    "status": "success",
    "message": "Password updated"
  }
  ```
- Example Error Response:
  ```json
  {
    "status": "error",
    "message": "New password is required"
  }
  ```

Route: `/api/reset-users`
- Request Type: DELETE
- Purpose: Recreates the users table (drops all users).
- Request Format: No parameters required
- Response Format: JSON
  - `status` (String): Success or error
  - `message` (String): Reset confirmation
  - `details` (String, optional): Error details if applicable
- Response Status Codes:
  - 200: Reset successful
  - 500: Server error
- Example Success Response:
  ```json
  {
    "status": "success",
    "message": "Users table reset"
  }
  ```
- Example Error Response:
  ```json
  {
    "status": "error",
    "message": "Internal error resetting users",
    "details": "Error message details"
  }
  ```

### Task Management

Route: `/api/tasks`
- Request Type: POST
- Purpose: Creates a new to-do task.
- Request Body:
  - `title` (String): Task title
  - `description` (String, optional): Task description
  - `due_date` (String, optional): Due date in ISO-8601 format
- Response Format: JSON
  - `status` (String): Success or error
  - `data` (Object): Task details when successful
    - `id` (Integer): Task ID
    - `title` (String): Task title
    - `description` (String): Task description
    - `completed` (Boolean): Completion status
    - `created_at` (String): Creation timestamp
    - `due_date` (String or null): Due date
  - `message` (String): Error message if applicable
  - `details` (String, optional): Error details if applicable
- Response Status Codes:
  - 201: Task created successfully
  - 400: Invalid request or validation error
  - 500: Server error
- Example Request:
  ```json
  {
    "title": "Complete assignment",
    "description": "Finish the CS411 homework",
    "due_date": "2023-10-15T23:59:59"
  }
  ```
- Example Success Response:
  ```json
  {
    "status": "success",
    "data": {
      "id": 1,
      "title": "Complete assignment",
      "description": "Finish the CS411 homework",
      "completed": false,
      "created_at": "2023-10-10T14:30:00",
      "due_date": "2023-10-15T23:59:59"
    }
  }
  ```
- Example Error Response:
  ```json
  {
    "status": "error",
    "message": "due_date must be ISO-8601"
  }
  ```

Route: `/api/tasks`
- Request Type: GET
- Purpose: Lists all to-do tasks.
- Request Format: No parameters required
- Response Format: JSON
  - `status` (String): Success or error
  - `data` (Array): List of task objects when successful
  - `message` (String): Error message if applicable
  - `details` (String, optional): Error details if applicable
- Response Status Codes:
  - 200: Success
  - 500: Server error
- Example Success Response:
  ```json
  {
    "status": "success",
    "data": [
      {
        "id": 1,
        "title": "Complete assignment",
        "description": "Finish the CS411 homework",
        "completed": false,
        "created_at": "2023-10-10T14:30:00",
        "due_date": "2023-10-15T23:59:59"
      },
      {
        "id": 2,
        "title": "Buy groceries",
        "description": "Get milk, eggs, and bread",
        "completed": true,
        "created_at": "2023-10-09T10:15:00",
        "due_date": null
      }
    ]
  }
  ```
- Example Error Response:
  ```json
  {
    "status": "error",
    "message": "Internal server error",
    "details": "Error message details"
  }
  ```

Route: `/api/tasks/<int:task_id>`
- Request Type: GET
- Purpose: Retrieves a specific task by ID.
- Request Format: Path parameter
  - `task_id` (Integer): ID of the task to retrieve
- Response Format: JSON
  - `status` (String): Success or error
  - `data` (Object): Task details when successful
  - `message` (String): Error message if applicable
  - `details` (String, optional): Error details if applicable
- Response Status Codes:
  - 200: Success
  - 404: Task not found
  - 500: Server error
- Example Request: GET `/api/tasks/1`
- Example Success Response:
  ```json
  {
    "status": "success",
    "data": {
      "id": 1,
      "title": "Complete assignment",
      "description": "Finish the CS411 homework",
      "completed": false,
      "created_at": "2023-10-10T14:30:00",
      "due_date": "2023-10-15T23:59:59"
    }
  }
  ```
- Example Error Response:
  ```json
  {
    "status": "error",
    "message": "Task not found"
  }
  ```

Route: `/api/tasks/<int:task_id>`
- Request Type: PUT/PATCH
- Purpose: Updates an existing task.
- Request Format: Path parameter + JSON body
  - Path: `task_id` (Integer): ID of the task to update
  - Body (all fields optional):
    - `title` (String): Updated task title
    - `description` (String): Updated task description
    - `completed` (Boolean): Updated completion status
    - `due_date` (String): Updated due date in ISO-8601 format
- Response Format: JSON
  - `status` (String): Success or error
  - `data` (Object): Updated task details when successful
  - `message` (String): Error message if applicable
  - `details` (String, optional): Error details if applicable
- Response Status Codes:
  - 200: Success
  - 400: Invalid request
  - 404: Task not found
  - 500: Server error
- Example Request: PUT `/api/tasks/1`
  ```json
  {
    "title": "Complete assignment",
    "completed": true
  }
  ```
- Example Success Response:
  ```json
  {
    "status": "success",
    "data": {
      "id": 1,
      "title": "Complete assignment",
      "description": "Finish the CS411 homework",
      "completed": true,
      "created_at": "2023-10-10T14:30:00",
      "due_date": "2023-10-15T23:59:59"
    }
  }
  ```
- Example Error Response:
  ```json
  {
    "status": "error",
    "message": "due_date must be ISO-8601"
  }
  ```

Route: `/api/tasks/<int:task_id>`
- Request Type: DELETE
- Purpose: Deletes a task by ID.
- Request Format: Path parameter
  - `task_id` (Integer): ID of the task to delete
- Response Format: JSON
  - `status` (String): Success or error
  - `message` (String): Confirmation or error message
  - `details` (String, optional): Error details if applicable
- Response Status Codes:
  - 200: Success
  - 401: Not authenticated
  - 404: Task not found
  - 500: Server error
- Example Request: DELETE `/api/tasks/1`
- Example Success Response:
  ```json
  {
    "status": "success",
    "message": "Task 1 deleted"
  }
  ```
- Example Error Response:
  ```json
  {
    "status": "error",
    "message": "Task not found"
  }
  ```

Route: `/api/tasks/random`
- Request Type: GET
- Purpose: Retrieves a random task from the user's task list.
- Request Format: No parameters required (requires authentication)
- Response Format: JSON
  - `status` (String): Success or error
  - `task` (Object): Random task details when successful
  - `message` (String): Error message if applicable
  - `details` (String, optional): Error details if applicable
- Response Status Codes:
  - 200: Success
  - 401: Not authenticated
  - 404: No tasks found
  - 500: Server error
- Example Success Response:
  ```json
  {
    "status": "success",
    "task": {
      "id": 2,
      "title": "Buy groceries",
      "description": "Get milk, eggs, and bread",
      "completed": true,
      "created_at": "2023-10-09T10:15:00",
      "due_date": null
    }
  }
  ```
- Example Error Response:
  ```json
  {
    "status": "error",
    "message": "No tasks found"
  }
  ``` 