# Automatic Declarative Module Generation

## Overview

The Cribl Ansible Collection generator now includes **automatic CRUD detection** that analyzes the OpenAPI specification and generates declarative modules for all resources that support full create, read, update, and delete operations.

---

## What Gets Auto-Generated

The generator automatically detects and creates declarative modules for resources that have:

- **List** or **Get** operation (read)  
- **Post** operation (create)  
- **Patch** or **Put** operation (update)  
- **Delete** operation (delete)  
- **ID-based endpoint** (e.g., `/resource/{id}`)

---

## Current Stats

Based on the latest Cribl OpenAPI specification (v4.14.0), the generator auto-detects:

| Collection | Declarative Modules | Examples |
|------------|--------------------:|----------|
| **cribl.core** | 22 | Users, Worker Groups, Roles, Teams, Secrets, Certificates |
| **cribl.stream** | 16 | Pipelines, Inputs, Outputs, Parsers, Schemas, Packs |
| **cribl.edge** | 1 | Processes |
| **cribl.search** | 10 | Datasets, Dashboards, Saved Searches, Macros |
| **cribl.lake** | 0 | _(no CRUD resources in API)_ |
| **Total** | **49** | **All major Cribl resources** |

---

## Usage

### Generate All Declarative Modules

```bash
# Auto-detect and generate ALL declarative modules
python scripts/generate_modules.py --declarative-only

# Generate declarative + imperative modules
python scripts/generate_modules.py --declarative

# Generate for specific product only
python scripts/generate_modules.py --product core --declarative
```

### Output

```
======================================================================
Auto-Detecting CRUD Resources & Generating Declarative Modules
======================================================================

Loading OpenAPI spec from schemas/cribl-apidocs-4.14.0.yml...
Loaded spec version 4.14.0

  [CORE] Detected 22 resources with CRUD operations
    [OK] cribl_user_declarative
    [OK] cribl_worker_group_declarative
    [OK] cribl_role_declarative
    [OK] cribl_team_declarative
    ...

  [STREAM] Detected 16 resources with CRUD operations
    [OK] cribl_pipeline_declarative
    [OK] cribl_input_declarative
    [OK] cribl_output_declarative
    ...

Generating tests for declarative modules...
    [TEST] Generated tests for core: test_core_declarative.py
    [TEST] Generated tests for stream: test_stream_declarative.py
    [TEST] Generated integration playbook: test_all_declarative.yml

======================================================================
[+] Generated 49 declarative modules
======================================================================
```

---

## How Detection Works

### 1. Resource Discovery

The CRUD detector analyzes the OpenAPI spec and groups endpoints by base resource path:

```
/system/users          → Base resource path
/system/users/{id}     → ID-specific operations
```

### 2. Operation Mapping

For each resource, it identifies available operations:

| Operation Type | HTTP Method | Example Endpoint |
|----------------|-------------|------------------|
| List | GET | `/system/users` |
| Create | POST | `/system/users` |
| Get One | GET | `/system/users/{id}` |
| Update | PATCH/PUT | `/system/users/{id}` |
| Delete | DELETE | `/system/users/{id}` |

### 3. CRUD Validation

A resource must have:
- At least one read operation (list OR get_one)
- Create operation (POST)
- At least one modify operation (update OR delete)
- ID-based endpoint for get/update/delete

### 4. Module Generation

For each valid CRUD resource:
1. **Extract parameters** from POST operation request body schema
2. **Generate module code** with full declarative logic
3. **Create unit tests** with idempotency checks
4. **Add to integration playbook** for E2E testing

---

## Generated Module Structure

### Module Features

Each auto-generated declarative module includes:

- **Idempotent operations** - Safe to run multiple times
- **Check mode support** - Preview changes with `--check`
- **Diff mode support** - See exact changes with `--diff`
- **Automatic state detection** - Only changes what's needed
- **Full error handling** - Clear error messages
- **Complete documentation** - DOCUMENTATION, EXAMPLES, RETURN blocks

### Example Generated Module

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: cribl_user_declarative
short_description: Manage Cribl User (declarative)
description:
    - Declaratively manage Cribl User with idempotent operations.
    - Automatically detects if resource exists and only makes changes when needed.
    - Supports check mode and diff mode.
...
'''

EXAMPLES = r'''
# Ensure user exists
- name: Ensure user exists
  cribl.core.cribl_user:
    base_url: https://cribl.example.com
    token: "{{ auth_token }}"
    id: my_user
    email: user@example.com
    roles: [admin]
    state: present
'''
```

---

## Generated Tests

### Unit Tests

For each declarative module, the generator creates comprehensive unit tests:

```python
def test_user_create(self, mock_module, mock_client):
    """Test creating user."""
    # Tests resource creation

def test_user_idempotency(self, mock_module, mock_client):
    """Test that user is idempotent."""
    # Tests no changes made when state matches

def test_user_update(self, mock_module, mock_client):
    """Test updating user."""
    # Tests resource updates

def test_user_delete(self, mock_module, mock_client):
    """Test deleting user."""
    # Tests resource deletion

def test_user_delete_idempotency(self, mock_module, mock_client):
    """Test that delete is idempotent when resource doesn't exist."""
    # Tests idempotent deletion

def test_user_check_mode(self, mock_module, mock_client):
    """Test user check mode."""
    # Tests check mode doesn't make changes
```

### Integration Playbook

A comprehensive integration playbook is generated to test all modules against a real Cribl instance:

```yaml
---
- name: Test All Declarative Modules
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Test cribl_user_declarative - Create
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        username: "{{ cribl_username }}"
        password: "{{ cribl_password }}"
        id: test_user_ansible
        state: present
      register: user_create
    
    - name: Test cribl_user_declarative - Idempotency
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        username: "{{ cribl_username }}"
        password: "{{ cribl_password }}"
        id: test_user_ansible
        state: present
      register: user_idempotent
    
    - name: Verify idempotency
      assert:
        that:
          - user_create.changed == true
          - user_idempotent.changed == false
```

---

## Resource Name Detection

The generator intelligently converts API paths to resource names:

| API Path | Resource Name | Module Name |
|----------|---------------|-------------|
| `/system/users` | `user` | `cribl_user_declarative` |
| `/master/groups` | `worker_group` * | `cribl_worker_group_declarative` |
| `/pipelines` | `pipeline` | `cribl_pipeline_declarative` |
| `/system/roles` | `role` | `cribl_role_declarative` |
| `/system/outputs` | `output` | `cribl_output_declarative` |

\* Special case handling for common resources

---

## Advanced Usage

### Custom Parameter Extraction

The generator automatically extracts parameters from the POST operation's request body schema:

```yaml
# From OpenAPI spec:
/system/users:
  post:
    requestBody:
      content:
        application/json:
          schema:
            properties:
              id:
                type: string
              email:
                type: string
              roles:
                type: array
                items:
                  type: string

# Generated module parameters:
options:
  id:
    description: User ID
    type: str
    required: true
  email:
    description: User email address
    type: str
    required: false
  roles:
    description: List of role IDs
    type: list
    elements: str
    required: false
```

### Update Method Detection

The generator automatically detects whether to use PATCH or PUT for updates:

```python
# Automatically determined from OpenAPI spec:
- PATCH → Partial updates (most common)
- PUT → Full replacements
```

---

## Benefits

### For Users

- **Complete API Coverage** - All CRUD resources have declarative modules
- **Consistent Interface** - All modules follow the same pattern
- **Production Ready** - Full idempotency and error handling
- **Time Saving** - No need to chain GET/POST/PATCH/DELETE calls

### For Developers

- **Auto-Generated** - No manual module writing
- **Tested** - Unit and integration tests included
- **Maintainable** - Regenerate for new Cribl versions
- **Documented** - Full documentation auto-generated

### For CI/CD

- **Repeatable** - Same command produces same results
- **Testable** - Integration playbook ready to run
- **Version Controlled** - Track changes over time

---

## Updating for New Cribl Versions

When Cribl releases a new version with new API endpoints:

```bash
# 1. Download new OpenAPI spec
curl -o schemas/cribl-apidocs-latest.yml \
  https://docs.cribl.io/api/cribl-apidocs.yml

# 2. Regenerate everything
python scripts/generate_modules.py \
  --spec schemas/cribl-apidocs-latest.yml \
  --declarative \
  --clean

# 3. Review what changed
git diff build/

# 4. Run tests
pytest tests/unit/test_*_declarative.py
ansible-playbook tests/integration/test_all_declarative.yml
```

---

## Troubleshooting

### No Modules Generated for a Resource

Check if the resource has all required operations:
```bash
# Look in OpenAPI spec for:
- /resource (GET, POST)
- /resource/{id} (GET, PATCH/PUT, DELETE)
```

### Module Doesn't Detect Parameter

The generator extracts parameters from the POST operation's request body. Check:
1. POST operation has `requestBody`
2. Content type is `application/json`
3. Schema has `properties` defined

### Tests Failing

1. Check Cribl instance is accessible
2. Verify credentials in `env/test.env`
3. Check API endpoint hasn't changed

---

## Related Documentation

- [Declarative Modules Guide](DECLARATIVE.md) - Complete guide to using declarative modules
- [Generator Guide](GENERATOR.md) - Advanced generator usage
- [Testing Guide](TESTING.md) - Running tests
- [API Reference](API_REFERENCE.md) - All module documentation

---

