import pytest
from unittest.mock import Mock, patch
from flask import session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import app
import session
from auth import get_session_creds, complete_oauth_flow, _oauth_flows, SCOPES
from task import Task

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    app.app.config['SECRET_KEY'] = 'test-key'
    # Clear session store before each test
    session.session_store.clear()
    with app.app.test_client() as client:
        yield client

@pytest.fixture
def mock_creds():
    return {
        'token': 'mock_token',
        'refresh_token': 'mock_refresh_token',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'mock_client_id',
        'client_secret': 'mock_client_secret',
        'scopes': ['https://www.googleapis.com/auth/tasks']
    }

@pytest.fixture
def mock_tasks():
    # Return Task objects directly instead of dictionaries
    return [
        Task(id='1', title='Test Task 1'),
        Task(id='2', title='Test Task 2')
    ]

@pytest.fixture(autouse=True)
def clear_oauth_flows():
    """Clear oauth flows before each test"""
    _oauth_flows.clear()
    yield
    _oauth_flows.clear()

class TestAuthentication:
    def test_index_redirects_without_auth(self, client):
        """Test that index route redirects to /auth when not authenticated"""
        response = client.get('/')
        assert response.status_code == 302
        assert '/auth' in response.location

    def test_update_redirects_without_auth(self, client):
        """Test that update route redirects to /auth when not authenticated"""
        response = client.post('/update')
        assert response.status_code == 302
        assert '/auth' in response.location

    def test_reload_redirects_without_auth(self, client):
        """Test that reload route redirects to /auth when not authenticated"""
        response = client.get('/reload')
        assert response.status_code == 302
        assert '/auth' in response.location

    @patch('auth.get_session_creds')
    @patch('app.tasklist.from_api')
    def test_auth_success_with_existing_creds(self, mock_from_api, mock_get_creds, client, mock_creds, mock_tasks):
        """Test successful authentication flow with existing valid credentials"""
        mock_creds_obj = Mock()
        mock_get_creds.return_value = mock_creds_obj
        # Return Task objects directly
        mock_from_api.return_value = mock_tasks
        
        response = client.get('/auth')
        assert response.status_code == 302
        assert response.location == '/'

    @patch('auth.get_session_creds')
    def test_auth_redirects_to_google(self, mock_get_creds, client):
        """Test authentication flow redirects to Google when new auth is needed"""
        mock_get_creds.return_value = {
            'auth_url': 'https://accounts.google.com/oauth2/auth?param=value',
            'state': 'test-state'
        }
        
        response = client.get('/auth')
        assert response.status_code == 302
        assert 'accounts.google.com' in response.location
        
        # Verify state is stored in session
        with client.session_transaction() as sess:
            assert sess.get('oauth_state') == 'test-state'

    @patch('auth.get_session_creds')
    def test_auth_failure(self, mock_get_creds, client):
        """Test authentication failure handling"""
        mock_get_creds.side_effect = Exception("Auth failed")
        
        response = client.get('/auth')
        assert response.status_code == 500
        assert "Authentication failed" in response.get_data(as_text=True)

    @patch('auth.complete_oauth_flow')
    @patch('app.tasklist.from_api')
    def test_oauth_callback_success(self, mock_from_api, mock_complete_flow, client, mock_creds):
        """Test successful OAuth callback handling"""
        mock_creds_obj = Mock()
        mock_complete_flow.return_value = mock_creds_obj
        mock_from_api.return_value = [Task(id='1', title='Test Task 1')]
        
        # Set up session with state
        test_session_id = 'test-oauth-callback'
        import session
        session.session_store[test_session_id] = {}
        
        with client.session_transaction() as sess:
            sess['session_id'] = test_session_id
            sess['oauth_state'] = 'test-state'
        
        response = client.get('/oauth/callback?state=test-state&code=auth-code')
        assert response.status_code == 302
        assert response.location == '/'
        
        # Verify flow was completed with correct parameters
        mock_complete_flow.assert_called_once_with('test-state', 'http://localhost/oauth/callback?state=test-state&code=auth-code')
        
        # Verify session was cleaned up
        with client.session_transaction() as sess:
            assert 'oauth_state' not in sess

    def test_oauth_callback_missing_state(self, client):
        """Test OAuth callback fails when no state is stored in session"""
        response = client.get('/oauth/callback?state=test-state&code=auth-code')
        assert response.status_code == 400
        assert "OAuth state not found" in response.get_data(as_text=True)

    def test_oauth_callback_invalid_state(self, client):
        """Test OAuth callback fails when state parameter doesn't match"""
        with client.session_transaction() as sess:
            sess['oauth_state'] = 'stored-state'
        
        response = client.get('/oauth/callback?state=different-state&code=auth-code')
        assert response.status_code == 400
        assert "Invalid state parameter" in response.get_data(as_text=True)

    @patch('auth.complete_oauth_flow')
    def test_oauth_callback_failure(self, mock_complete_flow, client):
        """Test OAuth callback failure handling"""
        mock_complete_flow.side_effect = Exception("OAuth failed")
        
        with client.session_transaction() as sess:
            sess['oauth_state'] = 'test-state'
        
        response = client.get('/oauth/callback?state=test-state&code=auth-code')
        assert response.status_code == 500
        assert "OAuth callback failed" in response.get_data(as_text=True)
        
        # Verify session was cleaned up even on failure
        with client.session_transaction() as sess:
            assert 'oauth_state' not in sess

class TestCredentialHandling:
    @patch('google.oauth2.credentials.Credentials.from_authorized_user_info')
    def test_session_creds_from_dict(self, mock_from_info):
        """Test converting dict back to credentials object"""
        mock_creds_dict = {
            'token': 'test_token',
            'refresh_token': 'test_refresh_token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'scopes': ['https://www.googleapis.com/auth/tasks']
        }
        
        mock_creds_obj = Mock()
        mock_creds_obj.valid = True
        mock_from_info.return_value = mock_creds_obj
        
        result = get_session_creds(mock_creds_dict)
        
        mock_from_info.assert_called_once_with(mock_creds_dict, SCOPES)
        assert result == mock_creds_obj

class TestOAuthFlow:
    @patch('auth.Flow.from_client_secrets_file')
    def test_get_session_creds_returns_auth_url_for_new_auth(self, mock_flow_class):
        """Test that get_session_creds returns auth URL when new authentication is needed"""
        mock_flow = Mock()
        mock_flow_class.return_value = mock_flow
        mock_flow.authorization_url.return_value = ('https://accounts.google.com/oauth2/auth', 'test-state')
        
        result = get_session_creds()
        
        assert isinstance(result, dict)
        assert 'auth_url' in result
        assert 'state' in result
        assert result['auth_url'] == 'https://accounts.google.com/oauth2/auth'
        assert result['state'] == 'test-state'
        # Verify flow is stored in module storage
        assert _oauth_flows['test-state'] == mock_flow
        # Verify flow was created with correct parameters
        mock_flow_class.assert_called_once_with(
            "credentials.json",
            scopes=SCOPES,
            redirect_uri="https://localhost:5001/oauth/callback"
        )
        mock_flow.authorization_url.assert_called_once_with(
            access_type="offline",
            prompt="consent"
        )

    @patch('google.oauth2.credentials.Credentials.from_authorized_user_info')
    def test_get_session_creds_with_valid_existing_creds(self, mock_from_info):
        """Test that get_session_creds returns credentials when existing creds are valid"""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_from_info.return_value = mock_creds
        
        existing_creds = {
            'token': 'test_token',
            'refresh_token': 'test_refresh_token'
        }
        
        result = get_session_creds(existing_creds)
        
        assert result == mock_creds
        mock_from_info.assert_called_once_with(existing_creds, SCOPES)

    @patch('google.oauth2.credentials.Credentials.from_authorized_user_info')
    @patch('google.auth.transport.requests.Request')
    def test_get_session_creds_refreshes_expired_creds(self, mock_request, mock_from_info):
        """Test that get_session_creds refreshes expired credentials"""
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = 'valid_refresh_token'
        mock_from_info.return_value = mock_creds
        
        # Mock successful refresh
        def refresh_side_effect(request):
            mock_creds.valid = True
        mock_creds.refresh.side_effect = refresh_side_effect
        
        existing_creds = {
            'token': 'expired_token',
            'refresh_token': 'valid_refresh_token'
        }
        
        result = get_session_creds(existing_creds)
        
        assert result == mock_creds
        mock_creds.refresh.assert_called_once()

    def test_complete_oauth_flow(self):
        """Test complete_oauth_flow function"""
        mock_flow = Mock()
        mock_creds = Mock()
        mock_flow.credentials = mock_creds
        
        # Store flow in the module's flow storage
        state = 'test-state'
        _oauth_flows[state] = mock_flow
        
        authorization_response = 'https://localhost:5001/oauth/callback?code=auth-code&state=test-state'
        
        result = complete_oauth_flow(state, authorization_response)
        
        assert result == mock_creds
        mock_flow.fetch_token.assert_called_once_with(authorization_response=authorization_response)
        assert state not in _oauth_flows