import uvicorn  # Server for hosting the API, ref: https://www.uvicorn.org/
from fastapi import FastAPI  # library for creating the API
from fastapi.testclient import TestClient  # test client for notebook to test API calls
from fastapi import HTTPException  # for raising exceptions

from .core import settings
from . import core
from .pingme_class import Card
from .services import NotificationService

from fastcore.script import call_parse

import json  # for parsing json data


app = FastAPI()


@app.post("/webhook/default")
def webhook_card_default(channel: str = None):
    """
    Send a default card to the webhook, intention is strictly for testing and showcasing.
    """
    try:
        return NotificationService.send_default_card_to_webhook(channel=channel)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/simple")
def webhook_card_simple(title: str, text: str, channel: str = None):
    """
    Send a simple card to the webhook, should be used for most general use cases of sending a message.

    Args:
        title (str):  Title of the card
        text (str): Text of the card
    """
    try:
        return NotificationService.send_simple_card_to_webhook(title, text, channel=channel)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/card/")
def webhook_card(card: Card, channel: str = None):
    """
    Send a card to the webhook, card defines a card thats installed into the config.yaml. Advanced usage which may not get used.

    Args:
        card (Card): Card object
    """
    try:
        return NotificationService.send_card_to_webhook(card, channel=channel)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/email/default")
def email_card_default():
    """
    Send a default card via email, intention is strictly for testing and showcasing.
    """
    try:
        return NotificationService.send_default_card_to_email()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/email/simple")
def email_card_simple(title: str, text: str):
    """
    Send a simple card via email, should be used for most general use cases of sending an email message.

    Args:
        title (str): Title of the email (subject)
        text (str): Text of the email
    """
    try:
        return NotificationService.send_simple_card_to_email(title, text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/email/card/")
def email_card(card: Card):
    """
    Send a card via email, card defines a card that's installed into the config.yaml. Advanced usage which may not get used.

    Args:
        card (Card): Card object
    """
    try:
        return NotificationService.send_card_to_email(card)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(path="/")
@app.get("/help", tags=["help"])
async def help():
    """
    Information on how to use API to users, when they hit the root URL. Ensure when you add new endpoints to update this function, check /docs for info on endpoints.
    """
    return {"msg": "please check /docs for more information on how to use the API"}

@call_parse
def webservice(
    host: str = "127.0.0.1",  # Host to run the server on
    port: int = 5000,  # Port to run the server on"
    config_file: str = None,  # Path to config file"
):
    """Start the PingMe API server
    
    Args:
        host (str): Host to run the server on, default is 127.0.1
        port (int): Port to run the server on, default is 5000
        config_file (str): Path to config file, default is None which uses default config file
    """
    # Override settings if provided
    if config_file is not None:
        settings.config_file = config_file

    

    # Run using module path instead of app instance to ensure updated config
    uvicorn.run("pingme.api:app", host=host, port=port, reload=core.DEV_MODE)
