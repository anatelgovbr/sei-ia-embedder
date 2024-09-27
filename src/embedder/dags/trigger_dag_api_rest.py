import requests
import json
from embedder.envs import AIRFLOW_API_BASE_URL, AIRFLOW_USERNAME, AIRFLOW_PASSWORD
from requests.exceptions import RequestException
import time


def trigger_dag_via_api(dag_id, conf=None):
    """
    Função para acionar uma DAG via API REST do Airflow com 3 tentativas em caso de falha.
    """
    endpoint = f"{AIRFLOW_API_BASE_URL}/dags/{dag_id}/dagRuns"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "conf": conf or {}
    }
    
    attempts = 5
    for attempt in range(1, attempts + 1):
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(payload),
                auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
            )
            
            if response.status_code == 200:
                print(f"DAG {dag_id} acionada com sucesso.")
                return response.json()
            else:
                print(f"Tentativa {attempt} falhou. Status code: {response.status_code}")

        
        except RequestException as e:
            print(f"Tentativa {attempt} encontrou um erro: {e}")
        
        if attempt < attempts:
            print("Tentando novamente...")
            time.sleep(3)

    print(f"Erro ao acionar DAG {dag_id} após {attempts} tentativas.")
    return None