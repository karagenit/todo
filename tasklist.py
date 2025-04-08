from task import Task
import api
from typing import Dict, List
from repeat import next_repeat_task
from repeat_validation import validate_repeat
from datetime import datetime, timedelta, date

# TODO maybe this could be a TaskList class, where it stores the creds inside it? That way we don't have to have the global creds we always pass in...

def from_api(creds) -> List[Task]:
    return from_api_response(api.get_tasks(creds))

def from_api_response(results: Dict) -> List[Task]:
    items = results.get("items", [])
    return [Task.from_api_response(item) for item in items]
    # TODO eventually iterate over the cursor token to get more than 100 results

def upsert_task(creds, tasks, task):
    if task.id:
        if task.deleted:
            delete_task(creds, tasks, task)
        else:
            update_task(creds, tasks, task)
    else:
        insert_task(creds, tasks, task)

def update_task(creds, tasks, task):
    api.patch_task(creds, task)
    # Remove old task from the array, and only replace it if not completed
    tasks[:] = [t for t in tasks if t.id != task.id]
    if not task.completed:
        tasks.append(task)
    if task.completed and (validate_repeat(task.repeat_start) or validate_repeat(task.repeat_due)):
        insert_task(creds, tasks, next_repeat_task(task))

def insert_task(creds, tasks, task):
    result = api.insert_task(creds, task)
    task.id = result['id']
    if task.parent_id:
        api.move_task(creds, task.id, task.parent_id, None)
    tasks.append(task)

def delete_task(creds, tasks, task):
    # FIXME this throws a 500 internal server error on google's side...
    # api.delete_task(creds, task)
    # tasks[:] = [t for t in tasks if t.id != task.id]
    # TODO as a temporary hack we'll set it completed but without assigned date
    task.assigned_date = ''
    task.completed = datetime.now().date().strftime('%Y-%m-%dT%H:%M:%SZ')
    task.status = 'completed'
    update_task(creds, tasks, task)
    # TODO make sure repeat doens't create a new one when deleting here
