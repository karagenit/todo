# Logic for validating and using repeating fields on tasks

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

def next_repeat_date(last_date, repeat_str):
    return None
