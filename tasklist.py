from task import Task
import api
from typing import Dict, List

# TODO maybe this could be a TaskList class, where it stores the creds inside it? That way we don't have to have the global creds we always pass in...

def from_api(creds) -> List[Task]:
    return from_api_response(api.get_tasks(creds))

def from_api_response(results: Dict) -> List[Task]:
    items = results.get("items", [])
    return [Task.from_api_response(item) for item in items]
    # TODO eventually iterate over the cursor token to get more than 100 results

def upsert_task(creds, tasks, task):
    if task.id:
        update_task(creds, tasks, task)
    else:
        insert_task(creds, tasks, task)

def update_task(creds, tasks, task):
    api.patch_task(creds, task)
    # Remove old task from the array, and only replace it if not completed
    tasks[:] = [t for t in tasks if t.id != task.id]
    if not task.completed:
        tasks.append(task)
    # FIXME for repeating
    # if status == 'completed' and validate_repeat(repeat):
    #     repeat_start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else datetime.now().date()
    #     next_start = next_repeat_date(repeat_start_date, datetime.now().date(), repeat).strftime('%Y-%m-%d')
    #     result = insert_task(creds, title, description, priority, next_start, due_date, None, 'needsAction', None, repeat)
    #     tasks.append({
    #         'id': result['id'],
    #         'parent': None,
    #         'title': title,
    #         'description': description,
    #         'priority': priority,
    #         'start_date': next_start,
    #         'due_date': due_date,
    #         'repeat': repeat
    #     })

def insert_task(creds, tasks, task):
    result = api.insert_task(creds, task)
    task.id = result['id']
    if task.parent_id:
        api.move_task(creds, task.id, task.parent_id, None)
    tasks.append(task)
