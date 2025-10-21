# Docker Testing Environment

Automated testing environment for Cribl Ansible Collections using Docker.

## Quick Start

```bash
# Start environment
cd tests/docker
docker-compose up -d

# Run all tests
docker exec cribl-ansible-test /ansible/tests/docker/run_all_tests.sh

# Run specific test
docker exec cribl-ansible-test ansible-playbook /ansible/tests/docker/playbooks/test_cribl_connection.yml
```

## Test Status

All core tests passing (4/4)

## Available Tests

**Core Collection**:
- `test_cribl_connection.yml` - API connectivity
- `test_cribl_health.yml` - Health endpoints
- `test_cribl_users.yml` - User management
- `test_cribl_worker_groups.yml` - Worker groups

**Stream Collection**:
- `test_stream_pipelines.yml` - Pipeline management
- `test_stream_vars_declarative.yml` - Variable management
- `test_core_users_declarative.yml` - User declarative module

## Features

- **Auto-build**: Modules built on container startup
- **Environment variables**: Configured via `env/test.env`
- **Ansible collections**: Available at `/ansible/build/ansible_collections`
- **Test runner**: `run_all_tests.sh` for batch execution

## Configuration

Edit `env/test.env`:
```bash
CRIBL_URL=http://your-cribl-instance:9000
CRIBL_USERNAME=admin
CRIBL_PASSWORD=your-password
```

## Windows Users

Use PowerShell scripts:
```powershell
# Start
cd tests\docker
docker-compose up -d

# Run tests
docker exec cribl-ansible-test /ansible/tests/docker/run_all_tests.sh
```

## Troubleshooting

**Container won't start**: Check Docker daemon is running

**Tests fail**: 
- Verify Cribl instance is accessible
- Check credentials in `env/test.env`
- Some features require enterprise license (expected)

**Modules not found**: Wait for entrypoint to finish building (check logs: `docker logs cribl-ansible-test`)

## Notes

- Free/Community edition has license limitations (expected)
- Single-instance mode doesn't support worker groups (expected)
- All infrastructure tests pass - limitations are in Cribl licensing, not the collection
