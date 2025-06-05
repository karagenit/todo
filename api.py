import os
import os.path

from task import Task

from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]

# Temporary storage for OAuth flows (in production, use Redis or similar)
_oauth_flows = {}

def get_session_creds(existing_creds=None):
    """Gets credentials for session-based authentication (no file storage)."""
    creds = existing_creds
    
    # If existing_creds is a dict (from session), convert to Credentials object
    if isinstance(existing_creds, dict):
        creds = Credentials.from_authorized_user_info(existing_creds, SCOPES)
    
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
            flow = Flow.from_client_secrets_file(
                "credentials.json", 
                scopes=SCOPES,
                redirect_uri="https://localhost:5001/oauth/callback"
            )
            auth_url, state = flow.authorization_url(
                access_type="offline",
                prompt="consent"
            )
            # Store flow temporarily using state as key
            _oauth_flows[state] = flow
            # Return auth_url and state so the caller can redirect the user
            return {"auth_url": auth_url, "state": state}

    return creds

def complete_oauth_flow(state, authorization_response):
    """Complete the OAuth flow with the authorization response."""
    if state not in _oauth_flows:
        raise ValueError("OAuth flow not found for state")
    
    flow = _oauth_flows.pop(state)  # Remove from storage after use
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials

def creds_to_dict(creds):
    """Convert credentials object to dict for session storage."""
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

# TODO for all these API methods - creds could be expired, need to check this and re-auth in that case. May need to store creds as a global or session variable.

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
        result = request.execute() # can throw RefreshError, need to get new creds
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