"""
Module: helena_bot.core.flask_server

This module is responsible for creating and configuring the Flask web application
used by HelenaBot. It defines basic HTTP endpoints for system health monitoring
and acts as the foundation for receiving webhooks from external services.

Endpoints exposed:
- GET `/`            : Internal container healthcheck (basic)
- GET `/healthcheck`: External-facing healthcheck used to verify tunnel accessibility

This module is typically initialized as part of the system startup (`startup.py`).
The `Flask` application is designed to run on a background thread in production
to allow concurrent execution with the Telegram bot services.

Usage:
    from core.flask_server import app

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging

from flask import Flask

logger = logging.getLogger(__name__)

#: Flask application instance used by the HelenaBot system
app: Flask = Flask(__name__)


@app.route("/", methods=["GET"])
def home() -> str:
    """
    Container-level healthcheck endpoint.

    This route is intended to be called internally (e.g., by Docker or orchestration
    systems like Kubernetes) to verify that the Flask server is running.

    Returns:
        str: A simple message confirming system availability.
    """
    return "HelenaBot is up and running!"


@app.route("/healthcheck", methods=["GET"])
def healthcheck() -> tuple[str, int]:
    """
    Public healthcheck endpoint.

    This route is used to verify public availability of the Flask app via
    Cloudflare tunnel or other network exposure mechanisms. The presence of
    this route allows scripts or systems to confirm that the bot is externally reachable.

    Returns:
        tuple[str, int]: A tuple containing:
            - Message string indicating system status
            - HTTP status code 200 if successful
    """
    return "👍 HelenaBot online!", 200
