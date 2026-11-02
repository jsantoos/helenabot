"""
Module: bot.setup_utils

Contains low-level setup utilities used during Telegram bot initialization
for each HelenaBot client. Responsible for preparing backend infrastructure
such as MongoDB, embedding models, vector indexes, chat engine, and document
indexing triggers.

Responsibilities:
- Initialize MongoDB client and collections.
- Set up embedding model, LLM (Groq), context and memory.
- Create and manage Chroma vector stores and LlamaIndex interfaces.
- Load or trigger PDF document indexing into ChromaDB.
- Return structured resources via TypedDicts for safe downstream use.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
import os

import chromadb
from helena_bot import app_state
from helena_bot.bot.types import (
    LLMBundle,
    MongoResources,
    SetupIndexingContext,
    VectorResources,
)
from helena_bot.embedding_config import EMBEDDING_CONFIG
from helena_bot.pipeline import render_and_index_pdfs
from helena_bot.utils.metrics import has_metrics_to_save
from helena_bot.utils.path import get_chroma_dir
from helena_bot.utils.storage import save_metrics
from llama_index.core import ServiceContext, VectorStoreIndex
from llama_index.core.memory import ChatSummaryMemoryBuffer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.chroma import ChromaVectorStore
from pymongo import MongoClient

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _init_mongo(mongo_url: str, client_name: str) -> MongoResources:
    """
    Initializes MongoDB connection and collections.

    Args:
        mongo_url (str): MongoDB URI.
        client_name (str): Client's folder name.

    Returns:
        MongoResources: Structured access to Mongo resources.
    """
    mongo_client = MongoClient(mongo_url)
    mongo_db = mongo_client[f"helena_db_{client_name}"]
    return {
        "client": mongo_client,
        "db": mongo_db,
        "collection": mongo_db["img_documents"],
        "metrics": mongo_db["helena_metrics"],
    }


def _init_embedding_and_llm(groq_api_key: str) -> LLMBundle:
    """
    Initializes embedding model, LLM, memory and service context.

    Args:
        groq_api_key (str): Groq API key.

    Returns:
        LLMBundle: Resources used for retrieval and response generation.
    """
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_CONFIG.model_name)
    llm = Groq(model="llama3-70b-8192", api_key=groq_api_key)
    service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
    memory = ChatSummaryMemoryBuffer(llm=llm, token_limit=4096)
    return {
        "embed": embed_model,
        "llm": llm,
        "context": service_context,
        "memory": memory,
    }


def _init_vector_index(
    client_name: str, service_context: ServiceContext
) -> VectorResources:
    """
    Initializes vector store and index from local ChromaDB for a client.

    Args:
        client_name (str): Client folder.
        service_context (ServiceContext): Includes LLM + embedding.

    Returns:
        VectorResources: Vector store and Llama index.
    """
    chroma_path = get_chroma_dir(client_name)

    os.makedirs(chroma_path, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    vector_store = ChromaVectorStore(
        chroma_client.get_or_create_collection(name=f"documentos_{client_name}")
    )
    index = VectorStoreIndex.from_vector_store(
        vector_store, service_context=service_context
    )
    return {
        "store": vector_store,
        "index": index,
    }


def _init_chat_engine(index, llm, memory, system_prompt):
    """
    Creates a configured chat engine using LlamaIndex.

    Returns:
        Chat engine instance.
    """
    return index.as_chat_engine(
        chat_mode="context",
        llm=llm,
        memory=memory,
        system_prompt=system_prompt,
    )


def _maybe_index_documents(ctx: SetupIndexingContext) -> None:
    """
    Index PDFs for a client if not already done.

    Args:
        ctx (SetupIndexingContext): All context for document indexing.

    Returns:
        None
    """
    if not has_metrics_to_save(app_state.metrics):
        logger.info(
            "Nenhuma métrica gerada ainda para %s; não haverá persistência.",
            ctx["client_name"],
        )
        return

    metrics_before = app_state.metrics.copy()

    if ctx["mongo_collection"].count_documents({"client": ctx["client_name"]}) == 0:
        logger.info("📄 Indexando documentos para cliente: %s", ctx["client_name"])
        render_and_index_pdfs(ctx)
    else:
        logger.info("📂 Documentos já indexados para %s, pulando.")

    if app_state.metrics == metrics_before:
        logger.info(
            "Nenhuma nova métrica gerada após indexação de %s; não haverá persistência.",
            ctx["client_name"],
        )
        return

    save_metrics(app_state.metrics, ctx["metrics_collection"])
