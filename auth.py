from flask import Blueprint, redirect, session, request
from session import get_user_data, set_user_data, clear_user_data
import api
import tasklist

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth')
def auth():
    try:
        existing_creds = get_user_data('creds')
        result = api.get_session_creds(existing_creds)
        
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
        creds = api.complete_oauth_flow(stored_state, authorization_response)
        
        set_user_data('creds', creds)
        tasks = tasklist.from_api(creds)
        set_user_data('tasks', tasks)
        
        session.pop('oauth_state', None)
        
        return redirect('/')
    except Exception as e:
        clear_user_data()
        session.pop('oauth_state', None)
        return f"OAuth callback failed: {str(e)}", 500