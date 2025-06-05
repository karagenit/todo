import pytest
from unittest.mock import Mock, patch
from flask import session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import app
import session
import api
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

    @patch('app.api.get_session_creds')
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

    @patch('app.api.get_session_creds')
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

    @patch('app.api.get_session_creds')
    def test_auth_failure(self, mock_get_creds, client):
        """Test authentication failure handling"""
        mock_get_creds.side_effect = Exception("Auth failed")
        
        response = client.get('/auth')
        assert response.status_code == 500
        assert "Authentication failed" in response.get_data(as_text=True)

    @patch('app.api.complete_oauth_flow')
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

    @patch('app.api.complete_oauth_flow')
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
        
        result = api.get_session_creds(mock_creds_dict)
        
        mock_from_info.assert_called_once_with(mock_creds_dict, api.SCOPES)
        assert result == mock_creds_obj

class TestOAuthLoopPrevention:
    def test_oauth_redirect_loop_prevention(self, client):
        """Test that OAuth redirect loops are prevented by proper session handling"""
        with patch('app.api.get_session_creds') as mock_get_creds, patch('app.tasklist.from_api') as mock_from_api:
            mock_creds_obj = Mock()
            mock_get_creds.return_value = mock_creds_obj
            mock_from_api.return_value = [Task(id='1', title='Test Task')]
            
            # First call to /auth should succeed and store credentials
            response1 = client.get('/auth')
            assert response1.status_code == 302
            assert response1.location == '/'
            
            # Verify credentials are stored in session store
            with client.session_transaction() as sess:
                session_id = sess.get('session_id')
                assert session_id is not None
                assert session_id in session.session_store
                assert 'creds' in session.session_store[session_id]
                assert 'tasks' in session.session_store[session_id]