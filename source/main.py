import argparse
from services.worker import create_ddl_strings, write_sql_query_into_sql_file, PGConnector

parser = argparse.ArgumentParser(
    description="Postgres Tables DDL Generator"
)

parser.add_argument("-H", "--host", type=str, help="Postres Connection HOST or IP")
parser.add_argument("-p", "--port", type=int, help="Postres Connection Port")
parser.add_argument("-U", "--username", type=str, help="Username Authentication for Postgres DB")
parser.add_argument("-P", "--password", type=str, help="Password Authentication for Postgres DB")
parser.add_argument("-d", "--dbname", type=str, help="Postgres Database Name")
parser.add_argument("-s", "--schema", type=str, default="public", help="Postgres Schema Name", required=False)
parser.add_argument("--tables", nargs="*", type=str, help="Postgres Table Names", required=False)
parser.add_argument("--all-tables", action="store_true", help="Process for All Tables in the Schema", required=False)
parser.add_argument("--ignore-fk", action="store_true", help="Ignore Foreign Key Constraints", required=False)
parser.add_argument("--dry-run", action="store_true", help="Print DDL Query Result without Creating File", required=False)

args = parser.parse_args()

if __name__ == "__main__":
    host, port, username, password, dbname = args.host, args.port, args.username, args.password, args.dbname
    worker = PGConnector(
        pg_host=host, pg_port=port, pg_username=username, pg_password=password, db_name=dbname
    )

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



