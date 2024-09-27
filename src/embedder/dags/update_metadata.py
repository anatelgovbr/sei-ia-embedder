"""modulo responsavel por atualizar os metadados dos documentos no pgvector."""
import logging

from embedder.db_connection.instances import app_db_instance, sei_db_instance
from embedder.db_models import MetadataEmbeddingsTable
from embedder.envs import DATABASE_TYPE
from embedder.query_templates.sql_templates import SELECT_METADATA_MSSQL, SELECT_METADATA_MYSQL, SELECT_METADATA_ORACLE

logger = logging.getLogger(__name__)



def update_metadata_from_sei_to_database() -> None:
    """Atualiza a tabela metadados do banco de aplicação com os metadados do SEI.

    Executa uma consulta SELECT no instância MySQL usando a instrução SQL `SELECT_METADATA.
    insere os resultados na tabela `metadata_embeddings` no banco de dados da aplicação.
    """
    dict_select_metadata = {
        "mysql": SELECT_METADATA_MYSQL,
        "mssql": SELECT_METADATA_MSSQL,
        "oracle": SELECT_METADATA_ORACLE,
    }

    result_set = sei_db_instance.select(sql = dict_select_metadata[DATABASE_TYPE], return_dataframe=False)
    app_db_instance.insert_replace(
        data = result_set,
        table_model = MetadataEmbeddingsTable
        )
