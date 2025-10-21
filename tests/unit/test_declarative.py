"""
Unit tests for declarative Cribl modules.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add the collection to the Python path (use build directory where modules are generated)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../build'))

from ansible_collections.cribl.core.plugins.module_utils.cribl_declarative import (
    CriblResource,
    create_declarative_module_args
)
from ansible_collections.cribl.core.plugins.module_utils.cribl_api import (
    CriblAPIError
)


class TestCriblResource:
    """Test the base CriblResource class."""

    def test_resource_initialization(self):
        """Test resource initialization."""
        module = Mock()
        client = Mock()
        
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        
        assert resource.module == module
        assert resource.client == client
        assert resource.resource_id == 'test-resource'
        assert resource.endpoint_base == '/system/test'

    def test_resource_differs_no_changes(self):
        """Test needs_update when states are the same."""
        module = Mock()
        client = Mock()
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        
        current = {'id': 'test', 'email': 'test@example.com'}
        desired = {'id': 'test', 'email': 'test@example.com'}
        
        assert resource.needs_update(current, desired) == False

    def test_resource_differs_with_changes(self):
        """Test needs_update when states differ."""
        module = Mock()
        client = Mock()
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        
        current = {'id': 'test', 'email': 'old@example.com'}
        desired = {'id': 'test', 'email': 'new@example.com'}
        
        assert resource.needs_update(current, desired) == True

    def test_resource_differs_missing_field(self):
        """Test needs_update when desired has new field."""
        module = Mock()
        client = Mock()
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        
        current = {'id': 'test'}
        desired = {'id': 'test', 'email': 'new@example.com'}
        
        assert resource.needs_update(current, desired) == True

    def test_ensure_present_creates_new_resource(self):
        """Test ensure_state creates resource when it doesn't exist."""
        module = Mock()
        module.check_mode = False
        client = Mock()
        
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        resource.get_current_state = Mock(return_value=None)
        resource.create_resource = Mock(return_value={'id': 'test-resource', 'email': 'test@example.com'})
        
        desired_state = {'id': 'test-resource', 'email': 'test@example.com'}
        result = resource.ensure_state('present', desired_state)
        
        assert result['changed'] == True
        assert 'Created' in result['msg']
        assert resource.create_resource.called

    def test_ensure_present_idempotent_no_changes(self):
        """Test ensure_state is idempotent when no changes needed."""
        module = Mock()
        module.check_mode = False
        client = Mock()
        
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        current = {'id': 'test-resource', 'email': 'test@example.com'}
        resource.get_current_state = Mock(return_value=current)
        resource.update_resource = Mock()
        
        desired_state = {'id': 'test-resource', 'email': 'test@example.com'}
        result = resource.ensure_state('present', desired_state)
        
        assert result['changed'] == False
        assert 'already in desired state' in result['msg']
        assert not resource.update_resource.called

    def test_ensure_present_updates_when_needed(self):
        """Test ensure_state updates resource when needed."""
        module = Mock()
        module.check_mode = False
        client = Mock()
        
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        current = {'id': 'test-resource', 'email': 'old@example.com'}
        resource.get_current_state = Mock(return_value=current)
        resource.update_resource = Mock(return_value={'id': 'test-resource', 'email': 'new@example.com'})
        
        desired_state = {'id': 'test-resource', 'email': 'new@example.com'}
        result = resource.ensure_state('present', desired_state)
        
        assert result['changed'] == True
        assert 'Updated' in result['msg']
        assert resource.update_resource.called

    def test_ensure_present_check_mode_create(self):
        """Test ensure_state in check mode when creating."""
        module = Mock()
        module.check_mode = True
        client = Mock()
        
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        resource.get_current_state = Mock(return_value=None)
        resource.create_resource = Mock()
        
        desired_state = {'id': 'test-resource', 'email': 'test@example.com'}
        result = resource.ensure_state('present', desired_state)
        
        assert result['changed'] == True
        assert 'Would create' in result['msg']
        assert not resource.create_resource.called

    def test_ensure_present_check_mode_update(self):
        """Test ensure_state in check mode when updating."""
        module = Mock()
        module.check_mode = True
        client = Mock()
        
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        current = {'id': 'test-resource', 'email': 'old@example.com'}
        resource.get_current_state = Mock(return_value=current)
        resource.update_resource = Mock()
        
        desired_state = {'id': 'test-resource', 'email': 'new@example.com'}
        result = resource.ensure_state('present', desired_state)
        
        assert result['changed'] == True
        assert 'Would update' in result['msg']
        assert not resource.update_resource.called

    def test_ensure_absent_deletes_resource(self):
        """Test ensure_state with absent deletes existing resource."""
        module = Mock()
        module.check_mode = False
        client = Mock()
        
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        current = {'id': 'test-resource'}
        resource.get_current_state = Mock(return_value=current)
        resource.delete_resource = Mock()
        
        result = resource.ensure_state('absent')
        
        assert result['changed'] == True
        assert 'Deleted' in result['msg']
        assert resource.delete_resource.called

    def test_ensure_absent_idempotent(self):
        """Test ensure_state with absent is idempotent when resource doesn't exist."""
        module = Mock()
        module.check_mode = False
        client = Mock()
        
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        resource.get_current_state = Mock(return_value=None)
        resource.delete_resource = Mock()
        
        result = resource.ensure_state('absent')
        
        assert result['changed'] == False
        assert 'already absent' in result['msg']
        assert not resource.delete_resource.called

    def test_ensure_absent_check_mode(self):
        """Test ensure_state with absent in check mode."""
        module = Mock()
        module.check_mode = True
        client = Mock()
        
        resource = CriblResource(module, client, 'test-resource', '/system/test')
        current = {'id': 'test-resource'}
        resource.get_current_state = Mock(return_value=current)
        resource.delete_resource = Mock()
        
        result = resource.ensure_state('absent')
        
        assert result['changed'] == True
        assert 'Would delete' in result['msg']
        assert not resource.delete_resource.called


@pytest.mark.skip(reason="CriblUser class no longer exists in generated code")
class TestCriblUser:
    """Test the CriblUser declarative resource."""

    def test_user_initialization(self):
        """Test user resource initialization."""
        module = Mock()
        client = Mock()
        
        user = CriblUser(module, client, 'test_user')
        
        assert user.user_id == 'test_user'

    def test_get_current_state_exists(self):
        """Test getting current state when user exists."""
        module = Mock()
        client = Mock()
        client.get = Mock(return_value={'id': 'test_user', 'email': 'test@example.com'})
        
        user = CriblUser(module, client, 'test_user')
        state = user.get_current_state()
        
        assert state['id'] == 'test_user'
        assert state['email'] == 'test@example.com'
        client.get.assert_called_with('/system/users/test_user')

    def test_get_current_state_not_found(self):
        """Test getting current state when user doesn't exist."""
        module = Mock()
        client = Mock()
        client.get = Mock(side_effect=CriblAPIError("404 Not Found"))
        
        user = CriblUser(module, client, 'test_user')
        state = user.get_current_state()
        
        assert state is None

    def test_create_resource(self):
        """Test creating user resource."""
        module = Mock()
        client = Mock()
        client.post = Mock(return_value={'id': 'test_user'})
        
        user = CriblUser(module, client, 'test_user')
        desired_state = {'id': 'test_user', 'email': 'test@example.com'}
        result = user.create_resource(desired_state)
        
        assert result['id'] == 'test_user'
        client.post.assert_called_with('/system/users', data=desired_state)

    def test_update_resource(self):
        """Test updating user resource."""
        module = Mock()
        client = Mock()
        client.patch = Mock(return_value={'id': 'test_user', 'email': 'new@example.com'})
        
        user = CriblUser(module, client, 'test_user')
        current_state = {'id': 'test_user', 'email': 'old@example.com'}
        desired_state = {'email': 'new@example.com'}
        result = user.update_resource(current_state, desired_state)
        
        assert result['email'] == 'new@example.com'
        client.patch.assert_called_with('/system/users/test_user', data=desired_state)

    def test_delete_resource(self):
        """Test deleting user resource."""
        module = Mock()
        client = Mock()
        client.delete = Mock(return_value={})
        
        user = CriblUser(module, client, 'test_user')
        current_state = {'id': 'test_user'}
        result = user.delete_resource(current_state)
        
        client.delete.assert_called_with('/system/users/test_user')


@pytest.mark.skip(reason="CriblWorkerGroup class no longer exists in generated code")
class TestCriblWorkerGroup:
    """Test the CriblWorkerGroup declarative resource."""

    def test_worker_group_initialization(self):
        """Test worker group resource initialization."""
        module = Mock()
        client = Mock()
        
        group = CriblWorkerGroup(module, client, 'test_group')
        
        assert group.group_id == 'test_group'

    def test_get_current_state_exists(self):
        """Test getting current state when worker group exists."""
        module = Mock()
        client = Mock()
        client.get = Mock(return_value={'id': 'test_group', 'description': 'Test'})
        
        group = CriblWorkerGroup(module, client, 'test_group')
        state = group.get_current_state()
        
        assert state['id'] == 'test_group'
        client.get.assert_called_with('/master/groups/test_group')

    def test_create_resource(self):
        """Test creating worker group resource."""
        module = Mock()
        client = Mock()
        client.post = Mock(return_value={'id': 'test_group'})
        
        group = CriblWorkerGroup(module, client, 'test_group')
        desired_state = {'id': 'test_group', 'description': 'Test Group'}
        result = group.create_resource(desired_state)
        
        assert result['id'] == 'test_group'
        client.post.assert_called_with('/master/groups', data=desired_state)


class TestDeclarativeModuleArgs:
    """Test declarative module argument creation."""

    def test_create_declarative_module_args(self):
        """Test creating common declarative module arguments."""
        args = create_declarative_module_args()
        
        assert 'base_url' in args
        assert 'username' in args
        assert 'password' in args
        assert 'token' in args
        assert 'validate_certs' in args
        assert 'timeout' in args
        assert 'state' in args
        
        assert args['state']['default'] == 'present'
        assert args['state']['choices'] == ['present', 'absent']
        assert args['validate_certs']['default'] == False
        assert args['timeout']['default'] == 30


@pytest.mark.integration
class TestDeclarativeIntegration:
    """Integration tests for declarative modules (requires running Cribl instance)."""

    @pytest.fixture
    def mock_module(self):
        """Create a mock Ansible module."""
        module = Mock()
        module.check_mode = False
        module.params = {
            'base_url': 'https://cribl.example.com',
            'token': 'test_token',
            'validate_certs': False,
            'timeout': 30
        }
        return module

    @pytest.mark.skip(reason="CriblUser class no longer exists in generated code")
    def test_full_lifecycle_user(self, mock_module):
        """Test full lifecycle: create, update, delete (mocked)."""
        client = Mock()
        
        # Mock API responses
        client.get = Mock(side_effect=[
            CriblAPIError("404"),  # First call - doesn't exist
            {'id': 'test', 'email': 'test@example.com'},  # Second call - exists
            {'id': 'test', 'email': 'test@example.com'},  # Third call - check unchanged
            {'id': 'test', 'email': 'test@example.com'},  # Fourth call - before delete
        ])
        client.post = Mock(return_value={'id': 'test', 'email': 'test@example.com'})
        client.delete = Mock(return_value={})
        
        user = CriblUser(mock_module, client, 'test')
        
        # 1. Create
        result = user.ensure_present({'id': 'test', 'email': 'test@example.com'})
        assert result['changed'] == True
        assert result['msg'] == 'Resource created'
        
        # 2. No changes needed (idempotent)
        result = user.ensure_present({'id': 'test', 'email': 'test@example.com'})
        assert result['changed'] == False
        assert result['msg'] == 'Resource already in desired state'
        
        # 3. Delete
        result = user.ensure_absent()
        assert result['changed'] == True
        assert result['msg'] == 'Resource deleted'

