"""
context_store.py

Stores temporary contextual data such as last questions and image suggestions per chat ID.

Standards:
- PEP 8
- PEP 257
- PEP 484
"""

from typing import Dict

# Stores per-user temporary image context
last_contextual_question: Dict[int, dict] = {}
