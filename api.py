"""
Google Tasks API integration module for the Todo application.
This module provides functions to interact with Google Tasks API for managing tasks.
"""
from googleapiclient.discovery import build

# TODO for all these API methods - creds could be expired, need to check this and re-auth in that case. May need to store creds as a global or session variable.

def get_tasks(creds):
    """
    Retrieve a list of incomplete tasks from Google Tasks API.
    
    Args:
        creds: Google API credentials
        
    Returns:
        Dictionary containing task data
    """
    return build("tasks", "v1", credentials=creds).tasks().list(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        showCompleted=False,
        maxResults=100
    ).execute()

def get_all_tasks(creds):
    """
    Retrieve all incomplete tasks from Google Tasks API with pagination support.
    
    Args:
        creds: Google API credentials
        
    Returns:
        List of dictionaries containing task data
    """
    task_resource = build("tasks", "v1", credentials=creds).tasks()
    results = []
    request = task_resource.list(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        showCompleted=False,
        maxResults=100
    )
    while request is not None:
        result = request.execute() # can throw RefreshError, need to get new creds
        results.append(result)
        request = task_resource.list_next(request, result) # this is how google tasks API does pagination
    return results

# TODO error handling
# TODO move this to TaskList object and do OOP?
def patch_task(creds, task):
    """
    Update an existing task in Google Tasks.
    
    Args:
        creds: Google API credentials
        task: Task object to be updated
        
    Returns:
        Updated task data from the API
    """
    return build("tasks", "v1", credentials=creds).tasks().patch(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task.id,
        body=task.to_api_format()
    ).execute()

def insert_task(creds, task):
    """
    Create a new task in Google Tasks.
    
    Args:
        creds: Google API credentials
        task: Task object to be created
        
    Returns:
        Newly created task data from the API
    """
    return build("tasks", "v1", credentials=creds).tasks().insert(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        body=task.to_api_format()
    ).execute()

def move_task(creds, task_id, parent_id, previous_id=None):
    """
    Move a task to a different position in the task hierarchy.
    
    Args:
        creds: Google API credentials
        task_id: ID of the task to move
        parent_id: ID of the new parent task
        previous_id: ID of the task that should come before this one
        
    Returns:
        Updated task data from the API
    """
    service = build("tasks", "v1", credentials=creds)
    result = service.tasks().move(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task_id,
        parent=parent_id,
        previous=previous_id
    ).execute()
    return result

def delete_task(creds, task):
    """
    Delete a task from Google Tasks.
    
    Args:
        creds: Google API credentials
        task: Task object to be deleted
        
    Returns:
        Response from the API
    """
    return build("tasks", "v1", credentials=creds).tasks().patch(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task.id
    ).execute()