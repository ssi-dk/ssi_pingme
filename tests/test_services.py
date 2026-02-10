"""Unit tests for notification services."""
import pytest
import json
from unittest.mock import patch, MagicMock
from pingme.services import NotificationService
from pingme.pingme_class import Card


class TestWebhookServices:
    """Tests for webhook notification services."""
    
    @patch('pingme.services.PingMe')
    def test_send_default_card_to_webhook_success(self, mock_pingme_class):
        """Test sending default webhook card successfully."""
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_instance.send_webhook.return_value = mock_response
        mock_pingme_class.return_value = mock_instance
        
        result = NotificationService.send_default_card_to_webhook()
        
        assert result["status_code"] == 200
        assert result["response"]["success"] is True
        mock_instance.send_webhook.assert_called_once()
    
    @patch('pingme.services.PingMe')
    def test_send_default_card_to_webhook_non_json_response(self, mock_pingme_class):
        """Test webhook service handles non-JSON responses."""
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Plain text response"
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_instance.send_webhook.return_value = mock_response
        mock_pingme_class.return_value = mock_instance
        
        result = NotificationService.send_default_card_to_webhook()
        
        assert result["status_code"] == 200
        assert result["response"]["content"] == "Plain text response"
    
    @patch('pingme.services.PingMe')
    def test_send_simple_card_to_webhook(self, mock_pingme_class):
        """Test sending simple webhook card with title and text."""
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "sent"}
        mock_instance.send_webhook.return_value = mock_response
        mock_pingme_class.return_value = mock_instance
        
        result = NotificationService.send_simple_card_to_webhook(
            "My Title", "My Text"
        )
        
        assert result["status_code"] == 200
        assert result["response"]["message"] == "sent"
        mock_pingme_class.assert_called_once()
    
    @patch('pingme.services.PingMe')
    def test_send_card_to_webhook(self, mock_pingme_class):
        """Test sending custom card to webhook."""
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "123"}
        mock_instance.send_webhook.return_value = mock_response
        mock_pingme_class.return_value = mock_instance
        
        card = Card(
            name="default",
            context={"title": "Custom", "text": "Message"}
        )
        
        result = NotificationService.send_card_to_webhook(card)
        
        assert result["status_code"] == 201
        assert result["response"]["id"] == "123"


class TestEmailServices:
    """Tests for email notification services."""
    
    @patch('pingme.services.PingMe')
    def test_send_default_card_to_email_success(self, mock_pingme_class):
        """Test sending default email card successfully."""
        mock_instance = MagicMock()
        mock_instance.send_email.return_value = '{"response": true}'
        mock_pingme_class.return_value = mock_instance
        
        result = NotificationService.send_default_card_to_email()
        
        assert result["status_code"] == 200
        assert "successfully" in result["response"]
        mock_instance.send_email.assert_called_once()
    
    @patch('pingme.services.PingMe')
    def test_send_default_card_to_email_failure(self, mock_pingme_class):
        """Test email service handles send failures."""
        mock_instance = MagicMock()
        mock_instance.send_email.return_value = '{"response": false}'
        mock_pingme_class.return_value = mock_instance
        
        result = NotificationService.send_default_card_to_email()
        
        assert result["status_code"] == 500
        assert "Failed" in result["response"]
    
    @patch('pingme.services.PingMe')
    def test_send_simple_card_to_email(self, mock_pingme_class):
        """Test sending simple email with title and text."""
        mock_instance = MagicMock()
        mock_instance.send_email.return_value = '{"response": true}'
        mock_pingme_class.return_value = mock_instance
        
        result = NotificationService.send_simple_card_to_email(
            "Email Subject", "Email Body"
        )
        
        assert result["status_code"] == 200
        assert "successfully" in result["response"]
        mock_pingme_class.assert_called_once()
    
    @patch('pingme.services.PingMe')
    def test_send_card_to_email(self, mock_pingme_class):
        """Test sending custom card via email."""
        mock_instance = MagicMock()
        mock_instance.send_email.return_value = '{"response": true}'
        mock_pingme_class.return_value = mock_instance
        
        card = Card(
            name="default",
            context={"title": "Custom Subject", "text": "Custom Body"}
        )
        
        result = NotificationService.send_card_to_email(card)
        
        assert result["status_code"] == 200
        assert "successfully" in result["response"]
    
    @patch('pingme.services.PingMe')
    def test_send_email_with_invalid_json_response(self, mock_pingme_class):
        """Test email service handles invalid JSON response format."""
        mock_instance = MagicMock()
        mock_instance.send_email.return_value = "Not valid JSON"
        mock_pingme_class.return_value = mock_instance
        
        # This should raise an exception when trying to parse invalid JSON
        with pytest.raises(json.JSONDecodeError):
            NotificationService.send_simple_card_to_email(
                "Test", "Test"
            )


class TestServiceConfiguration:
    """Tests for service configuration handling."""
    
    @patch('pingme.services.settings')
    @patch('pingme.services.PingMe')
    def test_config_file_override(self, mock_pingme_class, mock_settings):
        """Test that config file can be overridden."""
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_instance.send_webhook.return_value = mock_response
        mock_pingme_class.return_value = mock_instance
        
        # The actual config override happens in CLI functions
        # This tests that services use settings.config_file
        NotificationService.send_default_card_to_webhook()
        
        # Verify PingMe was called with settings.config_file
        call_args = mock_pingme_class.call_args
        assert 'config_file' in call_args[1]
