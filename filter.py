from task import Task

def filter_tasks(tasks, search_text):
    # Empty string or null search string does nothing
    if not search_text:
        return tasks
    filtered = []
    for task in tasks:
        if (search_text.lower() in task.title.lower() or 
            search_text.lower() in task.description.lower()):
            filtered.append(task)
    return filtered
    