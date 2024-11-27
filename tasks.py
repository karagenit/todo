import os.path

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
            if field.startswith('#P:'):
                try:
                    item['priority'] = int(field[3:].strip())
                except ValueError:
                    pass
        item['description'] = '<br>'.join([line.strip() for line in notes.splitlines() if not line.strip().startswith('#')])
        
     
    return items
# TODO eventually iterate over the cursor token to get more than 100 results