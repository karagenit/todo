import pytest
from unittest.mock import Mock, patch
from flask import session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import app
import api
from task import Task

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    app.app.config['SECRET_KEY'] = 'test-key'
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
    return [
        Task(id='1', title='Test Task 1').to_dict(),
        Task(id='2', title='Test Task 2').to_dict()
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

    @patch('api.get_session_creds')
    @patch('tasklist.from_api')
    def test_auth_success(self, mock_from_api, mock_get_creds, client, mock_creds, mock_tasks):
        """Test successful authentication flow"""
        mock_creds_obj = Mock()
        mock_get_creds.return_value = mock_creds_obj
        # Return Task objects that will be converted to dicts
        mock_tasks_objects = [Task(id='1', title='Test Task 1'), Task(id='2', title='Test Task 2')]
        mock_from_api.return_value = mock_tasks_objects
        
        with patch('api.creds_to_dict', return_value=mock_creds):
            response = client.get('/auth')
            assert response.status_code == 302
            assert response.location == '/'

    @patch('api.get_session_creds')
    def test_auth_failure(self, mock_get_creds, client):
        """Test authentication failure handling"""
        mock_get_creds.side_effect = Exception("Auth failed")
        
        response = client.get('/auth')
        assert response.status_code == 500
        assert "Authentication failed" in response.get_data(as_text=True)

class TestSessionManagement:
    def test_require_auth_decorator(self, client, mock_creds, mock_tasks):
        """Test that require_auth decorator allows access with valid session"""
        with client.session_transaction() as sess:
            sess['creds'] = mock_creds
            sess['tasks'] = mock_tasks
        
        with patch('summary.get_stats'), patch('filter.filter_tasks'), patch('sort.get_sorted_tasks'):
            response = client.get('/')
            assert response.status_code == 200

    def test_session_isolation(self, mock_creds, mock_tasks):
        """Test that different clients have isolated sessions"""
        client1 = app.app.test_client()
        client2 = app.app.test_client()
        
        # Set different session data for each client
        with client1.session_transaction() as sess:
            sess['creds'] = mock_creds
            sess['tasks'] = [Task(id='1', title='Client 1 Task').to_dict()]
        
        with client2.session_transaction() as sess:
            sess['creds'] = mock_creds
            sess['tasks'] = [Task(id='2', title='Client 2 Task').to_dict()]
        
        # Verify sessions are isolated
        with client1.session_transaction() as sess:
            assert sess['tasks'][0]['title'] == 'Client 1 Task'
        
        with client2.session_transaction() as sess:
            assert sess['tasks'][0]['title'] == 'Client 2 Task'

class TestRouteOperations:
    @patch('api.get_session_creds')
    @patch('tasklist.upsert_task')
    def test_update_task_with_session(self, mock_upsert, mock_get_creds, client, mock_creds, mock_tasks):
        """Test task update uses session credentials"""
        mock_creds_obj = Mock()
        mock_get_creds.return_value = mock_creds_obj
        
        with client.session_transaction() as sess:
            sess['creds'] = mock_creds
            sess['tasks'] = mock_tasks
        
        response = client.post('/update', data={'title': 'New Task'})
        assert response.status_code == 302
        mock_get_creds.assert_called_once_with(mock_creds)
        mock_upsert.assert_called_once()

    @patch('api.get_session_creds')
    @patch('tasklist.from_api')
    def test_reload_tasks_with_session(self, mock_from_api, mock_get_creds, client, mock_creds, mock_tasks):
        """Test reload uses session credentials and updates session tasks"""
        mock_creds_obj = Mock()
        mock_get_creds.return_value = mock_creds_obj
        # Return Task objects that will be converted to dicts
        mock_tasks_objects = [Task(id='1', title='Test Task 1'), Task(id='2', title='Test Task 2')]
        mock_from_api.return_value = mock_tasks_objects
        
        with client.session_transaction() as sess:
            sess['creds'] = mock_creds
            sess['tasks'] = []
        
        response = client.get('/reload')
        assert response.status_code == 302
        mock_get_creds.assert_called_once_with(mock_creds)
        mock_from_api.assert_called_once_with(mock_creds_obj)

class TestCredentialHandling:
    def test_creds_to_dict_conversion(self):
        """Test credential object to dict conversion"""
        mock_creds = Mock()
        mock_creds.token = 'test_token'
        mock_creds.refresh_token = 'test_refresh_token'
        mock_creds.token_uri = 'https://oauth2.googleapis.com/token'
        mock_creds.client_id = 'test_client_id'
        mock_creds.client_secret = 'test_client_secret'
        mock_creds.scopes = ['https://www.googleapis.com/auth/tasks']
        
        result = api.creds_to_dict(mock_creds)
        
        assert result['token'] == 'test_token'
        assert result['refresh_token'] == 'test_refresh_token'
        assert result['token_uri'] == 'https://oauth2.googleapis.com/token'
        assert result['client_id'] == 'test_client_id'
        assert result['client_secret'] == 'test_client_secret'
        assert result['scopes'] == ['https://www.googleapis.com/auth/tasks']

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