"""
Collection Manager

Manages Ansible collection structure and metadata files.
"""

from pathlib import Path
from typing import List, Dict
import shutil
from .templates import AuthSessionTemplate


class CollectionManager:
    """Manage collection directory structure and files."""

    PRODUCT_DESCRIPTIONS = {
        'core': 'Ansible collection for managing Cribl Core (authentication, users, teams, worker groups)',
        'stream': 'Ansible collection for managing Cribl Stream (pipelines, routes, inputs, outputs)',
        'edge': 'Ansible collection for managing Cribl Edge (edge nodes, processes, containers)',
        'search': 'Ansible collection for managing Cribl Search (datasets, searches, dashboards)',
        'lake': 'Ansible collection for managing Cribl Lake (data lakes, storage, datasets)'
    }

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def create_structure(self, product: str, version: str = '1.0.0'):
        """Create complete directory structure for a collection."""
        dirs = [
            self._get_path(product, 'plugins', 'modules'),
            self._get_path(product, 'plugins', 'module_utils'),
            self._get_path(product, 'plugins', 'doc_fragments'),
            self._get_path(product, 'examples'),
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self._create_init_files(product)
        self._create_doc_fragment(product)
        self._create_galaxy_yml(product, version)
        self._create_collection_readme(product)

    def _get_path(self, product: str, *parts) -> Path:
        """Get path within collection."""
        return self.base_dir / product / Path(*parts)

    def _create_init_files(self, product: str):
        """Create __init__.py files."""
        init_file = self._get_path(product, 'plugins', 'module_utils', '__init__.py')
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('''# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
''')

    def _create_doc_fragment(self, product: str):
        """Create documentation fragment."""
        doc_file = self._get_path(product, 'plugins', 'doc_fragments', 'cribl.py')
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(f'''# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r\'\'\'
options:
    session:
        description:
            - Existing session from auth_session module.
            - If provided, other auth parameters are ignored.
            - This is the recommended way to handle authentication.
        type: dict
        required: false
    base_url:
        description:
            - Base URL of the Cribl instance.
            - Required if session is not provided.
        type: str
        required: false
    username:
        description:
            - Username for authentication.
            - Required if session and token are not provided.
        type: str
        required: false
    password:
        description:
            - Password for authentication.
            - Required if session and token are not provided.
        type: str
        required: false
        no_log: true
    token:
        description:
            - Bearer token for authentication.
            - Can be used instead of username/password.
        type: str
        required: false
        no_log: true
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
notes:
    - This module is part of the cribl.{product} collection for Cribl {product.title()}.
    - For best results, use the auth_session module to create a session and pass it to other modules.
    - Sessions automatically handle token refresh and expiration.
\'\'\'
''')

    def _create_galaxy_yml(self, product: str, version: str = '1.0.0'):
        """Create galaxy.yml metadata file."""
        galaxy_file = self._get_path(product, 'galaxy.yml')
        description = self.PRODUCT_DESCRIPTIONS.get(product, f'Cribl {product.title()} Collection')
        
        with open(galaxy_file, 'w', encoding='utf-8') as f:
            f.write(f'''---
namespace: cribl
name: {product}
version: {version}
readme: README.md
authors:
  - Alex Asplund <alex@automativity.com>
description: {description}
license:
  - MIT
license_file: ''
tags:
  - cribl
  - {product}
  - logging
  - observability
dependencies: {{}}
repository: https://github.com/AlexAsplund/ansible-collections-cribl
documentation: https://github.com/AlexAsplund/ansible-collections-cribl/blob/main/README.md
homepage: https://github.com/AlexAsplund/ansible-collections-cribl/
issues: https://github.com/AlexAsplund/ansible-collections-cribl/issues
build_ignore: []
''')

    def _create_collection_readme(self, product: str):
        """Create README.md for the collection."""
        readme_file = self._get_path(product, 'README.md')
        description = self.PRODUCT_DESCRIPTIONS.get(product, f'Cribl {product.title()} Collection')
        
        # Module type descriptions
        module_types = {
            'core': {
                'declarative': 'User, Team, WorkerGroup, Role, Policy, Certificate, Key, etc.',
                'imperative': '276 API endpoint modules for system management'
            },
            'stream': {
                'declarative': 'Pipeline, Input, Output, Route, Pack, Schema, etc.',
                'imperative': '127 API endpoint modules for data processing'
            },
            'edge': {
                'declarative': 'Process management',
                'imperative': '19 API endpoint modules for edge operations'
            },
            'search': {
                'declarative': 'Dataset, Dashboard, SavedSearch, Macro, Job, etc.',
                'imperative': '80 API endpoint modules for search operations'
            },
            'lake': {
                'declarative': 'Not yet available',
                'imperative': '11 API endpoint modules for data lake operations'
            }
        }
        
        info = module_types.get(product, {'declarative': 'Various resources', 'imperative': 'API modules'})
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(f'''# Ansible Collection - cribl.{product}

{description}

## Installation

```bash
ansible-galaxy collection install cribl.{product}
```

## Modules

This collection includes:

### Declarative Modules (Idempotent)
{info['declarative']}

### Imperative Modules (Direct API Access)
{info['imperative']}

## Usage

### Example: Using Declarative Modules

```yaml
---
- name: Manage Cribl {product.title()} Resources
  hosts: localhost
  gather_facts: false
  
  tasks:
    # Authenticate once
    - name: Create Cribl session
      cribl.core.auth_session:
        base_url: "https://cribl.example.com"
        username: admin
        password: "{{{{ vault_password }}}}"
      register: cribl_session
      no_log: true

    # Use declarative modules for idempotent operations
    # See examples/ directory for more examples
```

### Example: Using Imperative Modules

```yaml
---
- name: Query Cribl {product.title()}
  hosts: localhost
  gather_facts: false
  
  tasks:
    # Get information
    - name: Query {product} resources
      cribl.{product}.some_resource_get:
        session: "{{{{ cribl_session.session }}}}"
      register: result
```

## Documentation

- [Main Documentation](https://github.com/AlexAsplund/ansible-collections-cribl)
- [API Reference](https://docs.cribl.io)
- [Examples](./examples/)

## License

MIT

## Author

Cribl Ansible Collection Contributors
''')

    def copy_api_client(self, product: str, source_dir: Path = None):
        """Copy API client to collection."""
        # Try to find the source API client
        possible_sources = [
            Path('ansible_collections/cribl/stream/plugins/module_utils/cribl_api.py'),
            self.base_dir / 'stream' / 'plugins' / 'module_utils' / 'cribl_api.py',
        ]
        
        if source_dir:
            possible_sources.insert(0, source_dir / 'stream' / 'plugins' / 'module_utils' / 'cribl_api.py')
        
        target = self._get_path(product, 'plugins', 'module_utils', 'cribl_api.py')
        
        # Try to copy from existing source
        for source in possible_sources:
            if source.exists() and source.resolve() != target.resolve():
                shutil.copy(source, target)
                return
        
        # Create from template if no source found
        with open(target, 'w', encoding='utf-8') as f:
            f.write(self._get_api_client_template())
    
    def copy_auth_session_module(self, product: str):
        """Copy auth_session module to collection."""
        target = self._get_path(product, 'plugins', 'modules', 'auth_session.py')
        
        # Generate auth_session module from template
        content = AuthSessionTemplate.create_auth_session_module(product)
        
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)

    def generate_module_index(self, product: str, modules: List[str]):
        """Generate MODULES.md index file."""
        index_file = self._get_path(product, 'MODULES.md')
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(f"# Cribl {product.title()} Collection - Module Index\n\n")
            f.write(f"Total modules: {len(modules)}\n\n")
            f.write("## Auto-Generated Modules\n\n")
            
            for module in sorted(modules):
                f.write(f"- `{module}`\n")

    def clean_generated_modules(self, product: str):
        """Remove generated module files."""
        modules_dir = self._get_path(product, 'plugins', 'modules')
        if modules_dir.exists():
            # Clean both old cribl_* modules and new modules (but keep custom ones)
            for file in modules_dir.glob("*.py"):
                # Skip special files
                if file.name in ['__init__.py', 'auth_session.py']:
                    continue
                # Keep declarative modules
                if '_declarative.py' not in file.name:
                    file.unlink()

    def _get_api_client_template(self) -> str:
        """Get API client template."""
        return '''# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import requests
import time
from typing import Optional, Dict, Any


class CriblAPIError(Exception):
    """Exception raised for Cribl API errors."""
    pass


class CriblSession:
    """Represents a Cribl API session with automatic token refresh."""
    
    def __init__(self, base_url: str, token: str, username: Optional[str] = None,
                 password: Optional[str] = None, validate_certs: bool = False,
                 timeout: int = 30, token_expiry: Optional[float] = None):
        """Initialize session from existing credentials or token."""
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.username = username
        self.password = password
        self.validate_certs = validate_certs
        self.timeout = timeout
        self.token_expiry = token_expiry or (time.time() + 3600)  # Default 1 hour
        
    def to_dict(self) -> Dict[str, Any]:
        """Export session for passing to other modules."""
        return {
            'base_url': self.base_url,
            'token': self.token,
            'username': self.username,
            'password': self.password,
            'validate_certs': self.validate_certs,
            'timeout': self.timeout,
            'token_expiry': self.token_expiry
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CriblSession':
        """Create session from dictionary (e.g., from registered variable)."""
        return cls(
            base_url=data['base_url'],
            token=data['token'],
            username=data.get('username'),
            password=data.get('password'),
            validate_certs=data.get('validate_certs', False),
            timeout=data.get('timeout', 30),
            token_expiry=data.get('token_expiry')
        )
    
    def is_expired(self) -> bool:
        """Check if token is expired or near expiry (within 5 minutes)."""
        return time.time() >= (self.token_expiry - 300)


class CriblAPIClient:
    """Client for interacting with the Cribl API with automatic session management."""

    def __init__(self, base_url: str = None, username: Optional[str] = None,
                 password: Optional[str] = None, token: Optional[str] = None,
                 validate_certs: bool = False, timeout: int = 30,
                 session: Optional[Dict[str, Any]] = None):
        """
        Initialize client with credentials or existing session.
        
        Args:
            base_url: Base URL of Cribl instance
            username: Username for auth
            password: Password for auth
            token: Existing bearer token
            validate_certs: Whether to validate SSL certificates
            timeout: Request timeout in seconds
            session: Existing session dict from auth_session module
        """
        if session:
            # Initialize from existing session
            self.session_obj = CriblSession.from_dict(session)
            self.base_url = self.session_obj.base_url
            self.username = self.session_obj.username
            self.password = self.session_obj.password
            self.token = self.session_obj.token
            self.validate_certs = self.session_obj.validate_certs
            self.timeout = self.session_obj.timeout
        else:
            # Initialize from credentials
            if not base_url:
                raise CriblAPIError("base_url is required when not using session")
            self.base_url = base_url.rstrip('/')
            self.username = username
            self.password = password
            self.token = token
            self.validate_certs = validate_certs
            self.timeout = timeout
            self.session_obj = None
        
        self.http_session = requests.Session()
        
        if not self.validate_certs:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def login(self) -> CriblSession:
        """Authenticate and get bearer token, returning a session object."""
        if self.token and self.session_obj and not self.session_obj.is_expired():
            return self.session_obj
        
        if not self.username or not self.password:
            raise CriblAPIError("Username and password required for login")
        
        url = f"{self.base_url}/api/v1/auth/login"
        response = self.http_session.post(
            url,
            json={"username": self.username, "password": self.password},
            verify=self.validate_certs,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise CriblAPIError(f"Login failed: {response.status_code} {response.text}")
        
        data = response.json()
        self.token = data.get("token")
        
        # Calculate token expiry (Cribl tokens typically last 1 hour)
        token_expiry = time.time() + data.get("expiresIn", 3600)
        
        # Create session object
        self.session_obj = CriblSession(
            base_url=self.base_url,
            token=self.token,
            username=self.username,
            password=self.password,
            validate_certs=self.validate_certs,
            timeout=self.timeout,
            token_expiry=token_expiry
        )
        
        return self.session_obj

    def _ensure_valid_token(self):
        """Ensure we have a valid token, refreshing if needed."""
        if self.session_obj and self.session_obj.is_expired():
            # Token expired, re-authenticate
            self.session_obj = self.login()
        elif not self.token:
            # No token yet, login
            self.login()

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make an API request with automatic token refresh."""
        self._ensure_valid_token()
        
        url = f"{self.base_url}/api/v1{endpoint}"
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'
        
        response = self.http_session.request(
            method,
            url,
            headers=headers,
            verify=self.validate_certs,
            timeout=self.timeout,
            **kwargs
        )
        
        # If we get 401, try refreshing token once
        if response.status_code == 401:
            self.session_obj = self.login()
            headers['Authorization'] = f'Bearer {self.token}'
            response = self.http_session.request(
                method,
                url,
                headers=headers,
                verify=self.validate_certs,
                timeout=self.timeout,
                **kwargs
            )
        
        if response.status_code >= 400:
            raise CriblAPIError(f"{method} {endpoint} failed: {response.status_code} {response.text}")
        
        if response.content:
            return response.json()
        return {}

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """GET request."""
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """POST request."""
        return self._request('POST', endpoint, json=data)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """PUT request."""
        return self._request('PUT', endpoint, json=data)

    def patch(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """PATCH request."""
        return self._request('PATCH', endpoint, json=data)

    def delete(self, endpoint: str) -> Any:
        """DELETE request."""
        return self._request('DELETE', endpoint)
    
    def get_session(self) -> Dict[str, Any]:
        """Get current session for passing to other modules."""
        if not self.session_obj:
            self.session_obj = self.login()
        return self.session_obj.to_dict()
'''

