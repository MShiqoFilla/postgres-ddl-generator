# PostgreSQL DDL Generator

CLI tool to generate `CREATE TABLE` DDL statements from existing PostgreSQL tables.

## Overview

This tool connects to a PostgreSQL database and extracts table definitions, then generates complete `CREATE TABLE` DDL (Data Definition Language) statements. It reads existing table metadata including columns, data types, constraints, defaults, and foreign keys—then outputs ready-to-use SQL scripts that recreate those tables.

The tool handles:
- Column definitions with proper data types, precision, and length
- `NOT NULL` constraints and default values
- `IDENTITY` columns (auto-increment)
- Primary keys, unique constraints, and foreign keys
- Proper table ordering to respect foreign key dependencies

## Why This Tool vs pg_dump

| Aspect | This Tool | pg_dump |
|--------|-----------|---------|
| Output | Clean `CREATE TABLE` statements only | Verbose dump with SET, COPY, comments |
| Focus | Schema-only, initialization-ready | Full dump with data restoration |
| Readability | Easy to read and modify | Harder to parse, lots of metadata |
| Use case | API initialization, documentation | Full database backups/migration |
| Size | Small, focused scripts | Large, comprehensive dumps |

**Use this tool when you need clean, human-readable DDL for documentation or initialization scripts. Use `pg_dump` when you need complete database backups with data.**

## Why & When to Use This Tool

**Why:**
- **Iterative development** - Schema evolves during API development; capture the final state as initialization scripts
- **Backup table structures** without exporting data
- **Document your schema** as readable SQL files
- **Migrate schemas** between databases or environments
- **Version control** your table definitions alongside your code

**When:**
- Your API's schema has evolved through ad-hoc queries and you need the final DDL for initialization
- You need to recreate tables in a new database
- You're setting up staging/dev environments that match production
- You want to review and document your database structure
- You need schema-only scripts (no data dumps)

## Installation

```bash
# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## Configuration

Database credentials can be provided in two ways:

**Option 1: Command-line arguments**
```bash
python source/main.py -H localhost -p 5432 -U admin -P secret -d mydb --all-tables
```

**Option 2: Environment file (.env)**
Create a `.env` file with your database credentials:
```bash
PG_HOST=localhost
PG_PORT=5432
PG_USER=admin
PG_PASS=secret
PG_DBNM=mydb
```

Then reference it with `--db-config`:
```bash
python source/main.py -c .env -s public --all-tables
```

## Usage

```bash
python source/main.py -H <host> -p <port> -U <username> -P <password> -d <database> -s <schema> [options]
```

### Arguments

| Argument | Short | Description | Required |
|----------|-------|-------------|----------|
| `--db-config` | `-c` | Path to `.env` file with DB credentials | † |
| `--host` | `-H` | PostgreSQL host or IP address | † |
| `--port` | `-p` | PostgreSQL port number | † |
| `--username` | `-U` | Database username | † |
| `--password` | `-P` | Database password | † |
| `--dbname` | `-d` | Database name | † |
| `--schema` | `-s` | Schema name, defaults to `public` | No |
| `--tables` | | Specific table names (space-separated) | No* |
| `--all-tables` | | Process all tables in the schema | No* |
| `--ignore-fk` | | Skip foreign key constraints in output | No |
| `--dry-run` | | Print DDL to terminal without creating file | No |

† Use `--db-config` OR provide individual connection arguments (`-H -p -U -P -d`).

*Either `--tables` or `--all-tables` must be specified.

### Examples

**Using .env file (recommended):**
```bash
python source/main.py -c .env -s public --all-tables
```

**Using command-line arguments:**
```bash
python source/main.py -H localhost -p 5432 -U admin -P secret -d mydb -s public --tables users orders
```

**Preview DDL without creating file (dry-run):**
```bash
python source/main.py -c .env -s public --tables users --dry-run
```

**Generate DDL without foreign keys:**
```bash
python source/main.py -c .env -s public --tables users --ignore-fk
```

## Example Output

Given a table like this:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

Running:
```bash
python source/main.py -H localhost -p 5432 -U admin -P secret -d mydb -s public --tables users
```

Generates `result/<hash>.sql`:
```sql
CREATE SCHEMA IF NOT EXISTS public;

CREATE SEQUENCE public.users_id_seq;
CREATE TABLE public.users (
    id integer NOT NULL DEFAULT nextval('public.users_id_seq'::regclass),
    username varchar(50) NOT NULL,
    email varchar(100) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email)
);
```

## Output

if `--dry-run` flag is not called, by default SQL files are saved to `./result/<hash>.sql` with:
- `CREATE SCHEMA IF NOT EXISTS` statements
- `CREATE TABLE` statements with columns, types, defaults, and constraints
- Properly ordered to handle foreign key dependencies

Otherwise it will print the query string result to terminal without file creation.

## Dependencies

- Python 3.11+
- pandas, psycopg2-binary, pydantic, python-dotenv, sqlalchemy, loguru