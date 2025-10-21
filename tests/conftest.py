"""Pytest configuration and fixtures for Cribl Ansible Collections tests."""

import pytest
import os
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def openapi_spec_path(project_root):
    """Return the path to the OpenAPI spec file."""
    return project_root / "schemas" / "cribl-apidocs-4.14.0-837595d5.yml"


@pytest.fixture
def collections_dir(project_root):
    """Return the path to the collections directory."""
    return project_root / "build" / "ansible_collections" / "cribl"


@pytest.fixture
def test_cribl_url():
    """Return a test Cribl URL."""
    return os.getenv("TEST_CRIBL_URL", "https://test.cribl.example.com")


@pytest.fixture
def test_cribl_username():
    """Return a test Cribl username."""
    return os.getenv("TEST_CRIBL_USERNAME", "test_user")


@pytest.fixture
def test_cribl_password():
    """Return a test Cribl password."""
    return os.getenv("TEST_CRIBL_PASSWORD", "test_password")


@pytest.fixture
def mock_api_response():
    """Return a mock API response."""
    return {
        "items": [
            {"id": "item1", "name": "Item 1"},
            {"id": "item2", "name": "Item 2"}
        ],
        "count": 2
    }


@pytest.fixture
def sample_module_data():
    """Return sample module data for testing."""
    return {
        "endpoint": "/system/users",
        "method": "GET",
        "operation": {
            "summary": "Get all users",
            "description": "Retrieves a list of all users",
            "parameters": [],
            "responses": {
                "200": {
                    "description": "Success"
                }
            }
        }
    }

