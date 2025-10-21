# Playbook Examples

Real-world examples for common Cribl automation tasks.

---

## Authentication Best Practice: Session Management

All examples now support session-based authentication for better performance and security.

```yaml
tasks:
  # Step 1: Create session once per playbook
  - name: Authenticate with Cribl
    cribl.core.auth_session:
      base_url: "{{ cribl_url }}"
      username: "{{ cribl_username }}"
      password: "{{ cribl_password }}"
      validate_certs: false
    register: cribl_session
    no_log: true

  # Step 2: Use session in all subsequent tasks
  - name: Your operation
    cribl.core.some_module:
      session: "{{ cribl_session.session }}"
      # ... your parameters ...
```

**Benefits:**
- Authenticate once, use everywhere
- Automatic token refresh 
- More efficient (no repeated authentication)
- More secure (credentials passed only once)

---

## Auto-Generated Examples

Each declarative module has auto-generated example playbooks:

**Location**: `build/ansible_collections/cribl/*/examples/`

- **Individual Examples** (`<resource>_example.yml`): CRUD operations for single resource
- **Combined Examples** (`declarative_resources.yml`): Managing multiple resources together

**Available Examples**:
- Core: 23 examples (user, role, worker_group, etc.)
- Stream: 17 examples (pipeline, input, output, parser, etc.)
- Edge: 2 examples (process, etc.)
- Search: 11 examples (dataset, dashboard, macro, etc.)

---

## Table of Contents

- [User Management](#user-management)
- [Worker Group Configuration](#worker-group-configuration)
- [System Monitoring](#system-monitoring)
- [Pipeline Management](#pipeline-management)
- [Bulk Operations](#bulk-operations)
- [Environment Promotion](#environment-promotion)

---

## User Management

### Create Users with Different Roles

```yaml
---
- name: Manage Cribl Users
  hosts: localhost
  gather_facts: false
  vars:
    cribl_url: https://cribl.example.com
    cribl_token: "{{ lookup('env', 'CRIBL_TOKEN') }}"
  
  tasks:
    - name: Ensure admin users exist
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: "{{ item.id }}"
        email: "{{ item.email }}"
        first: "{{ item.first }}"
        last: "{{ item.last }}"
        roles: "{{ item.roles }}"
        state: present
        validate_certs: true
      loop:
        - {id: admin1, email: admin1@example.com, first: Jane, last: Admin, roles: [admin]}
        - {id: admin2, email: admin2@example.com, first: John, last: Admin, roles: [admin]}

    - name: Ensure operator users exist
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: "{{ item.id }}"
        email: "{{ item.email }}"
        first: "{{ item.first }}"
        last: "{{ item.last }}"
        roles: [user]
        state: present
      loop:
        - {id: ops1, email: ops1@example.com, first: Operations, last: User1}
        - {id: ops2, email: ops2@example.com, first: Operations, last: User2}

    - name: Ensure viewer accounts exist
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: "{{ item.id }}"
        email: "{{ item.email }}"
        roles: [viewer]
        state: present
      loop:
        - {id: viewer1, email: viewer1@example.com}
        - {id: viewer2, email: viewer2@example.com}
```

### Disable and Re-enable Users

```yaml
---
- name: Manage User Status
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Disable user temporarily
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: vacation_user
        disabled: true
        state: present

    - name: Re-enable user
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: vacation_user
        disabled: false
        state: present
```

### Bulk User Cleanup

```yaml
---
- name: Cleanup Old Users
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Get all users
      cribl.core.system_users_get:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
      register: all_users

    - name: Remove test users
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: "{{ item.id }}"
        state: absent
      loop: "{{ all_users.response.items }}"
      when: item.id is match("test_.*")
```

---

## Worker Group Configuration

### Create Environment-Specific Groups

```yaml
---
- name: Configure Worker Groups
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Ensure production groups exist
      cribl.core.worker_group:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: "{{ item.id }}"
        description: "{{ item.description }}"
        tags: "{{ item.tags }}"
        state: present
      loop:
        - id: prod-us-east
          description: Production US East
          tags: [production, us-east-1]
        - id: prod-us-west
          description: Production US West
          tags: [production, us-west-2]
        - id: prod-eu-central
          description: Production EU Central
          tags: [production, eu-central-1]

    - name: Ensure staging groups exist
      cribl.core.worker_group:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: "{{ item }}"
        description: "Staging environment - {{ item }}"
        tags: [staging]
        state: present
      loop:
        - staging-us
        - staging-eu

    - name: Ensure development groups exist
      cribl.core.worker_group:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: dev-shared
        description: Shared development environment
        tags: [development]
        state: present
```

### Clone Worker Group Configuration

```yaml
---
- name: Clone Worker Group
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Get source worker group
      cribl.core.master_groups_id_get:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: prod-us-east
      register: source_group

    - name: Create cloned worker group
      cribl.core.worker_group:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: prod-us-east-dr
        description: "DR copy of {{ source_group.response.description }}"
        tags: "{{ source_group.response.tags | default([]) + ['disaster-recovery'] }}"
        state: present
```

---

## System Monitoring

### Health Check with Alerts

```yaml
---
- name: Monitor Cribl Health
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Check system health
      cribl.core.health_get:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
      register: health
      failed_when: health.response.status != "healthy"

    - name: Get system metrics
      cribl.core.system_instance_get:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
      register: instance

    - name: Display system info
      debug:
        msg:
          - "Cribl Version: {{ instance.response.version }}"
          - "Health: {{ health.response.status }}"
          - "Product: {{ instance.response.product }}"

    - name: Check input status
      cribl.core.system_inputs_get:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
      register: inputs

    - name: Alert if no inputs configured
      fail:
        msg: "WARNING: No inputs configured!"
      when: inputs.response.count == 0
      ignore_errors: true

    - name: Check output status
      cribl.core.system_outputs_get:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
      register: outputs

    - name: Alert if no outputs configured
      fail:
        msg: "WARNING: No outputs configured!"
      when: outputs.response.count == 0
      ignore_errors: true
```

### Scheduled Health Report

```yaml
---
- name: Generate Health Report
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Gather system info
      cribl.core.system_instance_get:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
      register: system

    - name: Get worker group status
      cribl.core.master_groups_get:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
      register: groups

    - name: Get user count
      cribl.core.system_users_get:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
      register: users

    - name: Create report
      copy:
        content: |
          Cribl Health Report
          ==================
          Date: {{ ansible_date_time.iso8601 }}
          
          System Information:
          - Version: {{ system.response.version }}
          - Product: {{ system.response.product }}
          - GUID: {{ system.response.guid }}
          
          Statistics:
          - Worker Groups: {{ groups.response.count }}
          - Users: {{ users.response.count }}
        dest: /tmp/cribl_health_{{ ansible_date_time.date }}.txt
```

---

## Pipeline Management

### List All Pipelines

```yaml
---
- name: Audit Pipelines
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Get all pipelines
      cribl.stream.pipelines_get:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
      register: pipelines

    - name: Display pipeline names
      debug:
        msg: "{{ pipelines.response.items | map(attribute='id') | list }}"

    - name: Save pipeline inventory
      copy:
        content: "{{ pipelines.response | to_nice_json }}"
        dest: /tmp/pipeline_inventory.json
```

---

## Bulk Operations

### Configure Multiple Resources from Inventory

```yaml
---
- name: Bulk Configuration from Inventory
  hosts: localhost
  gather_facts: false
  vars_files:
    - inventory.yml  # Contains lists of users, groups, etc.
  
  tasks:
    - name: Ensure all users from inventory exist
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: "{{ item.id }}"
        email: "{{ item.email }}"
        first: "{{ item.first | default(omit) }}"
        last: "{{ item.last | default(omit) }}"
        roles: "{{ item.roles }}"
        state: present
      loop: "{{ users }}"

    - name: Ensure all worker groups exist
      cribl.core.worker_group:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: "{{ item.id }}"
        description: "{{ item.description }}"
        tags: "{{ item.tags | default([]) }}"
        state: present
      loop: "{{ worker_groups }}"
```

**inventory.yml:**
```yaml
users:
  - id: user1
    email: user1@example.com
    roles: [admin]
  - id: user2
    email: user2@example.com
    roles: [user]

worker_groups:
  - id: production
    description: Production environment
    tags: [prod]
  - id: staging
    description: Staging environment
    tags: [stage]
```

### Parallel Deployment

```yaml
---
- name: Deploy to Multiple Cribl Instances
  hosts: cribl_instances
  gather_facts: false
  strategy: free  # Parallel execution
  
  tasks:
    - name: Ensure standard users exist
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: "{{ item.id }}"
        email: "{{ item.email }}"
        roles: "{{ item.roles }}"
        state: present
      loop: "{{ standard_users }}"
      delegate_to: localhost
```

---

## Environment Promotion

### Promote Configuration from Dev to Prod

```yaml
---
- name: Promote Configuration
  hosts: localhost
  gather_facts: false
  vars:
    dev_url: https://dev.cribl.example.com
    prod_url: https://prod.cribl.example.com
  
  tasks:
    # Export from Dev
    - name: Get dev worker groups
      cribl.core.master_groups_get:
        base_url: "{{ dev_url }}"
        token: "{{ dev_token }}"
      register: dev_groups

    - name: Get dev users
      cribl.core.system_users_get:
        base_url: "{{ dev_url }}"
        token: "{{ dev_token }}"
      register: dev_users

    # Import to Prod (only non-sensitive configs)
    - name: Promote worker groups to prod
      cribl.core.worker_group:
        base_url: "{{ prod_url }}"
        token: "{{ prod_token }}"
        id: "{{ item.id }}"
        description: "{{ item.description }} (promoted from dev)"
        state: present
      loop: "{{ dev_groups.response.items }}"
      when: "'test' not in item.id"

    - name: Create promotion report
      copy:
        content: |
          Promotion Report
          ===============
          Date: {{ ansible_date_time.iso8601 }}
          Source: {{ dev_url }}
          Target: {{ prod_url }}
          
          Promoted Resources:
          - Worker Groups: {{ dev_groups.response.count }}
        dest: /tmp/promotion_{{ ansible_date_time.date }}.txt
```

---

## Security Best Practices

### Using Ansible Vault

```yaml
---
- name: Secure Credential Management
  hosts: localhost
  gather_facts: false
  vars_files:
    - vault.yml  # Encrypted with ansible-vault
  
  tasks:
    - name: Manage users with vaulted credentials
      cribl.core.user:
        base_url: "{{ cribl_url }}"
        token: "{{ vault_cribl_token }}"
        id: secure_user
        email: secure@example.com
        roles: [admin]
        state: present
```

**Create vault:**
```bash
ansible-vault create vault.yml
```

**vault.yml:**
```yaml
vault_cribl_token: your-secret-token
cribl_url: https://cribl.example.com
```

**Run with vault:**
```bash
ansible-playbook playbook.yml --ask-vault-pass
```

---

## Testing Playbooks

### Dry Run with Check Mode

```bash
# See what would change without making changes
ansible-playbook playbook.yml --check --diff

# Verbose output for debugging
ansible-playbook playbook.yml -vvv

# Limit to specific tasks
ansible-playbook playbook.yml --tags users --check
```

### Conditional Execution

```yaml
---
- name: Conditional Configuration
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Configure production settings
      cribl.core.worker_group:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: production
        description: Production environment
        state: present
      when: environment == "production"

    - name: Configure dev settings
      cribl.core.worker_group:
        base_url: "{{ cribl_url }}"
        token: "{{ cribl_token }}"
        id: development
        description: Development environment
        state: present
      when: environment == "development"
```

---

## More Examples

Check the test playbooks for additional examples:
- [`tests/docker/playbooks/`](../tests/docker/playbooks/) - Docker integration test playbooks
- Each collection's `examples/` directory
