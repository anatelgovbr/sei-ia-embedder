"""Modulo de persistencia de embeddings."""
from embedder.db_models import EmbeddingsTable
from embedder.db_connection.instances import app_db_instance
import numpy as np

def persist_embeddings(
    id_documento: int, chunk_id: int, embedding: np.ndarray, emb_text: str,
    metadata_: dict, id_procedimento: int, start_position: int, finished_position: int, **args: dict
) -> int:
    """Persiste um conjunto de embeddings no banco de dados.

    Args:
        id_documento (int): ID do documento associado aos embeddings.
        chunk_id (int): ID do chunk associado aos embeddings.
        embedding (numpy.ndarray): Lista de embeddings a serem persistidos.
        emb_text (str): Texto associado aos embeddings.
        metadata_ (dict): Dicionário de metadados do documento.
        id_procedimento (int): ID do procedimento associado ao documento.
        start_position (int): Posição inicial do chunk no documento.
        finished_position (int): Posição final do chunk no documento.
        **args: argumentos para pgvector

    Returns:
        int: ID do registro inserido no banco de dados.
    """
    embd_obj = EmbeddingsTable(
        id_documento=id_documento,
        chunk_id=chunk_id,
        embedding=embedding,
        emb_text=emb_text,
        metadata_=metadata_,
        id_procedimento=id_procedimento,
        start_position=start_position,
        finished_position=finished_position
    )
    return app_db_instance.add(embd_obj, primary_key_field="id_documento", **args)


