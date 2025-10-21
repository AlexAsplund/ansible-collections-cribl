"""Unit tests for module utilities."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the module_utils to path (use build directory where modules are generated)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "build" / "ansible_collections" / "cribl" / "core" / "plugins" / "module_utils"))
from cribl_api import CriblAPIClient, CriblAPIError


@pytest.mark.unit
class TestCriblAPIClient:
    """Test the Cribl API client."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = CriblAPIClient(
            base_url="https://test.cribl.com",
            username="test",
            password="pass",
            validate_certs=False
        )
        
        assert client.base_url == "https://test.cribl.com"
        assert client.username == "test"
        assert client.password == "pass"
        assert client.validate_certs is False
        assert client.timeout == 30

    def test_base_url_trailing_slash(self):
        """Test that trailing slashes are removed from base_url."""
        client = CriblAPIClient(
            base_url="https://test.cribl.com/",
            username="test",
            password="pass"
        )
        
        assert client.base_url == "https://test.cribl.com"

    def test_login_success(self):
        """Test successful login."""
        client = CriblAPIClient(
            base_url="https://test.cribl.com",
            username="admin",
            password="password"
        )
        
        # Mock the http_session.post method
        with patch.object(client.http_session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test_token_123"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = client.login()
            
            # login() returns a CriblSession object, not a dict
            assert result.token == "test_token_123"
            assert client.token == "test_token_123"
            mock_post.assert_called_once()

    def test_login_failure(self):
        """Test login failure."""
        from requests.exceptions import HTTPError
        
        client = CriblAPIClient(
            base_url="https://test.cribl.com",
            username="admin",
            password="wrongpassword"
        )
        
        # Mock the http_session.post method
        with patch.object(client.http_session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_response.raise_for_status.side_effect = HTTPError("401 Unauthorized")
            mock_post.return_value = mock_response
            
            with pytest.raises(CriblAPIError):
                client.login()

    def test_login_without_credentials(self):
        """Test login without credentials raises error."""
        client = CriblAPIClient(
            base_url="https://test.cribl.com",
            token="existing_token"
        )
        
        with pytest.raises(CriblAPIError, match="Username and password required for login"):
            client.login()

    def test_get_request(self):
        """Test GET request."""
        client = CriblAPIClient(
            base_url="https://test.cribl.com",
            token="test_token"
        )
        
        # Mock the http_session.request method
        with patch.object(client.http_session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"items": [], "count": 0}
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response
            
            result = client.get("/system/users")
            
            assert result["count"] == 0
            assert result["items"] == []

    def test_post_request(self):
        """Test POST request."""
        client = CriblAPIClient(
            base_url="https://test.cribl.com",
            token="test_token"
        )
        
        # Mock the http_session.request method
        with patch.object(client.http_session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "new_user", "email": "test@example.com"}
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response
            
            data = {"id": "new_user", "email": "test@example.com"}
            result = client.post("/system/users", data=data)
            
            assert result["id"] == "new_user"
            assert result["email"] == "test@example.com"

    def test_delete_request(self):
        """Test DELETE request."""
        client = CriblAPIClient(
            base_url="https://test.cribl.com",
            token="test_token"
        )
        
        # Mock the http_session.request method
        with patch.object(client.http_session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response
            
            result = client.delete("/system/users/test_user")
            
            assert result == {}

    def test_request_without_token(self):
        """Test request automatically logs in when token not available."""
        client = CriblAPIClient(
            base_url="https://test.cribl.com",
            username="admin",
            password="password"
        )
        
        call_count = {'post': 0, 'request': 0}
        
        def mock_post_side_effect(*args, **kwargs):
            call_count['post'] += 1
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "auto_token"}
            mock_response.raise_for_status = Mock()
            return mock_response
            
        def mock_request_side_effect(*args, **kwargs):
            call_count['request'] += 1
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"items": []}
            mock_response.raise_for_status = Mock()
            return mock_response
        
        # Mock both post (for login) and request (for get)
        with patch.object(client.http_session, 'post', side_effect=mock_post_side_effect):
            with patch.object(client.http_session, 'request', side_effect=mock_request_side_effect):
                # Should automatically login and get token
                client.get("/system/users")
                
                # Verify login was called
                assert call_count['post'] == 1
                assert call_count['request'] == 1

