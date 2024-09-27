"""Módulo de extração de metadados de documentos externos."""
import logging
from datetime import datetime

from pydantic import BaseModel, model_validator

from embedder.db_connection.instances import sei_db_instance
from embedder.extract_docs.external_sei import raise_http_exception
from embedder.http_exceptions import HTTPException404, HTTPException409, HTTPException500
from embedder.query_templates.sql_templates import METADATA_DOCUMENTO_TEMPLATE
from embedder.text_preprocess import get_file_extension

logger = logging.getLogger(__name__)


class MetadataDocument(BaseModel):
    """Modelo de extração de metadados de documentos.

    Attributes:
        id_protocolo_formatado (str): ID formatado do protocolo do documento.
        id_procedimento (str): ID do protocolo do documento.
        id_protocolo_documento_formatado (str): ID formatado do protocolo do
            documento.
        documento_especificacao (str): Especificação do documento.
        id_tipo_documento (str): ID do tipo de documento.
        formato_arquivo (str): Formato do arquivo do documento.
        dta_inclusao (Optional[datetime | str]): Data de inclusão do documento.
        nome_id_tipo_documento (str): Nome do tipo de documento.
        id_protocolo_documento (str): ID do protocolo do documento.
    """
    id_protocolo_formatado: str
    id_procedimento: str
    id_documento_formatado: str
    documento_especificacao: str
    id_tipo_documento: str
    formato_arquivo: str
    dta_inclusao: datetime | str | None
    nome_id_tipo_documento: str
    id_documento: str

    @model_validator(mode="after")
    def parse_dta_inclusao(self) -> BaseModel:
        """Validador para parsear a data de inclusão do documento.

        Converte `dta_inclusao` para string no formato "YYYY-MM-DD HH:MM:SS"
        se for uma instância de `datetime`.

        Returns:
            MetadataDocument: A instância atual com `dta_inclusao` parseado.
        """
        if isinstance(self.dta_inclusao, datetime):
            self.dta_inclusao = self.dta_inclusao.strftime("%Y-%m-%d %H:%M:%S")
        return self

    @model_validator(mode="after")
    def parse_id_protocolo_formatado(self) -> BaseModel:
        """Validador para parsear o ID do protocolo formatado.

        Remove pontos, barras e traços de `id_protocolo_documento_formatado`.

        Returns:
            MetadataDocument: A instância atual com `id_protocolo_formatado`
                parseado.
        """
        self.id_protocolo_formatado = self.id_protocolo_formatado \
            .replace(".", "") \
            .replace("/", "") \
            .replace("-", "")
        return self

    class Config:
        """"Modulo de configuracao."""
        extra = "allow"


def get_doc_metadata_from_id(id_documento: str) -> dict:
    """Extrai os metadados de um documento a partir de seu ID."""
    sql = METADATA_DOCUMENTO_TEMPLATE.format(id_documento=id_documento)
    try:
        data_frame = sei_db_instance.select(sql=sql)
        if data_frame.empty:
            msg = f"Nenhum documento encontrado com o ID {id_documento}."
            raise_http_exception(HTTPException404(detail=msg), msg)
        if data_frame.shape[0] > 1:
            msg = f"Mais de um documento encontrado com o ID {id_documento}."
            raise_http_exception(HTTPException409(detail=msg), msg)
        metadata = data_frame.iloc[0].to_dict()
        metadata["formato_arquivo"] = get_file_extension(metadata["formato_arquivo"])
        metadata = {k: str(v) for k, v in metadata.items()}
    except Exception as e:
        error_message = f"Erro ao buscar o documento com ID {id_documento}."
        logger.exception(error_message)
        raise HTTPException500(error_message) from e

    return MetadataDocument(**metadata).model_dump()
