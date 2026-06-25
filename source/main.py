from services.worker import create_ddl_strings, write_sql_query_into_sql_file, PGConnector
from config.logger import logger

from dotenv import load_dotenv
import argparse
import os

parser = argparse.ArgumentParser(
    description="Postgres Tables DDL Generator"
)

parser.add_argument("-c", "--db-config", type=str, help=".env File Path of DB Config", required=False)
parser.add_argument("-H", "--host", type=str, help="Postres Connection HOST or IP", required=False)
parser.add_argument("-p", "--port", type=int, help="Postres Connection Port", required=False)
parser.add_argument("-U", "--username", type=str, help="Username Authentication for Postgres DB", required=False)
parser.add_argument("-P", "--password", type=str, help="Password Authentication for Postgres DB", required=False)
parser.add_argument("-d", "--dbname", type=str, help="Postgres Database Name", required=False)
parser.add_argument("-s", "--schema", type=str, default="public", help="Postgres Schema Name", required=False)
parser.add_argument("--tables", nargs="*", type=str, help="Postgres Table Names", required=False)
parser.add_argument("--all-tables", action="store_true", help="Process for All Tables in the Schema", required=False)
parser.add_argument("--ignore-fk", action="store_true", help="Ignore Foreign Key Constraints", required=False)
parser.add_argument("--dry-run", action="store_true", help="Print DDL Query Result without Creating File", required=False)

args = parser.parse_args()

if __name__ == "__main__":
    if env_path:=args.db_config:
        load_dotenv(env_path)
        host, port, username, password, dbname = os.getenv("PG_HOST"), os.getenv("PG_PORT"), os.getenv("PG_USER"), os.getenv("PG_PASS"), os.getenv("PG_DBNM")
    else:
        host, port, username, password, dbname = args.host, args.port, args.username, args.password, args.dbname
    
    required_fields = {
        "host": host, "port": port, "username": username,
        "password": password, "dbname": dbname,
    }
    missing_fields = [name for name, value in required_fields.items() if value is None]
    if missing_fields:
        logger.error(f"Missing required database authentication variables: {', '.join(missing_fields)}")
        exit()
    
    try:
        worker = PGConnector(
            pg_host=host, pg_port=port, pg_username=username, pg_password=password, db_name=dbname
        )
    except Exception as e:
        logger.error(f"Failed to connect with given DB Config :: {e}")
        exit()

    if schema_name:=args.schema:
        if tables:=args.tables:
            tables = worker.get_metadata_of_tables(
                schema_name=schema_name, table_names=tables
            )   
        if process_all:=args.all_tables:
            all_tables = worker.get_list_of_tables_by_schema(schema_name)
            tables = worker.get_metadata_of_tables(
                schema_name=schema_name, table_names=all_tables
            )
        
        query = create_ddl_strings(tables, args.ignore_fk)
        if args.dry_run:
            print("\n"+query+"\n")
        else:
            write_sql_query_into_sql_file(query)

