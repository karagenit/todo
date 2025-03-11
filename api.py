import os.path

from repeat import validate_repeat
from task import Task

from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]

def get_creds():
    """Gets and returns the credentials needed for the Tasks API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

def get_tasks(creds):
    return build("tasks", "v1", credentials=creds).tasks().list(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        showCompleted=False,
        maxResults=100
    ).execute()

# TODO error handling
# TODO move this to TaskList object and do OOP?
def patch_task(creds, task):
    return build("tasks", "v1", credentials=creds).tasks().patch(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task.id,
        body=task.to_api_format()
    ).execute()

def insert_task(creds, task):
    return build("tasks", "v1", credentials=creds).tasks().insert(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        body=task.to_api_format()
    ).execute()

def move_task(creds, task_id, parent_id, previous_id=None):
    service = build("tasks", "v1", credentials=creds)
    result = service.tasks().move(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task_id,
        parent=parent_id,
        previous=previous_id
    ).execute()
    return result