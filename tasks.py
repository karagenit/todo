import os.path

from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
            except ValueError:
                pass            
        item['description'] = '\n'.join([line.strip() for line in notes.splitlines() if not line.strip().startswith('#')])
    
    return items
# TODO eventually iterate over the cursor token to get more than 100 results

def patch_task(creds, task_id, title, description, priority, start_date, due_date, completed, status, due):
    service = build("tasks", "v1", credentials=creds)
        
    notes = description + "\n"
    if priority is not None:
        notes += f"#P:{priority}\n"
    if start_date:
        notes += f"#S:{start_date}\n"
    if due_date:
        notes += f"#D:{due_date}\n"
    
    task = {
        'title': title,
        'notes': notes.strip(),
        'completed': completed,
        'status': status,
        'due': due
    }

    print(task)
    
    
    result = service.tasks().patch(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task_id,
        body=task
    ).execute()
    
    return result