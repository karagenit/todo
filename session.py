from flask import session
from functools import wraps
import uuid

# In-memory session store to avoid large cookies
session_store = {}

def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_user_data(key, default=None):
    """Get user data from server-side session store"""
    session_id = get_session_id()
    if session_id not in session_store:
        session_store[session_id] = {}
    return session_store[session_id].get(key, default)

def set_user_data(key, value):
    """Set user data in server-side session store"""
    session_id = get_session_id()
    if session_id not in session_store:
        session_store[session_id] = {}
    session_store[session_id][key] = value

def clear_user_data():
    """Clear user data from server-side session store"""
    session_id = get_session_id()
    if session_id in session_store:
        del session_store[session_id]
    session.clear()

def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_user_data('creds') or not get_user_data('tasks'):
            from flask import redirect
            return redirect('/auth')
        return f(*args, **kwargs)
    return decorated_function