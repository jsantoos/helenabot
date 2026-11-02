"""
Module: helena_bot.bot.retrieval.image_retriever

Provides utilities to retrieve the most semantically relevant images from a MongoDB collection
based on cosine similarity of vector embeddings.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
from typing import List

import numpy as np
from helena_bot.embedding_config import EMBEDDING_CONFIG
from helena_bot.utils.embedding import safe_get_embedding
from pymongo.collection import Collection
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def find_relevant_images(
    question: str,
    embed_model,
    mongo_collection: Collection,
    top_k: int = 5,
    threshold: float = 0.29,
) -> List[dict]:
    """
    Retrieve the most semantically relevant images for a given user question.

    Args:
        question (str): The user's input question or query.
        embed_model: The embedding model instance that provides `get_text_embedding()`.
        mongo_collection (Collection): MongoDB collection containing embedded images.
        top_k (int): Maximum number of relevant images to return.
        threshold (float): Minimum cosine similarity score to be considered relevant.

    Returns:
        List[dict]: A list of MongoDB image documents that passed the similarity threshold.
    """
    question_embedding = safe_get_embedding(embed_model, question)
    if not question_embedding:
        logger.warning("❌ Embedding da pergunta não pôde ser gerado.")
        return []

    images = list(
        mongo_collection.find({"embedding_version": EMBEDDING_CONFIG.version})
    )
    if not images:
        logger.warning("⚠️ Nenhuma imagem encontrada no MongoDB.")
        return []

    scored = []
    logger.info("🔎 Comparando %d imagens com a pergunta: '%s'", len(images), question)

    for doc in images:
        try:
            image_embedding = doc.get("embedding")
            if not image_embedding:
                continue

            score = cosine_similarity(
                np.array(question_embedding).reshape(1, -1),
                np.array(image_embedding).reshape(1, -1),
            )[0][0]

            logger.debug("🧠 Similaridade: %.4f | Imagem: %s", score, doc.get("name"))

            if score >= threshold:
                scored.append((score, doc))

        except (ValueError, TypeError) as err:
            logger.warning("Erro ao comparar embeddings: %s", err)

    if not scored:
        logger.info(
            "⚠️ Nenhuma imagem ultrapassou o threshold. Usando imagem mais próxima."
        )
        images.sort(
            key=lambda doc: cosine_similarity(
                np.array(question_embedding).reshape(1, -1),
                np.array(doc.get("embedding")).reshape(1, -1),
            )[0][0],
            reverse=True,
        )
        return [images[0]] if images else []

    scored.sort(reverse=True, key=lambda x: x[0])
    return [doc for _, doc in scored[:top_k]]
