import pytest
from unittest.mock import Mock, patch
import api

@pytest.fixture(autouse=True)
def clear_oauth_flows():
    """Clear oauth flows before each test"""
    api._oauth_flows.clear()
    yield
    api._oauth_flows.clear()

class TestOAuthFlow:
    @patch('api.Flow.from_client_secrets_file')
    def test_get_session_creds_returns_auth_url_for_new_auth(self, mock_flow_class):
        """Test that get_session_creds returns auth URL when new authentication is needed"""
        mock_flow = Mock()
        mock_flow_class.return_value = mock_flow
        mock_flow.authorization_url.return_value = ('https://accounts.google.com/oauth2/auth', 'test-state')
        
        result = api.get_session_creds()
        
        assert isinstance(result, dict)
        assert 'auth_url' in result
        assert 'state' in result
        assert result['auth_url'] == 'https://accounts.google.com/oauth2/auth'
        assert result['state'] == 'test-state'
        # Verify flow is stored in module storage
        assert api._oauth_flows['test-state'] == mock_flow
        
        # Verify flow was created with correct parameters
        mock_flow_class.assert_called_once_with(
            "credentials.json",
            scopes=api.SCOPES,
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
        
        result = api.get_session_creds(existing_creds)
        
        assert result == mock_creds
        mock_from_info.assert_called_once_with(existing_creds, api.SCOPES)

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
        
        result = api.get_session_creds(existing_creds)
        
        assert result == mock_creds
        mock_creds.refresh.assert_called_once()

    def test_complete_oauth_flow(self):
        """Test complete_oauth_flow function"""
        mock_flow = Mock()
        mock_creds = Mock()
        mock_flow.credentials = mock_creds
        
        # Store flow in the module's flow storage
        state = 'test-state'
        api._oauth_flows[state] = mock_flow
        
        authorization_response = 'https://localhost:5001/oauth/callback?code=auth-code&state=test-state'
        
        result = api.complete_oauth_flow(state, authorization_response)
        
        assert result == mock_creds
        mock_flow.fetch_token.assert_called_once_with(authorization_response=authorization_response)
        
        # Verify flow is removed from storage after use
        assert state not in api._oauth_flows

    def test_complete_oauth_flow_invalid_state(self):
        """Test complete_oauth_flow with invalid state"""
        with pytest.raises(ValueError, match="OAuth flow not found for state"):
            api.complete_oauth_flow('invalid-state', 'some-response')