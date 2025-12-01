

# Cribl Cloud OAuth2 Authentication

This document explains how to authenticate with Cribl Cloud using OAuth2 Client Credentials in the Cribl Ansible collections.

## Overview

The Cribl Ansible collections support two authentication methods:

1. **Username/Password** - Traditional authentication for on-prem Cribl instances
2. **OAuth2 Client Credentials** - Modern authentication for Cribl Cloud (NEW!)

The `cribl.core.auth_session` module automatically detects which method to use based on the parameters you provide.

## Quick Start

### OAuth2 Authentication (Cribl Cloud)

```yaml
- name: Authenticate with Cribl Cloud
  cribl.core.auth_session:
    base_url: https://main-myorg.cribl.cloud
    client_id: "{{ cribl_client_id }}"
    client_secret: "{{ cribl_client_secret }}"
    validate_certs: true
  register: cribl_session
  no_log: true
```

### Traditional Authentication (On-Prem)

```yaml
- name: Authenticate with on-prem Cribl
  cribl.core.auth_session:
    base_url: https://cribl.example.com
    username: admin
    password: "{{ cribl_password }}"
    validate_certs: false
  register: cribl_session
  no_log: true
```

## Getting Cribl Cloud API Credentials

### Step 1: Access Cribl Cloud

1. Log in to your Cribl Cloud organization
2. Navigate to **Settings** → **API Credentials**

### Step 2: Create API Credentials

1. Click **Add Credentials** or **Create New**
2. Provide a description (e.g., "Ansible Automation")
3. Select appropriate scopes/permissions
4. Click **Save**

### Step 3: Save Credentials

You'll receive:
- **Client ID**: A unique identifier for your application
- **Client Secret**: A secret key (shown only once - save it securely!)

**⚠️ Important**: The client secret is shown only once. Store it securely immediately.

## OAuth2 Authentication Details

### How It Works

```
┌──────────┐                  ┌─────────────────┐                 ┌──────────────┐
│ Ansible  │                  │ Cribl Cloud     │                 │ Cribl Cloud  │
│ Playbook │                  │ OAuth2 Endpoint │                 │ API          │
└────┬─────┘                  └────────┬────────┘                 └──────┬───────┘
     │                                 │                                  │
     │ 1. POST /oauth/token            │                                  │
     │    (client_id + client_secret)  │                                  │
     ├─────────────────────────────────>                                  │
     │                                 │                                  │
     │ 2. Returns access_token         │                                  │
     │    (expires_in: 3600s)          │                                  │
     <─────────────────────────────────┤                                  │
     │                                 │                                  │
     │ 3. API requests with token      │                                  │
     │    Authorization: Bearer <token>│                                  │
     ├────────────────────────────────────────────────────────────────────>
     │                                 │                                  │
     │ 4. Token auto-refreshes when    │                                  │
     │    expired (transparent)        │                                  │
     ├─────────────────────────────────>                                  │
     │                                 │                                  │
```

### OAuth2 Flow Details

1. **Initial Authentication**:
   ```
   POST https://login.cribl.cloud/oauth/token
   Content-Type: application/json
   
   {
     "grant_type": "client_credentials",
     "client_id": "your_client_id",
     "client_secret": "your_client_secret",
     "audience": "https://api.cribl.cloud"
   }
   ```

2. **Token Response**:
   ```json
   {
     "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "Bearer",
     "expires_in": 3600
   }
   ```

3. **API Requests**:
   ```
   GET https://main-myorg.cribl.cloud/api/v1/system/users
   Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

4. **Automatic Token Refresh**:
   - The module tracks token expiry
   - Automatically refreshes 5 minutes before expiration
   - Completely transparent to your playbooks

## Authentication Method Selection

The `auth_session` module automatically selects the authentication method:

| Parameters Provided | Auth Method | Use Case |
|---------------------|-------------|----------|
| `client_id` + `client_secret` | OAuth2 | Cribl Cloud |
| `username` + `password` | Traditional | On-prem Cribl |

You cannot mix authentication methods - they are mutually exclusive.

## Complete Examples

### Example 1: Basic Cribl Cloud Authentication

```yaml
---
- name: Cribl Cloud Operations
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Authenticate with Cribl Cloud
      cribl.core.auth_session:
        base_url: https://main-myorg.cribl.cloud
        client_id: "{{ lookup('env', 'CRIBL_CLIENT_ID') }}"
        client_secret: "{{ lookup('env', 'CRIBL_CLIENT_SECRET') }}"
        validate_certs: true
      register: session
      no_log: true
    
    - name: Get system info
      cribl.core.system_instance_get:
        session: "{{ session.session }}"
      register: info
    
    - name: Display info
      debug:
        msg: "Cribl Cloud version: {{ info.response.items[0].version }}"
```

### Example 2: Worker Group Operations

```yaml
---
- name: Manage Cribl Cloud Worker Groups
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Authenticate
      cribl.core.auth_session:
        base_url: https://main-myorg.cribl.cloud
        client_id: "{{ cribl_client_id }}"
        client_secret: "{{ cribl_client_secret }}"
      register: session
      no_log: true
    
    - name: Create pipeline in production worker group
      cribl.stream.pipeline:
        session: "{{ session.session }}"
        worker_group: production
        id: data_processing
        conf:
          description: Production data processing pipeline
        state: present
```

### Example 3: Mixed Environments

```yaml
---
- name: Manage Multiple Cribl Instances
  hosts: localhost
  gather_facts: false
  
  tasks:
    # Cribl Cloud with OAuth2
    - name: Authenticate with Cribl Cloud
      cribl.core.auth_session:
        base_url: https://main-myorg.cribl.cloud
        client_id: "{{ cloud_client_id }}"
        client_secret: "{{ cloud_client_secret }}"
      register: cloud_session
      no_log: true
    
    # On-prem with username/password
    - name: Authenticate with on-prem
      cribl.core.auth_session:
        base_url: https://cribl-onprem.local
        username: admin
        password: "{{ onprem_password }}"
        validate_certs: false
      register: onprem_session
      no_log: true
    
    # Use both sessions
    - name: Get cloud users
      cribl.core.system_users_get:
        session: "{{ cloud_session.session }}"
      register: cloud_users
    
    - name: Get on-prem users
      cribl.core.system_users_get:
        session: "{{ onprem_session.session }}"
      register: onprem_users
```

## Security Best Practices

### 1. Use Ansible Vault

**Encrypt individual variables**:
```bash
ansible-vault encrypt_string 'your_client_id' --name 'cribl_client_id'
ansible-vault encrypt_string 'your_client_secret' --name 'cribl_client_secret'
```

**Use in playbook**:
```yaml
vars:
  cribl_client_id: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    ...
  cribl_client_secret: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    ...
```

### 2. Use Vault Files

**vault.yml (encrypted)**:
```yaml
---
vault_cribl_client_id: your_actual_client_id
vault_cribl_client_secret: your_actual_client_secret
```

**Encrypt**:
```bash
ansible-vault encrypt vault.yml
```

**Use in playbook**:
```yaml
---
- name: Secure playbook
  hosts: localhost
  vars_files:
    - vault.yml
  
  tasks:
    - name: Authenticate
      cribl.core.auth_session:
        base_url: "{{ cribl_url }}"
        client_id: "{{ vault_cribl_client_id }}"
        client_secret: "{{ vault_cribl_client_secret }}"
      register: session
      no_log: true
```

### 3. Environment Variables

```bash
export CRIBL_CLIENT_ID="your_client_id"
export CRIBL_CLIENT_SECRET="your_client_secret"
```

```yaml
- name: Authenticate
  cribl.core.auth_session:
    base_url: "{{ cribl_url }}"
    client_id: "{{ lookup('env', 'CRIBL_CLIENT_ID') }}"
    client_secret: "{{ lookup('env', 'CRIBL_CLIENT_SECRET') }}"
  register: session
  no_log: true
```

### 4. Always Use no_log

```yaml
- name: Authenticate
  cribl.core.auth_session:
    base_url: "{{ cribl_url }}"
    client_id: "{{ cribl_client_id }}"
    client_secret: "{{ cribl_client_secret }}"
  register: session
  no_log: true  # ← Always use this!
```

### 5. Limit API Credential Scope

In Cribl Cloud:
- Create separate credentials for different automation tasks
- Apply principle of least privilege
- Use descriptive names for tracking
- Regularly review and rotate credentials

### 6. SSL Certificate Validation

For **Cribl Cloud** (production):
```yaml
validate_certs: true  # Always validate SSL certs in production
```

For **on-prem/development**:
```yaml
validate_certs: false  # Only for self-signed certs in dev
```

## Custom OAuth2 Endpoint

If you have a custom OAuth2 setup:

```yaml
- name: Custom OAuth2 endpoint
  cribl.core.auth_session:
    base_url: https://custom.cribl.io
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    oauth_token_url: https://custom-auth.cribl.io/oauth/token
  register: session
  no_log: true
```

## Token Management

### Automatic Token Refresh

The session automatically refreshes tokens:
- Checks expiry before each request
- Refreshes 5 minutes before expiration
- Completely transparent to your playbooks
- No manual intervention needed

### Token Lifetime

- **Default**: 3600 seconds (1 hour)
- **Refresh**: Automatic 5 minutes before expiry
- **Stored**: In session object
- **Reusable**: Across entire playbook

### Long-Running Playbooks

For playbooks that run longer than token lifetime:

```yaml
- name: Long-running operations
  hosts: localhost
  tasks:
    - name: Authenticate once
      cribl.core.auth_session:
        base_url: "{{ cribl_url }}"
        client_id: "{{ client_id }}"
        client_secret: "{{ client_secret }}"
      register: session
      no_log: true
    
    # Token automatically refreshes for all these tasks
    - name: Operation 1 (minute 0)
      cribl.core.system_users_get:
        session: "{{ session.session }}"
    
    - name: Wait 30 minutes
      pause:
        minutes: 30
    
    - name: Operation 2 (minute 30)
      # Token still valid or auto-refreshed
      cribl.core.system_users_get:
        session: "{{ session.session }}"
    
    - name: Wait another 40 minutes
      pause:
        minutes: 40
    
    - name: Operation 3 (minute 70)
      # Token was auto-refreshed (expired at 60 min)
      cribl.core.system_users_get:
        session: "{{ session.session }}"
```

## Troubleshooting

### Invalid Client Credentials

**Error**:
```
OAuth2 authentication failed: 401 Unauthorized
```

**Solutions**:
- Verify client_id is correct
- Verify client_secret is correct (check for extra spaces/newlines)
- Ensure credentials haven't been revoked
- Check credentials are for the correct organization

### Invalid Audience

**Error**:
```
OAuth2 authentication failed: 403 Forbidden
```

**Solution**:
- The audience is automatically set to `https://api.cribl.cloud`
- For custom setups, this may need adjustment (contact Cribl support)

### Token Expired

**Error**:
```
401 Unauthorized
```

**Solution**:
- Should not happen with automatic refresh
- If it does, indicates a bug - please report
- Workaround: Re-authenticate

### SSL Certificate Errors

**Error**:
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions**:
- For Cribl Cloud: Use `validate_certs: true` (certificates are valid)
- For on-prem with self-signed: Use `validate_certs: false` (development only)
- For production on-prem: Install proper SSL certificates

## Migration Guide

### From Username/Password to OAuth2

**Old playbook**:
```yaml
- name: Authenticate
  cribl.core.auth_session:
    base_url: https://main-myorg.cribl.cloud
    username: admin
    password: "{{ password }}"
  register: session
```

**New playbook**:
```yaml
- name: Authenticate
  cribl.core.auth_session:
    base_url: https://main-myorg.cribl.cloud
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
  register: session
```

**Changes needed**:
1. Create API credentials in Cribl Cloud
2. Update playbook parameters
3. Update vault/secrets
4. Test thoroughly

**Benefits**:
- More secure (no user passwords in automation)
- Better audit trail (API credentials tracked separately)
- Finer-grained permissions
- Easier credential rotation

## API Reference

### auth_session Module Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `base_url` | string | Yes | - | Cribl instance URL |
| `username` | string | No* | - | Username for traditional auth |
| `password` | string | No* | - | Password for traditional auth |
| `client_id` | string | No* | - | OAuth2 client ID |
| `client_secret` | string | No* | - | OAuth2 client secret |
| `oauth_token_url` | string | No | `https://login.cribl.cloud/oauth/token` | OAuth2 token endpoint |
| `validate_certs` | bool | No | `false` | Validate SSL certificates |
| `timeout` | int | No | `30` | Request timeout (seconds) |

\* Either `username`/`password` OR `client_id`/`client_secret` is required

### Session Object Structure

```yaml
session:
  base_url: "https://main-myorg.cribl.cloud"
  token: "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
  token_expiry: 1701234567.89
  auth_type: "oauth2"
  validate_certs: true
  timeout: 30
```

## See Also

- [Example Playbook](../examples/cribl_cloud_oauth2_example.yml)
- [Worker Group Documentation](WORKER_GROUPS.md)
- [Cribl Cloud Documentation](https://docs.cribl.io/cloud/)
- [Cribl API Reference](https://docs.cribl.io/cribl-as-code/api-reference/)

## Support

For issues or questions:
- GitHub Issues: https://github.com/cribl/ansible-cribl-collection
- Cribl Community: https://cribl.io/community/
- Cribl Support: https://portal.support.cribl.io

