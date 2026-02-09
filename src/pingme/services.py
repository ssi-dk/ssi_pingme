import json
from .core import settings, logger
from .pingme_class import Card, PingMe
from fastcore.script import (
    call_parse,
)  # for @call_parse, https://fastcore.fast.ai/script

def parse_smtp_response(response):
    """
    Parses the SMTP response to determine if the email was sent successfully.
    The response should be a JSON string with a "response" key that is True if the email was sent successfully.

    Args:
    response: str: The SMTP response as a JSON string
    Returns:
    dict: A dictionary with status_code and response message
    """ 
    if json.loads(response).get("response") is True:
        response_data = {"status_code": 200, "response": "Email sent successfully"}
    else:
        response_data = {"status_code": 500, "response": "Failed to send email"}
    return response_data

def parse_webhook_response(response):
    """
    Parses the webhook response to determine if the message was sent successfully.
    The response should be a JSON string with a "status_code" key that is 200 if the message was sent successfully.

    Args:
    response: str: The webhook response as a JSON string
    Returns:
    dict: A dictionary with status_code and response message
    """ 

    try:
        response_data = response.json()
    except ValueError:
        # Return text content if not JSON
        response_data = {
            "content": response.text if response.text else "No content"
        }
    return {"status_code": response.status_code, "response": response_data}

class NotificationService:
    @staticmethod
    def send_default_card_to_webhook():
        # Handles all logic for processing notifications
        logger.info("Sending default webhook card")
        card = Card.model_validate(
            {
                "name": "default",
                "context": {"title": "Default Title", "text": "Test Text"},
            }
        )
        notification = PingMe(
            card,
            config_file=settings.config_file,
        )
        response = notification.send_webhook()
       
        return parse_webhook_response(response)

    @staticmethod
    def send_simple_card_to_webhook(title: str, text: str):
        # Handles all logic for processing notifications
        logger.info("Sending simple webhook card")
        card = Card.model_validate(
            {
                "name": "default",
                "context": {"title": title, "text": text},
            }
        )
        notification = PingMe(
            card,
            config_file=settings.config_file,
        )
        response = notification.send_webhook()
        # Handle response safely
        return parse_webhook_response(response)

    @staticmethod
    def send_card_to_webhook(card: Card):
        # Handles all logic for processing notifications
        logger.info("Sending webhook card")
        notification = PingMe(
            card,
            config_file=settings.config_file,
        )
        response = notification.send_webhook()
        # Handle response safely
        return parse_webhook_response(response)


    @staticmethod
    def send_default_card_to_email():
        # Handles all logic for processing email notifications
        logger.info("Sending default email card")
        card = Card.model_validate(
            {
                "name": "default",
                "context": {"title": "Default Title", "text": "Test Text"},
            }
        )
        notification = PingMe(
            card,
            config_file=settings.config_file,
        )
        response = notification.send_email()
        return parse_smtp_response(response)

    @staticmethod
    def send_simple_card_to_email(title: str, text: str):
        # Handles all logic for processing email notifications
        logger.info("Sending simple email card")
        card = Card.model_validate(
            {
                "name": "default",
                "context": {"title": title, "text": text},
            }
        )
        notification = PingMe(
            card,
            config_file=settings.config_file,
        )
        response = notification.send_email()
        return parse_smtp_response(response)

    @staticmethod
    def send_card_to_email(card: Card):
        # Handles all logic for processing email notifications
        logger.info("Sending email card")
        notification = PingMe(
            card,
            config_file=settings.config_file,
        )
        response = notification.send_email()
        return parse_smtp_response(response)

# Make a CLI function using `call_parse` to handle arguments
@call_parse
def pingme_send_default_card_to_webhook(
    config_file: str = None,
):
    """
    Send a card to the webhook with default values

    Args:
    - config_file: str = None: Path to the config file, none uses default
    """
    # Override settings if provided
    if config_file:
        settings.config_file = config_file
    NotificationService.send_default_card_to_webhook()


# Make a CLI function using `call_parse` to handle arguments
@call_parse
def pingme_send_simple_card_to_webhook(
    title: str,
    text: str,
    config_file: str = None,
):
    """
    Send a card to the webhook with title and text

    Args:
    - title: str: Title of the card
    - text: str: Text of the card
    - config_file: str = None: Path to the config file, none uses default
    """
    # Override settings if provided
    if config_file:
        settings.config_file = config_file
    NotificationService.send_simple_card_to_webhook(title, text)


@call_parse
def pingme_send_card_to_webhook(
    card: Card,
    config_file: str = None,
):
    """
    Send a card to the webhook

    Args:
    - card: Card: Card object to send
    - config_file: str = None: Path to the config file, none uses default
    """
    # Override settings if provided
    if config_file:
        settings.config_file = config_file
    NotificationService.send_card_to_webhook(card)


# Make a CLI function using `call_parse` to handle arguments
@call_parse
def pingme_send_default_card_to_email(
    config_file: str = None,
):
    """
    Send a card to email with default values

    Args:
    - config_file: str = None: Path to the config file, none uses default
    """
    # Override settings if provided
    if config_file:
        settings.config_file = config_file
    NotificationService.send_default_card_to_email()


# Make a CLI function using `call_parse` to handle arguments
@call_parse
def pingme_send_simple_card_to_email(
    title: str,
    text: str,
    config_file: str = None,
):
    """
    Send a card to email with title and text

    Args:
    - title: str: Title of the email
    - text: str: Text of the email
    - config_file: str = None: Path to the config file, none uses default
    """
    # Override settings if provided
    if config_file:
        settings.config_file = config_file
    NotificationService.send_simple_card_to_email(title, text)


@call_parse
def pingme_send_card_to_email(
    card: Card,
    config_file: str = None,
):
    """
    Send a card to email

    Args:
    - card: Card: Card object to send
    - config_file: str = None: Path to the config file, none uses default
    """
    # Override settings if provided
    if config_file:
        settings.config_file = config_file
    NotificationService.send_card_to_email(card)
