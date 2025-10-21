"""Unit tests for the module generator."""

import pytest
from pathlib import Path
import sys
import yaml

# Add parent directory to path to import the generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from generate_modules import CriblModuleGenerator


@pytest.mark.unit
@pytest.mark.generator
class TestCriblModuleGenerator:
    """Test the module generator."""

    def test_generator_initialization(self, openapi_spec_path):
        """Test generator can be initialized."""
        generator = CriblModuleGenerator(
            str(openapi_spec_path),
            "build/ansible_collections/cribl"
        )
        assert str(generator.parser.spec_file) == str(openapi_spec_path)
        assert generator.parser.spec is None
        assert len(generator.stats) == 5  # 5 products: core, stream, edge, search, lake

    def test_load_spec(self, openapi_spec_path):
        """Test loading the OpenAPI specification."""
        generator = CriblModuleGenerator(
            str(openapi_spec_path),
            "build/ansible_collections/cribl"
        )
        generator.parser.load()
        
        assert generator.parser.spec is not None
        assert 'info' in generator.parser.spec
        assert 'paths' in generator.parser.spec
        assert generator.parser.spec['info']['version'] == '4.14.0-837595d5'

    def test_categorize_endpoint(self, openapi_spec_path):
        """Test endpoint categorization."""
        generator = CriblModuleGenerator(
            str(openapi_spec_path),
            "build/ansible_collections/cribl"
        )
        
        # Test categorization
        assert generator.parser.categorize_endpoint("/auth/login") == "core"
        assert generator.parser.categorize_endpoint("/system/users") == "core"
        assert generator.parser.categorize_endpoint("/master/groups") == "core"
        assert generator.parser.categorize_endpoint("/pipelines") == "stream"
        assert generator.parser.categorize_endpoint("/system/inputs") == "stream"
        assert generator.parser.categorize_endpoint("/edge/processes") == "edge"
        assert generator.parser.categorize_endpoint("/search/datasets") == "search"
        assert generator.parser.categorize_endpoint("/products/lake/lakes/x/datasets") == "lake"

    def test_should_generate_module(self, openapi_spec_path):
        """Test module generation decision logic."""
        generator = CriblModuleGenerator(
            str(openapi_spec_path),
            "build/ansible_collections/cribl"
        )
        
        # Should generate auth/login (needed for token acquisition)
        assert generator.parser.should_generate("/auth/login", "post", {})
        
        # Should skip deprecated
        assert not generator.parser.should_generate("/some/endpoint", "get", {"deprecated": True})
        
        # Should generate for valid endpoints
        assert generator.parser.should_generate("/system/users", "get", {})
        assert generator.parser.should_generate("/system/users", "post", {})
        
        # Should skip invalid methods
        assert not generator.parser.should_generate("/system/users", "options", {})


@pytest.mark.unit
@pytest.mark.generator
def test_module_file_structure(collections_dir):
    """Test that generated module files have correct structure."""
    # Check core modules
    core_modules_dir = collections_dir / "core" / "plugins" / "modules"
    assert core_modules_dir.exists()
    
    # Get a sample module (look for any .py file that's not __init__.py)
    modules = [m for m in core_modules_dir.glob("*.py") if m.name != "__init__.py"]
    assert len(modules) > 0, "No modules found in core collection"
    
    # Check first module has required structure
    sample_module = modules[0]
    content = sample_module.read_text()
    
    assert "DOCUMENTATION = r'''" in content
    assert "EXAMPLES = r'''" in content
    assert "RETURN = r'''" in content
    assert "from ansible.module_utils.basic import AnsibleModule" in content
    assert "def main():" in content
    assert "if __name__ == '__main__':" in content


@pytest.mark.unit
@pytest.mark.generator
def test_collection_structure(collections_dir):
    """Test that all collections have proper structure."""
    collections = ["core", "stream", "edge", "search", "lake"]
    
    for collection in collections:
        coll_dir = collections_dir / collection
        assert coll_dir.exists(), f"{collection} collection not found"
        
        # Check required directories
        assert (coll_dir / "plugins" / "modules").exists()
        assert (coll_dir / "plugins" / "module_utils").exists()
        assert (coll_dir / "plugins" / "doc_fragments").exists()
        assert (coll_dir / "examples").exists()
        
        # Check required files
        assert (coll_dir / "galaxy.yml").exists()
        assert (coll_dir / "MODULES.md").exists()
        assert (coll_dir / "plugins" / "module_utils" / "cribl_api.py").exists()
        assert (coll_dir / "plugins" / "doc_fragments" / "cribl.py").exists()


@pytest.mark.unit
@pytest.mark.generator
def test_galaxy_yml_format(collections_dir):
    """Test that galaxy.yml files are properly formatted."""
    collections = ["core", "stream", "edge", "search", "lake"]
    
    for collection in collections:
        galaxy_file = collections_dir / collection / "galaxy.yml"
        assert galaxy_file.exists()
        
        with open(galaxy_file) as f:
            galaxy_data = yaml.safe_load(f)
        
        # Check required fields
        assert galaxy_data["namespace"] == "cribl"
        assert galaxy_data["name"] == collection
        # Version is extracted from OpenAPI schema and should be "4.14.0"
        assert galaxy_data["version"] == "4.14.0"
        assert "MIT" in galaxy_data["license"]
        assert len(galaxy_data["authors"]) > 0
        assert len(galaxy_data["description"]) > 0

