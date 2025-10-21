"""Integration tests for generated modules."""

import pytest
import subprocess
from pathlib import Path
import ast


@pytest.mark.integration
@pytest.mark.modules
class TestGeneratedModules:
    """Test generated modules are valid."""

    def test_core_modules_syntax(self, collections_dir):
        """Test core modules have valid Python syntax."""
        modules_dir = collections_dir / "core" / "plugins" / "modules"
        if not modules_dir.exists():
            pytest.skip("Modules not generated. Run 'python scripts/generate_modules.py' first.")
        modules = list(modules_dir.glob("cribl_*.py"))
        
        if len(modules) == 0:
            pytest.skip("No modules found. Run 'python scripts/generate_modules.py' first.")
        
        errors = []
        for module in modules:
            try:
                with open(module) as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                errors.append(f"{module.name}: {e}")
        
        assert len(errors) == 0, f"Syntax errors found:\n" + "\n".join(errors)

    def test_stream_modules_syntax(self, collections_dir):
        """Test stream modules have valid Python syntax."""
        modules_dir = collections_dir / "stream" / "plugins" / "modules"
        if not modules_dir.exists():
            pytest.skip("Modules not generated. Run 'python scripts/generate_modules.py' first.")
        modules = list(modules_dir.glob("cribl_*.py"))
        
        if len(modules) == 0:
            pytest.skip("No modules found. Run 'python scripts/generate_modules.py' first.")
        
        errors = []
        for module in modules:
            try:
                with open(module) as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                errors.append(f"{module.name}: {e}")
        
        assert len(errors) == 0, f"Syntax errors found:\n" + "\n".join(errors)

    def test_module_documentation_format(self, collections_dir):
        """Test modules have proper documentation format."""
        modules_dir = collections_dir / "core" / "plugins" / "modules"
        sample_modules = list(modules_dir.glob("cribl_*.py"))[:5]  # Test first 5
        
        for module in sample_modules:
            content = module.read_text()
            
            # Check required documentation blocks
            assert "DOCUMENTATION = r'''" in content, f"{module.name} missing DOCUMENTATION"
            assert "EXAMPLES = r'''" in content, f"{module.name} missing EXAMPLES"
            assert "RETURN = r'''" in content, f"{module.name} missing RETURN"
            
            # Check required imports
            assert "from ansible.module_utils.basic import AnsibleModule" in content
            
            # Check main function
            assert "def main():" in content
            assert "if __name__ == '__main__':" in content
            assert "main()" in content

    def test_module_extends_doc_fragment(self, collections_dir):
        """Test modules extend the correct doc fragment."""
        collections_list = ["core", "stream", "edge", "search", "lake"]
        
        for collection in collections_list:
            modules_dir = collections_dir / collection / "plugins" / "modules"
            sample_modules = list(modules_dir.glob("cribl_*.py"))[:2]  # Test first 2
            
            for module in sample_modules:
                content = module.read_text()
                expected_fragment = f"cribl.{collection}.cribl"
                assert expected_fragment in content, \
                    f"{module.name} doesn't extend {expected_fragment}"

    def test_module_imports_api_client(self, collections_dir):
        """Test modules import the API client correctly."""
        collections_list = ["core", "stream", "edge", "search", "lake"]
        
        for collection in collections_list:
            modules_dir = collections_dir / collection / "plugins" / "modules"
            sample_modules = list(modules_dir.glob("cribl_*.py"))[:2]
            
            for module in sample_modules:
                content = module.read_text()
                expected_import = f"from ansible_collections.cribl.{collection}.plugins.module_utils.cribl_api import"
                assert expected_import in content, \
                    f"{module.name} has incorrect import statement"

    def test_module_count_per_collection(self, collections_dir):
        """Test expected module counts per collection."""
        expected_counts = {
            "core": 276,
            "stream": 127,
            "edge": 19,
            "search": 80,
            "lake": 11
        }
        
        for collection, expected_count in expected_counts.items():
            modules_dir = collections_dir / collection / "plugins" / "modules"
            if not modules_dir.exists():
                pytest.skip("Modules not generated. Run 'python scripts/generate_modules.py' first.")
            actual_count = len(list(modules_dir.glob("cribl_*.py")))
            
            if actual_count == 0:
                pytest.skip("No modules found. Run 'python scripts/generate_modules.py' first.")
            
            # Allow some variance (±5) in case of updates
            assert abs(actual_count - expected_count) <= 5, \
                f"{collection} has {actual_count} modules, expected ~{expected_count}"


@pytest.mark.integration
def test_module_utils_api_client_exists(collections_dir):
    """Test that API client exists in each collection."""
    collections = ["core", "stream", "edge", "search", "lake"]
    
    for collection in collections:
        api_client = collections_dir / collection / "plugins" / "module_utils" / "cribl_api.py"
        assert api_client.exists(), f"API client not found in {collection}"
        
        # Check it has the CriblAPIClient class
        content = api_client.read_text()
        assert "class CriblAPIClient" in content
        assert "def login" in content
        assert "def get" in content
        assert "def post" in content

