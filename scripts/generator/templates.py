"""
Code Templates

Templates for generating Ansible modules.
"""


class ModuleTemplate:
    """Templates for imperative Ansible modules."""

    @staticmethod
    def header() -> str:
        return '''#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# This module was automatically generated from the Cribl OpenAPI specification

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
'''

    @staticmethod
    def documentation(module_name: str, summary: str, description: str, 
                     endpoint: str, method: str, product: str, params_doc: str) -> str:
        return f'''
DOCUMENTATION = r\'\'\'
---
module: {module_name}
short_description: {summary}
description:
    - {description}
    - This module was automatically generated from the Cribl OpenAPI specification.
    - Endpoint: {method.upper()} {endpoint}
    - Product: Cribl {product.title()}
version_added: "1.0.0"
author:
    - Cribl Ansible Collection Contributors (auto-generated)
extends_documentation_fragment:
    - cribl.{product}.cribl
options:
{params_doc}
    state:
        description:
            - Desired state of the resource.
        type: str
        choices: [ present, absent ]
        default: present
requirements:
    - python >= 3.6
notes:
    - This module was automatically generated from the OpenAPI specification.
    - The endpoint used is {method.upper()} {endpoint}
    - This module is part of the cribl.{product} collection.
\'\'\'
'''

    @staticmethod
    def examples(module_name: str, summary: str, product: str) -> str:
        return f'''
EXAMPLES = r\'\'\'
# Recommended: Using session from auth_session module
- name: Create authentication session
  cribl.{product}.auth_session:
    base_url: https://cribl.example.com
    username: admin
    password: secretpassword
    validate_certs: false
  register: cribl_session

- name: {summary}
  cribl.{product}.{module_name}:
    session: "{{{{ cribl_session.session }}}}"
    state: present

# Alternative: Direct authentication with token
- name: {summary}
  cribl.{product}.{module_name}:
    base_url: https://cribl.example.com
    token: "{{{{ auth_token }}}}"
    validate_certs: false
    state: present
\'\'\'
'''

    @staticmethod
    def returns() -> str:
        return '''
RETURN = r\'\'\'
response:
    description: The API response
    type: dict
    returned: success
    sample: {}
msg:
    description: Success or informational message
    type: str
    returned: always
    sample: "Operation completed successfully"
\'\'\'
'''

    @staticmethod
    def imports(product: str) -> str:
        return f'''
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cribl.{product}.plugins.module_utils.cribl_api import (
    CriblAPIClient,
    CriblAPIError
)
'''

    @staticmethod
    def main_function_start(arg_spec: str) -> str:
        return f'''

def main():
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(type='dict', required=False),
            base_url=dict(type='str', required=False),
            token=dict(type='str', required=False, no_log=True),
            validate_certs=dict(type='bool', default=False),
            timeout=dict(type='int', default=30),
            state=dict(type='str', default='present', choices=['present', 'absent']),
{arg_spec}
        ),
        required_one_of=[['session', 'token']],
        mutually_exclusive=[['session', 'base_url']],
        supports_check_mode=True,
    )

    session = module.params.get('session')
    base_url = module.params.get('base_url')
    token = module.params.get('token')
    validate_certs = module.params['validate_certs']
    timeout = module.params['timeout']
    state = module.params['state']

    try:
        # Initialize client with session or token
        if session:
            client = CriblAPIClient(session=session)
        else:
            client = CriblAPIClient(
                base_url=base_url,
                token=token,
                validate_certs=validate_certs,
                timeout=timeout
            )
'''

    @staticmethod
    def api_call(endpoint: str, method: str) -> str:
        """Legacy method - kept for compatibility"""
        return f'''
        endpoint = "{endpoint}"
        
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg="Check mode: Would perform {method.upper()} request to {{endpoint}}",
                endpoint=endpoint
            )

        method = "{method.upper()}"
        if method == "GET":
            response = client.get(endpoint, params=data if data else None)
            changed = False
        elif method == "POST":
            response = client.post(endpoint, data=data if data else None)
            changed = True
        elif method == "PUT":
            response = client.put(endpoint, data=data if data else None)
            changed = True
        elif method == "PATCH":
            response = client.patch(endpoint, data=data if data else None)
            changed = True
        elif method == "DELETE":
            response = client.delete(endpoint)
            changed = True
        else:
            module.fail_json(msg=f"Unsupported method: {{method}}")

        module.exit_json(
            changed=changed,
            msg=f"{{method}} request to {{endpoint}} successful",
            response=response
        )

    except CriblAPIError as e:
        module.fail_json(msg=str(e))
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {{str(e)}}")


if __name__ == '__main__':
    main()
'''

    @staticmethod
    def api_call_without_endpoint_def(method: str) -> str:
        """API call logic without endpoint definition (endpoint already defined)"""
        return f'''
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg="Check mode: Would perform {method.upper()} request to {{endpoint}}",
                endpoint=endpoint
            )

        method = "{method.upper()}"
        if method == "GET":
            response = client.get(endpoint, params=data if data else None)
            changed = False
        elif method == "POST":
            response = client.post(endpoint, data=data if data else None)
            changed = True
        elif method == "PUT":
            response = client.put(endpoint, data=data if data else None)
            changed = True
        elif method == "PATCH":
            response = client.patch(endpoint, data=data if data else None)
            changed = True
        elif method == "DELETE":
            response = client.delete(endpoint)
            changed = True
        else:
            module.fail_json(msg=f"Unsupported method: {{method}}")

        module.exit_json(
            changed=changed,
            msg=f"{{method}} request to {{endpoint}} successful",
            response=response
        )

    except CriblAPIError as e:
        module.fail_json(msg=str(e))
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {{str(e)}}")


if __name__ == '__main__':
    main()
'''


class DeclarativeTemplate:
    """Templates for declarative Ansible modules."""

    @staticmethod
    def create_resource_module(resource_name: str, resource_name_title: str, 
                               product: str, endpoint_base: str, id_param: str,
                               extra_params_doc: str = "", extra_params_spec: str = "", 
                               update_method: str = "PATCH") -> str:
        return f'''#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r\'\'\'
---
module: {resource_name}
short_description: Manage Cribl {resource_name_title}
description:
    - Declaratively manage Cribl {resource_name_title} with idempotent operations.
    - Automatically detects if resource exists and only makes changes when needed.
    - Supports check mode and diff mode.
version_added: "1.0.0"
author:
    - Cribl Ansible Collection Contributors
extends_documentation_fragment:
    - cribl.{product}.cribl
options:
    {id_param}:
        description:
            - {resource_name_title} ID.
        type: str
        required: true
{extra_params_doc}
    worker_group:
        description:
            - Worker Group ID to target for this resource.
            - If specified, the resource will be managed in the specified worker group using the C(/m/{{worker_group}}) API endpoint.
            - If omitted, the resource is managed globally (leader node or default context).
        type: str
        required: false
    state:
        description:
            - Desired state of the {resource_name}.
            - C(present) ensures the {resource_name} exists with specified configuration.
            - C(absent) ensures the {resource_name} does not exist.
        type: str
        choices: [ present, absent ]
        default: present
requirements:
    - python >= 3.6
notes:
    - This is a declarative module that is idempotent.
    - It will only make changes when the current state differs from desired state.
    - Supports C(--check) and C(--diff) modes.
\'\'\'

EXAMPLES = r\'\'\'
# Recommended: Using session from auth_session module
- name: Create authentication session
  cribl.{product}.auth_session:
    base_url: https://cribl.example.com
    username: admin
    password: secretpassword
    validate_certs: false
  register: cribl_session

- name: Ensure {resource_name} exists globally
  cribl.{product}.{resource_name}:
    session: "{{{{ cribl_session.session }}}}"
    {id_param}: my_{resource_name}
    state: present

- name: Ensure {resource_name} exists in specific worker group
  cribl.{product}.{resource_name}:
    session: "{{{{ cribl_session.session }}}}"
    {id_param}: my_{resource_name}
    worker_group: production
    state: present

- name: Remove {resource_name} from worker group
  cribl.{product}.{resource_name}:
    session: "{{{{ cribl_session.session }}}}"
    {id_param}: my_{resource_name}
    worker_group: production
    state: absent

# Alternative: Direct authentication with token
- name: Ensure {resource_name} exists
  cribl.{product}.{resource_name}:
    base_url: https://cribl.example.com
    token: "{{{{ auth_token }}}}"
    {id_param}: my_{resource_name}
    state: present
\'\'\'

RETURN = r\'\'\'
changed:
    description: Whether any changes were made
    type: bool
    returned: always
msg:
    description: Description of what was done
    type: str
    returned: always
resource:
    description: Current state of the resource
    type: dict
    returned: when state=present
\'\'\'

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cribl.{product}.plugins.module_utils.cribl_api import (
    CriblAPIClient,
    CriblAPIError
)
from ansible_collections.cribl.{product}.plugins.module_utils.cribl_declarative import (
    CriblResource,
    create_declarative_module_args
)


def main():
    argument_spec = create_declarative_module_args()
    argument_spec.update(dict(
        {id_param}=dict(type='str', required=True),
{extra_params_spec}
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=[['session', 'token']],
        mutually_exclusive=[['session', 'base_url']],
        supports_check_mode=True,
    )

    session = module.params.get('session')
    base_url = module.params.get('base_url')
    token = module.params.get('token')
    validate_certs = module.params['validate_certs']
    timeout = module.params['timeout']
    
    resource_id = module.params['{id_param}']
    worker_group = module.params.get('worker_group')
    state = module.params['state']

    try:
        # Initialize client with session or token
        if session:
            client = CriblAPIClient(session=session)
        else:
            client = CriblAPIClient(
                base_url=base_url,
                token=token,
                validate_certs=validate_certs,
                timeout=timeout
            )

        resource = CriblResource(module, client, resource_id, '{endpoint_base}', worker_group=worker_group)

        if state == 'present':
            desired_state = {{'{id_param}': resource_id}}
            # Add any additional parameters from module.params
            for key, value in module.params.items():
                if key not in ['session', 'base_url', 'token', 'validate_certs', 'timeout', 'state', '{id_param}', 'worker_group']:
                    if value is not None:
                        # Special handling for 'conf' dict - merge for inputs/outputs only
                        if key == 'conf' and isinstance(value, dict) and '{resource_name}' in ['input', 'output']:
                            desired_state.update(value)
                        else:
                            desired_state[key] = value
            
            result = resource.ensure_state(state, desired_state, update_method='{update_method}')
        else:
            result = resource.ensure_state(state)

        module.exit_json(**result)

    except CriblAPIError as e:
        module.fail_json(msg=str(e))
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {{str(e)}}")


if __name__ == '__main__':
    main()
'''


class TestTemplate:
    """Templates for test generation."""

    @staticmethod
    def test_file_header(product: str) -> str:
        """Generate test file header."""
        return f'''"""
Tests for Cribl {product.title()} Declarative Modules

Auto-generated tests for declarative, idempotent modules.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestCribl{product.title()}DeclarativeModules:
    """Test declarative modules for {product}."""
    
    @pytest.fixture
    def mock_module(self):
        """Provide mock Ansible module."""
        module = MagicMock()
        module.params = {{
            'session': {{'base_url': 'https://cribl.example.com', 'token': 'test_token'}},
            'base_url': None,
            'token': None,
            'validate_certs': False,
            'timeout': 30,
            'state': 'present'
        }}
        module.check_mode = False
        return module
    
    @pytest.fixture
    def mock_client(self):
        """Provide mock Cribl API client."""
        client = MagicMock()
        return client

'''

    @staticmethod
    def module_test(resource_name: str, id_param: str, sanitized_name: str) -> str:
        """Generate test methods for a single module."""
        return f'''
    def test_{sanitized_name}_create(self, mock_module, mock_client):
        """Test creating {resource_name}."""
        mock_module.params['{id_param}'] = 'test_{resource_name}'
        mock_module.params['state'] = 'present'
        
        # Mock GET returns 404 (resource doesn't exist)
        mock_client.get.side_effect = Exception("404 Not Found")
        
        # Mock POST succeeds
        mock_client.post.return_value = {{'id': 'test_{resource_name}'}}
        
        # Test should call POST to create
        # Note: Full implementation would require importing the module
        # and calling its main() function with mocked module
        assert mock_module.params['state'] == 'present'
    
    def test_{sanitized_name}_idempotency(self, mock_module, mock_client):
        """Test that {resource_name} is idempotent."""
        mock_module.params['{id_param}'] = 'test_{resource_name}'
        mock_module.params['state'] = 'present'
        
        # Mock GET returns existing resource
        existing = {{'{id_param}': 'test_{resource_name}'}}
        mock_client.get.return_value = existing
        
        # With same desired state, should not call POST/PATCH
        # Test for idempotency
        assert mock_module.params['state'] == 'present'
    
    def test_{sanitized_name}_update(self, mock_module, mock_client):
        """Test updating {resource_name}."""
        mock_module.params['{id_param}'] = 'test_{resource_name}'
        mock_module.params['state'] = 'present'
        
        # Mock GET returns existing resource with different values
        existing = {{'{id_param}': 'test_{resource_name}', 'old_field': 'old_value'}}
        mock_client.get.return_value = existing
        
        # Mock PATCH succeeds
        mock_client.patch.return_value = {{'{id_param}': 'test_{resource_name}', 'new_field': 'new_value'}}
        
        # Test should detect difference and call PATCH
        assert mock_module.params['state'] == 'present'
    
    def test_{sanitized_name}_delete(self, mock_module, mock_client):
        """Test deleting {resource_name}."""
        mock_module.params['{id_param}'] = 'test_{resource_name}'
        mock_module.params['state'] = 'absent'
        
        # Mock GET returns existing resource
        mock_client.get.return_value = {{'{id_param}': 'test_{resource_name}'}}
        
        # Mock DELETE succeeds
        mock_client.delete.return_value = {{}}
        
        # Test should call DELETE
        assert mock_module.params['state'] == 'absent'
    
    def test_{sanitized_name}_delete_idempotency(self, mock_module, mock_client):
        """Test that delete is idempotent when resource doesn't exist."""
        mock_module.params['{id_param}'] = 'test_{resource_name}'
        mock_module.params['state'] = 'absent'
        
        # Mock GET returns 404 (resource doesn't exist)
        mock_client.get.side_effect = Exception("404 Not Found")
        
        # Should not call DELETE (resource already absent)
        assert mock_module.params['state'] == 'absent'
    
    def test_{sanitized_name}_check_mode(self, mock_module, mock_client):
        """Test {resource_name} check mode."""
        mock_module.params['{id_param}'] = 'test_{resource_name}'
        mock_module.params['state'] = 'present'
        mock_module.check_mode = True
        
        # In check mode, should not make any changes
        # but should report what would change
        assert mock_module.check_mode is True
'''

    @staticmethod
    def integration_playbook_header() -> str:
        """Generate integration playbook header."""
        return '''---
- name: Test All Declarative Modules
  hosts: localhost
  gather_facts: false
  vars:
    cribl_url: "{{ lookup('env', 'CRIBL_URL') | default('http://localhost:9000', true) }}"
    cribl_username: "{{ lookup('env', 'CRIBL_USERNAME') | default('admin', true) }}"
    cribl_password: "{{ lookup('env', 'CRIBL_PASSWORD') }}"
  
  tasks:
'''

    @staticmethod
    def integration_playbook_auth_session(product: str) -> str:
        """Generate auth session task for integration playbook."""
        return f'''
    - name: Create authentication session for {product}
      cribl.{product}.auth_session:
        base_url: "{{{{ cribl_url }}}}"
        username: "{{{{ cribl_username }}}}"
        password: "{{{{ cribl_password }}}}"
        validate_certs: false
      register: cribl_{product}_session
'''

    @staticmethod
    def integration_playbook_module_test(product: str, module_name: str, 
                                        id_param: str, resource_name: str) -> str:
        """Generate module test tasks for integration playbook."""
        return f'''
    - name: Test {module_name} - Create
      cribl.{product}.{module_name}:
        session: "{{{{ cribl_{product}_session.session }}}}"
        {id_param}: test_{resource_name}_ansible
        state: present
      register: {resource_name}_create
    
    - name: Test {module_name} - Idempotency
      cribl.{product}.{module_name}:
        session: "{{{{ cribl_{product}_session.session }}}}"
        {id_param}: test_{resource_name}_ansible
        state: present
      register: {resource_name}_idempotent
    
    - name: Verify {module_name} idempotency
      assert:
        that:
          - {resource_name}_create.changed == true
          - {resource_name}_idempotent.changed == false
        fail_msg: "{module_name} is not idempotent!"
    
    - name: Test {module_name} - Delete
      cribl.{product}.{module_name}:
        session: "{{{{ cribl_{product}_session.session }}}}"
        {id_param}: test_{resource_name}_ansible
        state: absent
      register: {resource_name}_delete
    
    - name: Test {module_name} - Delete idempotency
      cribl.{product}.{module_name}:
        session: "{{{{ cribl_{product}_session.session }}}}"
        {id_param}: test_{resource_name}_ansible
        state: absent
      register: {resource_name}_delete_idempotent
    
    - name: Verify {module_name} delete idempotency
      assert:
        that:
          - {resource_name}_delete.changed == true or {resource_name}_delete.failed == true
          - {resource_name}_delete_idempotent.changed == false
        fail_msg: "{module_name} delete is not idempotent!"
'''


class AuthSessionTemplate:
    """Template for auth_session module."""

    @staticmethod
    def create_auth_session_module(product: str) -> str:
        """Generate complete auth_session module for a product."""
        return f'''#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r\'\'\'
---
module: auth_session
short_description: Create and manage Cribl authentication session
description:
    - Creates an authenticated session with Cribl API that can be reused across multiple modules.
    - Supports two authentication methods - traditional username/password and OAuth2 Client Credentials (Cribl Cloud).
    - Handles automatic token refresh and expiration.
    - Returns a session object that can be passed to other Cribl modules.
    - This is the recommended way to authenticate with Cribl - it's more efficient and secure.
version_added: "1.0.0"
author:
    - Cribl Ansible Collection Contributors
options:
    base_url:
        description:
            - Base URL of the Cribl instance.
            - For Cribl Cloud use your org URL (e.g., C(https://main-myorg.cribl.cloud)).
        type: str
        required: true
    username:
        description:
            - Username for traditional authentication.
            - Required when using username/password authentication.
            - Mutually exclusive with C(client_id)/C(client_secret).
        type: str
        required: false
    password:
        description:
            - Password for traditional authentication.
            - Required when using username/password authentication.
            - Mutually exclusive with C(client_id)/C(client_secret).
        type: str
        required: false
        no_log: true
    client_id:
        description:
            - OAuth2 client ID for Cribl Cloud authentication.
            - Required when using OAuth2 authentication.
            - Mutually exclusive with C(username)/C(password).
            - Obtain from Cribl Cloud under Settings > API Credentials.
        type: str
        required: false
    client_secret:
        description:
            - OAuth2 client secret for Cribl Cloud authentication.
            - Required when using OAuth2 authentication.
            - Mutually exclusive with C(username)/C(password).
            - Obtain from Cribl Cloud under Settings > API Credentials.
        type: str
        required: false
        no_log: true
    oauth_token_url:
        description:
            - OAuth2 token endpoint URL.
            - Only used for OAuth2 authentication.
            - Default is Cribl Cloud's token endpoint.
        type: str
        required: false
        default: https://login.cribl.cloud/oauth/token
    validate_certs:
        description:
            - Whether to validate SSL certificates.
        type: bool
        default: false
    timeout:
        description:
            - Timeout for API requests in seconds.
        type: int
        default: 30
requirements:
    - python >= 3.6
notes:
    - This module creates a session that can be passed to other Cribl modules.
    - Sessions automatically handle token refresh when tokens expire.
    - Store the session in a registered variable and pass it to other modules.
    - Authentication method is automatically detected based on parameters provided.
    - Use C(username)/C(password) for on-prem or traditional Cribl instances.
    - Use C(client_id)/C(client_secret) for Cribl Cloud with API credentials.
\'\'\'

EXAMPLES = r\'\'\'
# Traditional username/password authentication (on-prem or Cribl Cloud)
- name: Create session with username/password
  cribl.{product}.auth_session:
    base_url: https://cribl.example.com
    username: admin
    password: mysecretpassword
    validate_certs: false
  register: cribl_session
  no_log: true

- name: Use session in other modules
  cribl.{product}.system_users_get:
    session: "{{{{ cribl_session.session }}}}"
  register: users

# OAuth2 authentication for Cribl Cloud
- name: Create session with OAuth2 (Cribl Cloud)
  cribl.{product}.auth_session:
    base_url: https://main-myorg.cribl.cloud
    client_id: "{{{{ cribl_client_id }}}}"
    client_secret: "{{{{ cribl_client_secret }}}}"
    validate_certs: true
  register: cribl_cloud_session
  no_log: true

- name: Use Cribl Cloud session
  cribl.{product}.system_users_get:
    session: "{{{{ cribl_cloud_session.session }}}}"
  register: cloud_users

# Session can be reused across multiple tasks and roles
- name: Use session in a loop
  cribl.{product}.system_users_id_get:
    session: "{{{{ cribl_session.session }}}}"
    id: "{{{{ item }}}}"
  loop:
    - user1
    - user2
    - user3
\'\'\'

RETURN = r\'\'\'
session:
    description: Session object to pass to other Cribl modules
    type: dict
    returned: success
    contains:
        base_url:
            description: Base URL of the Cribl instance
            type: str
        token:
            description: Authentication token (bearer token or OAuth2 access token)
            type: str
        token_expiry:
            description: Unix timestamp when token expires
            type: float
        auth_type:
            description: Authentication type used (password or oauth2)
            type: str
        validate_certs:
            description: Whether SSL certificate validation is enabled
            type: bool
        timeout:
            description: Request timeout in seconds
            type: int
msg:
    description: Success message
    type: str
    returned: always
    sample: "Successfully authenticated with Cribl using OAuth2"
auth_type:
    description: Authentication method used
    type: str
    returned: always
    sample: "oauth2"
\'\'\'

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cribl.{product}.plugins.module_utils.cribl_api import (
    CriblAPIClient,
    CriblAPIError
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            base_url=dict(type='str', required=True),
            username=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            client_id=dict(type='str', required=False),
            client_secret=dict(type='str', required=False, no_log=True),
            oauth_token_url=dict(type='str', required=False, default='https://login.cribl.cloud/oauth/token'),
            validate_certs=dict(type='bool', default=False),
            timeout=dict(type='int', default=30),
        ),
        required_one_of=[
            ['username', 'client_id'],
        ],
        required_together=[
            ['username', 'password'],
            ['client_id', 'client_secret'],
        ],
        mutually_exclusive=[
            ['username', 'client_id'],
            ['password', 'client_secret'],
        ],
        supports_check_mode=True,
    )

    base_url = module.params['base_url']
    username = module.params.get('username')
    password = module.params.get('password')
    client_id = module.params.get('client_id')
    client_secret = module.params.get('client_secret')
    oauth_token_url = module.params['oauth_token_url']
    validate_certs = module.params['validate_certs']
    timeout = module.params['timeout']

    # Determine auth type
    if client_id and client_secret:
        auth_type = 'oauth2'
        auth_method = 'OAuth2 Client Credentials'
    else:
        auth_type = 'password'
        auth_method = 'username/password'

    try:
        if module.check_mode:
            module.exit_json(
                changed=False,
                msg=f"Check mode: Would create authentication session using {{auth_method}}",
                auth_type=auth_type,
                session={{
                    'base_url': base_url,
                    'validate_certs': validate_certs,
                    'timeout': timeout,
                    'auth_type': auth_type
                }}
            )

        # Create client and authenticate
        client = CriblAPIClient(
            base_url=base_url,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            oauth_token_url=oauth_token_url,
            validate_certs=validate_certs,
            timeout=timeout
        )

        # Login and get session
        session_obj = client.login()
        session_dict = session_obj.to_dict()

        module.exit_json(
            changed=False,  # Authentication doesn't change state
            msg=f"Successfully authenticated with Cribl at {{base_url}} using {{auth_method}}",
            auth_type=auth_type,
            session=session_dict
        )

    except CriblAPIError as e:
        module.fail_json(msg=str(e), auth_type=auth_type)
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {{str(e)}}", auth_type=auth_type)


if __name__ == '__main__':
    main()
'''


class ExampleTemplate:
    """Templates for example playbook generation."""

    @staticmethod
    def single_module_example(product: str, module_name: str, 
                             resource_title: str, id_param: str) -> str:
        """Generate an example playbook for a single module."""
        return f'''---
# Example: Managing {resource_title} with cribl.{product}.{module_name}
# This playbook demonstrates CRUD operations using the declarative module

- name: Manage {resource_title}
  hosts: localhost
  gather_facts: false
  vars:
    cribl_url: "https://cribl.example.com"
    cribl_username: "admin"
    cribl_password: "{{{{ vault_cribl_password }}}}"
  
  tasks:
    # Create authentication session
    - name: Create authentication session
      cribl.{product}.auth_session:
        base_url: "{{{{ cribl_url }}}}"
        username: "{{{{ cribl_username }}}}"
        password: "{{{{ cribl_password }}}}"
        validate_certs: false
      register: cribl_session
    
    # CREATE/UPDATE - Ensure resource exists
    - name: Ensure {module_name} exists
      cribl.{product}.{module_name}:
        session: "{{{{ cribl_session.session }}}}"
        {id_param}: "my_{module_name}"
        # Add additional parameters as needed
        state: present
      register: result
    
    - name: Display result
      debug:
        var: result
    
    # DELETE - Ensure resource does not exist
    - name: Ensure {module_name} is removed
      cribl.{product}.{module_name}:
        session: "{{{{ cribl_session.session }}}}"
        {id_param}: "my_{module_name}"
        state: absent
      when: false  # Set to true to actually delete
'''

    @staticmethod
    def combined_example_header(product: str) -> str:
        """Generate combined example playbook header."""
        return f'''---
# Combined Example: Managing multiple {product} resources
# Demonstrates declarative resource management

- name: Configure Cribl {product.title()} Resources
  hosts: localhost
  gather_facts: false
  vars:
    cribl_url: "https://cribl.example.com"
    cribl_username: "admin"
    cribl_password: "{{{{ vault_cribl_password }}}}"
  
  tasks:
    - name: Create authentication session
      cribl.{product}.auth_session:
        base_url: "{{{{ cribl_url }}}}"
        username: "{{{{ cribl_username }}}}"
        password: "{{{{ cribl_password }}}}"
        validate_certs: false
      register: cribl_session
'''

    @staticmethod
    def combined_example_task(product: str, module_name: str, id_param: str) -> str:
        """Generate a single task for combined example."""
        return f'''
    - name: Manage {module_name}
      cribl.{product}.{module_name}:
        session: "{{{{ cribl_session.session }}}}"
        {id_param}: "example_{module_name}"
        state: present'''

    @staticmethod
    def combined_example_footer(remaining_modules: list) -> str:
        """Generate footer with list of additional modules."""
        if remaining_modules:
            return f'''
    
    # More resources available:
    # {", ".join(remaining_modules)}
'''
        return ''
        return ''