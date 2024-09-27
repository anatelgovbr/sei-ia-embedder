"""Módulo de extracao de documentos internos e externos."""

import logging

from embedder.extract_docs.external_sei import get_doc_ext_from_id, raise_http_exception, check_exist_content_doc_ext_from_id
from embedder.extract_docs.internal_sei import get_doc_int_from_id, check_exist_content_doc_int_from_id
from embedder.extract_docs.type_doc_sei import get_type_doc_from_id
from embedder.http_exceptions import HTTPException204, HTTPException406

logger = logging.getLogger(__name__)


def get_doc_from_id(
        id_documento: str,
        pag_ini: int | None = None,
        pag_fim: int | None = None) -> str:
    """Recupera o conteúdo de um documento com base em seu identificador.

    O método determina primeiro se o documento é interno ou externo e,
    em seguida, recupera o conteúdo de acordo com essa classificação.

    Args:
        id_documento (str): O identificador único do documento a ser
            recuperado.
        pag_ini (int, optional): Número da página inicial para recuperação
            de conteúdo específico de página. Default: None.
        pag_fim (int, optional): Número da página final para recuperação de
            conteúdo específico de página. Default: None.

    Returns:
        str: O conteúdo do documento recuperado.
    """
    logger.debug("entrou no get_doc_from_id")
    (
        internal,
        _,  # type doc
        num_doc_formatado,
        _  # protocolo_formatado
        ) = get_type_doc_from_id(id_documento)
    if internal:
        if pag_ini or pag_fim:
            logger.error(f"O documento id {id_documento} (nº {num_doc_formatado}) é interno!)")
            msg = "Não posso definir um intervalo de páginas para esse documento"
            raise_http_exception(HTTPException406(detail=msg), msg)
        try:
            return (get_doc_int_from_id(id_documento), num_doc_formatado)
        except HTTPException204:
            return (get_doc_ext_from_id(id_documento), num_doc_formatado)
    return (get_doc_ext_from_id(
                id_documento,
                pag_ini,
                pag_fim), num_doc_formatado)

def check_exist_content(id_documento: str) -> bool:
    """Verifica se um documento com o ID fornecido existe e possui conteúdo.

    Args:
        id_documento (str): O identificador único do documento a ser verificado.

    Returns:
        bool: True se o documento existe e possui conteúdo, False caso contrário.
    """
    logger.debug("entrou em check_exist_content")
    (
        internal,
        _,  # type doc
        num_doc_formatado,
        _  # protocolo_formatado
        ) = get_type_doc_from_id(id_documento)
    if internal:
        return check_exist_content_doc_int_from_id(id_documento)
    return check_exist_content_doc_ext_from_id(id_documento)
