import json
from sqlalchemy import create_engine, MetaData, Table, and_
import os
import pickle

def fetch_dag_runs(dag_id: str, not_in_states = ['success']) -> list:
    engine = create_engine(os.getenv("AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"))
    connection = engine.connect()
    metadata = MetaData()
    metadata.reflect(bind=engine)

    dag_run_table = Table('dag_run', metadata, autoload_with=engine)

    query = dag_run_table.select().where(
        and_(
            dag_run_table.c.dag_id == dag_id,
            dag_run_table.c.state not in not_in_states
        )
    )

    result = connection.execute(query)
    connection.close()
    return result

def filter_list_to_trigger(result_confs) -> set:
    queue = set()
    for conf in result_confs:
        list_to_trigger = conf.get('list_to_trigger')
        if list_to_trigger is not None:
            for item in list_to_trigger:
                queue.add(item['id_documento'])
    return queue

def load_queue_dag_run_from_db(dag_id: str, not_in_states = ['success']) -> set:
    result = fetch_dag_runs(dag_id, not_in_states)
    if result.rowcount == 0:
        return set()

    result_confs = [pickle.loads(row.conf) for row in result]
    return filter_list_to_trigger(result_confs)
