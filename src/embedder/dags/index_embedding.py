"""modulo responsavel pelos metodos executados pelas dags do airflow para criar a fila de embeddings."""

import logging
import argparse
import json

from embedder.dags.load_dag_queue import load_queue_dag_run_from_db
from embedder.dags.trigger_dag_api_rest import trigger_dag_via_api
from embedder.db_connection.instances import app_db_instance
from embedder.db_models import EmbeddingsTableV2, IndexedVersionsTable, MetadataEmbeddingsTable
from embedder.embeddings import create_embeddings, embed_long_text, split_chunks
from embedder.envs import EMBEDDING_MODEL, MAX_LENGTH_CHUNK_SIZE
from embedder.extract_docs.extract_content import check_exist_content, get_doc_from_id
from embedder.http_exceptions import HTTPException204, HTTPException404, HTTPException409
from embedder.text_preprocess import html_to_markdown
from tqdm import tqdm


logger = logging.getLogger(__name__)


# ruff: noqa: S608
def remove_obsolete_embeddings() -> int:
    """Remove os embeddings obsoletos da tabela EmbeddingsTableV2."""
    sql_delete = f"""
        DELETE FROM {EmbeddingsTableV2.__tablename__}
        WHERE id_documento IN (
            SELECT i.id_documento
            FROM {IndexedVersionsTable.__tablename__} i
            LEFT JOIN {MetadataEmbeddingsTable.__tablename__} m ON i.id_documento = m.id_documento
            WHERE m.id_documento IS NULL
        )
    """
    result = app_db_instance.execute(sql=sql_delete)
    return result.rowcount


def query_need_index() -> list:
    """Comparando a tabela de metadata e indexed_version para listar documentos a serem indexados"""
    sql = f"""
            SELECT m.id_documento, m.hash_versao
            FROM {MetadataEmbeddingsTable.__tablename__} m
            LEFT JOIN {IndexedVersionsTable.__tablename__} i ON m.id_documento = i.id_documento
            WHERE i.id_documento IS NULL OR m.hash_versao != i.hash_versao
            """
    return app_db_instance.select(sql=sql, return_dataframe=False)


# ruff: noqa: S608
def send_ids_to_index(
    trigger_batch_size: int, dag_index, use_progress_bar: bool = False, progress_update: int = 5000
) -> None:
    """
    Insere os ids que precisam ser indexados ou reindexados na fila do airflow.

    Args:
        trigger_batch_size (int): Tamanho do lote de ids para trigger do indexing_embeddings.
        dag_index (str): Nome da DAG para trigger.
        use_progress_bar (bool): Habilitar ou desabilitar a barra de progresso.
        progress_update (int): Intervalo de atualização da barra de progresso.
    """

    index_list = query_need_index()
    if len(index_list) > 0:
        queued = load_queue_dag_run_from_db(dag_id=dag_index)

    send_to_index = []
    progress_bar = tqdm(index_list, disable=not use_progress_bar) if use_progress_bar else index_list
    logger.info(f"Found {len(index_list)} documents to index")
    for i, res in enumerate(progress_bar, start=1):
        if res["id_documento"] in queued:
            continue
        try:
            if check_exist_content(res["id_documento"]):
                send_to_index.append(res)
                if len(send_to_index) >= trigger_batch_size or i == len(index_list):
                    trigger_dag_via_api(dag_id=dag_index, conf={"list_to_trigger": send_to_index})
                    logger.info(f"Triggering indexing_embeddings with {len(send_to_index)} documents")
                    send_to_index = []
            else:
                app_db_instance.add(IndexedVersionsTable(tem_conteudo=False, **res), primary_key_field="id_documento")
        except (HTTPException204, HTTPException404, HTTPException409) as e:
            # logger.warning(f"Documento {res['id_documento']} \n Exception: {e}")
            app_db_instance.add(IndexedVersionsTable(tem_conteudo=False, **res), primary_key_field="id_documento")

        if use_progress_bar and i % 5000 == 0:
            progress_bar.update(5000)


def indexing_embeddings(list_to_trigger: list) -> None:
    """Executa de fato a indexação dos embeddings V2.

    Args:
        list_to_trigger (list): Lista de ids para trigger do indexing_embeddings, cada item tem o id_documento e hash_versao.
    """
    for item in list_to_trigger:
        id_documento = item["id_documento"]
        try:
            doc, _ = get_doc_from_id(id_documento)
            conteudo_markdown = html_to_markdown(doc)
            doc_chunks, positions = split_chunks(
                conteudo_markdown,
                model_path=EMBEDDING_MODEL,
                chunk_size=MAX_LENGTH_CHUNK_SIZE,
                chunk_overlap=50,
                return_positions=True,
            )
            for idx, chunk in enumerate(doc_chunks):
                if len(chunk) > MAX_LENGTH_CHUNK_SIZE:
                    embedding = embed_long_text(chunk, model_path=EMBEDDING_MODEL, max_length=MAX_LENGTH_CHUNK_SIZE)
                else:
                    embedding = create_embeddings(text=chunk, model=EMBEDDING_MODEL)
                obj_embedding = EmbeddingsTableV2(
                    chunk_id=idx,
                    id_documento=int(id_documento),
                    embedding=embedding,
                    emb_text=chunk,
                    start_position=positions[idx][0],
                    finished_position=positions[idx][1],
                )
                app_db_instance.add(obj_embedding, primary_key_field=False)
            app_db_instance.add(IndexedVersionsTable(tem_conteudo=True, **item), primary_key_field="id_documento")
        except (HTTPException204, HTTPException404, HTTPException409) as e:
            logger.warning(f"Documento {id_documento} \n Exception: {e}")


def main():
    parser = argparse.ArgumentParser(description="Exemplo de script com argparse")

    parser.add_argument("--list_to_trigger", type=str, required=True, help="lista para trigar")
    args = parser.parse_args()
    list_to_trigger_str = args.list_to_trigger.replace("'", '"')
    list_to_trigger = json.loads(list_to_trigger_str)

    indexing_embeddings(list_to_trigger=list_to_trigger)


if __name__ == "__main__":
    main()
