from task import Task
import api
from typing import Dict, List
from repeat import next_repeat_task
from repeat_validation import validate_repeat
from datetime import datetime, timedelta, date

# TODO maybe this could be a TaskList class, where it stores the creds inside it? That way we don't have to have the global creds we always pass in...

# TODO clean this up once we're sure it's working for a while
def debug_ordering(items):
    """
    Debug function to analyze task ordering from Google Tasks API.
    
    Args:
        items: List of task items from API responses
    """
    print("=== DEBUG: Task Ordering Analysis ===")
    
    print(f"Total tasks fetched: {len(items)}")
    
    # Print first 10 tasks for comparison with UI
    print("\nFirst 10 tasks from API:")
    for i, task in enumerate(items[:10]):
        print(f"{i+1}. {task.get('title', 'No title')} (ID: {task.get('id', 'No ID')})")
    
    # Count tasks with position field and print first 10 position values
    tasks_with_position = [task for task in items if 'position' in task]
    print(f"\nTasks with position field: {len(tasks_with_position)} out of {len(items)}")
    
    print("\nFirst 10 position values:")
    for i, task in enumerate(tasks_with_position[:10]):
        print(f"{i+1}. {task.get('title', 'No title')} - Position: {task.get('position')}")
    
    # Check if tasks are in position field order
    positions = [task.get('position') for task in items if 'position' in task]
    is_in_order = all(positions[i] <= positions[i+1] for i in range(len(positions)-1))
    print(f"\nTasks in position field order: {is_in_order}")
    
    print("=== END DEBUG ===\n")

def from_api(creds) -> List[Task]:
    api_responses = api.get_all_tasks(creds)
    items = [item for response in api_responses for item in response.get("items", [])]
    # Sort by position field to maintain proper order (Google API returns by last updated, not position)
    # TODO might be better to store position on Task and sort when needed so we don't have to worry about keeping tasks in the correct UI order
    items.sort(key=lambda x: x.get('position', ''))
    debug_ordering(items)
    return [Task.from_api_response(item) for item in items]

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
        # TODO we don't want to prepend child tasks, we want to insert them in the array right after the parent (this is how google sorts them by default)
    tasks.insert(0, task)

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
