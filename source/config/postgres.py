from sqlalchemy import create_engine, URL, text, Engine
from sqlalchemy.dialects.postgresql import insert
from loguru import logger
import pandas as pd
import os


def _create_engine(
        user:str, password:str, dbname:str, host:str, port:int=5432
):
    return create_engine(
        url=URL.create(drivername="postgresql+psycopg2", username=user, password=password, host=host, port=port, database=dbname),
        pool_size=10,
        max_overflow=5,
        pool_timeout=5,
        pool_recycle=1800,
    )

class PostgreService:
    def __init__(self, engine : Engine):
        self.engine = engine

    def execute_sql_select(self, query, params:dict|None=None):
        with self.engine.connect() as connect:
            return pd.read_sql(text(query), con=connect, params=params)
    
    def execute_sql_dml(self, query):
        with self.engine.connect() as connect:
            connect.execute(text(query))
            connect.commit()
