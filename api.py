import os
import os.path

from task import Task
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# TODO for all these API methods - creds could be expired, need to check this and re-auth in that case. May need to store creds as a global or session variable.

def get_tasks(creds):
    return build("tasks", "v1", credentials=creds).tasks().list(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        showCompleted=False,
        maxResults=100
    ).execute()

def get_all_tasks(creds):
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
    return build("tasks", "v1", credentials=creds).tasks().patch(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task.id,
        body=task.to_api_format()
    ).execute()

def insert_task(creds, task):
    return build("tasks", "v1", credentials=creds).tasks().insert(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        body=task.to_api_format()
    ).execute()

def move_task(creds, task_id, parent_id, previous_id=None):
    service = build("tasks", "v1", credentials=creds)
    result = service.tasks().move(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task_id,
        parent=parent_id,
        previous=previous_id
    ).execute()
    return result

def delete_task(creds, task):
    return build("tasks", "v1", credentials=creds).tasks().patch(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task.id
    ).execute()