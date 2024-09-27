""""Modulo responsavel por carregar as variaveis de ambiente."""

import os
from urllib.parse import quote

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


ENVIROMENT = os.getenv("ENVIROMENT","prod")
DB_SEI_HOST = os.getenv("DB_SEI_HOST")
DB_SEI_PORT = os.getenv("DB_SEI_PORT")
DB_SEI_USER = os.getenv("DB_SEI_USER")
DB_SEI_PWD = os.getenv("DB_SEI_PWD")
DB_SEI_DATABASE = os.getenv("DB_SEI_DATABASE")
DATABASE_TYPE = os.getenv("DATABASE_TYPE")
DB_SEI_SCHEMA = os.getenv("DB_SEI_SCHEMA")

ASSISTENTE_PGVECTOR_HOST = os.getenv("ASSISTENTE_PGVECTOR_HOST")
ASSISTENTE_PGVECTOR_USER = os.getenv("ASSISTENTE_PGVECTOR_USER")
ASSISTENTE_PGVECTOR_PWD = quote(os.getenv("ASSISTENTE_PGVECTOR_PWD"))
ASSISTENTE_PGVECTOR_DB = os.getenv("ASSISTENTE_PGVECTOR_DB")
ASSISTENTE_PGVECTOR_PORT = os.getenv("ASSISTENTE_PGVECTOR_PORT","5432")


SEI_SOLR_ADDRESS = os.getenv("SEI_SOLR_ADDRESS")
SEI_SOLR_CORE = os.getenv("SEI_SOLR_CORE")

SEI_IAWS_URL = os.getenv("SEI_IAWS_URL")
SEI_IAWS_KEY = os.getenv("SEI_IAWS_KEY")


EMBEDDINGS_TABLE_NAME = os.getenv("EMBEDDINGS_TABLE_NAME", "embeddings_400_50")
HF_HOME = os.getenv("HF_HOME", "./models")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL","sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
#model_path = Path(os.getenv("EMBEDDING_MODEL_PATH", "~/local_model"))
# if not model_path.exists():
#     from sentence_transformers import SentenceTransformer
#     model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
#     model.save(str(model_path))
#     EMBEDDING_MODEL = model_path
# else:
#     EMBEDDING_MODEL = str(model_path)

MAX_LENGTH_CHUNK_SIZE = int(os.getenv("MAX_LENGTH_CHUNK_SIZE", "128"))

############ airflow
AIRFLOW_API_BASE_URL = os.getenv("AIRFLOW_API_BASE_URL","http://localhost:8080/api/v1")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME","airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD","airflow")