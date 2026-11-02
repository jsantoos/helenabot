"""
Package: helena_bot.llm.engine_wrappers

Defines retryable and fail-safe logic for running LLM chat interactions.

Exposed:
- try_generate_response: Runs LLM chat with retry logic, handling rate limits and memory issues.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .retry_generate import try_generate_response

__all__ = ["try_generate_response"]
