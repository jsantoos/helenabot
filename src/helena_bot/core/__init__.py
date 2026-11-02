"""
core package
Package: helena_bot.core

This package contains the foundational modules to initialize and orchestrate
HelenaBot’s core services, including the Flask server, webhook handling,
Cloudflare tunnel resolution, health checking, and bot initialization.

Modules:
- flask_server: Exposes Flask app and health endpoints
- webhook: Handles Telegram webhook routing
- cloudflare: Reads Cloudflare tunnel URL
- healthcheck: Verifies accessibility and sets webhooks
- bot_launcher: Initializes Telegram bot with client-specific context
- startup: Main orchestrator script

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from . import bot_launcher, cloudflare, flask_server, healthcheck, startup, webhook

__all__ = [
    "flask_server",
    "webhook",
    "cloudflare",
    "healthcheck",
    "bot_launcher",
    "startup",
]
