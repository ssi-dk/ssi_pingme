"""Unit tests for PingMe class and related functions."""
import pytest
import json
from unittest.mock import patch, MagicMock
from pingme.pingme_class import Card, resolved_payload, PingMe, send_to_webhook, send_to_email


class TestCard:
    """Tests for Card model."""
    
    def test_card_creation(self):
        """Test Card can be created with valid data."""
        card = Card(
            name="test",
            context={"title": "Test", "text": "Message"}
        )
        
        assert card.name == "test"
        assert card.context["title"] == "Test"
        assert card.context["text"] == "Message"
    
    def test_card_validation(self):
        """Test Card validates required fields."""
        with pytest.raises(Exception):
            Card(name="test")  # Missing context


class TestResolvedPayload:
    """Tests for resolved_payload function."""
    
    def test_resolve_single_variable(self):
        """Test resolving a single variable in payload."""
        template = {"message": "${text}"}
        context = {"text": "Hello"}
        
        result = resolved_payload(template, context)
        
        assert result["message"] == "Hello"
    
    def test_resolve_multiple_variables(self):
        """Test resolving multiple variables in payload."""
        template = {
            "title": "${title}",
            "body": "${text}",
            "user": "${name}"
        }
        context = {
            "title": "Welcome",
            "text": "Hello World",
            "name": "Kim"
        }
        
        result = resolved_payload(template, context)
        
        assert result["title"] == "Welcome"
        assert result["body"] == "Hello World"
        assert result["user"] == "Kim"
    
    def test_resolve_nested_variables(self):
        """Test resolving variables in nested structures."""
        template = {
            "outer": {
                "inner": "${value}"
            }
        }
        context = {"value": "test"}
        
        result = resolved_payload(template, context)
        
        assert result["outer"]["inner"] == "test"
    
    def test_unresolved_variables_raise_error(self):
        """Test that unresolved variables raise ValueError."""
        template = {"message": "${missing}"}
        context = {}
        
        with pytest.raises(ValueError, match="Unresolved variables"):
            resolved_payload(template, context)
    
    def test_none_payload_raises_error(self):
        """Test that None payload raises ValueError."""
        with pytest.raises(ValueError, match="Payload is None"):
            resolved_payload(None, {})
    
    def test_no_variables_in_payload(self):
        """Test payload without variables works correctly."""
        template = {"static": "value"}
        context = {}
        
        result = resolved_payload(template, context)
        
        assert result["static"] == "value"


class TestSendToWebhook:
    """Tests for send_to_webhook function."""
    
    @patch('requests.post')
    def test_successful_webhook_post(self, mock_post):
        """Test successful webhook POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        payload = {"message": "test"}
        response = send_to_webhook(
            "https://example.com/webhook",
            json.dumps(payload)
        )
        
        assert response.status_code == 200
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_webhook_with_custom_headers(self, mock_post):
        """Test webhook with custom headers."""
        mock_response = MagicMock()
        mock_post.return_value = mock_response
        
        headers = {"Authorization": "Bearer token"}
        send_to_webhook(
            "https://example.com/webhook",
            '{"test": true}',
            headers
        )
        
        call_args = mock_post.call_args
        assert call_args[1]["headers"] == headers
    
    def test_webhook_none_url_raises_error(self):
        """Test that None URL raises exception."""
        with pytest.raises(Exception, match="Webhook URL not set"):
            send_to_webhook(None, '{}')
    
    @patch('requests.post')
    def test_webhook_connection_error(self, mock_post):
        """Test webhook handles connection errors."""
        mock_post.side_effect = ConnectionError("Network error")
        
        with pytest.raises(Exception, match="Error sending message to webhook"):
            send_to_webhook("https://example.com/webhook", '{}')


class TestSendToEmail:
    """Tests for send_to_email function."""
    
    @patch('smtplib.SMTP')
    def test_successful_email_send(self, mock_smtp):
        """Test successful email sending."""
        mock_connection = MagicMock()
        mock_smtp.return_value = mock_connection
        
        result = send_to_email(
            payload={"message": "test"},
            subject="Test Subject",
            from_="sender@example.com",
            to="recipient@example.com",
            host="smtp.example.com",
            port=587,
            user="user",
            password="pass"
        )
        
        result_data = json.loads(result)
        assert result_data["response"] is True
        mock_connection.sendmail.assert_called_once()
        mock_connection.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_email_with_default_port(self, mock_smtp):
        """Test email with default port."""
        mock_connection = MagicMock()
        mock_smtp.return_value = mock_connection
        
        send_to_email(
            payload={},
            subject="Test",
            from_="from@test.com",
            to="to@test.com",
            host="smtp.test.com"
        )
        
        mock_smtp.assert_called_with("smtp.test.com", 25)
    
    @patch('smtplib.SMTP')
    def test_email_connection_cleanup_on_error(self, mock_smtp):
        """Test that email connection is closed even on error."""
        mock_connection = MagicMock()
        mock_connection.sendmail.side_effect = Exception("Send failed")
        mock_smtp.return_value = mock_connection
        
        result = send_to_email(
            payload={},
            subject="Test",
            from_="from@test.com",
            to="to@test.com",
            host="smtp.test.com",
            user="user",
            password="pass"
        )
        
        # Connection should still be closed
        mock_connection.quit.assert_called_once()
        result_data = json.loads(result)
        assert result_data["response"] is False


class TestPingMeClass:
    """Tests for PingMe class."""
    
    @patch('pingme.pingme_class.core.get_config')
    def test_pingme_initialization(self, mock_get_config):
        """Test PingMe initialization with valid config."""
        mock_config = {
            "pingme": {
                "cards": {
                    "default": {
                        "variables": {"title": "Default", "text": "Text"},
                        "template": {"type": "message", "body": "${text}"}
                    }
                },
                "options": {
                    "email": {
                        "from": "test@example.com",
                        "to": "recipient@example.com",
                        "smtp": {
                            "host": "smtp.example.com",
                            "port": 587,
                            "user": "user",
                            "password": "pass"
                        }
                    },
                    "webhook": {"url": "https://example.com/webhook"},
                    "logfile": {"path": "/tmp/test.log"}
                }
            }
        }
        mock_get_config.return_value = mock_config
        
        card = Card(name="default", context={"title": "Test", "text": "Message"})
        pingme = PingMe(card)
        
        assert pingme.title == "Test"
        assert pingme.text == "Message"
        assert pingme.webhook["url"] == "https://example.com/webhook"
    
    @patch('pingme.pingme_class.core.get_config')
    def test_pingme_card_not_found(self, mock_get_config):
        """Test PingMe raises error for non-existent card."""
        mock_config = {
            "pingme": {
                "cards": {},
                "options": {
                    "email": {"from": "", "to": "", "smtp": {}},
                    "webhook": {},
                    "logfile": {}
                }
            }
        }
        mock_get_config.return_value = mock_config
        
        card = Card(name="nonexistent", context={})
        
        with pytest.raises(ValueError, match="Card name nonexistent not found"):
            PingMe(card)
    
    @patch('pingme.pingme_class.core.get_config')
    def test_pingme_uses_default_variables(self, mock_get_config):
        """Test PingMe uses default variable values when not provided."""
        mock_config = {
            "pingme": {
                "cards": {
                    "default": {
                        "variables": {
                            "title": "Default Title",
                            "text": "Default Text",
                            "extra": "Extra Value"
                        },
                        "template": {"msg": "${text}"}
                    }
                },
                "options": {
                    "email": {"from": "", "to": "", "smtp": {}},
                    "webhook": {},
                    "logfile": {}
                }
            }
        }
        mock_get_config.return_value = mock_config
        
        card = Card(name="default", context={"title": "Custom"})
        pingme = PingMe(card)
        
        assert pingme.card["context"]["title"] == "Custom"
        assert pingme.card["context"]["text"] == "Default Text"
        assert pingme.card["context"]["extra"] == "Extra Value"
