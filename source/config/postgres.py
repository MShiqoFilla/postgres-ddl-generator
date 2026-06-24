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

    def insert_on_conflict_nothing(self, table, conn, keys, data_iter):
        data = [dict(zip(keys, row)) for row in data_iter]
        insert_statement = insert(table.table).values(data)
        conflict_update = insert_statement.on_conflict_do_update(
            constraint=f"{table.table.name}_pkey",
            set_={column.key: column for column in insert_statement.excluded},
        )
        result = conn.execute(conflict_update)
        return result.rowcount
    
    def ingest(self, df: pd.DataFrame, schema: str, table_name: str):
        try:
            connect = self.engine.connect() 
            df.to_sql(table_name, con = connect,
                if_exists='append', #append if using method = insert_on_conflict_nothing
                index=False, method=self.insert_on_conflict_nothing,
                schema=schema
            )
            connect.commit()
            connect.close()
        except Exception as e:
            logger.error(f"Error Happened :: {e}")
            self.connect.rollback()
            self.connect.close()
            return
    
    def ingest_v2(self, df: pd.DataFrame, schema: str, table_name: str, dtype : dict = {}):
        with self.engine.connect() as connect:
            df.to_sql(table_name, con=connect, if_exists='append', index=False, method=self.insert_on_conflict_nothing, schema=schema, dtype=dtype)
            connect.commit() 

    def ingest_replace(self, df: pd.DataFrame, schema: str, table_name: str):
        with self.engine.connect() as connect:
            df.to_sql(table_name, con=connect, if_exists="append", index=False, schema=schema)
            connect.commit() 

    def read_table(self, schema: str, table_name: str, query: str = None):
        if query == None:
            query = f"""SELECT * FROM {schema}.{table_name};"""
        with self.engine.connect() as connect:
            df = pd.read_sql(query, con=connect)
        return df

    def execute_sql_select(self, query, params:dict|None=None):
        with self.engine.connect() as connect:
            return pd.read_sql(text(query), con=connect, params=params)
    
    def execute_sql_dml(self, query):
        with self.engine.connect() as connect:
            connect.execute(text(query))
            connect.commit()
