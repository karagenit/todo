import os.path

from repeat import validate_repeat

from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# TODO repeat
def get_tasks(creds):
    service = build("tasks", "v1", credentials=creds)
    # Call the Tasks API
    results = service.tasks().list(tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow", showCompleted=False, maxResults=100).execute()
    items = results.get("items", [])
    
    for item in items:
        notes = item.get('notes', '')
        desc_fields = [line.strip() for line in notes.splitlines() if line.strip().startswith('#')]
        item['priority'] = 0 # default value
        for field in desc_fields:
            try:
                if field.startswith('#P:'):
                    item['priority'] = int(field[3:].strip())
                elif field.startswith('#D:'):
                    date_str = field[3:].strip()
                    item['due_date'] = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                elif field.startswith('#S:'):
                    date_str = field[3:].strip()
                    item['start_date'] = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                elif field.startswith('#R:'):
                    repeat_str = field[3:].strip()
                    if not validate_repeat(repeat_str):
                        repeat_str = ''
                    item['repeat'] = repeat_str
            except ValueError:
                pass            
        item['description'] = '\n'.join([line.strip() for line in notes.splitlines() if not line.strip().startswith('#')])
        # What google calendar calls "due" we call the "assigned" date (the date it shows up on the calendar on)
        due_str = item.get('due', '')
        item['assigned_date'] = datetime.strptime(due_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d') if due_str else ''    

    return items
# TODO eventually iterate over the cursor token to get more than 100 results

def patch_task(creds, task_id, title, description, priority, start_date, due_date, completed, status, due, repeat):
    service = build("tasks", "v1", credentials=creds)
        
    notes = description + "\n"
    if priority is not None:
        notes += f"#P:{priority}\n"
    if start_date:
        notes += f"#S:{start_date}\n"
    if due_date:
        notes += f"#D:{due_date}\n"
    if repeat:
        notes += f"#R:{repeat}\n"
    
    task = {
        'title': title,
        'notes': notes.strip(),
        'completed': completed,
        'status': status,
        'due': due # TODO only overwrite if intentional? ie if we arent changing the due date in our app we should keep the existing one... maybe differentiate None vs ''
    }    
    
    result = service.tasks().patch(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task_id,
        body=task
    ).execute()
    
    return result

def insert_task(creds, title, description, priority, start_date, due_date, completed, status, due, repeat):
    service = build("tasks", "v1", credentials=creds)
            
    notes = description + "\n"
    if priority is not None:
        notes += f"#P:{priority}\n"
    if start_date:
        notes += f"#S:{start_date}\n"
    if due_date:
        notes += f"#D:{due_date}\n"
    if repeat:
        notes += f"#R:{repeat}\n"
    
    task = {
        'title': title,
        'notes': notes.strip(),
        'completed': completed,
        'status': status,
        'due': due
    }    
    
    result = service.tasks().insert(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        body=task
    ).execute()
    
    return result

def move_task(creds, task_id, parent_id, previous_id=None):
    service = build("tasks", "v1", credentials=creds)
    result = service.tasks().move(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task_id,
        parent=parent_id,
        previous=previous_id
    ).execute()
    return result
