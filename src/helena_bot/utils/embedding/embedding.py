"""
Module: helena_bot.utils.embedding_utils

Provides safe text embedding functionality for HelenaBot by applying chunking
and overflow protection using `SentenceSplitter`. Prevents token limit violations
when working with large texts in transformer-based embedding models.

This module is typically used within the PDF ingestion pipeline, diagram annotation,
and context-aware image retrieval routines.

Responsibilities:
- Chunk and sanitize long texts before embedding
- Handle errors gracefully during embedding
- Integrate with embedding models like HuggingFaceEmbedding

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
import time
from typing import List, Optional

from llama_index.core.node_parser import SentenceSplitter

logger = logging.getLogger(__name__)
node_parser = SentenceSplitter(chunk_size=1200)

def safe_get_embedding(
    embed_model, text: str, identifier: str = ""
) -> Optional[List[float]]:
    """
    Generate an embedding vector for a given text, safely handling long content.

    This function uses SentenceSplitter to divide the input text into manageable
    chunks, reducing the likelihood of token overflows or model errors. It then
    processes only the first valid chunk for embedding, or uses a fallback if needed.

    Args:
        embed_model: Instance of an embedding model implementing `get_text_embedding(str) -> List[float]`.
        text (str): Raw text to be embedded. Can be paragraph-length or multi-page.
        identifier (str): Optional logging identifier (e.g., document name or page label).

    Returns:
        Optional[List[float]]: A single vector embedding for the input text, or None if generation fails.
    """
    start_time = time.time()
    logger.debug("⏱️ Embedding iniciado (%s)", identifier)

    if not text or len(text.strip()) == 0:
        logger.warning("⚠️ Texto insuficiente para embedding (%s): '%s'", identifier, text[:100])
        return None

    try:
        logger.debug("🧪 Texto bruto recebido (%s): %r", identifier, text[:300])
        chunks = node_parser.split_text(text.strip())
        valid_chunks = [c for c in chunks if c.strip()]

        if not valid_chunks:
            logger.warning("❌ Nenhum chunk válido extraído via SentenceSplitter (%s)", identifier)
            fallback = text.strip()[:300]
            if fallback:
                logger.warning("⚠️ Usando fallback de 300 caracteres para embedding (%s)", identifier)
                chunk = fallback
            else:
                logger.warning("❌ Texto vazio após limpeza (%s)", identifier)
                return None
        else:
            for idx, chunk_preview in enumerate(valid_chunks[:3]):
                logger.debug(
                    "🔹 Chunk %d (%s) - Tokens: %d | Preview: %s",
                    idx + 1,
                    identifier,
                    len(chunk_preview.split()),
                    chunk_preview[:100].replace("\n", " "),
                )
            chunk = valid_chunks[0]

        try:
            embedding = embed_model.get_text_embedding(chunk)
            elapsed = time.time() - start_time
            logger.debug("✅ Embedding concluído para '%s' em %.2fs", identifier, elapsed)
        
            return embedding
        except IndexError as e:
            logger.critical("🚨 Erro de indexação no modelo de embedding (%s): %s", identifier, e)
            logger.debug("🔎 Chunk problemático (%s): %r", identifier, chunk)
            return None

    except (ValueError, RuntimeError) as err:
        logger.error("❌ Erro esperado ao gerar embedding (%s): %s", identifier, err)
        logger.debug("🔎 Texto problemático (%s): %s", identifier, text[:300])
        return None
    except IndexError as e:
        logger.critical("🚨 Erro de indexação ao gerar embedding textual (%s): %s", identifier, e)
        return None
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.critical("🚨 Erro inesperado ao gerar embedding (%s): %s", identifier, repr(err))
        logger.debug("🔍 Texto bruto (%s): %s", identifier, text[:300])
        return None
