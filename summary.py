from datetime import datetime, timedelta
from task import Task

# TODO need to use the implied due dates from the sorting algo here?
def get_stats(tasks: list[Task]) -> dict:
    today = datetime.now().date()
    return {
        'p3': sum(1 for task in tasks if task.priority == 3),
        'p2': sum(1 for task in tasks if task.priority == 2),
        'p1': sum(1 for task in tasks if task.priority == 1),
        'p0': sum(1 for task in tasks if task.priority == 0),
        'overdue': sum(1 for task in tasks if task.due_date and task.due_date < today),
        'today': sum(1 for task in tasks if task.due_date and today <= task.due_date < today + timedelta(days=1)),
        'week':  sum(1 for task in tasks if task.due_date and today + timedelta(days=1) <= task.due_date <= today + timedelta(days=7)),
        'month': sum(1 for task in tasks if task.due_date and today + timedelta(days=7) < task.due_date <= today + timedelta(days=30))
    }