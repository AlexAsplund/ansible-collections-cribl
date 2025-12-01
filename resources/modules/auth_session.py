#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
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
'''

EXAMPLES = r'''
# Traditional username/password authentication (on-prem or Cribl Cloud)
- name: Create session with username/password
  cribl.core.auth_session:
    base_url: https://cribl.example.com
    username: admin
    password: mysecretpassword
    validate_certs: false
  register: cribl_session
  no_log: true

- name: Use session in other modules
  cribl.core.system_users_get:
    session: "{{ cribl_session.session }}"
  register: users

# OAuth2 authentication for Cribl Cloud
- name: Create session with OAuth2 (Cribl Cloud)
  cribl.core.auth_session:
    base_url: https://main-myorg.cribl.cloud
    client_id: "{{ cribl_client_id }}"
    client_secret: "{{ cribl_client_secret }}"
    validate_certs: true
  register: cribl_cloud_session
  no_log: true

- name: Use Cribl Cloud session
  cribl.core.system_users_get:
    session: "{{ cribl_cloud_session.session }}"
  register: cloud_users

# OAuth2 with custom token endpoint
- name: Create session with custom OAuth2 endpoint
  cribl.core.auth_session:
    base_url: https://custom.cribl.io
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    oauth_token_url: https://custom-auth.cribl.io/oauth/token
  register: custom_session
  no_log: true

# Session can be reused across multiple tasks and roles
- name: Use session in a loop
  cribl.core.system_users_id_get:
    session: "{{ cribl_session.session }}"
    id: "{{ item }}"
  loop:
    - user1
    - user2
    - user3

# Store credentials in Ansible Vault
- name: Authenticate using vaulted credentials
  cribl.core.auth_session:
    base_url: "{{ cribl_url }}"
    client_id: "{{ vault_cribl_client_id }}"
    client_secret: "{{ vault_cribl_client_secret }}"
  register: secure_session
  no_log: true
'''

RETURN = r'''
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
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cribl.core.plugins.module_utils.cribl_api import (
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
                msg=f"Check mode: Would create authentication session using {auth_method}",
                auth_type=auth_type,
                session={
                    'base_url': base_url,
                    'validate_certs': validate_certs,
                    'timeout': timeout,
                    'auth_type': auth_type
                }
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
            msg=f"Successfully authenticated with Cribl at {base_url} using {auth_method}",
            auth_type=auth_type,
            session=session_dict
        )

    except CriblAPIError as e:
        module.fail_json(msg=str(e), auth_type=auth_type)
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}", auth_type=auth_type)


if __name__ == '__main__':
    main()

