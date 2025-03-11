from datetime import datetime, timedelta

def should_display_task(task):
    today = datetime.now().date()
    no_start_date = not task.start_date
    starts_today_or_earlier = task.start_date and task.start_date <= today
    no_parent = not task.parent_id
    return (no_start_date or starts_today_or_earlier) and no_parent

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

# TODO Rename to get sorted parent tasks
def get_sorted_tasks(tasks):
    return sorted([task for task in tasks if should_display_task(task)], key=task_sort_key)