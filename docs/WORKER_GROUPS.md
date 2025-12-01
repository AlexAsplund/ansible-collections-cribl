# Worker Group-Specific Resource Management

This document describes the worker group support available in Cribl Ansible declarative modules.

## Overview

All declarative modules in the Cribl Ansible collections now support the `worker_group` parameter, which allows you to manage resources specific to individual worker groups or fleets.

## What is a Worker Group?

In Cribl Stream's distributed deployment architecture:
- **Worker Groups** are collections of worker nodes that process data
- Each worker group can have its own configuration for pipelines, routes, inputs, outputs, etc.
- The **Leader Node** manages worker groups and their configurations
- Resources can be **global** (managed on the leader) or **worker group-specific**

## API Endpoint Transformation

When you specify the `worker_group` parameter, the module automatically transforms the API endpoint:

| Without worker_group | With worker_group='production' |
|---------------------|--------------------------------|
| `/pipelines` | `/m/production/pipelines` |
| `/routes` | `/m/production/routes` |
| `/system/inputs` | `/m/production/system/inputs` |
| `/system/outputs` | `/m/production/system/outputs` |
| `/system/projects` | `/m/production/system/projects` |

## Supported Modules

The `worker_group` parameter is available in ALL declarative modules:

### cribl.stream Collection
- `pipeline` - Manage pipelines
- `route` - Manage routes
- `input` - Manage inputs/sources
- `output` - Manage outputs/destinations
- `pack` - Manage packs
- `var` - Manage variables
- `parser` - Manage parsers
- `breaker` - Manage event breakers
- `grok` - Manage grok patterns
- `regex` - Manage regex patterns
- `schema` - Manage schemas
- And more...

### cribl.core Collection
- `project` - Manage projects
- `lookup` - Manage lookup tables
- `certificate` - Manage certificates (typically global)
- `secret` - Manage secrets (typically global)
- `user` - Manage users (typically global)
- `role` - Manage roles (typically global)
- And more...

## Usage Examples

### Basic Usage

```yaml
# Global resource (no worker group specified)
- name: Create global pipeline
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: my_pipeline
    state: present

# Worker group-specific resource
- name: Create pipeline in production worker group
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: my_pipeline
    worker_group: production
    state: present
```

### Same Resource, Different Worker Groups

You can create resources with the same ID in different worker groups:

```yaml
- name: Configure input in production
  cribl.stream.input:
    session: "{{ cribl_session.session }}"
    id: syslog_514
    worker_group: production
    type: tcp
    port: 5514
    state: present

- name: Configure input in staging
  cribl.stream.input:
    session: "{{ cribl_session.session }}"
    id: syslog_514
    worker_group: staging
    type: tcp
    port: 5515  # Different port
    state: present
```

### Loop Through Worker Groups

```yaml
- name: Deploy pipeline to multiple worker groups
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: data_enrichment
    worker_group: "{{ item }}"
    conf:
      description: "Data enrichment for {{ item }}"
      functions:
        - id: eval
          conf:
            add:
              - name: worker_group
                value: "'{{ item }}'"
    state: present
  loop:
    - production
    - staging
    - development
```

### Environment-Specific Configurations

```yaml
- name: Configure environment-specific outputs
  cribl.stream.output:
    session: "{{ cribl_session.session }}"
    id: splunk_main
    worker_group: "{{ item.group }}"
    type: splunk
    host: "{{ item.host }}"
    port: 9997
    state: present
  loop:
    - group: us-east-prod
      host: splunk-us-east.example.com
    - group: us-west-prod
      host: splunk-us-west.example.com
    - group: eu-prod
      host: splunk-eu.example.com
```

## Common Use Cases

### 1. Multi-Environment Management

Deploy different configurations to production, staging, and development worker groups:

```yaml
- name: Deploy to environments
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: processing_pipeline
    worker_group: "{{ item.env }}"
    conf:
      description: "{{ item.description }}"
      # Environment-specific configuration
    state: present
  loop:
    - env: production
      description: Production processing with full features
    - env: staging
      description: Staging with debug logging
    - env: development
      description: Development with verbose output
```

### 2. Geographic Distribution

Configure region-specific settings:

```yaml
- name: Configure regional outputs
  cribl.stream.output:
    session: "{{ cribl_session.session }}"
    id: s3_archive
    worker_group: "{{ item.region }}"
    type: s3
    bucket: "cribl-data-{{ item.region }}"
    region: "{{ item.aws_region }}"
    state: present
  loop:
    - region: us-east
      aws_region: us-east-1
    - region: us-west
      aws_region: us-west-2
    - region: eu-west
      aws_region: eu-west-1
```

### 3. Multi-Tenant Configurations

Isolate configurations per tenant:

```yaml
- name: Configure tenant-specific pipelines
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: tenant_pipeline
    worker_group: "tenant-{{ item.id }}"
    conf:
      description: "Pipeline for {{ item.name }}"
      # Tenant-specific processing
    state: present
  loop: "{{ tenants }}"
```

### 4. Canary/Blue-Green Deployments

Test new configurations in a subset of workers before full rollout:

```yaml
# Step 1: Deploy to canary
- name: Deploy new config to canary
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: new_feature
    worker_group: canary
    conf:
      description: New feature in canary testing
    state: present

# Step 2: Monitor and validate...

# Step 3: Deploy to production
- name: Deploy validated config to production
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: new_feature
    worker_group: production
    conf:
      description: New feature deployed to production
    state: present
```

### 5. Cleanup and Maintenance

Remove resources from specific worker groups while keeping them in others:

```yaml
- name: Remove deprecated pipeline from production
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: old_pipeline
    worker_group: production
    state: absent

- name: Keep in legacy worker group for backward compatibility
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: old_pipeline
    worker_group: legacy-systems
    state: present
```

## Best Practices

### 1. Use Variables for Worker Group Names

```yaml
vars:
  prod_group: production
  stage_group: staging

tasks:
  - name: Deploy to production
    cribl.stream.pipeline:
      worker_group: "{{ prod_group }}"
      # ...
```

### 2. Document Worker Group Usage

Add comments or use descriptive names:

```yaml
- name: Configure production worker group input
  cribl.stream.input:
    id: syslog_prod
    worker_group: production  # Production environment only
    # ...
```

### 3. Validate Worker Group Exists

Use the worker_group module first:

```yaml
- name: Ensure worker group exists
  cribl.core.worker_group:
    session: "{{ cribl_session.session }}"
    id: production
    description: Production worker group
    state: present

- name: Configure resources in worker group
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    worker_group: production
    # ...
```

### 4. Use Check Mode for Safety

Test changes before applying:

```yaml
- name: Test configuration changes
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    worker_group: production
    # ...
  check_mode: true
```

### 5. Global vs Worker Group Resources

Some resources are typically global:
- **Global**: Users, roles, certificates, secrets, global lookup tables
- **Worker Group**: Pipelines, routes, inputs, outputs, worker-specific projects

```yaml
# Global certificate (omit worker_group)
- name: Create company certificate
  cribl.core.certificate:
    session: "{{ cribl_session.session }}"
    id: company_cert
    state: present

# Worker group-specific pipeline
- name: Create processing pipeline
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: processing
    worker_group: production
    state: present
```

## Backward Compatibility

The `worker_group` parameter is **optional** and **backward compatible**:

- **Existing playbooks** that don't specify `worker_group` continue to work unchanged
- **Default behavior**: When `worker_group` is omitted, resources are managed globally
- **No breaking changes**: All existing functionality remains the same

## Troubleshooting

### Error: Worker Group Not Found

```
Failed to get current state from /m/production/pipelines: 404
```

**Solution**: Ensure the worker group exists first:

```yaml
- name: Create worker group
  cribl.core.worker_group:
    session: "{{ cribl_session.session }}"
    id: production
    state: present
```

### Different Behavior: Global vs Worker Group

If a resource exists globally but you're trying to manage it in a worker group (or vice versa), they are treated as separate resources:

```yaml
# This creates a GLOBAL pipeline
- name: Global pipeline
  cribl.stream.pipeline:
    id: my_pipeline
    # No worker_group specified

# This creates a DIFFERENT pipeline in the worker group
- name: Worker group pipeline
  cribl.stream.pipeline:
    id: my_pipeline
    worker_group: production
```

These are **separate resources** with the same ID but in different contexts.

## Migration Guide

### Migrating from Imperative Modules

**Old approach** (imperative modules with groupId):

```yaml
- name: Get pipelines in worker group
  cribl.core.m_id_system_pipelines_get:
    groupId: production
  register: result
```

**New approach** (declarative with worker_group):

```yaml
- name: Manage pipeline in worker group
  cribl.stream.pipeline:
    id: my_pipeline
    worker_group: production
    state: present
```

## See Also

- [Example Playbook: worker_group_declarative_example.yml](../examples/worker_group_declarative_example.yml)
- [Example Playbook: worker_group_resources_example.yml](../build/ansible_collections/cribl/stream/examples/worker_group_resources_example.yml)
- [Cribl Distributed Deployment Documentation](https://docs.cribl.io/stream/deploy-distributed/)
- [API Reference](API_REFERENCE.md)

## Support

For issues or questions:
- GitHub Issues: https://github.com/cribl/ansible-cribl-collection
- Cribl Community: https://cribl.io/community/

