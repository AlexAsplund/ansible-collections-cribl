# Declarative Module Usage Guide

## Overview

The Cribl Ansible collections include **declarative modules** that provide idempotent, state-based resource management. These modules automatically detect the current state and only make changes when needed.

## Imperative vs Declarative

### Imperative (Generated Modules)

```yaml
# Always makes the API call
- name: Create user
  cribl.core.system_users_post:
    base_url: "{{ cribl_url }}"
    token: "{{ token }}"
    id: jsmith
    email: jsmith@example.com
```

**Characteristics:**
- Directly maps to API endpoints
- Always executes the operation
- No state checking
- May fail if resource already exists

### Declarative (Declarative Modules)

```yaml
# Only makes changes if needed
- name: Ensure user exists
  cribl.core.user:
    base_url: "{{ cribl_url }}"
    token: "{{ token }}"
    id: jsmith
    email: jsmith@example.com
    state: present
```

**Characteristics:**
- Describes desired end state
- Checks current state first
- Only makes changes when needed
- **Idempotent** - safe to run multiple times
- Supports check mode and diff

## Available Declarative Modules

### cribl.core Collection

- `cribl_user_declarative` - Manage users
- `cribl_worker_group_declarative` - Manage worker groups

### More coming soon...

Additional declarative modules can be created using the `CriblResource` base class.

## Key Features

### 1. Idempotency

Run the same playbook multiple times - only makes changes when needed:

```yaml
- name: Ensure user exists
  cribl.core.user:
    id: jsmith
    email: jsmith@example.com
    roles: [admin]
    state: present

# First run: Creates user (changed=true)
# Second run: No changes needed (changed=false)
# Third run: Still no changes (changed=false)
```

### 2. Check Mode (Dry Run)

See what would change without making changes:

```bash
# Check mode for entire playbook
ansible-playbook playbook.yml --check

# Or per task
- name: Check what would change
  cribl.core.user:
    id: jsmith
    email: newemail@example.com
    state: present
  check_mode: yes
```

### 3. Diff Mode

See exactly what will change:

```bash
# Run with diff
ansible-playbook playbook.yml --check --diff
```

Output:
```
TASK [Update user email]
changed: [localhost]
--- before
+++ after
@@ -1 +1 @@
-email: old@example.com
+email: new@example.com
```

### 4. State Management

**Present State** - Ensure resource exists:
```yaml
- name: Ensure user exists
  cribl.core.user:
    id: jsmith
    email: jsmith@example.com
    state: present
```

**Absent State** - Ensure resource does NOT exist:
```yaml
- name: Ensure user is removed
  cribl.core.user:
    id: jsmith
    state: absent
```

## Complete Example

```yaml
---
- name: Declarative Cribl Management
  hosts: localhost
  gather_facts: false
  
  tasks:
    # Ensure users exist with desired configuration
    - name: Ensure operations user exists
      cribl.core.user:
        base_url: https://cribl.example.com
        token: "{{ cribl_token }}"
        id: ops_user
        email: ops@example.com
        first: Operations
        last: User
        roles: [user]
        disabled: false
        state: present

    # Update user roles (idempotent)
    - name: Ensure admin user has correct roles
      cribl.core.user:
        base_url: https://cribl.example.com
        token: "{{ cribl_token }}"
        id: admin_user
        roles: [admin, user]
        state: present

    # Ensure worker groups exist
    - name: Ensure production worker group exists
      cribl.core.worker_group:
        base_url: https://cribl.example.com
        token: "{{ cribl_token }}"
        id: production
        description: Production environment
        state: present

    # Ensure test resources are removed
    - name: Ensure test user is absent
      cribl.core.user:
        base_url: https://cribl.example.com
        token: "{{ cribl_token }}"
        id: test_user
        state: absent
```

## Creating Custom Declarative Modules

### Step 1: Define Resource Class

```python
from ansible_collections.cribl.core.plugins.module_utils.cribl_declarative import CriblResource

class CriblMyResource(CriblResource):
    def __init__(self, module, client, resource_id):
        super().__init__(module, client)
        self.resource_id = resource_id

    def get_current_state(self):
        """Get current resource state."""
        try:
            return self.client.get(f"/api/endpoint/{self.resource_id}")
        except CriblAPIError as e:
            if "404" in str(e):
                return None
            raise

    def create_resource(self, desired_state):
        """Create resource."""
        return self.client.post("/api/endpoint", data=desired_state)

    def update_resource(self, current_state, desired_state):
        """Update resource."""
        return self.client.patch(
            f"/api/endpoint/{self.resource_id}", 
            data=desired_state
        )

    def delete_resource(self, current_state):
        """Delete resource."""
        return self.client.delete(f"/api/endpoint/{self.resource_id}")
```

### Step 2: Create Module

```python
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cribl.core.plugins.module_utils.cribl_declarative import (
    create_declarative_module_args
)

def main():
    argument_spec = create_declarative_module_args()
    argument_spec.update(dict(
        id=dict(type='str', required=True),
        # Add resource-specific parameters
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # Create client and resource
    client = CriblAPIClient(...)
    resource = CriblMyResource(module, client, module.params['id'])

    # Build desired state
    if module.params['state'] == 'present':
        desired_state = {...}
        result = resource.ensure_state('present', desired_state)
    else:
        result = resource.ensure_state('absent')

    module.exit_json(**result)
```

## Best Practices

### 1. Use Declarative for State Management

**Do:**
```yaml
- name: Ensure user has admin role
  cribl.core.user:
    id: jsmith
    roles: [admin]
    state: present
```

**Don't:**
```yaml
- name: Create user
  cribl.core.system_users_post:
    id: jsmith
```

### 2. Leverage Check Mode

Always test with `--check` first:

```bash
# Test without making changes
ansible-playbook playbook.yml --check --diff

# If looks good, run for real
ansible-playbook playbook.yml
```

### 3. Use State: absent

Instead of delete modules, use `state: absent`:

**Do:**
```yaml
- name: Ensure old user is removed
  cribl.core.user:
    id: old_user
    state: absent
```

### 4. Combine with Loops

```yaml
- name: Ensure all required users exist
  cribl.core.user:
    base_url: "{{ cribl_url }}"
    token: "{{ token }}"
    id: "{{ item.id }}"
    email: "{{ item.email }}"
    roles: "{{ item.roles }}"
    state: present
  loop:
    - {id: user1, email: user1@example.com, roles: [user]}
    - {id: user2, email: user2@example.com, roles: [admin]}
```

### 5. Use with_items for Bulk Operations

```yaml
- name: Ensure test resources are cleaned up
  cribl.core.user:
    base_url: "{{ cribl_url }}"
    token: "{{ token }}"
    id: "{{ item }}"
    state: absent
  with_items:
    - test_user_1
    - test_user_2
    - test_user_3
```

## Testing Declarative Modules

```python
def test_user_idempotency():
    # First run - creates user
    result1 = run_module(cribl_user_declarative, {
        'id': 'test_user',
        'email': 'test@example.com',
        'state': 'present'
    })
    assert result1['changed'] == True

    # Second run - no changes
    result2 = run_module(cribl_user_declarative, {
        'id': 'test_user',
        'email': 'test@example.com',
        'state': 'present'
    })
    assert result2['changed'] == False
```

## Migration Path

### Migrating from Imperative to Declarative

**Before (Imperative):**
```yaml
- name: Create user
  cribl.core.system_users_post:
    id: jsmith
    email: jsmith@example.com
  ignore_errors: true  # Needed if user exists

- name: Update user
  cribl.core.system_users_id_patch:
    id: jsmith
    roles: [admin]
```

**After (Declarative):**
```yaml
- name: Ensure user exists with correct config
  cribl.core.user:
    id: jsmith
    email: jsmith@example.com
    roles: [admin]
    state: present
```

## Summary

| Feature | Imperative | Declarative |
|---------|-----------|-------------|
| Idempotent | No | Yes |
| Check Mode | Limited | Full Support |
| Diff Mode | No | Yes |
| State Checking | No | Yes |
| API Calls | Every run | Only when needed |
| Complexity | Low | Medium |
| Best For | One-off operations | Configuration management |

**Recommendation:** Use **declarative modules** for all configuration management and state enforcement. Use imperative modules only for one-off operations or read-only queries.

