# clients/__init__.py

import os

from dotenv import dotenv_values
from helena_bot.utils.path import get_documents_dir


def load_all_clients() -> dict:
    """
    Loads all client configurations from the 'clients/' directory.

    Each subdirectory inside 'clients/' must contain a '.env' file and a 'documents/' folder.
    Returns a dictionary with client name as key and its configuration as value.
    """
    clients = {}

    base_dir = os.path.abspath(os.path.dirname(__file__))

    for name in os.listdir(base_dir):
        client_path = os.path.join(base_dir, name)
        env_path = os.path.join(client_path, ".env")
        if os.path.isdir(client_path) and os.path.isfile(env_path):
            env_vars = dotenv_values(env_path)
            clients[name] = {
                "env": env_vars,
                "docs_path": get_documents_dir(name),
            }

    return clients
