import os.path

from task import Task

from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

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
        # TODO catch ValueError (missing refresh_token) and just delete it? Ideally should never happen since we create the token w access_type=offline and prompt=consent

    # If there are no creds or invalid creds, get new creds
    if not creds or not creds.valid:
        # Whether we need an entirely new set of creds
        should_reauth = True

        # If we can, just use the refresh token to get new creds
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                should_reauth = False
            except RefreshError:
                # If there was a problem with the refresh token (e.g. it expired) we'll have to just get new creds
                should_reauth = True
        
        # If we need to, get new creds totally
        if should_reauth:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

        # Finally, save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

def get_tasks(creds):
    return build("tasks", "v1", credentials=creds).tasks().list(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        showCompleted=False,
        maxResults=100
    ).execute()

def get_all_tasks(creds):
    task_resource = build("tasks", "v1", credentials=creds).tasks()
    results = []
    request = task_resource.list(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        showCompleted=False,
        maxResults=100
    )
    while request is not None:
        result = request.execute()
        results.append(result)
        request = task_resource.list_next(request, result) # this is how google tasks API does pagination
    return results

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

def delete_task(creds, task):
    return build("tasks", "v1", credentials=creds).tasks().patch(
        tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow",
        task=task.id
    ).execute()