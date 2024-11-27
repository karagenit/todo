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
    return items

# TODO eventually iterate over the cursor token to get more than 100 results