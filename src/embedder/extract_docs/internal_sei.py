"""Módulo de extração de documentos internos."""

import logging

from embedder.db_connection.instances import sei_db_instance
from embedder.http_exceptions import (
    HTTPException204,
    HTTPException404,
    HTTPException409,
)
from embedder.query_templates.sql_templates import CHECK_IF_HAS_CONTENT_TEMPLATE, INTERNAL_DOCS_FROM_PROCESS_TEMPLATE
from embedder.text_preprocess import html_to_markdown
from embedder.envs import DB_SEI_SCHEMA


logger = logging.getLogger(__name__)


def get_doc_int_from_id(id_documento: str) -> str:
    """Funcao de obtencao de documentos interno.

    Args:
        id_documento (str): ID_DOCUMENTO

    Returns:
        str: Retorna o conteudo do documento
    """
    sql = INTERNAL_DOCS_FROM_PROCESS_TEMPLATE.format(id_documento)
    df_docs = sei_db_instance.select(sql=sql)
    l_df = len(df_docs)
    if l_df == 0:
        logger.error(f"Documento {id_documento}: nao encontrado")
        raise HTTPException404
    if l_df == 1:
        if isinstance(df_docs["content_doc"][0], str):
            return html_to_markdown(df_docs["content_doc"][0])
        if df_docs["content_doc"][0] is None:
            logger.error(f"Documento {id_documento}: sem conteudo")
            raise HTTPException204
        raise HTTPException404
    logger.error(f"Documento {id_documento}: mais de um documento encontrado")
    raise HTTPException409

def check_exist_content_doc_int_from_id(id_documento: str) -> str:
    """Funcao para checar se existe conteudo do documento interno.

    Args:
        id_documento (str): ID_DOCUMENTO

    Returns:
        str: Retorna o conteudo do documento
    """
    sql = CHECK_IF_HAS_CONTENT_TEMPLATE.format(id_documento)
    df_docs = sei_db_instance.select(sql=sql)
    l_df = len(df_docs)
    if l_df == 0:
        logger.error(f"Documento {id_documento}: nao encontrado")
        raise HTTPException404
    if l_df == 1:
        if df_docs["status_content_doc"][0] == 1:
            return True
        if df_docs["status_content_doc"][0] == 0:
            return False
    logger.error(f"Documento {id_documento}: mais de um documento encontrado")
    raise HTTPException409