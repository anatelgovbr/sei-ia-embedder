"""Modulo de modelo de tabelas do banco de dados."""

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from embedder.db_connection.instances import BasePgvector
from embedder.envs import EMBEDDINGS_TABLE_NAME


class EmbeddingsTable(BasePgvector):
    """Modelo de dados para embeddings de dimensão 400x50.

    Attributes:
    - id_documento (int): ID do documento associado ao embedding.
    - chunk_id (int): ID do chunk associado ao embedding.
    - embedding (Vector): Vetor de embedding de dimensão 400x50.
    - emb_text (str): Texto do embedding.
    - metadata_ (dict): Dicionário de metadados do documento.
    - created_at (DateTime): Data e hora de criação do registro (padrão é a data e hora atual UTC).
    - id_procedimento (int): ID do procedimento associado ao documento.
    - start_position (int): Posição inicial do chunk no documento.
    - finished_position (int): Posição final do chunk no documento
    """

    __tablename__ = EMBEDDINGS_TABLE_NAME

    id_documento: Mapped[int] = mapped_column(Integer, primary_key=True)
    chunk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    embedding: Mapped[Vector] = mapped_column(Vector)
    emb_text: Mapped[str] = mapped_column()
    metadata_: Mapped[JSONB] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    id_procedimento: Mapped[int] = mapped_column(Integer)
    start_position: Mapped[int] = mapped_column(Integer)
    finished_position: Mapped[int] = mapped_column(Integer)


class EmbeddingsTableV2(BasePgvector):
    """Modelo de dados para embeddings de dimensão 400x50.

    Attributes:
    - chunk_id (int): ID do chunk associado ao embedding.
    - id_documento (int): ID do documento associado ao embedding.
    - id_procedimento (int): ID do procedimento associado ao embedding.
    - embedding (Vector): Vetor de embedding de dimensão 400x50.
    - emb_text (str): Texto do embedding.
    - start_position (int): Posição inicial do texto no documento.
    - finished_position (int): Posição final do texto no documento.
    - created_at (DateTime): Data e hora de criação do registro (padrão é a data e hora atual UTC).
    """

    __tablename__ = "embeddings_400_50_v2"

    chunk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_documento: Mapped[int] = mapped_column(Integer, primary_key=True)
    embedding: Mapped[Vector] = mapped_column(Vector)
    emb_text: Mapped[str] = mapped_column(String)
    start_position: Mapped[int] = mapped_column(Integer)
    finished_position: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class MetadataEmbeddingsTable(BasePgvector):
    """Modelo de dados para metadados de embeddings de dimensão 400x50.

    Atributos:
        id_documento (int): ID do documento associado ao embedding.
        id_procedimento (int): ID do procedimento associado ao embedding.
        formato_arquivo (str): Formato do arquivo associado ao embedding.
        id_documento_formatado (int): ID do documento formatado associado ao embedding.
        id_protocolo_formatado (int): ID do protocolo formatado associado ao embedding.
        sta_documento (str): Status do documento associado ao embedding.
        hash_externo (str): Hash externo associado ao embedding.
        maxdth_interno (str): Maxdth interno associado ao embedding.
        flag_finalizado (bool): Flag de finalização do embedding.
        created_at (datetime): Data e hora de criação do registro.
    """

    __tablename__ = "metadata_embeddings_400_50"

    id_documento: Mapped[int] = mapped_column(Integer, primary_key=True)
    sin_bloqueado: Mapped[str] = mapped_column(String(1))
    id_procedimento: Mapped[int] = mapped_column(Integer)
    sta_documento: Mapped[str] = mapped_column(String(1))
    doc_formatado: Mapped[int] = mapped_column(Integer)
    procedimento_formatado: Mapped[str] = mapped_column(String)
    hash_anexo_doc_externo: Mapped[str] = mapped_column(String, nullable=True)
    max_dth_atualizacao_vsd_doc_interno: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    hash_versao: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.current_timestamp(), server_default=func.current_timestamp()
    )


class IndexedVersionsTable(BasePgvector):
    """Modelo de dados para as Hash Version referente a indexacao do embedding do documento."""

    __tablename__ = "indexed_versions"

    id_documento: Mapped[int] = mapped_column(Integer, primary_key=True)
    hash_versao: Mapped[str] = mapped_column(String)
    tem_conteudo: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.current_timestamp(), server_default=func.current_timestamp()
    )
