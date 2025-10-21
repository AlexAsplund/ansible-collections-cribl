# API Reference

Quick reference for all Cribl Ansible modules.

---

## Common Parameters

All modules support these authentication parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `base_url` | string | Yes | Cribl instance URL (e.g., `https://cribl.example.com`) |
| `username` | string | Yes* | Username for authentication |
| `password` | string | Yes* | Password for authentication |
| `token` | string | Yes* | API token (alternative to username/password) |
| `validate_certs` | boolean | No | Validate SSL certificates (default: `false`) |

\* Either `username`/`password` OR `token` is required

---

## Collections Overview

### cribl.core (276 modules)

**Authentication & Users:**
- `auth_login_post` - Login and get token
- `auth_logout_post` - Logout
- `system_users_get` - List users
- `system_users_post` - Create user
- `system_users_id_get` - Get user details
- `system_users_id_patch` - Update user
- `system_users_id_delete` - Delete user
- `user_declarative` ⭐ - Manage users (declarative)

**Worker Groups:**
- `master_groups_get` - List worker groups
- `master_groups_post` - Create worker group
- `master_groups_id_get` - Get worker group
- `master_groups_id_patch` - Update worker group
- `master_groups_id_delete` - Delete worker group
- `worker_group_declarative` ⭐ - Manage worker groups (declarative)

**System:**
- `health_get` - Get system health
- `system_instance_get` - Get instance info
- `version_get` - Get version
- `system_settings_get` - Get settings
- `system_settings_patch` - Update settings

**Certificates & Secrets:**
- `system_certificates_get` - List certificates
- `system_certificates_post` - Upload certificate
- `system_secrets_get` - List secrets
- `system_secrets_post` - Create secret

**Roles & Permissions:**
- `system_roles_get` - List roles
- `system_roles_post` - Create role
- `system_roles_id_get` - Get role
- `system_roles_id_patch` - Update role

---

### cribl.stream (127 modules)

**Pipelines:**
- `pipelines_get` - List pipelines
- `pipelines_post` - Create pipeline
- `pipelines_id_get` - Get pipeline
- `pipelines_id_patch` - Update pipeline
- `pipelines_id_delete` - Delete pipeline

**Routes:**
- `routes_get` - List routes
- `routes_post` - Create route
- `routes_id_get` - Get route
- `routes_id_patch` - Update route
- `routes_id_delete` - Delete route

**Inputs:**
- `system_inputs_get` - List inputs
- `system_inputs_post` - Create input
- `system_inputs_id_get` - Get input
- `system_inputs_id_patch` - Update input
- `system_inputs_id_delete` - Delete input

**Outputs:**
- `system_outputs_get` - List outputs
- `system_outputs_post` - Create output
- `system_outputs_id_get` - Get output
- `system_outputs_id_patch` - Update output
- `system_outputs_id_delete` - Delete output

**Packs:**
- `packs_get` - List packs
- `packs_post` - Create pack
- `packs_id_get` - Get pack
- `packs_id_patch` - Update pack
- `packs_id_delete` - Delete pack

**Library Items:**
- `lib_parsers_get` - List parsers
- `lib_schemas_get` - List schemas
- `lib_variables_get` - List variables
- `lib_grok_get` - List grok patterns
- `lib_regex_get` - List regex patterns

**Functions:**
- `functions_get` - List functions
- `functions_post` - Create function
- `functions_id_get` - Get function
- `functions_id_patch` - Update function

---

### cribl.search (80 modules)

**Datasets:**
- `datasets_get` - List datasets
- `datasets_post` - Create dataset
- `datasets_id_get` - Get dataset
- `datasets_id_patch` - Update dataset
- `datasets_id_delete` - Delete dataset

**Search Jobs:**
- `jobs_get` - List search jobs
- `jobs_post` - Create search job
- `jobs_id_get` - Get job status
- `jobs_id_delete` - Cancel job

**Dashboards:**
- `dashboards_get` - List dashboards
- `dashboards_post` - Create dashboard
- `dashboards_id_get` - Get dashboard
- `dashboards_id_patch` - Update dashboard
- `dashboards_id_delete` - Delete dashboard

**Saved Searches:**
- `saved_searches_get` - List saved searches
- `saved_searches_post` - Create saved search
- `saved_searches_id_get` - Get saved search
- `saved_searches_id_patch` - Update saved search

**Macros:**
- `macros_get` - List macros
- `macros_post` - Create macro
- `macros_id_get` - Get macro
- `macros_id_patch` - Update macro

---

### cribl.edge (19 modules)

**Processes:**
- `processes_get` - List edge processes
- `processes_id_get` - Get process details

**Containers:**
- `containers_get` - List containers
- `containers_id_get` - Get container details

**AppScope:**
- `appscope_processes_get` - List AppScope processes
- `appscope_processes_post` - Attach AppScope
- `appscope_processes_id_get` - Get AppScope process
- `appscope_processes_id_put` - Update AppScope process
- `appscope_processes_id_delete` - Detach AppScope

**Events:**
- `events_collectors_get` - List event collectors
- `events_query_get` - Query events

**Files:**
- `file_ingest_post` - Ingest file
- `file_sample_get` - Sample file
- `fileinspect_get` - Inspect file

**Logs:**
- `logs_get` - Get edge logs
- `kube_logs_post` - Get Kubernetes logs
- `kube_proxy_get` - Kubernetes proxy

---

### cribl.lake (11 modules)

**Datasets:**
- `lakes_id_datasets_get` - List lake datasets
- `lakes_id_datasets_post` - Create dataset
- `lakes_id_datasets_id_get` - Get dataset
- `lakes_id_datasets_id_patch` - Update dataset
- `lakes_id_datasets_id_delete` - Delete dataset
- `lakes_id_datasets_patch` - Bulk update datasets

**Storage Locations:**
- `lakes_id_storage_locations_get` - List storage locations
- `lakes_id_storage_locations_post` - Create storage location
- `lakes_id_storage_locations_id_get` - Get storage location
- `lakes_id_storage_locations_id_patch` - Update storage location
- `lakes_id_storage_locations_id_delete` - Delete storage location

---

## Declarative Modules

These modules provide idempotent, state-based resource management:

### cribl_user_declarative

**Purpose:** Manage Cribl users declaratively

**Parameters:**
- `id` (string, required) - User ID
- `email` (string) - Email address
- `first` (string) - First name
- `last` (string) - Last name
- `roles` (list) - List of role IDs
- `disabled` (boolean) - Disable user
- `state` (string) - `present` or `absent`

**Example:**
```yaml
- name: Ensure user exists
  cribl.core.user:
    base_url: https://cribl.example.com
    session: "{{ cribl_session.session }}"
    id: jsmith
    email: jsmith@example.com
    first: John
    last: Smith
    roles: [admin]
    state: present
```

**Features:**
- Idempotent
- Check mode support
- Diff support
- Only makes changes when needed

---

### cribl_worker_group_declarative

**Purpose:** Manage worker groups declaratively

**Parameters:**
- `id` (string, required) - Worker group ID
- `description` (string) - Description
- `tags` (list) - List of tags
- `state` (string) - `present` or `absent`

**Example:**
```yaml
- name: Ensure worker group exists
  cribl.core.worker_group:
    base_url: https://cribl.example.com
    session: "{{ cribl_session.session }}"
    id: production
    description: Production environment
    tags: [prod, us-east-1]
    state: present
```

**Features:**
- Idempotent
- Check mode support
- Diff support
- Only makes changes when needed

---

## Module Naming Convention

All imperative modules follow this pattern:

```
cribl_<endpoint_path>_<http_method>
```

**Examples:**

| API Endpoint | HTTP Method | Module Name |
|--------------|-------------|-------------|
| `/system/users` | GET | `system_users_get` |
| `/system/users` | POST | `system_users_post` |
| `/system/users/{id}` | GET | `system_users_id_get` |
| `/system/users/{id}` | PATCH | `system_users_id_patch` |
| `/system/users/{id}` | DELETE | `system_users_id_delete` |
| `/master/groups` | GET | `master_groups_get` |
| `/pipelines/{id}` | GET | `pipelines_id_get` |

---

## Finding Modules

### List All Modules in a Collection

```bash
ansible-doc -t module -l cribl.core | grep cribl
ansible-doc -t module -l cribl.stream | grep cribl
```

### View Module Documentation

```bash
ansible-doc cribl.core.system_users_get
ansible-doc cribl.core.user
ansible-doc cribl.stream.pipelines_get
```

### Search for Specific Modules

```bash
# Find all user-related modules
ansible-doc -t module -l cribl.core | grep user

# Find all pipeline modules
ansible-doc -t module -l cribl.stream | grep pipeline
```

---

## Response Format

All modules return a standard response:

```yaml
response:
  description: API response data
  returned: success
  type: dict
  sample:
    items: [...]      # For list operations
    count: 10         # Number of items
    # ... other response fields

changed:
  description: Whether a change was made
  returned: always
  type: bool

failed:
  description: Whether the module failed
  returned: always
  type: bool

msg:
  description: Human-readable message
  returned: when changed or failed
  type: str
```

**Example Usage:**
```yaml
- name: Get users
  cribl.core.system_users_get:
    base_url: "{{ cribl_url }}"
    session: "{{ cribl_session.session }}"
  register: result

- name: Display user count
  debug:
    msg: "Found {{ result.response.count }} users"

- name: Show all usernames
  debug:
    msg: "{{ result.response.items | map(attribute='id') | list }}"
```

---

## Error Handling

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 401 | Unauthorized | Invalid credentials or expired token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (POST) or version mismatch |
| 422 | Validation Error | Invalid parameters |
| 500 | Server Error | Cribl internal error |

### Handling Errors

```yaml
- name: Try to get user
  cribl.core.system_users_id_get:
    base_url: "{{ cribl_url }}"
    session: "{{ cribl_session.session }}"
    id: unknown_user
  register: result
  ignore_errors: true

- name: Handle error
  debug:
    msg: "User not found"
  when: result.failed and '404' in result.msg
```

---

## Additional Resources

- [Cribl API Documentation](https://docs.cribl.io/cribl-as-code/api-reference/)
- [Ansible Module Development](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
- [Example Playbooks](EXAMPLES.md)
- [Declarative Modules Guide](DECLARATIVE.md)

**For complete module documentation, use `ansible-doc`:**
```bash
ansible-doc cribl.core.<module_name>
```
