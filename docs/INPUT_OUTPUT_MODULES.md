# Input and Output Declarative Modules

## Overview

The `cribl.stream.input` and `cribl.stream.output` declarative modules use a special `conf` parameter to handle their complex, type-specific configurations.

## Why Use `conf`?

Inputs and outputs have **40+ parameters each** that vary by type:
- **S3 output**: bucket, region, destPath, compress, etc.
- **Splunk output**: host, port, authToken, etc.
- **Syslog input**: host, port, protocol, etc.
- **HTTP input**: port, authType, etc.

Rather than defining all 40+ parameters as separate module options (which would be confusing and inflexible), we use a single `conf` dict that accepts **all configuration parameters**.

## Usage Pattern

### Input Example

```yaml
- name: Create syslog input
  cribl.stream.input:
    session: "{{ cribl_session.session }}"
    id: in_syslog
    conf:
      type: syslog
      host: 0.0.0.0
      tcpPort: 5514
      disabled: false
      sendToRoutes: true
      pqEnabled: false
    state: present
```

### Output Example

```yaml
- name: Create S3 output
  cribl.stream.output:
    session: "{{ cribl_session.session }}"
    id: out_s3
    conf:
      type: s3
      bucket: my-data-bucket
      region: us-east-1
      destPath: logs/${host}/
      compress: gzip
      format: json
      maxFileSizeMB: 32
      awsAuthenticationMethod: auto
    state: present
```

### With Worker Groups

```yaml
- name: Create input in production worker group
  cribl.stream.input:
    session: "{{ cribl_session.session }}"
    id: in_syslog_prod
    worker_group: production
    conf:
      type: syslog
      host: 0.0.0.0
      tcpPort: 5514
    state: present
```

## How It Works

The `conf` dict is **merged** into the API request at the top level:

```yaml
# Your playbook
conf:
  type: s3
  bucket: my-bucket
  region: us-east-1
```

```python
# What gets sent to Cribl API
POST /api/v1/system/outputs
{
  "id": "out_s3",
  "type": "s3",           # From conf
  "bucket": "my-bucket",  # From conf
  "region": "us-east-1"   # From conf
}
```

## Common Input Types

### Syslog Input

```yaml
- name: Syslog TCP input
  cribl.stream.input:
    id: in_syslog
    conf:
      type: syslog
      host: 0.0.0.0
      tcpPort: 514
      disabled: false
    state: present
```

### HTTP Input

```yaml
- name: HTTP webhook input
  cribl.stream.input:
    id: in_http
    conf:
      type: http
      port: 10080
      authType: none
      disabled: false
    state: present
```

### Splunk HEC Input

```yaml
- name: Splunk HEC input
  cribl.stream.input:
    id: in_hec
    conf:
      type: splunk_hec
      host: 0.0.0.0
      port: 8088
      disabled: false
    state: present
```

### TCP JSON Input

```yaml
- name: TCP JSON input
  cribl.stream.input:
    id: in_tcp_json
    conf:
      type: tcp_json
      host: 0.0.0.0
      port: 10001
      disabled: false
    state: present
```

## Common Output Types

### S3 Output

```yaml
- name: S3 output
  cribl.stream.output:
    id: out_s3
    conf:
      type: s3
      bucket: my-data-bucket
      region: us-east-1
      destPath: logs/
      compress: gzip
      format: json
      maxFileSizeMB: 32
      awsAuthenticationMethod: auto
    state: present
```

### Splunk Output

```yaml
- name: Splunk output
  cribl.stream.output:
    id: out_splunk
    conf:
      type: splunk
      host: splunk.example.com
      port: 9997
      connectionTimeout: 10000
      writeTimeout: 60000
      maxPayloadSizeKB: 1024
      compress: true
    state: present
```

### Elasticsearch Output

```yaml
- name: Elasticsearch output
  cribl.stream.output:
    id: out_elastic
    conf:
      type: elasticsearch
      url: https://elastic.example.com:9200
      index: cribl-logs
      bulkMaxSizeMB: 5
      flushPeriodSec: 1
    state: present
```

### HTTP Output (Webhook)

```yaml
- name: HTTP webhook output
  cribl.stream.output:
    id: out_webhook
    conf:
      type: http
      url: https://api.example.com/webhook
      method: POST
      headers:
        - name: Content-Type
          value: application/json
      maxPayloadSizeKB: 4096
    state: present
```

## Finding Configuration Parameters

To find available parameters for your input/output type:

### Method 1: Cribl UI
1. Create the input/output in Cribl UI
2. Export to JSON or view in developer tools
3. See all available parameters

### Method 2: Cribl API Docs
- Visit [Cribl API Documentation](https://docs.cribl.io/cribl-as-code/api-reference/)
- Find input/output schemas
- See all available parameters

### Method 3: Existing Resources
```yaml
# Get existing output configuration
- name: Get existing output
  cribl.stream.system_outputs_id_get:
    session: "{{ session.session }}"
    id: existing_output
  register: result

- name: Display configuration
  debug:
    var: result.response
```

## Complete Example

```yaml
---
- name: Configure Inputs and Outputs
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Authenticate
      cribl.core.auth_session:
        base_url: "{{ cribl_url }}"
        username: "{{ username }}"
        password: "{{ password }}"
      register: session
      no_log: true
    
    # Create syslog input
    - name: Create syslog input
      cribl.stream.input:
        session: "{{ session.session }}"
        id: in_syslog
        conf:
          type: syslog
          host: 0.0.0.0
          tcpPort: 514
          protocol: tcp
          disabled: false
          sendToRoutes: true
        state: present
    
    # Create S3 output
    - name: Create S3 output
      cribl.stream.output:
        session: "{{ session.session }}"
        id: out_s3
        conf:
          type: s3
          bucket: my-logs
          region: us-east-1
          destPath: cribl/${host}/
          compress: gzip
          format: json
        state: present
    
    # Create processing pipeline
    - name: Create pipeline
      cribl.stream.pipeline:
        session: "{{ session.session }}"
        id: process_logs
        conf:
          description: Process and route logs
          functions:
            - id: eval
              filter: "true"
              conf:
                add:
                  - name: processed
                    value: "true"
        state: present
    
    # Create route
    - name: Create route
      cribl.stream.route:
        session: "{{ session.session }}"
        id: default
        conf:
          routes:
            - id: to_s3
              filter: "true"
              pipeline: process_logs
              output: out_s3
        state: present
```

## Best Practices

### 1. Use Minimal Required Parameters

Only specify parameters you need to change:

```yaml
# Minimal S3 output
- name: Simple S3 output
  cribl.stream.output:
    id: out_s3
    conf:
      type: s3
      bucket: my-bucket
      region: us-east-1
    state: present
```

### 2. Use Variables for Reusability

```yaml
vars:
  s3_outputs:
    - id: out_s3_prod
      bucket: prod-logs
      region: us-east-1
    - id: out_s3_dev
      bucket: dev-logs
      region: us-west-2

tasks:
  - name: Create S3 outputs
    cribl.stream.output:
      session: "{{ session.session }}"
      id: "{{ item.id }}"
      conf:
        type: s3
        bucket: "{{ item.bucket }}"
        region: "{{ item.region }}"
      state: present
    loop: "{{ s3_outputs }}"
```

### 3. Worker Group Specific Inputs/Outputs

```yaml
- name: Configure regional inputs
  cribl.stream.input:
    session: "{{ session.session }}"
    id: in_syslog
    worker_group: "{{ item.region }}"
    conf:
      type: syslog
      host: 0.0.0.0
      tcpPort: "{{ item.port }}"
    state: present
  loop:
    - region: us-east
      port: 5514
    - region: us-west
      port: 5515
```

## Troubleshooting

### Missing Required Parameters

**Error**: `should have required property 'type'`

**Solution**: Ensure `conf` includes all required parameters for the type:

```yaml
conf:
  type: s3  # ← Required!
  bucket: my-bucket  # ← Usually required
  region: us-east-1  # ← Usually required
```

### Nested conf Not Working

**Error**: Parameters not being recognized

**Bad**:
```yaml
input:
  conf:
    conf:  # ❌ Double nested
      type: syslog
```

**Good**:
```yaml
input:
  conf:  # ✅ Single conf level
    type: syslog
```

### Type-Specific Parameters

Different types have different required/optional parameters. Check Cribl docs for your specific type.

## See Also

- [Cribl Input Types](https://docs.cribl.io/stream/sources/)
- [Cribl Output Types](https://docs.cribl.io/stream/destinations/)
- [Worker Group Documentation](WORKER_GROUPS.md)
- [Examples](../examples/worker_group_declarative_example.yml)

