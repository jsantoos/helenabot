"""
Module: helena_bot.utils.metrics.safe_ops

Provides utility functions for safely updating runtime metric counters
in HelenaBot, ensuring proper initialization of both global and per-client scopes.

This module is used to avoid KeyError exceptions when incrementing
metrics dynamically during execution.

Responsibilities:
- Increment counters for global or per-client metrics.
- Initialize metric fields with default values when missing.
- Centralize safe metric operations to maintain code consistency.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import Dict


def safe_increment(
    metrics: Dict, client_name: str, field: str, global_only: bool = False
) -> None:
    """
    Incrementa um campo de métrica de forma segura, inicializando-o se necessário.

    Args:
        metrics (Dict): Referência para app_state.metrics.
        client_name (str): Nome do cliente.
        field (str): Nome do campo a incrementar.
        global_only (bool): Se True, incrementa apenas no escopo global.
    """
    metrics["global"].setdefault(field, 0)
    metrics["global"][field] += 1

    if not global_only:
        if client_name not in metrics["per_client"]:
            metrics["per_client"][client_name] = {}
        metrics["per_client"][client_name].setdefault(field, 0)
        metrics["per_client"][client_name][field] += 1
