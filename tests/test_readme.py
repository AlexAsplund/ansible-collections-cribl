"""Tests for project documentation."""

import pytest
from pathlib import Path


@pytest.mark.unit
def test_readme_exists(project_root):
    """Test that README.md exists."""
    readme = project_root / "README.md"
    assert readme.exists(), "README.md not found"
    
    content = readme.read_text(encoding='utf-8')
    assert len(content) > 1000, "README.md is too short"


@pytest.mark.unit
def test_readme_has_badges(project_root):
    """Test that README has badges."""
    readme = project_root / "README.md"
    content = readme.read_text(encoding='utf-8')
    
    assert "![License:" in content, "License badge not found"
    assert "![Ansible" in content, "Ansible badge not found"
    assert "![Python" in content, "Python badge not found"


@pytest.mark.unit
def test_readme_has_sections(project_root):
    """Test that README has all required sections."""
    readme = project_root / "README.md"
    content = readme.read_text(encoding='utf-8')
    
    required_sections = [
        "# Cribl Ansible Collections",
        "Quick Start",  # Match with or without emoji
        "What's Included",
        "Usage Examples",
        "Testing",
        "Module Generator",
        "Documentation",
        "License"
    ]
    
    for section in required_sections:
        assert section in content, f"Section '{section}' not found in README"


@pytest.mark.unit
def test_license_exists(project_root):
    """Test that LICENSE file exists."""
    license_file = project_root / "LICENSE"
    assert license_file.exists(), "LICENSE file not found"
    
    content = license_file.read_text(encoding='utf-8')
    assert "MIT License" in content, "Not an MIT license"


@pytest.mark.unit
def test_contributing_exists(project_root):
    """Test that CONTRIBUTING.md exists."""
    contributing = project_root / "CONTRIBUTING.md"
    assert contributing.exists(), "CONTRIBUTING.md not found"
    
    content = contributing.read_text(encoding='utf-8')
    assert len(content) > 500, "CONTRIBUTING.md is too short"
    assert "Pull Request" in content, "PR guidelines not found"


@pytest.mark.unit
def test_gitignore_exists(project_root):
    """Test that .gitignore exists and has required entries."""
    gitignore = project_root / ".gitignore"
    assert gitignore.exists(), ".gitignore not found"
    
    content = gitignore.read_text(encoding='utf-8')
    
    required_entries = [
        "*.pyc",
        "__pycache__",
        ".venv",
        "*.tar.gz",
        ".DS_Store"
    ]
    
    for entry in required_entries:
        assert entry in content, f"{entry} not found in .gitignore"

