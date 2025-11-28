#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Declarative base classes for Cribl Ansible modules.

Provides generic base classes for creating idempotent, state-based Cribl resource modules.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# Import from the local cribl_api module (relative import works across collections)
from .cribl_api import CriblAPIClient, CriblAPIError


class CriblResource:
    """Base class for declarative Cribl resources."""
    
    def __init__(self, module, client, resource_id, endpoint_base):
        """
        Initialize a declarative Cribl resource.
        
        Args:
            module: Ansible module instance
            client: CriblAPIClient instance
            resource_id: Resource identifier
            endpoint_base: Base API endpoint (e.g., '/system/users')
        """
        self.module = module
        self.client = client
        self.resource_id = resource_id
        self.endpoint_base = endpoint_base.rstrip('/')
    
    def get_current_state(self):
        """
        Get the current state of the resource.
        
        Returns:
            dict: Current resource state, or None if doesn't exist
        """
        endpoint = f"{self.endpoint_base}/{self.resource_id}"
        try:
            response = self.client.get(endpoint)
            
            # Cribl API returns list structure: {"count": N, "items": [...]}
            # When resource doesn't exist, returns {"count": 0, "items": []}
            if isinstance(response, dict):
                if 'items' in response:
                    items = response.get('items', [])
                    count = response.get('count', 0)
                    
                    # Check if no items exist
                    if count == 0 or not items or len(items) == 0:
                        return None
                    
                    # Return first (and should be only) item
                    return items[0]
                elif 'count' in response and response.get('count', 0) == 0:
                    return None
            
            # If response doesn't have items structure, return it as-is
            # (some endpoints may return the resource directly)
            return response
        except CriblAPIError as e:
            error_str = str(e)
            
            # Check for 404 or not found errors - these indicate resource doesn't exist
            if "404" in error_str:
                return None
            if any(phrase in error_str.lower() for phrase in ["not found", "item not found", "does not exist", "entity with"]):
                # "entity with" catches "Entity with ID does not exist" messages
                # But NOT "already exists" which indicates resource DOES exist
                if "already exists" not in error_str.lower():
                    return None
            
            # For any other error, re-raise it (don't assume resource doesn't exist)
            # Include the endpoint in the error for debugging
            raise CriblAPIError(f"Failed to get current state from {endpoint}: {error_str}")
        except Exception as e:
            # Catch any other exception and re-raise with context
            raise CriblAPIError(f"Failed to get current state from {endpoint}: {str(e)}")
    
    def create_resource(self, desired_state):
        """
        Create a new resource.
        
        Args:
            desired_state: Desired resource configuration
            
        Returns:
            dict: Created resource data
        """
        response = self.client.post(self.endpoint_base, data=desired_state)
        return response
    
    def update_resource(self, current_state, desired_state, method='PATCH'):
        """
        Update an existing resource.
        
        Args:
            current_state: Current resource state
            desired_state: Desired resource state
            method: HTTP method to use ('PATCH' or 'PUT')
            
        Returns:
            dict: Updated resource data
        """
        endpoint = f"{self.endpoint_base}/{self.resource_id}"
        if method.upper() == 'PUT':
            response = self.client.put(endpoint, data=desired_state)
        else:
            response = self.client.patch(endpoint, data=desired_state)
        return response
    
    def delete_resource(self, current_state):
        """
        Delete a resource.
        
        Args:
            current_state: Current resource state
            
        Returns:
            dict: Delete response
        """
        endpoint = f"{self.endpoint_base}/{self.resource_id}"
        response = self.client.delete(endpoint)
        return response
    
    def needs_update(self, current_state, desired_state):
        """
        Check if resource needs to be updated.
        
        Args:
            current_state: Current resource state
            desired_state: Desired resource state
            
        Returns:
            bool: True if update is needed
        """
        # Compare relevant fields (exclude metadata)
        for key, value in desired_state.items():
            if key in ['id', 'createdAt', 'updatedAt', 'version']:
                continue
            
            if key not in current_state:
                return True
            
            if current_state[key] != value:
                return True
        
        return False
    
    def ensure_state(self, state, desired_state=None, update_method='PATCH'):
        """
        Ensure resource is in desired state.
        
        Args:
            state: Desired state ('present' or 'absent')
            desired_state: Desired resource configuration (for 'present')
            update_method: HTTP method for updates ('PATCH' or 'PUT')
            
        Returns:
            dict: Result with changed, msg, and resource keys
        """
        current_state = self.get_current_state()
        
        if state == 'present':
            if desired_state is None:
                desired_state = {'id': self.resource_id}
            
            if current_state is None:
                # Resource doesn't exist - create it
                if self.module.check_mode:
                    return {
                        'changed': True,
                        'msg': f'Would create {self.resource_id}',
                        'resource': desired_state
                    }
                
                try:
                    resource = self.create_resource(desired_state)
                    return {
                        'changed': True,
                        'msg': f'Created {self.resource_id}',
                        'resource': resource
                    }
                except CriblAPIError as e:
                    self.module.fail_json(msg=f'Failed to create {self.resource_id}: {str(e)}')
            
            else:
                # Resource exists - check if update needed
                if self.needs_update(current_state, desired_state):
                    if self.module.check_mode:
                        return {
                            'changed': True,
                            'msg': f'Would update {self.resource_id}',
                            'resource': desired_state,
                            'diff': {
                                'before': current_state,
                                'after': desired_state
                            }
                        }
                    
                    try:
                        resource = self.update_resource(current_state, desired_state, update_method)
                        return {
                            'changed': True,
                            'msg': f'Updated {self.resource_id}',
                            'resource': resource
                        }
                    except CriblAPIError as e:
                        self.module.fail_json(msg=f'Failed to update {self.resource_id}: {str(e)}')
                
                else:
                    # No changes needed
                    return {
                        'changed': False,
                        'msg': f'{self.resource_id} already in desired state',
                        'resource': current_state
                    }
        
        elif state == 'absent':
            if current_state is None:
                # Resource doesn't exist - nothing to do
                return {
                    'changed': False,
                    'msg': f'{self.resource_id} already absent'
                }
            
            else:
                # Resource exists - delete it
                if self.module.check_mode:
                    return {
                        'changed': True,
                        'msg': f'Would delete {self.resource_id}'
                    }
                
                try:
                    self.delete_resource(current_state)
                    return {
                        'changed': True,
                        'msg': f'Deleted {self.resource_id}'
                    }
                except CriblAPIError as e:
                    self.module.fail_json(msg=f'Failed to delete {self.resource_id}: {str(e)}')


def create_declarative_module_args():
    """
    Create common argument spec for declarative modules.
    
    Returns:
        dict: Argument specification
    """
    return dict(
        session=dict(type='dict', required=False),
        base_url=dict(type='str', required=False),
        token=dict(type='str', required=False, no_log=True),
        validate_certs=dict(type='bool', default=False),
        timeout=dict(type='int', default=30),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

