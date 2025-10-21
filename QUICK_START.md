# Quick Start Guide

## 5-Minute Setup

### Option 1: Use Pre-Built Collections (When Published)

```bash
# Install from Ansible Galaxy
ansible-galaxy collection install cribl.core
ansible-galaxy collection install cribl.stream

# Create a playbook
cat > test.yml << 'EOF'
---
- hosts: localhost
  collections:
    - cribl.core
  tasks:
    - auth_session:
        base_url: https://cribl.example.com
        username: admin
        password: "{{ vault_password }}"
      register: session
EOF

# Run it
ansible-playbook test.yml
```

### Option 2: Build from Source

```bash
# 1. Generate modules (takes ~30 seconds)
make generate

# 2. Install to project directory
make install-local

# 3. Use in playbooks
ansible-playbook examples/session_authentication_example.yml --check
```

## Common Commands

### Generation & Build
```bash
make generate                    # Generate all modules
make build                       # Build distribution tarballs
make build-one COLLECTION=core   # Build single collection
```

### Installation
```bash
make install-local              # Install to ./ansible_collections/
make install-collections        # Install to ~/.ansible/collections/
make install-collection COLLECTION=core  # Install one collection
```

### Testing
```bash
make test                       # Run all tests
make test-unit                  # Unit tests only
make test-docker                # Docker integration tests
ansible-playbook playbook.yml --check --diff  # Test playbook
```

### Cleanup
```bash
make clean                      # Remove build artifacts
make clean-collections          # Remove local collections
make uninstall-collections      # Remove installed collections
```

## Windows Users

Use PowerShell script:

```powershell
# Generate
.\scripts\build_and_install.ps1 -Action generate

# Build
.\scripts\build_and_install.ps1 -Action build

# Install locally
.\scripts\build_and_install.ps1 -Action install-local

# Install to user directory
.\scripts\build_and_install.ps1 -Action install-user
```

## Simple Playbook Example

```yaml
---
- name: Manage Cribl
  hosts: localhost
  gather_facts: false
  collections:
    - cribl.core
    - cribl.stream
  
  tasks:
    # 1. Authenticate
    - name: Login
      auth_session:
        base_url: "{{ cribl_url }}"
        username: "{{ cribl_username }}"
        password: "{{ cribl_password }}"
      register: cribl_session
    
    # 2. Manage resources
    - name: Create user
      user_declarative:
        session: "{{ cribl_session.session }}"
        id: test_user
        email: test@example.com
        state: present
    
    - name: Create pipeline
      cribl.stream.pipeline:
        session: "{{ cribl_session.session }}"
        id: my_pipeline
        conf:
          description: "Test pipeline"
        state: present
```

Run with:
```bash
ansible-playbook playbook.yml --check     # Dry run
ansible-playbook playbook.yml --diff      # Show changes
ansible-playbook playbook.yml             # Apply changes
```

## Verify Installation

```bash
# List installed collections
ansible-galaxy collection list | grep cribl

# View module documentation
ansible-doc cribl.core.user

# List all modules
ansible-doc -l cribl.core
ansible-doc -l cribl.stream

# Check Ansible can find collections
ansible-config dump | grep COLLECTIONS_PATHS
```

## Directory Structure After Install

### Local Installation (`make install-local`)
```
your-project/
├── ansible_collections/
│   └── cribl/
│       ├── core/
│       ├── stream/
│       ├── edge/
│       ├── search/
│       └── lake/
├── ansible.cfg          # Points to ./ansible_collections/
└── playbook.yml
```

### User Installation (`make install-collections`)
```
~/.ansible/collections/
└── ansible_collections/
    └── cribl/
        ├── core/
        ├── stream/
        ├── edge/
        ├── search/
        └── lake/
```

## Common Use Cases

### Use Case 1: Development

```bash
# 1. Generate and install locally
make generate
make install-local

# 2. Make changes to generator
vim scripts/generator/declarative_generator.py

# 3. Regenerate
make clean
make generate
make install-local

# 4. Test
ansible-playbook test.yml
```

### Use Case 2: CI/CD

```yaml
# .github/workflows/build.yml
- name: Generate modules
  run: make generate

- name: Build collections
  run: make build

- name: Test collections
  run: |
    make install-local
    ansible-playbook tests/integration/test_all_declarative.yml --syntax-check
```

### Use Case 3: Distribution

```bash
# 1. Generate and build
make generate
make build

# 2. Tarballs are in dist/
ls -lh dist/
# cribl-core-1.0.0.tar.gz
# cribl-stream-1.0.0.tar.gz
# ...

# 3. Publish to Ansible Galaxy
ansible-galaxy collection publish dist/cribl-core-1.0.0.tar.gz
```

### Use Case 4: Air-Gapped Environments

```bash
# On connected machine:
make generate
make build
tar -czf cribl-collections.tar.gz dist/

# Transfer to air-gapped machine:
scp cribl-collections.tar.gz user@airgapped:/tmp/

# On air-gapped machine:
cd /tmp
tar -xzf cribl-collections.tar.gz
for tarball in dist/*.tar.gz; do
  ansible-galaxy collection install $tarball
done
```

## Configuration

### Generator Config (`scripts/generator_config.yml`)

```yaml
spec_file: schemas/cribl-apidocs-4.14.0-837595d5.yml
output_dir: build/ansible_collections/cribl
products: null              # null = all, or ['core', 'stream']
clean: true                 # Clean before generation
generate_declarative: true  # Generate declarative modules
generate_imperative: true   # Generate imperative modules
```

### Ansible Config (`ansible.cfg`)

```ini
[defaults]
collections_paths = ./ansible_collections:~/.ansible/collections
inventory = ./inventory
host_key_checking = False
stdout_callback = yaml
```

## Troubleshooting

### "Collection not found"

```bash
# Check if installed
ansible-galaxy collection list | grep cribl

# Check paths
ansible-config dump | grep COLLECTIONS_PATHS

# Reinstall
make install-local
# OR
make install-collections
```

### "Module not found"

```yaml
# Use FQCN (Fully Qualified Collection Name)
- cribl.core.user:  # Good ✓
    ...

# Instead of short name
- user_declarative:  # May fail ✗
    ...
```

### "Import error: cribl_api"

```bash
# Regenerate to ensure all files are copied
make clean
make generate
make install-local
```

### Build fails on Windows

```powershell
# Use PowerShell script instead of Makefile
.\scripts\build_and_install.ps1 -Action generate
.\scripts\build_and_install.ps1 -Action build
```

## More Information

- **[README.md](README.md)** - Full project documentation
- **[docs/EXAMPLES.md](docs/EXAMPLES.md)** - Usage examples
- **[docs/DECLARATIVE.md](docs/DECLARATIVE.md)** - Declarative module guide

## Pro Tips

1. **Use check mode first**: `ansible-playbook playbook.yml --check --diff`
2. **Start with local install**: Easier for development
3. **Use session authentication**: More efficient than per-task auth
4. **Prefer declarative modules**: Idempotent and safer
5. **Test before applying**: Always use `--check` mode first

## Next Steps

1. Generate modules
2. Install collections
3. Create a simple playbook
4. Test with `--check` mode
5. Apply changes
6. Automate your Cribl infrastructure

