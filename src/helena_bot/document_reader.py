# document_reader.py

from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document
from typing import List

def load_documents(directory_path: str) -> List[Document]:
    """
    Carrega documentos de uma pasta especificada.

    Args:
        directory_path (str): Caminho para a pasta contendo os documentos.

    Returns:
        List[Document]: Lista de documentos carregados.
    """
    reader = SimpleDirectoryReader(input_dir=directory_path)
    documents = reader.load_data()
    return documents
