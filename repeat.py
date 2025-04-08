# Logic for validating and using repeating fields on tasks

from datetime import datetime, timedelta
from repeat_validation import validate_repeat
from task import Task

def matches_repeat_field(repeat_field, value):
    if repeat_field == '*':
        return True
        
    for part in repeat_field.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            if start <= value <= end:
                return True
        elif '/' in part:
            base, step = part.split('/')
            if base == '*' and value % int(step) == 0:
                return True
        elif int(part) == value:
            return True
            
    return False

# last_date should be a Date object not a string
# last_date is the previous start date. Completion date is usually today's date
def next_repeat_date(last_date, completion_date, repeat_str):
    if not validate_repeat(repeat_str):
        return None

    parts = repeat_str.split()
        
    next_date = completion_date if parts[4] == 'C' else last_date

    days_to_add = int(parts[3])
    next_date = next_date + timedelta(days=days_to_add)
    
    # look ahead up to 1000 days in the future to find the next valid date that matches all criteria
    for i in range(1000):
        day_of_month = next_date.day
        month_of_year = next_date.month
        # Python gives us monday=0 but crontab standard has sunday=0
        day_of_week = (next_date.weekday() + 1) % 7

        if (matches_repeat_field(parts[0], day_of_month) and
            matches_repeat_field(parts[1], month_of_year) and
            matches_repeat_field(parts[2], day_of_week)):
            return next_date

        next_date = next_date + timedelta(days=1)
    
    return None

def next_repeat_task(task: Task) -> Task:
    repeat_completed_date = datetime.now().date() # TODO should we use the actual assigned date??
    repeat_start_date = task.start_date or repeat_completed_date
    repeat_due_date = task.due_date or repeat_completed_date
    # This will just give us None if there's a blank repeat_start/repeat_due, which makes sense (just clear the field for the next task)
    next_start = next_repeat_date(repeat_start_date, repeat_completed_date, task.repeat_start)   
    next_due = next_repeat_date(repeat_due_date, repeat_completed_date, task.repeat_due)         
    return Task(
        title=task.title,
        description=task.description,
        start_date=next_start,
        # due_date=task.due_date + (next_start - repeat_start_date) if task.due_date else None, # TODO interesting idea but want to just have separate due repeating in the future
        due_date=next_due,
        repeat_start=task.repeat_start,
        repeat_due=task.repeat_due,
        priority=task.priority
    )    