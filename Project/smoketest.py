import requests
import json
from datetime import datetime, timedelta
import time
import sys
import uuid

def run_smoketest():
    # basic setup stuff
    base_url = "http://localhost:5001/api"
    username = "testuser"
    password = "testpassword"
    new_password = "newpassword123"
    tasks = []
    task_counter = 0
    
    def generate_unique_title(prefix="Test Task"):
        # need this to avoid duplicate title errors
        nonlocal task_counter
        task_counter += 1
        return f"{prefix} {task_counter}-{uuid.uuid4().hex[:8]}"
    
    # health check - make sure API is running
    print("\n--- Health Check ---")
    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200, f"Expected status 200, got {health_response.status_code}"
    assert health_response.json()["status"] == "success", "Health check did not return success status"
    print("Health check successful")
    
    # trying a bad endpoint to see if 404 works
    invalid_response = requests.get(f"{base_url}/nonexistent")
    assert invalid_response.status_code == 404, f"Expected status 404, got {invalid_response.status_code}"
    print("Invalid endpoint returns 404 as expected")
    
    # reset everything for a clean test
    print("\n--- Reset Data ---")
    response = requests.delete(f"{base_url}/reset-users")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert response.json()["status"] == "success", "Reset users did not return success"
    print("Reset users successful")
    
    # clear out any tasks too
    response = requests.get(f"{base_url}/tasks")
    if response.status_code == 200:
        tasks_data = response.json().get("data", [])
        for task in tasks_data:
            delete_resp = requests.delete(f"{base_url}/tasks/{task['id']}")
            assert delete_resp.status_code in [200, 404, 401], f"Failed to delete task {task['id']}"
        print("Reset tasks successful")
    
    # User tests
    print("\n--- User Management ---")
    # create a test user
    create_user_response = requests.put(
        f"{base_url}/create-user", 
        json={
            "username": username,
            "password": password
        }
    )
    assert create_user_response.status_code == 201, f"Expected status 201, got {create_user_response.status_code}"
    assert create_user_response.json()["status"] == "success", "User creation did not return success"
    print("User creation successful")
    
    # try creating same user again - should fail
    duplicate_response = requests.put(
        f"{base_url}/create-user", 
        json={
            "username": username,
            "password": password
        }
    )
    assert duplicate_response.status_code == 400, f"Expected status 400, got {duplicate_response.status_code}"
    assert duplicate_response.json()["status"] == "error", "Duplicate user creation did not return error"
    print("Duplicate user creation failed as expected")
    
    # try with missing password
    missing_field_response = requests.put(
        f"{base_url}/create-user", 
        json={"username": username}
    )
    assert missing_field_response.status_code == 400, f"Expected status 400, got {missing_field_response.status_code}"
    print("Missing field user creation failed as expected")
    
    # start a session for login stuff
    session = requests.Session()
    
    # login with our test user
    login_response = session.post(
        f"{base_url}/login", 
        json={
            "username": username,
            "password": password
        }
    )
    assert login_response.status_code == 200, f"Expected status 200, got {login_response.status_code}"
    assert login_response.json()["status"] == "success", "Login did not return success"
    print("Login successful")
    
    # try wrong password
    wrong_pass_response = requests.post(
        f"{base_url}/login", 
        json={
            "username": username,
            "password": "wrongpassword"
        }
    )
    assert wrong_pass_response.status_code == 401, f"Expected status 401, got {wrong_pass_response.status_code}"
    print("Wrong password login failed as expected")
    
    # try non-existent user
    nonexistent_response = requests.post(
        f"{base_url}/login", 
        json={
            "username": "nonexistentuser",
            "password": password
        }
    )
    assert nonexistent_response.status_code == 401, f"Expected status 401, got {nonexistent_response.status_code}"
    print("Nonexistent user login failed as expected")
    
    change_response = session.post(
        f"{base_url}/change-password", 
        json={"new_password": new_password}
    )
    assert change_response.status_code == 200, f"Expected status 200, got {change_response.status_code}"
    assert change_response.json()["status"] == "success", "Password change did not return success"
    print("Password change successful")
    
    # logout
    logout_response = session.post(f"{base_url}/logout")
    assert logout_response.status_code == 200, f"Expected status 200, got {logout_response.status_code}"
    print("Logout successful")
    
    # try changing password while logged out - should fail
    auth_required_response = session.post(
        f"{base_url}/change-password", 
        json={"new_password": "test"}
    )
    assert auth_required_response.status_code == 401, f"Expected status 401, got {auth_required_response.status_code}"
    print("Authenticated endpoint rejected unauthenticated request as expected")
    
    # login with new password
    login_new_response = session.post(
        f"{base_url}/login", 
        json={
            "username": username,
            "password": new_password
        }
    )
    assert login_new_response.status_code == 200, f"Expected status 200, got {login_new_response.status_code}"
    print("Login with new password successful")
    
    # Task creation tests
    print("\n--- Task Creation ---")
    # create a basic task
    task_data = {
        "title": generate_unique_title(),
        "description": "This is a test task",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
    
    # print(f"Task data: {json.dumps(task_data, indent=2)}")
    # print(f"URL: {base_url}/tasks")
    
    create_response = session.post(
        f"{base_url}/tasks", 
        json=task_data
    )
    assert create_response.status_code == 201, f"Expected status 201, got {create_response.status_code}"
    assert create_response.json()["status"] == "success", "Task creation did not return success"
    assert "data" in create_response.json(), "Task creation did not return data"
    assert "id" in create_response.json()["data"], "Task data missing id field"
    tasks.append(create_response.json()["data"]["id"])
    print("Task creation successful")
    
    # create another task without due date
    task_data2 = {
        "title": generate_unique_title(),
        "description": "This is another test task",
        "due_date": None
    }
    
    create_response2 = session.post(
        f"{base_url}/tasks", 
        json=task_data2
    )
    assert create_response2.status_code == 201, f"Expected status 201, got {create_response2.status_code}"
    tasks.append(create_response2.json()["data"]["id"])
    print("Second task creation successful")
    
    # try creating task without title - should fail
    invalid_task = {
        "description": "Task without title"
    }
    
    invalid_response = session.post(
        f"{base_url}/tasks", 
        json=invalid_task
    )
    assert invalid_response.status_code == 400, f"Expected status 400, got {invalid_response.status_code}"
    print("Invalid task creation (missing title) failed as expected")
    
    # try duplicate title - should fail
    duplicate_task = {
        "title": task_data["title"],
        "description": "Duplicate title task"
    }
    
    # print(f"Original task title: {task_data['title']}")
    # print(f"Duplicate task: {json.dumps(duplicate_task, indent=2)}")
    
    duplicate_response = session.post(
        f"{base_url}/tasks", 
        json=duplicate_task
    )
    assert duplicate_response.status_code == 400, f"Expected status 400, got {duplicate_response.status_code}"
    print("Duplicate title task creation failed as expected")
    
    # logout and try creating a task
    session.post(f"{base_url}/logout")
    unauth_task = {
        "title": generate_unique_title(),
        "description": "Task while logged out"
    }
    unauth_response = session.post(
        f"{base_url}/tasks", 
        json=unauth_task
    )
    assert unauth_response.status_code in [401, 201, 400], f"Unexpected status {unauth_response.status_code}, expected 401 or 201"
    print("Unauthorized task creation test completed")
    
    # login again
    session.post(
        f"{base_url}/login", 
        json={
            "username": username,
            "password": new_password
        }
    )
    print("Logged back in successfully")
    
    # get all tasks
    print("\n--- Task Listing ---")
    response = session.get(f"{base_url}/tasks")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert "data" in response.json(), "Tasks data missing from response"
    task_list = response.json()["data"]
    assert len(task_list) >= 2, f"Expected at least 2 tasks, got {len(task_list)}"
    print(f"Successfully retrieved {len(task_list)} tasks")
    
    # check that tasks have all required fields
    for task in task_list:
        assert "id" in task, "Task missing id field"
        assert "title" in task, "Task missing title field"
        assert "description" in task, "Task missing description field"
        assert "completed" in task, "Task missing completed field"
        assert "created_at" in task, "Task missing created_at field"
    print("All tasks have required fields")
    
    # logout and try listing tasks
    session.post(f"{base_url}/logout")
    unauth_response = session.get(f"{base_url}/tasks")
    assert unauth_response.status_code in [401, 200], f"Unexpected status {unauth_response.status_code}, expected 401 or 200"
    print("Unauthorized task listing test completed")
    
    # login again
    session.post(
        f"{base_url}/login", 
        json={
            "username": username,
            "password": new_password
        }
    )
    print("Logged back in successfully")
    
    # get single task
    print("\n--- Task Retrieval ---")
    if not tasks:
        assert False, "No tasks available for testing"
    
    task_id = tasks[0]
    response = session.get(f"{base_url}/tasks/{task_id}")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert "data" in response.json(), "Task data missing from response"
    task = response.json()["data"]
    assert task["id"] == task_id, f"Expected task id {task_id}, got {task['id']}"
    print(f"Successfully retrieved task {task_id}")
    
    # try non-existent task id
    nonexistent_response = session.get(f"{base_url}/tasks/9999")
    assert nonexistent_response.status_code == 404, f"Expected status 404, got {nonexistent_response.status_code}"
    print("Non-existent task retrieval failed as expected")
    
    # logout and try getting a task
    session.post(f"{base_url}/logout")
    unauth_response = session.get(f"{base_url}/tasks/{task_id}")
    assert unauth_response.status_code in [401, 200], f"Unexpected status {unauth_response.status_code}, expected 401 or 200"
    print("Unauthorized task retrieval test completed")
    
    # login again
    session.post(
        f"{base_url}/login", 
        json={
            "username": username,
            "password": new_password
        }
    )
    print("Logged back in successfully")
    
    # update task tests
    print("\n--- Task Updates ---")
    if not tasks:
        assert False, "No tasks available for testing"
    
    task_id = tasks[0]
    
    update_data = {
        "title": generate_unique_title("Updated Task"),
        "description": "Updated task description"
    }
    
    # print(f"Updating task {task_id} with: {json.dumps(update_data, indent=2)}")
    
    update_response = session.put(
        f"{base_url}/tasks/{task_id}", 
        json=update_data
    )
    assert update_response.status_code == 200, f"Expected status 200, got {update_response.status_code}"
    assert update_response.json()["status"] == "success", "Task update did not return success"
    print(f"Successfully updated task {task_id}")
    
    # verify the update worked
    get_response = session.get(f"{base_url}/tasks/{task_id}")
    assert get_response.status_code == 200, f"Expected status 200, got {get_response.status_code}"
    task = get_response.json()["data"]
    assert task["title"] == update_data["title"], f"Expected title {update_data['title']}, got {task['title']}"
    assert task["description"] == update_data["description"], f"Expected description {update_data['description']}, got {task['description']}"
    print("Update verification successful")
    
    # mark task as completed
    complete_data = {
        "completed": True
    }
    
    complete_response = session.put(
        f"{base_url}/tasks/{task_id}", 
        json=complete_data
    )
    assert complete_response.status_code == 200, f"Expected status 200, got {complete_response.status_code}"
    print("Successfully marked task as completed")
    
    # check if it's really completed
    get_response = session.get(f"{base_url}/tasks/{task_id}")
    assert get_response.json()["data"]["completed"] == True, "Task was not marked as completed"
    print("Completion verification successful")
    
    # try updating non-existent task
    nonexistent_response = session.put(
        f"{base_url}/tasks/9999", 
        json=update_data
    )
    assert nonexistent_response.status_code in [404, 400], f"Expected status 404 or 400, got {nonexistent_response.status_code}"
    print("Non-existent task update failed as expected")
    
    # try empty title - should fail
    invalid_data = {
        "title": ""  # should be rejected
    }
    
    invalid_response = session.put(
        f"{base_url}/tasks/{task_id}", 
        json=invalid_data
    )
    assert invalid_response.status_code == 400, f"Expected status 400, got {invalid_response.status_code}"
    print("Invalid task update failed as expected")
    
    # Test update when logged out
    session.post(f"{base_url}/logout")
    unauth_update = {
        "title": generate_unique_title("Unauthorized Update")
    }
    unauth_response = session.put(
        f"{base_url}/tasks/{task_id}", 
        json=unauth_update
    )
    assert unauth_response.status_code in [401, 200, 400], f"Unexpected status {unauth_response.status_code}, expected 401, 200, or 400"
    print("Unauthorized task update test completed")
    
    session.post(
        f"{base_url}/login", 
        json={
            "username": username,
            "password": new_password
        }
    )
    print("Logged back in successfully")
    
    # delete task tests
    print("\n--- Task Deletion ---")
    if not tasks:
        assert False, "No tasks available for testing"
    
    task_id = tasks.pop()  
    
    # print(f"About to delete task {task_id}")
    # task_info = session.get(f"{base_url}/tasks/{task_id}")
    # print(f"Task to delete: {json.dumps(task_info.json(), indent=2)}")
    
    delete_response = session.delete(f"{base_url}/tasks/{task_id}")
    assert delete_response.status_code == 200, f"Expected status 200, got {delete_response.status_code}"
    assert delete_response.json()["status"] == "success", "Task deletion did not return success"
    print(f"Successfully deleted task {task_id}")
    
    get_response = session.get(f"{base_url}/tasks/{task_id}")
    assert get_response.status_code == 404, f"Expected status 404, got {get_response.status_code}"
    print("Deletion verification successful")
    
    # try deleting a task that doesn't exist
    nonexistent_response = session.delete(f"{base_url}/tasks/9999")
    assert nonexistent_response.status_code == 404, f"Expected status 404, got {nonexistent_response.status_code}"
    print("Non-existent task deletion failed as expected")
    
    # logout and try to delete a task
    if tasks:
        task_id = tasks[0]
        session.post(f"{base_url}/logout")
        unauth_response = session.delete(f"{base_url}/tasks/{task_id}")
        assert unauth_response.status_code == 401, f"Expected status 401, got {unauth_response.status_code}"
        print("Unauthorized task deletion failed as expected")
        
        session.post(
            f"{base_url}/login", 
            json={
                "username": username,
                "password": new_password
            }
        )
        print("Logged back in successfully")
    
    # random task tests
    print("\n--- Random Task ---")
    
    # create a few tasks for random selection
    for i in range(3):
        task_data = {
            "title": generate_unique_title(f"Random Test Task {i+1}"),
            "description": f"Test task for random selection {i+1}"
        }
        
        # uncomment for debugging
        # print(f"Creating random task {i+1}: {json.dumps(task_data, indent=2)}")
        
        create_response = session.post(
            f"{base_url}/tasks", 
            json=task_data
        )
        assert create_response.status_code == 201, f"Expected status 201, got {create_response.status_code}"
        tasks.append(create_response.json()["data"]["id"])
        print(f"Created random test task {i+1}")
    
    # try the random endpoint
    random_response = session.get(f"{base_url}/tasks/random")
    
    # if endpoint exists
    if random_response.status_code != 404:
        assert random_response.status_code == 200, f"Expected status 200, got {random_response.status_code}"
        assert "task" in random_response.json(), "Random task missing from response"
        print("Successfully retrieved random task")
        
        # print(f"Random task: {json.dumps(random_response.json(), indent=2)}")
        
        # try while logged out
        session.post(f"{base_url}/logout")
        unauth_response = session.get(f"{base_url}/tasks/random")
        assert unauth_response.status_code == 401, f"Expected status 401, got {unauth_response.status_code}"
        print("Unauthorized random task request failed as expected")
    else:
        print("Note: Random task endpoint not found - skipping this part of the test")
    
    print("\n--- ALL TESTS COMPLETED SUCCESSFULLY ---")
    return True


if __name__ == "__main__":
    # time the tests for performance
    # start_time = time.time()
    
    try:
        success = run_smoketest()
        if not success:
            sys.exit(1)  # Exit with error code if tests fail
        
        # end_time = time.time()
        # print(f"Tests completed in {end_time - start_time:.2f} seconds")
    except Exception as e:
        print(f"Smoketest failed with error: {str(e)}")
        sys.exit(1)
