from datetime import datetime, timedelta

def task_sort_key(task):
    start_date_str = task.start_date_str()
    if not start_date_str:
        start_date = datetime.now()
    else:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    
    if start_date.date() < datetime.now().date():
        start_date = datetime.now()
    
    sort_key = task.assigned_date_str() or task.due_date_str()
    if not sort_key:
        priority = task.priority
        if priority == 3:
            sort_key = (start_date + timedelta(days=7)).strftime('%Y-%m-%d')
        elif priority == 2:
            sort_key = (start_date + timedelta(days=14)).strftime('%Y-%m-%d')
        elif priority == 1:
            sort_key = (start_date + timedelta(days=30)).strftime('%Y-%m-%d')
        elif priority == 0:
            sort_key = (start_date + timedelta(days=-7)).strftime('%Y-%m-%d')

    # Add priority to the sort order as a tiebreaker for equal dates
    return sort_key + '-' + str(3 - task.priority)

def get_sorted_tasks(tasks):
    return sorted(tasks, key=task_sort_key)