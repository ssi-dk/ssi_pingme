"""Unit tests for API endpoints."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pingme.api import app
from pingme.pingme_class import Card


client = TestClient(app)


class TestWebhookEndpoints:
    """Tests for webhook API endpoints."""
    
    @patch('pingme.services.NotificationService.send_default_card_to_webhook')
    def test_webhook_card_default_success(self, mock_send):
        """Test default webhook endpoint returns success."""
        mock_send.return_value = {
            "status_code": 200,
            "response": {"success": True}
        }
        
        response = client.post("/webhook/default")
        
        assert response.status_code == 200
        assert response.json()["status_code"] == 200
        mock_send.assert_called_once()
    
    @patch('pingme.services.NotificationService.send_default_card_to_webhook')
    def test_webhook_card_default_error(self, mock_send):
        """Test default webhook endpoint handles errors."""
        mock_send.side_effect = Exception("Connection error")
        
        response = client.post("/webhook/default")
        
        assert response.status_code == 500
        assert "Connection error" in response.json()["detail"]
    
    @patch('pingme.services.NotificationService.send_simple_card_to_webhook')
    def test_webhook_card_simple_success(self, mock_send):
        """Test simple webhook endpoint with parameters."""
        mock_send.return_value = {
            "status_code": 200,
            "response": {"success": True}
        }
        
        response = client.post(
            "/webhook/simple",
            params={"title": "Test Title", "text": "Test Text"}
        )
        
        assert response.status_code == 200
        mock_send.assert_called_once_with("Test Title", "Test Text", channel=None)
    
    @patch('pingme.services.NotificationService.send_card_to_webhook')
    def test_webhook_card_custom_success(self, mock_send):
        """Test custom webhook endpoint with Card object."""
        mock_send.return_value = {
            "status_code": 200,
            "response": {"success": True}
        }
        
        card_data = {
            "name": "default",
            "context": {"title": "Custom Title", "text": "Custom Text"}
        }
        
        response = client.post("/webhook/card/", json=card_data)
        
        assert response.status_code == 200
        mock_send.assert_called_once()


class TestEmailEndpoints:
    """Tests for email API endpoints."""
    
    @patch('pingme.services.NotificationService.send_default_card_to_email')
    def test_email_card_default_success(self, mock_send):
        """Test default email endpoint returns success."""
        mock_send.return_value = {
            "status_code": 200,
            "response": "Email sent successfully"
        }
        
        response = client.post("/email/default")
        
        assert response.status_code == 200
        assert response.json()["status_code"] == 200
        mock_send.assert_called_once()
    
    @patch('pingme.services.NotificationService.send_default_card_to_email')
    def test_email_card_default_error(self, mock_send):
        """Test default email endpoint handles errors."""
        mock_send.side_effect = Exception("SMTP connection failed")
        
        response = client.post("/email/default")
        
        assert response.status_code == 500
        assert "SMTP connection failed" in response.json()["detail"]
    
    @patch('pingme.services.NotificationService.send_simple_card_to_email')
    def test_email_card_simple_success(self, mock_send):
        """Test simple email endpoint with parameters."""
        mock_send.return_value = {
            "status_code": 200,
            "response": "Email sent successfully"
        }
        
        response = client.post(
            "/email/simple",
            params={"title": "Test Subject", "text": "Test Body"}
        )
        
        assert response.status_code == 200
        mock_send.assert_called_once_with("Test Subject", "Test Body")
    
    @patch('pingme.services.NotificationService.send_card_to_email')
    def test_email_card_custom_success(self, mock_send):
        """Test custom email endpoint with Card object."""
        mock_send.return_value = {
            "status_code": 200,
            "response": "Email sent successfully"
        }
        
        card_data = {
            "name": "default",
            "context": {"title": "Custom Subject", "text": "Custom Body"}
        }
        
        response = client.post("/email/card/", json=card_data)
        
        assert response.status_code == 200
        mock_send.assert_called_once()


class TestHelpEndpoint:
    """Tests for help/root endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns help message."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "msg" in response.json()
        assert "docs" in response.json()["msg"]
    
    def test_help_endpoint(self):
        """Test help endpoint returns help message."""
        response = client.get("/help")
        
        assert response.status_code == 200
        assert "msg" in response.json()
        assert "docs" in response.json()["msg"]
