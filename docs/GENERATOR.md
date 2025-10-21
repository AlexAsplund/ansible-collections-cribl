# Module Generator Guide

## Overview

The Cribl Ansible Collections use an automated generator that creates Ansible modules from Cribl's OpenAPI specification. This allows for complete API coverage and easy updates when new Cribl versions are released.

---

## Quick Start

```bash
# Generate all modules (imperative + declarative)
python scripts/generate_modules.py --declarative

# Clean and regenerate everything
python scripts/generate_modules.py --clean

# Generate specific product only
python scripts/generate_modules.py --product core

# Use custom OpenAPI spec
python scripts/generate_modules.py --spec schemas/cribl-apidocs-latest.yml
```

---

## Generator Architecture

### Components

```
scripts/
├── generate_modules.py              # CLI entry point
└── generator/
    ├── __init__.py                  # Package init
    ├── openapi_parser.py            # Parse OpenAPI specifications
    ├── module_generator.py          # Generate imperative modules
    ├── declarative_generator.py     # Generate declarative modules
    ├── collection_manager.py        # Manage collection structure
    └── templates.py                 # Module code templates
```

### How It Works

1. **Parse OpenAPI** - Extract endpoints, schemas, parameters
2. **Categorize Routes** - Route to correct product collection (core/stream/edge/search/lake)
3. **Generate Modules** - Create Python module files with Ansible boilerplate
4. **Create Documentation** - Generate DOCUMENTATION, EXAMPLES, RETURN blocks
5. **Build Collections** - Structure into Ansible Galaxy-compatible collections

---

## Command-Line Options

### Basic Usage

```bash
python scripts/generate_modules.py [OPTIONS]
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--spec PATH` | Path to OpenAPI spec file | `--spec schemas/custom-api.yml` |
| `--product NAME` | Generate specific product only | `--product core` |
| `--declarative` | Generate declarative modules too | `--declarative` |
| `--declarative-only` | Only generate declarative modules | `--declarative-only` |
| `--clean` | Clean build directory first | `--clean` |
| `--output DIR` | Custom output directory | `--output /tmp/ansible` |
| `--verbose` | Verbose output | `--verbose` |

### Examples

```bash
# Generate everything with declarative modules
python scripts/generate_modules.py --declarative --clean

# Generate only core collection
python scripts/generate_modules.py --product core

# Use custom spec and output location
python scripts/generate_modules.py \
  --spec /path/to/cribl-api.yml \
  --output /tmp/collections

# Only generate declarative modules (no imperative)
python scripts/generate_modules.py --declarative-only
```

---

## Module Generation Process

### 1. OpenAPI Parsing

**Input:** OpenAPI YAML specification

```yaml
paths:
  /system/users:
    get:
      summary: List all users
      operationId: getUserList
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
```

**Output:** Structured endpoint data

```python
{
    'path': '/system/users',
    'method': 'GET',
    'operation_id': 'getUserList',
    'parameters': {
        'query': [{'name': 'limit', 'type': 'int'}]
    },
    'summary': 'List all users'
}
```

### 2. Route Categorization

Routes are categorized into collections based on path:

```python
ROUTE_MAPPING = {
    'core': ['/auth/', '/system/', '/master/', '/health', '/version'],
    'stream': ['/pipelines', '/routes', '/packs', '/lib/'],
    'search': ['/datasets', '/jobs', '/dashboards', '/saved_searches'],
    'edge': ['/processes', '/containers', '/appscope'],
    'lake': ['/lakes/']
}
```

### 3. Module Template

**Generated Module Structure:**

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = r'''
---
module: cribl_system_users_get
short_description: Get list of users
description:
  - Retrieves list of users from Cribl
  - Maps to GET /api/v1/system/users
options:
  base_url:
    description: Cribl instance URL
    type: str
    required: true
  ...
'''

EXAMPLES = r'''
- name: List all users
  cribl.core.system_users_get:
    base_url: https://cribl.example.com
    username: admin
    password: mypassword
  register: users
'''

RETURN = r'''
response:
  description: API response
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cribl.core.plugins.module_utils.cribl_api import CriblAPIClient

def main():
    module = AnsibleModule(
        argument_spec={...},
        supports_check_mode=False
    )
    
    # Module logic
    ...
    
    module.exit_json(**result)

if __name__ == '__main__':
    main()
```

### 4. Documentation Generation

Auto-generates from OpenAPI:

- **Parameters** from `parameters` and `requestBody` schemas
- **Examples** from common use cases
- **Return values** from `responses` schemas
- **Description** from `summary` and `description` fields

---

## Customization

### Adding Custom Declarative Modules

1. **Create generator definition:**

```python
# scripts/generator/declarative_generator.py

DECLARATIVE_MODULES = [
    {
        'name': 'cribl_pipeline_declarative',
        'collection': 'stream',
        'resource_type': 'pipeline',
        'get_endpoint': '/pipelines/{id}',
        'create_endpoint': '/pipelines',
        'update_endpoint': '/pipelines/{id}',
        'delete_endpoint': '/pipelines/{id}',
        'id_field': 'id',
        'comparison_fields': ['conf', 'functions']
    }
]
```

2. **Regenerate modules:**

```bash
python scripts/generate_modules.py --declarative
```

### Modifying Templates

Edit `scripts/generator/templates.py`:

```python
# Add custom module header
MODULE_HEADER = '''
#!/usr/bin/python
# -*- coding: utf-8 -*-
# Custom header content
'''

# Modify documentation template
DOCUMENTATION_TEMPLATE = '''
---
module: {module_name}
short_description: {short_description}
# Custom documentation fields
'''
```

---

## Updating for New Cribl Versions

When a new Cribl version is released:

1. **Download new OpenAPI spec:**
```bash
curl -o schemas/cribl-apidocs-latest.yml \
  https://docs.cribl.io/api/cribl-apidocs.yml
```

2. **Regenerate modules:**
```bash
python scripts/generate_modules.py \
  --spec schemas/cribl-apidocs-latest.yml \
  --clean \
  --declarative
```

3. **Test generated modules:**
```bash
make test
```

4. **Review changes:**
```bash
git diff build/ansible_collections/
```

---

## Testing Generated Modules

### Syntax Check

```bash
# Check all generated modules
python -m py_compile build/ansible_collections/cribl/*/plugins/modules/*.py
```

### Import Check

```bash
# Test imports
python -c "from ansible_collections.cribl.core.plugins.modules import cribl_system_users_get"
```

### Ansible Validation

```bash
# Validate module documentation
ansible-doc -t module cribl.core.system_users_get
```

### Run Test Playbook

```yaml
---
- name: Test generated module
  hosts: localhost
  tasks:
    - name: Use generated module
      cribl.core.system_users_get:
        base_url: https://cribl.example.com
        username: admin
        password: test
      register: result
      
    - name: Verify result
      assert:
        that:
          - result.response is defined
          - result.response.items is defined
```

---

## Generator Statistics

Current generation (as of latest run):

```
Collection Statistics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Collection         Modules    Lines of Code
──────────────────────────────────────────
cribl.core           276         89,000
cribl.stream         127         38,000
cribl.search          80         24,500
cribl.edge            19          6,800
cribl.lake            11          3,200
──────────────────────────────────────────
Total                513        161,500
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Declarative Modules:
  - cribl_user_declarative
  - cribl_worker_group_declarative

Generation Time: ~8 seconds
```

---

## Troubleshooting

### Module Generation Fails

```bash
# Check OpenAPI spec is valid
python -c "import yaml; yaml.safe_load(open('schemas/cribl-apidocs.yml'))"

# Run with verbose output
python scripts/generate_modules.py --verbose

# Check Python dependencies
pip install -r requirements-dev.txt
```

### Module Not Found After Generation

```bash
# Verify module was created
ls -la build/ansible_collections/cribl/core/plugins/modules/

# Check collection structure
tree build/ansible_collections/cribl/core/
```

### Import Errors in Generated Modules

```bash
# Validate Python syntax
python -m py_compile build/ansible_collections/cribl/core/plugins/modules/*.py

# Test module imports
python -c "import sys; sys.path.insert(0, 'build'); from ansible_collections.cribl.core.plugins.modules import *"
```

---

## Advanced Topics

### Custom Module Utils

Add shared code to `module_utils/`:

```python
# build/ansible_collections/cribl/core/plugins/module_utils/custom_helper.py

def custom_parser(data):
    """Custom parsing logic."""
    return processed_data
```

Use in generated modules:

```python
from ansible_collections.cribl.core.plugins.module_utils.custom_helper import custom_parser
```

### Hook into Generation Process

```python
# scripts/custom_generator_hook.py

def post_generation_hook(module_path, module_data):
    """Called after each module is generated."""
    # Custom processing
    with open(module_path, 'a') as f:
        f.write('\n# Custom footer\n')

# Use in generator
from custom_generator_hook import post_generation_hook
generator.register_hook('post_generate', post_generation_hook)
```

---

## Additional Resources

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Ansible Module Development](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
- [Cribl API Reference](https://docs.cribl.io/cribl-as-code/api-reference/)
- [YAML Parsing in Python](https://pyyaml.org/wiki/PyYAMLDocumentation)
