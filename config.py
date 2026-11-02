"""
config.py

Configuration settings for HelenaBot.

Standards: PEP 8, PEP 257
"""
import os
from typing import Dict, Any


class Config:
    """Base configuration."""
    
    TESTING = False
    DEBUG = False
    MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    MONGO_DB = os.getenv('MONGO_DB', 'helena_bot')
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'intfloat/multilingual-e5-large')
    EMBEDDING_VERSION = os.getenv('EMBEDDING_VERSION', 'v1-e5-large')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    PORT = int(os.getenv('PORT', 5001))
    HOST = os.getenv('HOST', '0.0.0.0')


class TestConfig(Config):
    """Test configuration."""
    
    TESTING = True
    DEBUG = True
    MONGO_URL = 'mongodb://localhost:27017'
    MONGO_DB = 'helena_bot_test'
    TELEGRAM_TOKEN = 'test_token'
    EMBEDDING_MODEL = 'intfloat/multilingual-e5-small'
    EMBEDDING_VERSION = 'v1-e5-small'
    GROQ_API_KEY = 'test_key'
    PORT = 5002
    HOST = 'localhost'


def get_test_config() -> Dict[str, Any]:
    """Get test configuration dictionary.
    
    Returns:
        Dict[str, Any]: Test configuration settings.
    """
    return {
        'TESTING': True,
        'DEBUG': True,
        'MONGO_URL': 'mongodb://localhost:27017',
        'MONGO_DB': 'helena_bot_test',
        'TELEGRAM_TOKEN': 'test_token',
        'EMBEDDING_MODEL': 'intfloat/multilingual-e5-small',
        'EMBEDDING_VERSION': 'v1-e5-small',
        'GROQ_API_KEY': 'test_key',
        'PORT': 5002,
        'HOST': 'localhost'
    }


__all__ = ['Config', 'TestConfig', 'get_test_config'] 