"""
Tests for the HealthCheck class and related functionality.
"""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from datetime import timedelta

from main import HealthCheck


def create_temp_yaml_file(content):
    """Helper to create a temporary YAML file with given content."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
    temp_file.write(content.encode("utf-8"))
    temp_file.close()
    return temp_file.name


@pytest.fixture
def sample_endpoints_yaml():
    """Sample YAML content for testing."""
    return """
- name: Test Endpoint 1
  url: https://blackowiak.org
  method: GET
- name: Test Endpoint 2
  url: https://api.blackowiak.org
  method: POST
  headers:
    Content-Type: application/json
  body: '{"test": true}'
"""


@pytest.fixture
def health_check(sample_endpoints_yaml):
    """Fixture that creates a HealthCheck instance with sample data."""
    file_path = create_temp_yaml_file(sample_endpoints_yaml)

    # Create health check instance
    check = HealthCheck(file_path, 15)

    yield check

    # Cleanup
    os.unlink(file_path)


def test_initialization(health_check):
    """Test that the HealthCheck class initializes correctly."""
    assert health_check.test_interval == 15
    assert len(health_check.endpoints) == 2
    assert health_check.run_count == 0


def test_get_domain(health_check):
    """Test domain extraction from URLs."""
    assert health_check.get_domain("https://blackowiak.org") == "blackowiak.org"
    assert (
        health_check.get_domain("http://api.blackowiak.org/v1/test")
        == "api.blackowiak.org"
    )


@patch("requests.request")
def test_begin_health_check(mock_request, health_check):
    """Test health check with successful and failed endpoints."""
    # Create mock responses for each endpoint
    responses = [
        MagicMock(status_code=200, elapsed=timedelta(milliseconds=100)),
        MagicMock(status_code=404, elapsed=timedelta(milliseconds=50)),
    ]
    mock_request.side_effect = responses

    # Run the health check
    health_check.begin_health_check()

    # Verify the results
    assert health_check.results["blackowiak.org"]["requests"] == 1
    assert health_check.results["blackowiak.org"]["UP"] == 1

    assert health_check.results["api.blackowiak.org"]["requests"] == 1
    assert health_check.results["api.blackowiak.org"]["UP"] == 0

    assert health_check.run_count == 1


def test_invalid_config_file():
    """Test that invalid config files are handled properly."""
    # Create an invalid YAML file
    file_path = create_temp_yaml_file("This is not valid YAML: :")

    # Attempting to create a HealthCheck with this file should exit
    with pytest.raises(SystemExit):
        HealthCheck(file_path, 15)

    # Clean up
    os.unlink(file_path)
