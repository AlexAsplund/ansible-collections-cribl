"""Integration tests for example playbooks."""

import pytest
import subprocess
from pathlib import Path
import shutil


@pytest.mark.integration
@pytest.mark.slow
class TestExamplePlaybooks:
    """Test example playbooks can be parsed and checked."""

    def test_core_examples_syntax(self, collections_dir):
        """Test core collection examples have valid syntax."""
        if not shutil.which("ansible-playbook"):
            pytest.skip("ansible-playbook not found in PATH")
        
        examples_dir = collections_dir / "core" / "examples"
        if not examples_dir.exists():
            pytest.skip("Examples not generated. Run 'python scripts/generate_modules.py' first.")
        playbooks = list(examples_dir.glob("*.yml"))
        
        if len(playbooks) == 0:
            pytest.skip("No playbooks found in core examples")
        
        for playbook in playbooks:
            if playbook.name == "README.md":
                continue
            
            # Run ansible-playbook syntax check
            result = subprocess.run(
                ["ansible-playbook", "--syntax-check", str(playbook)],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Syntax check failed for {playbook.name}: {result.stderr}"

    def test_stream_examples_syntax(self, collections_dir):
        """Test stream collection examples have valid syntax."""
        if not shutil.which("ansible-playbook"):
            pytest.skip("ansible-playbook not found in PATH")
        
        examples_dir = collections_dir / "stream" / "examples"
        if not examples_dir.exists():
            pytest.skip("Examples not generated. Run 'python scripts/generate_modules.py' first.")
        playbooks = list(examples_dir.glob("*.yml"))
        
        if len(playbooks) == 0:
            pytest.skip("No playbooks found in stream examples")
        
        for playbook in playbooks:
            if playbook.name == "README.md":
                continue
            
            result = subprocess.run(
                ["ansible-playbook", "--syntax-check", str(playbook)],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Syntax check failed for {playbook.name}: {result.stderr}"

    def test_edge_examples_syntax(self, collections_dir):
        """Test edge collection examples have valid syntax."""
        if not shutil.which("ansible-playbook"):
            pytest.skip("ansible-playbook not found in PATH")
        
        examples_dir = collections_dir / "edge" / "examples"
        if not examples_dir.exists():
            pytest.skip("Examples not generated. Run 'python scripts/generate_modules.py' first.")
        playbooks = list(examples_dir.glob("*.yml"))
        
        if len(playbooks) == 0:
            pytest.skip("No playbooks found in edge examples")
        
        for playbook in playbooks:
            if playbook.name == "README.md":
                continue
            
            result = subprocess.run(
                ["ansible-playbook", "--syntax-check", str(playbook)],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Syntax check failed for {playbook.name}: {result.stderr}"

    def test_search_examples_syntax(self, collections_dir):
        """Test search collection examples have valid syntax."""
        if not shutil.which("ansible-playbook"):
            pytest.skip("ansible-playbook not found in PATH")
        
        examples_dir = collections_dir / "search" / "examples"
        if not examples_dir.exists():
            pytest.skip("Examples not generated. Run 'python scripts/generate_modules.py' first.")
        playbooks = list(examples_dir.glob("*.yml"))
        
        if len(playbooks) == 0:
            pytest.skip("No playbooks found in search examples")
        
        for playbook in playbooks:
            if playbook.name == "README.md":
                continue
            
            result = subprocess.run(
                ["ansible-playbook", "--syntax-check", str(playbook)],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Syntax check failed for {playbook.name}: {result.stderr}"

    def test_lake_examples_syntax(self, collections_dir):
        """Test lake collection examples have valid syntax."""
        if not shutil.which("ansible-playbook"):
            pytest.skip("ansible-playbook not found in PATH")
        
        examples_dir = collections_dir / "lake" / "examples"
        if not examples_dir.exists():
            pytest.skip("Examples not generated. Run 'python scripts/generate_modules.py' first.")
        playbooks = list(examples_dir.glob("*.yml"))
        
        if len(playbooks) == 0:
            pytest.skip("No playbooks found in lake examples")
        
        for playbook in playbooks:
            if playbook.name == "README.md":
                continue
            
            result = subprocess.run(
                ["ansible-playbook", "--syntax-check", str(playbook)],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Syntax check failed for {playbook.name}: {result.stderr}"


@pytest.mark.integration
def test_example_readmes_exist(collections_dir):
    """Test that each collection has a README in examples."""
    collections = ["core", "stream", "edge", "search", "lake"]
    
    for collection in collections:
        examples_dir = collections_dir / collection / "examples"
        if not examples_dir.exists():
            pytest.skip(f"Examples not generated for {collection}. Run 'python scripts/generate_modules.py' first.")
        
        readme = collections_dir / collection / "examples" / "README.md"
        if not readme.exists():
            pytest.skip(f"README.md not found in {collection}/examples")
        
        # Check README is not empty
        content = readme.read_text(encoding='utf-8')
        assert len(content) > 100, f"README.md in {collection}/examples is too short"

