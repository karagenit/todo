from task import Task
from datetime import date

def filter_tasks(tasks, filter_args):
    tasks = filter_tasks_by_text(tasks, filter_args.search)
    tasks = filter_tasks_by_children(tasks, filter_args.hide_children)
    tasks = filter_tasks_by_start(tasks, filter_args.show_future)
    return tasks

def filter_tasks_by_text(tasks, search_text):
    # Empty string or null search string does nothing
    if not search_text:
        return tasks
    filtered = []
    for task in tasks:
        if (search_text.lower() in task.title.lower() or 
            search_text.lower() in task.description.lower()):
            filtered.append(task)
    return filtered

def filter_tasks_by_children(tasks, hide_children):
    if not hide_children:
        return tasks
    filtered = []
    for task in tasks:
        if not task.parent_id:
            filtered.append(task)
    return filtered

def filter_tasks_by_start(tasks, show_future):
    if show_future:
        return tasks
    
    today = date.today()
    
    filtered = []
    for task in tasks:
        no_start_date = not task.start_date
        starts_today_or_earlier = task.start_date and task.start_date <= today
        if no_start_date or starts_today_or_earlier:
            filtered.append(task)
    return filtered
    