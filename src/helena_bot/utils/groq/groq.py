"""
Module: helena_bot.utils.groq_utils

Utility function for transcribing audio files using Groq's Whisper API.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
import os

import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
GROQ_API = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_DATA_MODEL", "")
GROQ_TIMEOUT_SECONDS = int(os.getenv("GROQ_TIMEOUT", "30"))


def transcribe_with_groq(audio_path: str) -> str:
    """
    Transcribes an audio file using Groq's Whisper API (OpenAI-compatible endpoint).

    Sends a multipart/form-data POST request to the Groq transcription endpoint,
    using the Whisper model configured via environment variable. Automatically handles
    authentication and returns the transcribed text, or an empty string on error.

    Args:
        audio_path (str): Path to the audio file to be transcribed (.wav format recommended).

    Returns:
        str: Transcribed text if successful, or an empty string if the request fails.
    """
    try:
        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
            data = {"model": GROQ_MODEL}
            headers = {"Authorization": f"Bearer {GROQ_API}"}

            response = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers=headers,
                data=data,
                files=files,
                timeout=GROQ_TIMEOUT_SECONDS,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")

            logger.error(
                "Transcription failed: HTTP %d - %s",
                response.status_code,
                response.text[:200],
            )
            return f"[ERROR] - HTTP {response.status_code} - {response.text}"

    except FileNotFoundError as err:
        logger.error("Arquivo de áudio não encontrado: %s", err)
    except RequestException as err:
        logger.error("Erro de conexão com a API da Groq: %s", err)
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.critical("Erro inesperado na transcrição: %s", err)

    return ""
