from config.postgres import _create_engine, PostgreService
from services.models import TableMetadata
from services.queries import TABLE_METADATA_QUERIES, LIST_TABLES_OF_SCHEMA_QUERIES
from config.logger import logger
from typing import List
import hashlib
import os

def generate_id(string:str):
    return hashlib.md5(string.encode()).hexdigest()

class PGConnector:
    def __init__(
            self, pg_host:str, pg_port:int, pg_username:str, pg_password:str, db_name:str
        ):
        self.pg_client = PostgreService(
            engine=_create_engine(
                user=pg_username, password=pg_password, dbname=db_name, host=pg_host, port=pg_port
            )
        )

    def get_list_of_tables_by_schema(self, schema_name):
        schemas_df = self.pg_client.execute_sql_select(LIST_TABLES_OF_SCHEMA_QUERIES, params={"schema_name" : schema_name})
        return list(schemas_df['tables'])

    def get_metadata_of_tables(
            self, schema_name:str, table_names:list[str]
    ) -> List[TableMetadata]:

        placeholders = ", ".join(
            f":table_{i}"
            for i in range(len(table_names))
        )
        query_string = TABLE_METADATA_QUERIES.format(placeholders=placeholders)
        params = {
            "schema_name": schema_name,
            **{
                f"table_{i}": name
                for i, name in enumerate(table_names)
            }
        }
        tables_df = self.pg_client.execute_sql_select(query_string, params=params)
        tables = []

        tables_record = tables_df.to_dict(orient="records")
        tables_record.sort(key=lambda x: x["has_fk"])
        for table_meta in tables_record:
            tables.append(TableMetadata.model_validate(table_meta))

        exists_tables = set([t["table_name"] for t in tables_record])
        non_exist_tables = set(table_names).difference(exists_tables)

        if non_exist_tables:
            logger.warning(f"These tables don't exist :: {non_exist_tables} in schema {schema_name}")

        return tables

def create_schema_query(schema_name):
    return f"CREATE SCHEMA IF NOT EXISTS {schema_name}"

def create_single_table_ddl(table_metadata:TableMetadata, ignore_foreign_key:bool=False):
    table_name = table_metadata.table_name
    schema_name = table_metadata.schema_name
    columns = table_metadata.columns
    constraints = table_metadata.constraints

    column_defs = []
    for col in columns:
        col_name = col.name
        if col.udt_name in ("geometry", "geography", "vector", "varchar"):
            data_type = col.udt_name
        else:
            data_type = col.data_type

        col_def = f'    {col_name} {data_type}'
        if max_length:=col.character_maximum_length: 
            col_def += f'({int(max_length)})'
        elif col.data_type == "numeric":
            numeric_precision = col.numeric_precision
            numeric_scale = col.numeric_scale
            col_def += f'({int(numeric_precision)}, {int(numeric_scale)})'

        if col.is_identity=="YES":
            col_def += f" GENERATED {col.identity_generation} AS IDENTITY"
        if col.is_nullable == "NO":
            col_def += " NOT NULL"
        if col_default:=col.column_default:
            col_def += f' DEFAULT {col_default}'
        column_defs.append(col_def)

    create_table_query = (
        f"CREATE TABLE {schema_name}.{table_name} (\n"
        + ",\n".join(column_defs)
    )
    constraint_defs = []
    for cons in constraints:
        if ignore_foreign_key:
            if cons.type == "FOREIGN KEY":
                continue
        col_def = f"    CONSTRAINT {cons.name} {cons.definition}"
        constraint_defs.append(col_def)
    if constraint_defs:
        create_table_query = (
            create_table_query + ","
            + "\n"
            + ",\n".join(constraint_defs)
        )

    create_table_query += "\n);"
    return create_table_query

def create_ddl_strings(tables:List[TableMetadata], ignore_foreign_key:bool=False):
    schemas = set()
    query_create_tables=""
    for table in tables:
        schemas.add(table.schema_name)
        query_create_tables += create_single_table_ddl(table, ignore_foreign_key)
        query_create_tables += "\n\n"

    query_create_schemas = (
        ";\n".join([create_schema_query(schema_name) for schema_name in schemas])
    ) + ";"
    query = query_create_schemas + "\n\n" + query_create_tables

    return query.strip()

def write_sql_query_into_sql_file(query:str):
    os.makedirs("result", exist_ok=True)
    filename = f"{generate_id(query)}.sql"
    with open(f"result/{filename}", "w") as f:
        f.write(query)
    logger.success(f"CREATED sql file :: ./result/{filename}")