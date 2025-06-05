from flask import Blueprint, redirect, session, request
from session import get_user_data, set_user_data, clear_user_data
import api
import tasklist
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
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

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth')
def auth():
    try:
        existing_creds = get_user_data('creds')
        result = get_session_creds(existing_creds)
        
        if isinstance(result, dict) and 'auth_url' in result:
            session['oauth_state'] = result['state']
            return redirect(result['auth_url'])
        
        creds = result
        set_user_data('creds', creds)
        tasks = tasklist.from_api(creds)
        set_user_data('tasks', tasks)
        return redirect('/')
    except Exception as e:
        clear_user_data()
        return f"Authentication failed: {str(e)}", 500

@auth_bp.route('/oauth/callback')
def oauth_callback():
    try:
        stored_state = session.get('oauth_state')
        
        if not stored_state:
            return "OAuth state not found. Please restart authentication.", 400
        
        if request.args.get('state') != stored_state:
            return "Invalid state parameter. Possible CSRF attack.", 400
        
        authorization_response = request.url
        creds = complete_oauth_flow(stored_state, authorization_response)
        
        set_user_data('creds', creds)
        tasks = tasklist.from_api(creds)
        set_user_data('tasks', tasks)
        
        session.pop('oauth_state', None)
        
        return redirect('/')
    except Exception as e:
        clear_user_data()
        session.pop('oauth_state', None)
        return f"OAuth callback failed: {str(e)}", 500