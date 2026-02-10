"""Pytest configuration and fixtures for pingme tests."""
import os
import pytest
from pathlib import Path


@pytest.fixture
def test_config_file():
    """Return path to test config file."""
    return str(Path(__file__).parent.parent / "test.config.env")


@pytest.fixture
def mock_card_data():
    """Return mock card data for testing."""
    return {
        "name": "default",
        "context": {"title": "Test Title", "text": "Test Text"}
    }


@pytest.fixture
def mock_email_response():
    """Return mock email response."""
    return '{"response": true}'


@pytest.fixture
def mock_webhook_response():
    """Return mock successful webhook response."""
    class MockResponse:
        status_code = 200
        text = "Success"
        
        def json(self):
            return {"success": True}
    
    return MockResponse()


@pytest.fixture
def mock_failed_webhook_response():
    """Return mock failed webhook response."""
    class MockResponse:
        status_code = 500
        text = "Internal Server Error"
        
        def json(self):
            raise ValueError("Not JSON")
    
    return MockResponse()
