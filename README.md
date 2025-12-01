# Cribl Ansible Collections

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ansible](https://img.shields.io/badge/Ansible-2.9%2B-blue.svg)](https://www.ansible.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

## 📦 Latest Release

**Current Version**: `v4.15.0` | **Released**:  | [Download](https://github.com/AlexAsplund/ansible-collections-cribl/releases/tag/v4.15.0)

Generated from [Cribl API Spec 4.15.0](https://cdn.cribl.io/dl/4.15.0/cribl-apidocs-4.15.0-f275b803.yml)

---
> **Declarative, idempotent Ansible collections for managing Cribl Stream, Edge, Search, Lake, and Core via Infrastructure as Code.**
> Automate your Cribl infrastructure with confidence using **state-based management** that only makes changes when needed. Built for DevOps teams who need reliable, repeatable Cribl deployments.

> **This project not affiliated with Cribl and in it's early stages. It is also focused mainly on on-prem environments. So use with caution**

---

## Why Use This?

- **Auto-Generated Declarative Modules** - 49+ declarative modules automatically generated from CRUD detection
- **Cribl Cloud OAuth2 Support** - NEW! Authenticate with Cribl Cloud using client_id/client_secret
- **Worker Group Support** - NEW! Manage resources in specific worker groups with a simple `worker_group` parameter
- **53 Example Playbooks** - Ready-to-use examples auto-generated for all declarative modules
- **Declarative & Idempotent** - Define desired state, run playbooks repeatedly without side effects
- **Production Safe** - Built-in check mode (`--check`) and diff support (`--diff`)
- **Complete API Coverage** - 513 auto-generated imperative modules + 49 declarative modules
- **Docker Testing Included** - Test against real Cribl instances in isolated containers
- **OpenAPI-Driven** - Regenerate modules for any Cribl version
- **Well Organized** - 5 focused collections matching [Cribl&#39;s official API structure](https://docs.cribl.io/cribl-as-code/api-reference/)
- **Auto-Generated Tests** - Unit tests and integration playbooks created automatically

---

## Quick Start
Download the latest [release](https://github.com/AlexAsplund/ansible-collections-cribl/releases) and install

### Build it manually

```bash
# Clone the repository
git clone https://github.com/AlexAsplund/ansible-collections-cribl.git
cd ansible-cribl-collection

# Start Docker test environment (auto-builds modules)
cd tests/docker
docker-compose up -d

# Or manually generate and build
python scripts/generate_modules.py
make build
```

### Your First Playbook (Declarative with Session Auth)

```yaml
---
- name: Configure Cribl Infrastructure
  hosts: localhost
  gather_facts: false
  vars:
    cribl_url: https://cribl.example.com
  
  tasks:
    # Step 1: Create authenticated session (once per playbook)
    - name: Authenticate with Cribl
      cribl.core.auth_session:
        base_url: "{{ cribl_url }}"
        username: admin
        password: "{{ vault_password }}"
        validate_certs: false
      register: cribl_session
      no_log: true

    # Step 2: Use session for all operations - no re-authentication needed!
    - name: Ensure operations user exists
      cribl.core.user:
        session: "{{ cribl_session.session }}"
        id: ops_user
        email: ops@example.com
        first: Operations
        last: User
        password: "{{ vault.ops_user_password }}" # Password is needed if the user is created
        roles: [user]
        state: present  # Ensures user exists with these attributes

    # Test your changes safely first
    # Run: ansible-playbook playbook.yml --check --diff
```

**Result:** Session authenticates once, user is created on first run, no changes on subsequent runs.

---

## Cribl Cloud OAuth2 Authentication

Authenticate with Cribl Cloud using OAuth2 Client Credentials!

```yaml
# Cribl Cloud with OAuth2
- name: Authenticate with Cribl Cloud
  cribl.core.auth_session:
    base_url: https://main-myorg.cribl.cloud
    client_id: "{{ cribl_client_id }}"
    client_secret: "{{ cribl_client_secret }}"
    validate_certs: true
  register: session
  no_log: true

# Traditional on-prem authentication still works
- name: Authenticate with on-prem
  cribl.core.auth_session:
    base_url: https://cribl.local
    username: admin
    password: "{{ password }}"
  register: session
  no_log: true
```

**Benefits:**
- ✅ Automatic auth method detection
- ✅ Secure OAuth2 Client Credentials flow
- ✅ Automatic token refresh
- ✅ Perfect for Cribl Cloud
- ✅ Backward compatible with username/password

**See:** [Cribl Cloud OAuth2 Documentation](docs/CRIBL_CLOUD_AUTH.md) | [Examples](examples/cribl_cloud_oauth2_example.yml)

### Worker Group Support

All declarative modules now support the `worker_group` parameter for managing resources in specific worker groups!

```yaml
# Global pipeline (no worker group)
- name: Create global pipeline
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: my_pipeline
    state: present

# Worker group-specific pipeline
- name: Create pipeline in production worker group
  cribl.stream.pipeline:
    session: "{{ cribl_session.session }}"
    id: my_pipeline
    worker_group: production  # <-- NEW!
    state: present
```

**Benefits:**
- ✅ Same module for global and worker group resources
- ✅ Different configs per environment (prod/staging/dev)
- ✅ Multi-tenant isolation
- ✅ Geographic distribution
- ✅ Canary/blue-green deployments

**See:** [Worker Group Documentation](docs/WORKER_GROUPS.md) | [Examples](examples/worker_group_declarative_example.yml)

---

## Installation & Building

### Quick Install for Users
Download from [releases](https://github.com/AlexAsplund/ansible-collections-cribl/releases) and install:
```bash
wget https://github.com/AlexAsplund/ansible-collections-cribl/releases/download/v4.15.0/cribl-core-4.15.0.tar.gz
wget https://github.com/AlexAsplund/ansible-collections-cribl/releases/download/v4.15.0/cribl-stream-4.15.0.tar.gz
ansible galaxy collection install cribl-core-4.15.0.tar.gz
ansible galaxy collection install cribl-stream-4.15.0.tar.gz
```

### Build from Source

```bash
# 1. Clone repository
git clone https://github.com/AlexAsplund/ansible-collections-cribl
cd ansible-cribl-collection

# 2. Generate modules from OpenAPI spec
make generate
# OR: python scripts/generate_modules.py

# 3. Build collection tarballs
make build

# 4. Install locally
make install-local          # To ./ansible_collections/
# OR
make install-collections    # To ~/.ansible/collections/
```

See **[QUICK_START.md](QUICK_START.md)** for quick start guide and **[RELEASE.md](RELEASE.md)** for releasing to GitHub.

---

## What's Included

### 5 Product-Focused Collections

| Collection             | Imperative Modules | Declarative Modules | Purpose                                                        |
| ---------------------- | -----------------: | ------------------: | -------------------------------------------------------------- |
| **cribl.core**   |                276 |                  22 | Users, teams, worker groups, authentication, system management |
| **cribl.stream** |                127 |                  16 | Pipelines, routes, inputs, outputs, packs, data processing     |
| **cribl.search** |                 80 |                  10 | Datasets, searches, dashboards, jobs                           |
| **cribl.edge**   |                 19 |                   1 | Edge nodes, processes, containers, AppScope                    |
| **cribl.lake**   |                 11 |                   0 | Data lakes, storage locations, datasets                        |
| **Total**        |      **513** |        **49** | **Complete Cribl API automation**                        |

### Module Types

#### Declarative Modules (Recommended for Configuration Management)

**Idempotent, state-based resource management:**

```yaml
- cribl.core.user           # Manage users
- cribl.core.worker_group   # Manage worker groups
- cribl.stream.pipeline     # Manage pipelines
# More declarative modules available...
```

**Benefits:**

- Idempotent - safe to run repeatedly
- Check mode support - see changes before applying
- Diff support - see exactly what will change
- Smart - only makes API calls when needed

#### Imperative Modules (513 Generated from OpenAPI)

**Direct API mapping for specific operations:**

```yaml
- cribl.core.system_instance_get    # Read operations
- cribl.core.health_get             # Status checks
- cribl.stream.pipelines_get        # Query resources
- cribl.core.auth_session           # Session management (NEW!)
# ... 509 more modules
```

**Best for:** One-off operations, queries, specific API calls

---

## Usage Examples

### Declarative Configuration Management

```yaml
---
- name: Manage Cribl Environment
  hosts: localhost
  gather_facts: false
  vars_files:
    - vault.yml  # Encrypted credentials
  
  tasks:
    # Create session once for all tasks
    - name: Authenticate with Cribl
      cribl.core.auth_session:
        base_url: "{{ cribl_url }}"
        username: "{{ cribl_username }}"
        password: "{{ cribl_password }}"
        validate_certs: true
      register: cribl_session
      no_log: true

    # Ensure users exist with correct configuration
    - name: Ensure required users exist
      cribl.core.user:
        session: "{{ cribl_session.session }}"
        id: "{{ item.id }}"
        email: "{{ item.email }}"
        roles: "{{ item.roles }}"
        password: "{{ vault.password }}" # Password is needed if the user is created
        state: present
      loop:
        - {id: admin_user, email: admin@example.com, roles: [admin]}
        - {id: ops_user, email: ops@example.com, roles: [user]}
        - {id: viewer, email: viewer@example.com, roles: [viewer]}

    # Ensure test users are removed
    - name: Clean up test users
      cribl.core.user:
        session: "{{ cribl_session.session }}"
        id: "{{ item }}"
        state: absent
      loop:
        - test_user_1
        - old_admin
```

## Creating pipelines

```yml
- name: Manage Cribl Environment
  hosts: localhost
  gather_facts: false
  vars_files:
    - vault.yml  # Encrypted credentials
  tasks:
    - name: Create pipeline
      cribl.stream.pipeline:
        session: "{{ cribl_session.session }}"
        id: my_pipeline
        conf:
          description: "Comprehensive test pipeline"
          functions: "{{ my_pipeline_functions }}"
        state: present
      register: test_pipeline_create
      ignore_errors: true
      vars:
        my_pipeline_functions:
          - id: comment
            filter: "true"
            conf:
              comment: Parse syslog.
          - id: regex_extract
            description: Extract raw CSV payload to field 'fl'
            filter: "true"
            conf:
              source: _raw
              iterations: 100
              overwrite: true
              regex: '/^(?<_sourcetype>[^:]+): ?(?<message>.*)/'
          
```

**Run safely:**

```bash
# See what would change (no actual changes made)
ansible-playbook configure-cribl.yml --check --diff

# Apply changes
ansible-playbook configure-cribl.yml
```

### Query and Monitor (Imperative with Session)

```yaml
---
- name: Check Cribl Health
  hosts: localhost
  gather_facts: false
  
  tasks:
    # Create session - authenticates once, auto-refreshes if needed
    - name: Authenticate with Cribl
      cribl.core.auth_session:
        base_url: "{{ cribl_url }}"
        username: "{{ cribl_username }}"
        password: "{{ cribl_password }}"
        validate_certs: false
      register: cribl_session
      no_log: true

    # All subsequent tasks use the session - much more efficient!
    - name: Get system health
      cribl.core.health_get:
        session: "{{ cribl_session.session }}"
      register: health

    - name: Display health status
      debug:
        msg: "Cribl is {{ health.response.status }}"

    - name: Get all pipelines
      cribl.stream.pipelines_get:
        session: "{{ cribl_session.session }}"
      register: pipelines

    - name: Show pipeline count
      debug:
        msg: "Found {{ pipelines.response.count }} pipelines"
```

---

## Testing

### Docker Integration Tests

Test your Ansible modules against a **real Cribl instance** using Docker:

```bash
# Quick start - automatically builds modules and runs all tests
cd tests/docker
docker-compose up -d
pytest test_docker_integration.py -v -m docker

# Or use Make
make test-docker
```

**Features:**

- Tests against real Cribl Stream instance
- Automatic module building in container
- Comprehensive test coverage (connection, health, users, CRUD operations)
- CI/CD ready
- No manual setup required

**Documentation:** See [`docs/TESTING.md`](docs/TESTING.md) for complete guide.

### Other Tests

```bash
# Run all tests
make test

# Unit tests only
make test-unit

# With coverage
make test-coverage

# Linting
make lint
```

---

## Module Generator

Auto-generate all Ansible modules from Cribl's OpenAPI specification:

```bash
# Generate all modules (imperative + declarative)
python scripts/generate_modules.py --declarative

# Clean and regenerate
python scripts/generate_modules.py --clean

# Specific collection only
python scripts/generate_modules.py --product core

# Use custom OpenAPI spec
python scripts/generate_modules.py --spec path/to/cribl-api.yml
```

**Features:**

- Automatic parameter extraction from OpenAPI schemas
- Smart categorization (routes to correct product collection)
- Documentation generation (DOCUMENTATION, EXAMPLES, RETURN blocks)
- Type conversion (OpenAPI types → Ansible types)
- Built-in error handling and authentication

**Documentation:** See [`docs/GENERATOR.md`](docs/GENERATOR.md) for advanced usage.

---

## Security

### SSL Certificates

```yaml
# Development (self-signed certs)
validate_certs: false

# Production (valid certs)
validate_certs: true
```

### Secure Credentials with Ansible Vault

```bash
# Create encrypted vault
ansible-vault create vault.yml

# Add your credentials
cribl_username: admin
cribl_password: your-secure-password
cribl_token: your-api-token

# Use in playbooks
ansible-playbook playbook.yml -e @vault.yml --ask-vault-pass
```

### Environment Variables

```yaml
vars:
  cribl_url: "{{ lookup('env', 'CRIBL_URL') }}"
  cribl_token: "{{ lookup('env', 'CRIBL_TOKEN') }}"
```

---

## Documentation

- **[Auto-Generation Guide](docs/AUTO_GENERATION.md)** - How automatic CRUD detection works
- **[Declarative Modules Guide](docs/DECLARATIVE.md)** - Complete guide to state-based management
- **[Testing Guide](docs/TESTING.md)** - Docker tests, unit tests, integration tests
- **[Generator Guide](docs/GENERATOR.md)** - Module generation and customization
- **[API Reference](docs/API_REFERENCE.md)** - All modules and parameters
- **[Examples](docs/EXAMPLES.md)** - Real-world playbook examples
- **[Contributing](CONTRIBUTING.md)** - How to contribute

---

## Project Structure

```
.
├── scripts/
│   ├── generate_modules.py              # CLI entry point
│   └── generator/                       # Modular generator
│       ├── openapi_parser.py            # Parse OpenAPI specs
│       ├── module_generator.py          # Generate imperative modules
│       ├── declarative_generator.py     # Generate declarative modules
│       ├── collection_manager.py        # Manage collection structure
│       └── templates.py                 # Code templates
├── schemas/
│   └── cribl-apidocs-4.15.0.yml        # OpenAPI specification
├── build/
│   └── ansible_collections/cribl/       # Generated collections
│       ├── core/                        # 276 modules
│       ├── stream/                      # 127 modules
│       ├── edge/                        # 19 modules
│       ├── search/                      # 80 modules
│       └── lake/                        # 11 modules
├── docs/                                # Documentation
├── tests/                               # Test suite
│   ├── docker/                          # Docker integration tests
│   ├── unit/                            # Unit tests
│   └── integration/                     # Integration tests
├── Makefile                             # Development commands
└── README.md                            # This file
```

---

## Requirements

- **Python**: 3.6 or higher
- **Ansible**: 2.9 or higher
- **PyYAML**: For OpenAPI parsing
- **Docker**: For integration tests (optional)
- **Cribl Instance**: Stream, Edge, Search, or Lake

---

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code style guidelines
- Testing requirements
- Pull request process
- Development setup

---

## Support

- **Documentation**: [Cribl Docs](https://docs.cribl.io)
- **API Reference**: [Cribl API](https://docs.cribl.io/cribl-as-code/api-reference/)
- **Issues**: [GitHub Issues](https://github.com/AlexAsplund/ansible-collections-cribl/issues)
- **Cribl Community**: [Slack](https://cribl.io/community)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Roadmap

- [X] 513 imperative modules (all Cribl API endpoints)
- [X] **Automatic CRUD detection and declarative module generation**
- [X] 49 auto-generated declarative modules across all collections
- [X] Auto-generated unit tests and integration playbooks
- [X] Docker integration testing
- [X] Check mode and diff support
- [X] Cribl Cloud Support
- [X] Smart declarative functions targeting worker groups

---

## Acknowledgments

- Built for the [Cribl Community](https://cribl.io/community)
- Uses [Cribl&#39;s OpenAPI Specification](https://docs.cribl.io)
- Inspired by Infrastructure as Code best practices
