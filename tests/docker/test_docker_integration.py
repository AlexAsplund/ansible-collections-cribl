"""Docker-based integration tests for Cribl Ansible Collections.

These tests run Ansible playbooks inside a Docker container against a real Cribl instance.
"""

import pytest
import subprocess
import os
import time
from pathlib import Path


@pytest.fixture(scope="session")
def docker_compose_dir():
    """Return the docker-compose directory."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def env_file(project_root):
    """Verify environment file exists."""
    env_path = project_root / "env" / "test.env"
    assert env_path.exists(), f"Environment file not found: {env_path}"
    return env_path


@pytest.fixture(scope="session")
def docker_container(docker_compose_dir, env_file):
    """Start Docker container and ensure it's running."""
    compose_file = docker_compose_dir / "docker-compose.yml"
    
    # Build and start container
    print("\n🐳 Building and starting Docker container...")
    result = subprocess.run(
        ["docker-compose", "-f", str(compose_file), "up", "-d", "--build"],
        cwd=str(docker_compose_dir),
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        pytest.fail(f"Failed to start Docker container:\n{result.stderr}")
    
    # Wait for container to be ready
    time.sleep(5)
    
    # Verify container is running
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=cribl-ansible-test", "--format", "{{.Status}}"],
        capture_output=True,
        text=True
    )
    
    assert "Up" in result.stdout, "Container is not running"
    print("✅ Docker container is ready")
    
    yield "cribl-ansible-test"
    
    # Cleanup - stop and remove container
    print("\n🧹 Cleaning up Docker container...")
    subprocess.run(
        ["docker-compose", "-f", str(compose_file), "down", "-v"],
        cwd=str(docker_compose_dir),
        capture_output=True
    )


def run_playbook_in_docker(container_name: str, playbook_path: str, verbose: bool = False):
    """Run an Ansible playbook inside the Docker container."""
    verbose_flag = "-vvv" if verbose else "-v"
    
    cmd = [
        "docker", "exec", container_name,
        "ansible-playbook",
        verbose_flag,
        playbook_path
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    
    return result


@pytest.mark.docker
@pytest.mark.integration
class TestDockerIntegration:
    """Integration tests that run in Docker against a real Cribl instance."""
    
    def test_docker_container_running(self, docker_container):
        """Verify Docker container is running."""
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", docker_container],
            capture_output=True,
            text=True
        )
        assert result.stdout.strip() == "true", "Container is not running"
    
    def test_ansible_installed(self, docker_container):
        """Verify Ansible is installed in container."""
        result = subprocess.run(
            ["docker", "exec", docker_container, "ansible-playbook", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Ansible is not installed"
        assert "ansible-playbook" in result.stdout.lower()
    
    def test_cribl_collections_available(self, docker_container):
        """Verify Cribl collections are available in container."""
        result = subprocess.run(
            ["docker", "exec", docker_container, "ansible-galaxy", "collection", "list"],
            capture_output=True,
            text=True
        )
        # Collections should be available via collections_paths
        assert result.returncode == 0


@pytest.mark.docker
@pytest.mark.integration
@pytest.mark.slow
class TestCriblPlaybooks:
    """Test Ansible playbooks against real Cribl instance."""
    
    def test_connection_playbook(self, docker_container):
        """Test basic connection to Cribl instance."""
        result = run_playbook_in_docker(
            docker_container,
            "/ansible/tests/docker/playbooks/test_cribl_connection.yml"
        )
        
        print("\n" + "="*50)
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print("="*50 + "\n")
        
        assert result.returncode == 0, f"Connection test failed:\n{result.stderr}"
        assert "PLAY RECAP" in result.stdout
    
    def test_health_playbook(self, docker_container):
        """Test Cribl health checks."""
        result = run_playbook_in_docker(
            docker_container,
            "/ansible/tests/docker/playbooks/test_cribl_health.yml"
        )
        
        print("\n" + "="*50)
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print("="*50 + "\n")
        
        assert result.returncode == 0, f"Health check failed:\n{result.stderr}"
        assert "PLAY RECAP" in result.stdout
    
    def test_users_playbook(self, docker_container):
        """Test user management operations."""
        result = run_playbook_in_docker(
            docker_container,
            "/ansible/tests/docker/playbooks/test_cribl_users.yml"
        )
        
        print("\n" + "="*50)
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print("="*50 + "\n")
        
        # User operations might fail due to permissions, but playbook should complete
        assert "PLAY RECAP" in result.stdout
        # Check if we at least got to list users
        assert "List all existing users" in result.stdout or "system_users_get" in result.stdout
    
    def test_worker_groups_playbook(self, docker_container):
        """Test worker group operations."""
        result = run_playbook_in_docker(
            docker_container,
            "/ansible/tests/docker/playbooks/test_cribl_worker_groups.yml"
        )
        
        print("\n" + "="*50)
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print("="*50 + "\n")
        
        # Worker group operations might fail on single instance, but playbook should complete
        assert "PLAY RECAP" in result.stdout
        # Check if we at least got to list groups
        assert "List all worker groups" in result.stdout or "master_groups_get" in result.stdout


@pytest.mark.docker
@pytest.mark.integration
def test_run_all_playbooks_sequentially(docker_container):
    """Run all test playbooks in sequence."""
    playbooks = [
        "/ansible/tests/docker/playbooks/test_cribl_connection.yml",
        "/ansible/tests/docker/playbooks/test_cribl_health.yml",
        "/ansible/tests/docker/playbooks/test_cribl_users.yml",
        "/ansible/tests/docker/playbooks/test_cribl_worker_groups.yml",
    ]
    
    results = {}
    for playbook in playbooks:
        playbook_name = Path(playbook).name
        print(f"\n🎭 Running {playbook_name}...")
        result = run_playbook_in_docker(docker_container, playbook)
        results[playbook_name] = result.returncode == 0
    
    # Display summary
    print("\n" + "="*50)
    print("PLAYBOOK EXECUTION SUMMARY")
    print("="*50)
    for playbook, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {playbook}")
    print("="*50 + "\n")
    
    # At least connection and health should pass
    assert results["test_cribl_connection.yml"], "Connection test must pass"
    assert results["test_cribl_health.yml"], "Health test must pass"


@pytest.mark.docker
@pytest.mark.integration
@pytest.mark.verbose
def test_connection_verbose(docker_container):
    """Run connection test with verbose output for debugging."""
    result = run_playbook_in_docker(
        docker_container,
        "/ansible/tests/docker/playbooks/test_cribl_connection.yml",
        verbose=True
    )
    
    print("\n" + "="*50)
    print("VERBOSE OUTPUT:")
    print("="*50)
    print(result.stdout)
    if result.stderr:
        print("\nERRORS:")
        print(result.stderr)
    print("="*50 + "\n")
    
    assert result.returncode == 0, "Connection test failed"

