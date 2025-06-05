import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import session
from flask import Flask

@pytest.fixture
def app():
    """Create a test Flask app"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-key'
    return app

@pytest.fixture
def client(app):
    """Create a test client"""
    # Clear session store before each test
    session.session_store.clear()
    with app.test_client() as client:
        yield client

class TestSessionStore:
    def test_session_store_initialization(self):
        """Test that session store is properly initialized"""
        assert isinstance(session.session_store, dict)

    def test_session_store_clear(self):
        """Test that session store can be cleared"""
        session.session_store['test'] = {'data': 'value'}
        assert 'test' in session.session_store
        session.session_store.clear()
        assert len(session.session_store) == 0

class TestSessionFunctions:
    def test_get_session_id_creates_new_id(self, client):
        """Test that get_session_id creates a new session ID when none exists"""
        with client.application.test_request_context():
            session_id = session.get_session_id()
            assert session_id is not None

    def test_get_session_id_returns_existing_id(self, client):
        """Test that get_session_id returns existing session ID"""
        existing_id = 'test-session-id'
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = existing_id
            session_id = session.get_session_id()
            assert session_id == existing_id

    def test_get_user_data_with_default(self, client):
        """Test getting user data with default value when no data exists"""
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'test-session'
            result = session.get_user_data('nonexistent_key', 'default_value')
            assert result == 'default_value'

    def test_get_user_data_without_default(self, client):
        """Test getting user data without default value when no data exists"""
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'test-session'
            result = session.get_user_data('nonexistent_key')
            assert result is None

    def test_set_and_get_user_data(self, client):
        """Test setting and getting user data"""
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'test-session'
            session.set_user_data('test_key', 'test_value')
            result = session.get_user_data('test_key')
            assert result == 'test_value'

    def test_set_user_data_creates_session_entry(self, client):
        """Test that setting user data creates session store entry"""
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'test-session'
            session.set_user_data('test_key', 'test_value')
            assert 'test-session' in session.session_store
            assert session.session_store['test-session']['test_key'] == 'test_value'

    def test_clear_user_data(self, client):
        """Test clearing user data"""
        # Set some data first
        session.session_store['test-session'] = {'test_key': 'test_value'}
        
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'test-session'
            session.clear_user_data()
            assert 'test-session' not in session.session_store
            assert len(flask_session) == 0

    def test_session_isolation(self, client):
        """Test that different sessions are isolated"""
        # Set up two different sessions
        session.session_store['session1'] = {'key': 'value1'}
        session.session_store['session2'] = {'key': 'value2'}
        
        # Verify they are isolated
        assert session.session_store['session1']['key'] == 'value1'
        assert session.session_store['session2']['key'] == 'value2'
        
        # Modify one session
        session.session_store['session1']['key'] = 'modified'
        assert session.session_store['session1']['key'] == 'modified'
        assert session.session_store['session2']['key'] == 'value2'

class TestRequireAuthDecorator:
    def test_require_auth_with_valid_session(self, client):
        """Test require_auth decorator allows access with valid credentials and tasks"""
        @session.require_auth
        def test_route():
            return 'success'
        
        with client.session_transaction() as sess:
            sess['session_id'] = 'test-session'
        
        # Set valid session data
        session.session_store['test-session'] = {
            'creds': {'token': 'valid_token'},
            'tasks': [{'id': '1', 'title': 'Test Task'}]
        }
        
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'test-session'
            result = test_route()
            assert result == 'success'

    def test_require_auth_without_creds(self, client):
        """Test require_auth decorator redirects when no credentials"""
        @session.require_auth
        def test_route():
            return 'success'
        
        with client.session_transaction() as sess:
            sess['session_id'] = 'test-session'
        
        # Set session data without creds
        session.session_store['test-session'] = {
            'tasks': [{'id': '1', 'title': 'Test Task'}]
        }
        
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'test-session'
            result = test_route()
            # Should redirect to /auth
            assert result.status_code == 302
            assert '/auth' in result.location

    def test_require_auth_without_tasks(self, client):
        """Test require_auth decorator redirects when no tasks"""
        @session.require_auth
        def test_route():
            return 'success'
        
        with client.session_transaction() as sess:
            sess['session_id'] = 'test-session'
        
        # Set session data without tasks
        session.session_store['test-session'] = {
            'creds': {'token': 'valid_token'}
        }
        
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'test-session'
            result = test_route()
            # Should redirect to /auth
            assert result.status_code == 302
            assert '/auth' in result.location

    def test_require_auth_without_session_data(self, client):
        """Test require_auth decorator redirects when no session data exists"""
        @session.require_auth
        def test_route():
            return 'success'
        
        with client.session_transaction() as sess:
            sess['session_id'] = 'test-session'
        
        # No session data set
        
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'test-session'
            result = test_route()
            # Should redirect to /auth
            assert result.status_code == 302
            assert '/auth' in result.location

class TestSessionDataPersistence:
    def test_data_persists_across_function_calls(self, client):
        """Test that session data persists across multiple function calls"""
        with client.session_transaction() as sess:
            sess['session_id'] = 'persist-test'
        
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'persist-test'
            # Set data
            session.set_user_data('persistent_key', 'persistent_value')
            
            # Get data in same context
            result1 = session.get_user_data('persistent_key')
            assert result1 == 'persistent_value'
        
        # Get data in new context
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'persist-test'
            result2 = session.get_user_data('persistent_key')
            assert result2 == 'persistent_value'

    def test_multiple_keys_in_session(self, client):
        """Test storing multiple keys in the same session"""
        with client.session_transaction() as sess:
            sess['session_id'] = 'multi-key-test'
        
        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session['session_id'] = 'multi-key-test'
            session.set_user_data('key1', 'value1')
            session.set_user_data('key2', 'value2')
            session.set_user_data('key3', {'nested': 'object'})
            
            assert session.get_user_data('key1') == 'value1'
            assert session.get_user_data('key2') == 'value2'
            assert session.get_user_data('key3') == {'nested': 'object'}
            
            # Verify all keys exist in session store
            assert 'multi-key-test' in session.session_store
            session_data = session.session_store['multi-key-test']
            assert len(session_data) == 3
            assert 'key1' in session_data
            assert 'key2' in session_data
            assert 'key3' in session_data