"""Módulo de extracao do tipo e extensao do documento."""
import logging

from embedder.db_connection.instances import sei_db_instance
from embedder.http_exceptions import HTTPException404, HTTPException409
from embedder.query_templates.sql_templates import TYPE_DOC_TEMPLATE
from embedder.text_preprocess import get_file_extension

logger = logging.getLogger(__name__)



def get_type_doc_from_id(id_documento: str) -> tuple[bool, str]:
    """Funcao de obtencao do tipo e extencao dos documentos.

    Args:
        id_documento (str): ID_DOCUMENTO

    Returns:
        str: Retorna o conteudo do documento
    """
    logger.debug("Buscando o tipo do documento")
    sql = TYPE_DOC_TEMPLATE.format(id_documento)
    df_types = sei_db_instance.select(sql)

    l_df = len(df_types)
    if l_df == 0:
        raise HTTPException404
    if l_df == 1 and isinstance(df_types["type_doc"][0], str):
        if df_types["type_doc"][0].lower() == "x":
            logger.debug("o documento e externo")
            formato_arquivo = get_file_extension(df_types["formato_arquivo"][0])
            return (
                False,
                formato_arquivo,
                str(df_types["num_doc"][0]),
                str(df_types["num_proc"][0])
                )
        logger.debug("o documento e interno")
        return (
            True,
            "html",
            str(df_types["num_doc"][0]),
            str(df_types["num_proc"][0])
            )
    raise HTTPException409
