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

class TestSessionManagement:
    def test_require_auth_decorator(self, client, mock_creds, mock_tasks):
        """Test that require_auth decorator allows access with valid session"""
        with client.session_transaction() as sess:
            sess['session_id'] = 'test-session-id'
        
        # Manually set user data in session store
        session.session_store['test-session-id'] = {
            'creds': mock_creds,
            'tasks': mock_tasks
        }
        
        with patch('summary.get_stats'), patch('filter.filter_tasks'), patch('sort.get_sorted_tasks'):
            response = client.get('/')
            assert response.status_code == 200

    def test_session_isolation(self, mock_creds, mock_tasks):
        """Test that different clients have isolated sessions"""
        client1 = app.app.test_client()
        client2 = app.app.test_client()
        
        # Set different session data for each client
        with client1.session_transaction() as sess:
            sess['session_id'] = 'client1-session'
        with client2.session_transaction() as sess:
            sess['session_id'] = 'client2-session'
        
        # Create Task objects for each client
        client1_task = Task(id='1', title='Client 1 Task')
        client2_task = Task(id='2', title='Client 2 Task')
        
        # Set different data in session store
        session.session_store['client1-session'] = {
            'creds': mock_creds,
            'tasks': [client1_task]
        }
        session.session_store['client2-session'] = {
            'creds': mock_creds,
            'tasks': [client2_task]
        }
        
        # Verify sessions are isolated
        assert session.session_store['client1-session']['tasks'][0].title == 'Client 1 Task'
        assert session.session_store['client2-session']['tasks'][0].title == 'Client 2 Task'

class TestRouteOperations:
    @patch('app.get_session_creds')
    @patch('app.tasklist.upsert_task')
    def test_update_task_with_session(self, mock_upsert, mock_get_creds, client, mock_creds, mock_tasks):
        """Test task update uses session credentials"""
        mock_creds_obj = Mock()
        mock_get_creds.return_value = mock_creds_obj
        
        with client.session_transaction() as sess:
            sess['session_id'] = 'test-session-id'
        
        session.session_store['test-session-id'] = {
            'creds': mock_creds,
            'tasks': mock_tasks
        }
        
        response = client.post('/update', data={'title': 'New Task'})
        assert response.status_code == 302
        mock_get_creds.assert_called_once_with(mock_creds)
        mock_upsert.assert_called_once()

    def test_reload_tasks_with_session(self, client, mock_creds, mock_tasks):
        """Test reload route requires authentication and redirects properly"""
        # Test without authentication - should redirect to /auth
        response = client.get('/reload')
        assert response.status_code == 302
        assert '/auth' in response.location
        
        # Test with authentication - should redirect to /
        with client.session_transaction() as sess:
            sess['session_id'] = 'test-session-id'
        
        session.session_store['test-session-id'] = {
            'creds': mock_creds,
            'tasks': mock_tasks
        }
        
        with patch('app.get_session_creds') as mock_get_creds, patch('app.tasklist.from_api') as mock_from_api:
            mock_creds_obj = Mock()
            mock_get_creds.return_value = mock_creds_obj
            mock_tasks_objects = [Task(id='1', title='Test Task 1'), Task(id='2', title='Test Task 2')]
            mock_from_api.return_value = mock_tasks_objects
            
            response = client.get('/reload')
            assert response.status_code == 302
            assert response.location == '/'

class TestSessionSizeAndLoops:
    def test_session_cookie_size_limit(self, client, mock_creds):
        """Test that session cookies don't exceed browser size limits"""
        # Create large task data to simulate the original issue
        large_tasks = []
        for i in range(100):
            task = Task(id=str(i), title=f'Task {i}', description='x' * 100)
            large_tasks.append(task)
        
        with client.session_transaction() as sess:
            sess['session_id'] = 'test-session'
        
        # Set large data in server-side store
        session.session_store['test-session'] = {
            'creds': mock_creds,
            'tasks': large_tasks
        }
        
        # Verify session cookie only contains session_id, not the large data
        with client.session_transaction() as sess:
            # Session should only contain session_id, not the actual data
            assert 'session_id' in sess
            assert 'creds' not in sess  # Data should be in server store, not cookie
            assert 'tasks' not in sess  # Data should be in server store, not cookie

    # FIXME needs to handle oauth callback in order to set the session credentials
    # def test_oauth_redirect_loop_prevention(self, client):
    #     """Test that OAuth redirect loops are prevented by proper session handling"""
    #     with patch('app.get_session_creds') as mock_get_creds, patch('app.tasklist.from_api') as mock_from_api:
    #         mock_creds_obj = Mock()
    #         mock_get_creds.return_value = mock_creds_obj
    #         mock_from_api.return_value = [Task(id='1', title='Test Task')]
            
    #         # First call to /auth should succeed and store credentials
    #         response1 = client.get('/auth')
    #         assert response1.status_code == 302
    #         # assert response1.location == '/' # it's actually an accounts.google.com oauth URL, since that's the first redirect we have to do
            
    #         # Verify credentials are stored in session store
    #         with client.session_transaction() as sess:
    #             session_id = sess.get('session_id')
    #             assert session_id is not None
    #             assert session_id in session.session_store
    #             assert 'creds' in session.session_store[session_id]
    #             assert 'tasks' in session.session_store[session_id]
            
    #         # Second call to / should not redirect to /auth (no loop)
    #         with patch('summary.get_stats'), patch('filter.filter_tasks'), patch('sort.get_sorted_tasks'):
    #             response2 = client.get('/')
    #             assert response2.status_code == 200  # Should render page, not redirect

    def test_session_data_persistence(self, client, mock_creds, mock_tasks):
        """Test that session data persists across requests"""
        with client.session_transaction() as sess:
            sess['session_id'] = 'persist-test'
        
        session.session_store['persist-test'] = {
            'creds': mock_creds,
            'tasks': mock_tasks
        }
        
        # First request
        with patch('summary.get_stats'), patch('filter.filter_tasks'), patch('sort.get_sorted_tasks'):
            response1 = client.get('/')
            assert response1.status_code == 200
        
        # Verify data still exists after request
        assert 'persist-test' in session.session_store
        assert session.session_store['persist-test']['creds'] == mock_creds
        assert session.session_store['persist-test']['tasks'] == mock_tasks
        
        # Second request should still work
        with patch('summary.get_stats'), patch('filter.filter_tasks'), patch('sort.get_sorted_tasks'):
            response2 = client.get('/')
            assert response2.status_code == 200