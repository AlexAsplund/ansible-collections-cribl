# Testing Guide

## Test Status: All Passing (100%)

**Core Tests**: 4/4 PASSED | **Infrastructure**: 100% Working

---

## Overview

This guide covers all testing approaches for the Cribl Ansible Collections, including Docker integration tests, unit tests, and integration tests.

---

## Docker Integration Tests (Recommended)

Test your Ansible modules against a **real Cribl instance** in an isolated Docker environment.

### Quick Start

```bash
# From project root
cd tests/docker

# Start container (auto-builds modules)
docker-compose up -d

# Run all tests
pytest test_docker_integration.py -v -m docker --no-cov
```

Or use Make:
```bash
# From project root
make test-docker           # Run all tests
make test-docker-shell     # Interactive shell
make test-docker-up        # Start container
make test-docker-down      # Stop container
```

### Features

- **Automatic Module Building** - Container builds modules on startup  
- **Real Cribl Instance** - Tests against actual Cribl Stream API  
- **Comprehensive Coverage** - Connection, health, users, worker groups, CRUD operations  
- **No Manual Setup** - Everything works out of the box  
- **CI/CD Ready** - Easy to integrate into pipelines  

### Test Playbooks

Located in `tests/docker/playbooks/`:

1. **`test_cribl_connection.yml`** - Basic connectivity
2. **`test_cribl_health.yml`** - Health and status checks  
3. **`test_cribl_users.yml`** - User CRUD operations (with cleanup)
4. **`test_cribl_worker_groups.yml`** - Worker group management
5. **`test_cribl_comprehensive.yml`** - Complete feature testing

### Configuration

Create `env/test.env`:
```bash
CRIBL_USERNAME=admin
CRIBL_PASSWORD=your-password
CRIBL_URL=http://your-cribl-instance:9000
```

### Running Individual Playbooks

```bash
# Inside container
docker exec cribl-ansible-test ansible-playbook \
  /ansible/tests/docker/playbooks/test_cribl_comprehensive.yml -v
```

### Test Results

```
============================= test session starts =============================
tests/docker/test_docker_integration.py::TestDockerIntegration::test_docker_container_running PASSED [ 11%]
tests/docker/test_docker_integration.py::TestDockerIntegration::test_ansible_installed PASSED [ 22%]
tests/docker/test_docker_integration.py::TestDockerIntegration::test_cribl_collections_available PASSED [ 33%]
tests/docker/test_docker_integration.py::TestCriblPlaybooks::test_connection_playbook PASSED [ 44%]
tests/docker/test_docker_integration.py::TestCriblPlaybooks::test_health_playbook PASSED [ 55%]
tests/docker/test_docker_integration.py::TestCriblPlaybooks::test_users_playbook PASSED [ 66%]
tests/docker/test_docker_integration.py::TestCriblPlaybooks::test_worker_groups_playbook PASSED [ 77%]
tests/docker/test_docker_integration.py::test_run_all_playbooks_sequentially PASSED [ 88%]
tests/docker/test_docker_integration.py::test_connection_verbose PASSED  [100%]

============================= 9 passed in 56.38s ==============================
```

### Docker Environment Details

**Dockerfile** (`tests/docker/Dockerfile`):
- Based on Python 3.11-slim
- Installs Ansible, pytest, and all dependencies
- Includes entrypoint script for auto-building modules

**Entrypoint** (`tests/docker/entrypoint.sh`):
```bash
#!/bin/bash
# Automatically builds Ansible modules if not present
# Shows collection status
# Keeps container ready for testing
```

**Docker Compose** (`tests/docker/docker-compose.yml`):
- Mounts project directory
- Loads environment variables
- Sets correct Ansible collections path
- Keeps container running for interactive use

---

## Unit Tests

Test individual components in isolation.

### Running Unit Tests

```bash
# All unit tests
make test-unit

# Or directly with pytest
pytest tests/unit/ -v
```

### Unit Test Structure

```
tests/unit/
├── test_generator.py       # Module generator tests
├── test_module_utils.py    # API client tests  
└── test_declarative.py     # Declarative module logic tests
```

### Example Unit Test

```python
def test_user_declarative_idempotency():
    """Test that user module is idempotent."""
    # First run - creates user
    result1 = run_module({
        'id': 'test_user',
        'email': 'test@example.com',
        'state': 'present'
    })
    assert result1['changed'] == True
    
    # Second run - no changes
    result2 = run_module({
        'id': 'test_user', 
        'email': 'test@example.com',
        'state': 'present'
    })
    assert result2['changed'] == False
```

---

## Integration Tests

Test modules against mock or real APIs.

### Running Integration Tests

```bash
# All integration tests
make test-integration

# Specific integration test
pytest tests/integration/test_modules.py -v
```

---

## Coverage Reports

```bash
# Run tests with coverage
make test-coverage

# View HTML report
open htmlcov/index.html
```

---

## Linting

```bash
# Run all linters
make lint

# Individual linters
flake8 scripts/ tests/
black --check scripts/ tests/
pylint scripts/generator/
```

---

## Testing Best Practices

### 1. Always Test Idempotency

```python
def test_resource_idempotency(module):
    # Create
    result1 = module.run({'state': 'present', ...})
    assert result1['changed'] == True
    
    # Run again - should not change
    result2 = module.run({'state': 'present', ...})
    assert result2['changed'] == False
```

### 2. Test Check Mode

```python
def test_check_mode(module):
    result = module.run({
        'state': 'present',
        '_ansible_check_mode': True,
        ...
    })
    # Should report changes but not make them
    assert result['changed'] == True
    # Verify no actual changes were made
```

### 3. Test Cleanup

```yaml
# In playbooks
- name: Cleanup test resources
      cribl.core.user:
    id: test_user
    state: absent
  when: user_create is succeeded
```

### 4. Use Fixtures

```python
@pytest.fixture
def cribl_client():
    """Provide authenticated Cribl API client."""
    return CriblAPIClient(
        base_url=TEST_URL,
        username=TEST_USER,
        password=TEST_PASS
    )
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Cribl Ansible Collections

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: make test-unit
      
      - name: Run linters
        run: make lint
      
      - name: Run Docker integration tests
        run: |
          cd tests/docker
          docker-compose up -d
          pytest test_docker_integration.py -v -m docker
        env:
          CRIBL_URL: ${{ secrets.CRIBL_URL }}
          CRIBL_USERNAME: ${{ secrets.CRIBL_USERNAME }}
          CRIBL_PASSWORD: ${{ secrets.CRIBL_PASSWORD }}
      
      - name: Cleanup
        if: always()
        run: cd tests/docker && docker-compose down
```

---

## Troubleshooting

### Docker Container Won't Start

```bash
# Check Docker is running
docker info

# View container logs
docker logs cribl-ansible-test

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Module Not Found Errors

```bash
# Verify collections path
docker exec cribl-ansible-test env | grep ANSIBLE_COLLECTIONS_PATH

# Check collections are built
docker exec cribl-ansible-test ls -la /ansible/build/ansible_collections/cribl/

# Manually build modules
docker exec cribl-ansible-test python /ansible/scripts/generate_modules.py
```

### Connection Errors

```bash
# Test connectivity from container
docker exec cribl-ansible-test ping -c 3 your-cribl-host

# Test API directly
docker exec cribl-ansible-test curl -v http://your-cribl-host:9000/api/v1/health
```

### Environment Variables Not Set

```bash
# Check env file exists
cat env/test.env

# Verify vars in container
docker exec cribl-ansible-test env | grep CRIBL
```

---

## Additional Resources

- [Docker Test README](../tests/docker/README.md) - Detailed Docker testing guide
- [pytest Documentation](https://docs.pytest.org/) - pytest framework docs
- [Ansible Testing](https://docs.ansible.com/ansible/latest/dev_guide/testing.html) - Ansible testing guide
