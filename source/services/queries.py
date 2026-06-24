LIST_TABLES_OF_SCHEMA_QUERIES = """
SELECT tablename AS tables FROM pg_catalog.pg_tables pt WHERE pt.schemaname = :schema_name;
"""

TABLE_METADATA_QUERIES = """
WITH columns_cte AS (
    SELECT
        table_schema,
        table_name,
        json_agg(
            json_build_object(
                'name', column_name,
                'data_type', data_type,
                'udt_name', udt_name,
                'character_maximum_length', character_maximum_length,
                'is_nullable', is_nullable,
                'column_default', column_default,
                'numeric_precision', numeric_precision,
                'numeric_scale', numeric_scale,
                'is_identity', is_identity,
                'identity_generation', identity_generation
            )
            ORDER BY ordinal_position
        ) AS columns
    FROM information_schema.columns
    WHERE table_schema = :schema_name
    AND table_name IN ({placeholders})
    GROUP BY
        table_schema,
        table_name
),
constraints_cte AS (
    SELECT
        n.nspname AS table_schema,
        c.relname AS table_name,
        BOOL_OR(con.contype = 'f') AS has_fk,
        json_agg(
            json_build_object(
                'name', con.conname,
                'type',
                CASE con.contype
                    WHEN 'p' THEN 'PRIMARY KEY'
                    WHEN 'u' THEN 'UNIQUE'
                    WHEN 'f' THEN 'FOREIGN KEY'
                    WHEN 'c' THEN 'CHECK'
                    WHEN 'x' THEN 'EXCLUDE'
                END,
                'definition',
                pg_get_constraintdef(con.oid)
            )
            ORDER BY
                CASE con.contype
                    WHEN 'p' THEN 1
                    WHEN 'u' THEN 2
                    WHEN 'c' THEN 3
                    WHEN 'f' THEN 4
                    WHEN 'x' THEN 5
                    ELSE 99
                END,
                con.conname
        ) AS constraints
    FROM pg_constraint con
    JOIN pg_class c
        ON c.oid = con.conrelid
    JOIN pg_namespace n
        ON n.oid = c.relnamespace
    WHERE n.nspname = :schema_name
    AND c.relname IN ({placeholders})
    GROUP BY
        n.nspname,
        c.relname
)
SELECT
    c.table_schema as schema_name,
    c.table_name,
    COALESCE(k.has_fk, false) AS has_fk,
    c.columns,
    COALESCE(
        k.constraints,
        '[]'::json
    ) AS constraints
FROM columns_cte c
LEFT JOIN constraints_cte k
ON c.table_schema = k.table_schema
AND c.table_name = k.table_name
ORDER by c.table_name
;
"""