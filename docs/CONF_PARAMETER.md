# Understanding the `conf` Parameter

## Quick Reference

Some Cribl declarative modules use a `conf` parameter for configuration instead of individual parameters.

### Modules Using `conf`

- `cribl.stream.input` - Input/source configuration (merged at top level)
- `cribl.stream.output` - Output/destination configuration (merged at top level)
- `cribl.stream.pipeline` - Pipeline configuration (nested object)
- Any module with complex, type-specific configurations

**Important**: Inputs and outputs **merge** `conf` into the API request at the top level. Pipelines keep `conf` as a nested object.

### Correct Pattern

```yaml
- name: Create S3 output
  cribl.stream.output:
    session: "{{ session.session }}"
    id: my_output
    worker_group: production  # Optional
    state: present           # Module parameter
    conf:                     # Configuration dict
      type: s3
      bucket: my-bucket
      region: us-east-1
```

### Common Mistake ❌

```yaml
- name: WRONG - state inside conf
  cribl.stream.output:
    session: "{{ session.session }}"
    id: my_output
    conf:
      type: s3
      bucket: my-bucket
      state: present  # ❌ WRONG! state should be outside conf
```

## Why Use `conf`?

Inputs and outputs have 40+ parameters each that vary by type:

**Without `conf` (impractical)**:
```yaml
# Would need to define 40+ module parameters
type: s3
bucket: ...
region: ...
destPath: ...
compress: ...
# ... 35 more parameters
```

**With `conf` (clean)**:
```yaml
conf:
  type: s3
  bucket: ...
  region: ...
  # Only specify what you need
```

## How It Works Internally

The module automatically merges `conf` into the API request:

```yaml
# Your playbook
id: my_output
conf:
  type: s3
  bucket: my-bucket
```

```python
# What gets sent to Cribl API
{
  "id": "my_output",
  "type": "s3",      # Merged from conf
  "bucket": "my-bucket"  # Merged from conf
}
```

## Module Parameters vs Configuration

### Module Level (Outside `conf`)
- `session` - Authentication session
- `base_url` - Cribl URL (if not using session)
- `token` - API token (if not using session)  
- `id` - Resource identifier
- `worker_group` - Target worker group
- `state` - Desired state (present/absent)
- `validate_certs` - SSL validation
- `timeout` - Request timeout

### Configuration Level (Inside `conf`)
- `type` - Input/output type (s3, splunk, http, etc.)
- All type-specific parameters
- `disabled` - Enable/disable
- `description` - Description
- And all other resource-specific configuration

## Examples by Resource Type

### Input with Minimal Config

```yaml
- name: Simple syslog input
  cribl.stream.input:
    id: in_syslog
    state: present
    conf:
      type: syslog
      host: 0.0.0.0
      tcpPort: 514
```

### Input with Full Config

```yaml
- name: Advanced syslog input
  cribl.stream.input:
    id: in_syslog_advanced
    worker_group: production
    state: present
    conf:
      type: syslog
      host: 0.0.0.0
      tcpPort: 514
      disabled: false
      sendToRoutes: true
      pqEnabled: true
      pipeline: syslog_processing
      maxActiveCxn: 1000
      tls:
        disabled: false
        cert: my_cert
```

### Output with Minimal Config

```yaml
- name: Simple S3 output
  cribl.stream.output:
    id: out_s3
    state: present
    conf:
      type: s3
      bucket: my-bucket
      region: us-east-1
```

### Output with Full Config

```yaml
- name: Advanced S3 output
  cribl.stream.output:
    id: out_s3_advanced
    worker_group: production
    state: present
    conf:
      type: s3
      bucket: my-production-logs
      region: us-east-1
      destPath: logs/${_time:%Y}/${_time:%m}/${_time:%d}/
      partitionExpr: "`${sourcetype}`"
      format: json
      compress: gzip
      maxFileSizeMB: 100
      systemFields:
        - cribl_pipe
      awsAuthenticationMethod: auto
```

### Pipeline (Also Uses `conf`)

```yaml
- name: Create pipeline
  cribl.stream.pipeline:
    id: my_pipeline
    state: present
    conf:
      description: My processing pipeline
      asyncFuncTimeout: 1000
      functions:
        - id: eval
          filter: "true"
          conf:
            add:
              - name: environment
                value: "'production'"
```

## Troubleshooting

### Error: "should have required property 'type'"

**Cause**: Missing `type` in `conf`

**Fix**:
```yaml
conf:
  type: s3  # ← Add type!
  bucket: my-bucket
```

### Error: Parameters not being recognized

**Cause**: Parameters at wrong level

**Wrong**:
```yaml
type: s3  # ❌ Top level
conf:
  bucket: my-bucket
```

**Right**:
```yaml
conf:
  type: s3  # ✅ Inside conf
  bucket: my-bucket
```

### Error: Unsupported parameter 'conf'

**Cause**: Old module version without conf support

**Fix**: Regenerate modules:
```bash
docker run -it -v "$($pwd.Path):/workspace" ansible-cribl:build make generate
```

## Summary

✅ **Use `conf` for**: input, output, pipeline (complex configurations)  
✅ **Module parameters**: id, state, worker_group, session (outside conf)  
✅ **Configuration**: type, bucket, host, port, etc. (inside conf)  
✅ **Merge behavior**: conf contents are merged at API level  

See also: [INPUT_OUTPUT_MODULES.md](INPUT_OUTPUT_MODULES.md)

