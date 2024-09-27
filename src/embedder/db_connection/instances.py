"""Modulo de instacias dos bancos de dados."""
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

from embedder.db_connection.db_connect import DBConnector
from embedder.envs import (
    ASSISTENTE_PGVECTOR_DB,
    ASSISTENTE_PGVECTOR_HOST,
    ASSISTENTE_PGVECTOR_PORT,
    ASSISTENTE_PGVECTOR_PWD,
    ASSISTENTE_PGVECTOR_USER,
    DATABASE_TYPE,
    DB_SEI_DATABASE,
    DB_SEI_HOST,
    DB_SEI_PORT,
    DB_SEI_PWD,
    DB_SEI_SCHEMA,
    DB_SEI_USER,
)

BasePgvector = declarative_base()


if DATABASE_TYPE == "mysql":
    CONN_SEI_STRING = (
        f"mysql+pymysql://{DB_SEI_USER}:{DB_SEI_PWD}@"
        f"{DB_SEI_HOST}:{DB_SEI_PORT}/{DB_SEI_DATABASE}"
    )
    sei_db_instance = DBConnector(CONN_SEI_STRING, schema=DB_SEI_SCHEMA)

if DATABASE_TYPE == "oracle":
    import sys

    import oracledb
    oracledb.version = "8.3.0"
    oracledb.init_oracle_client()
    sys.modules["cx_Oracle"] = oracledb
    CONN_SEI_STRING = f"oracle://{DB_SEI_USER}:{DB_SEI_PWD}@{DB_SEI_HOST}:{DB_SEI_PORT}/?sid=xe&mode=SYSDBA"
    sql="SELECT * FROM SEI.ASSUNTO"
    sei_db_instance = DBConnector(CONN_SEI_STRING, schema="")

if DATABASE_TYPE == "mssql":

    connection_string = \
        f"UID={DB_SEI_USER};PWD={DB_SEI_PWD};SERVER={DB_SEI_HOST},{DB_SEI_PORT};DATABASE={DB_SEI_DATABASE};DRIVER=ODBC+Driver+18+for+SQL+Server;TrustServerCertificate=yes"
    conn_str = sa.engine.URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
    sei_db_instance = DBConnector(connection_string=conn_str, schema=DB_SEI_SCHEMA)



CONN_PGVECTOR_STRING = (
    f"postgresql://{ASSISTENTE_PGVECTOR_USER}:{ASSISTENTE_PGVECTOR_PWD}@"
    f"{ASSISTENTE_PGVECTOR_HOST}:{ASSISTENTE_PGVECTOR_PORT}/{ASSISTENTE_PGVECTOR_DB}"
)


app_db_instance = DBConnector(CONN_PGVECTOR_STRING, schema="sei_llm", base=BasePgvector)
