# Logic for validating and using repeating fields on tasks

from datetime import datetime, timedelta

def validate_single_repeat(day, min, max):
    if day != '*':
        for d in day.split(','):
            if '-' in d:
                start, end = d.split('-')
                if not (start.isdigit() and end.isdigit() and min <= int(start) <= max and min <= int(end) <= max):
                    return False
            elif '/' in d:
                base, step = d.split('/')
                if not (base == '*' and step.isdigit()):
                    return False
            elif not (d.isdigit() and min <= int(d) <= max):
                return False

    return True

def validate_repeat(repeat_str):
    if not repeat_str:
        return False
            
    parts = repeat_str.split()
    if len(parts) != 5:
        return False

    # Validate day of month (1-31, *, ranges like 1-15, lists like 1,15, or */5)
    if not validate_single_repeat(parts[0], 1, 31):
        return False

    if not validate_single_repeat(parts[1], 1, 12):
        return False

    if not validate_single_repeat(parts[2], 0, 6):
        return False

    if not parts[3].isdigit() or not (0 <= int(parts[3]) <= 999):
        return False
    
    if parts[4] not in ['C', 'S']:
        return False
    
    return True

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