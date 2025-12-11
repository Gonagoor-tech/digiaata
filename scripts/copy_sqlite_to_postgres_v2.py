# scripts/copy_sqlite_to_postgres_v2.py
"""
Robust SQLite -> PostgreSQL migration script.

Behavior:
- Reads sqlite schema from sqlite_master
- Transforms SQLite DDL to Postgres-friendly DDL (DATETIME -> TIMESTAMP,
  INTEGER PRIMARY KEY -> SERIAL PRIMARY KEY, remove AUTOINCREMENT)
- Creates tables in Postgres in DDL/autocommit mode (so DDL errors do not poison transactions)
- Copies rows table-by-table with per-row short transactions; coerces boolean-like values for boolean columns
- Adds foreign-key constraints AFTER rows are inserted to avoid ordering issues
- Resets serial sequences at the end

Usage:
 - Ensure your sqlite file is present (default: digi_aata.db in the same folder)
 - Set environment variable DATABASE_URL (postgresql+psycopg2://user:pass@host:port/db)
 - Run: python scripts/copy_sqlite_to_postgres_v2.py
"""

import os
import re
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

SQLITE_URL = "sqlite:///digi_aata.db"
POSTGRES_URL = os.getenv("DATABASE_URL")

if not POSTGRES_URL:
    raise SystemExit("Please set DATABASE_URL environment variable (postgresql+psycopg2://...)")

# Engines
src = create_engine(SQLITE_URL)
dst = create_engine(POSTGRES_URL)


def transform_create_sql(sql):
    """Make SQLite CREATE TABLE SQL more Postgres-compatible (basic transformations)."""
    if not sql:
        return None, []

    # collect foreign-key clauses to re-add later
    fk_matches = re.findall(
        r'FOREIGN KEY\s*\(([^)]+)\)\s*REFERENCES\s*([^\s(]+)\s*\(([^)]+)\)',
        sql, flags=re.I
    )
    fk_alters = []
    for cols, ref_table, ref_cols in fk_matches:
        cols_clean = cols.strip()
        ref_table_clean = ref_table.strip().strip('"')
        ref_cols_clean = ref_cols.strip()
        fk_alters.append((cols_clean, ref_table_clean, ref_cols_clean))

    # remove inline FOREIGN KEY (...) REFERENCES ... clauses to avoid ordering issues
    sql_no_fk = re.sub(
        r',\s*FOREIGN KEY\s*\([^)]+\)\s*REFERENCES\s*[^\)]+\([^)]+\)',
        '',
        sql,
        flags=re.I | re.S
    )

    # DATETIME -> TIMESTAMP
    sql_no_fk = re.sub(r'\bDATETIME\b', 'TIMESTAMP', sql_no_fk, flags=re.I)

    # remove AUTOINCREMENT
    sql_no_fk = re.sub(r'\bAUTOINCREMENT\b', '', sql_no_fk, flags=re.I)

    # INTEGER PRIMARY KEY -> SERIAL PRIMARY KEY (simple heuristic)
    sql_no_fk = re.sub(r'\bINTEGER\s+PRIMARY\s+KEY\b', 'SERIAL PRIMARY KEY', sql_no_fk, flags=re.I)

    # Return transformed DDL and fk list
    return sql_no_fk.strip(), fk_alters


def create_table_if_not_exists(name, create_sql):
    """Execute DDL in autocommit so failure doesn't poison connection."""
    try:
        with dst.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text(create_sql))
        print(f'  Created table {name} on Postgres (DDL executed).')
    except SQLAlchemyError as e:
        print(f'  Could not create table {name}: {e}')


def copy_rows(table_name):
    """Copy rows safely, coercing booleans and using short transactions per row."""
    src_conn = src.connect()
    dst_conn = dst.connect()

    # Determine boolean columns on target table
    try:
        col_info = dst_conn.execute(text(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name = :tbl"
        ), {"tbl": table_name}).mappings().all()
        bool_cols = {r['column_name'] for r in col_info if r['data_type'] in ('boolean',)}
    except Exception:
        bool_cols = set()

    try:
        rows = src_conn.execute(text(f'SELECT * FROM "{table_name}"')).mappings().all()
    except Exception as e:
        print(f"  Could not read rows from {table_name}: {e}")
        src_conn.close()
        dst_conn.close()
        return 0

    if not rows:
        print("  No rows to copy.")
        src_conn.close()
        dst_conn.close()
        return 0

    cols = list(rows[0].keys())
    col_list = ",".join([f'"{c}"' for c in cols])
    placeholders = ",".join([f":{c}" for c in cols])

    inserted = 0
    for r in rows:
        row = dict(r)  # mutable copy
        # Coerce boolean-like columns (1/0, '1'/'0', 'true'/'false', etc.)
        for c in list(row.keys()):
            if c in bool_cols:
                val = row[c]
                if val is None:
                    row[c] = None
                else:
                    # integers -> bool
                    if isinstance(val, int):
                        row[c] = bool(val)
                    else:
                        sval = str(val).strip().lower()
                        if sval in ("1", "true", "t", "yes", "y"):
                            row[c] = True
                        elif sval in ("0", "false", "f", "no", "n"):
                            row[c] = False
                        else:
                            try:
                                row[c] = bool(int(sval))
                            except Exception:
                                # leave as-is; Postgres may reject if incompatible
                                row[c] = row[c]
        try:
            with dst.begin() as tconn:
                tconn.execute(text(f'INSERT INTO "{table_name}" ({col_list}) VALUES ({placeholders})'), row)
            inserted += 1
        except IntegrityError as ie:
            print(f"    Skipped a row due to IntegrityError: {ie.orig if hasattr(ie, 'orig') else ie}")
        except Exception as e:
            print(f"    Skipped a row due to error: {e}")
    print(f"  Inserted {inserted} rows into Postgres.{table_name}")

    src_conn.close()
    dst_conn.close()
    return inserted


def add_fk_constraints(dst_engine, table_name, fk_alters):
    """Add FK constraints after data is in place. Uses autocommit per ALTER."""
    for idx, (cols, ref_table, ref_cols) in enumerate(fk_alters, start=1):
        constraint_name = f"fk_{table_name}_{idx}"
        alter_sql = f'ALTER TABLE "{table_name}" ADD CONSTRAINT "{constraint_name}" FOREIGN KEY ({cols}) REFERENCES "{ref_table}" ({ref_cols});'
        try:
            with dst_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                conn.execute(text(alter_sql))
            print(f'  Added FK constraint on {table_name} -> {ref_table}')
        except SQLAlchemyError as e:
            # likely duplicate constraint or referenced table missing — report and continue
            print(f'  Could not add FK constraint for {table_name}: {e}')


def reset_serials():
    """Reset serial sequences using a connection (Engine.execute removed in SQLAlchemy 2.x)."""
    with dst.connect() as conn:
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.columns WHERE column_name='id' AND table_schema='public';"
        )).fetchall()
        for row in result:
            tbl = row[0]
            try:
                seq_sql = text(
                    "SELECT setval(pg_get_serial_sequence(:table, 'id'), COALESCE((SELECT MAX(id) FROM \"{}\"), 1), false)".format(tbl)
                )
                conn.execute(seq_sql, {"table": tbl})
            except Exception:
                # ignore tables without sequences or other errors
                pass


def main():
    src_conn = src.connect()
    try:
        tbls = src_conn.execute(text(
            "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )).mappings().all()
    except Exception as e:
        print("Could not read sqlite schema:", e)
        src_conn.close()
        return

    create_list = []
    for row in tbls:
        name = row['name']
        sql = row['sql']
        transformed_sql, fk_alters = transform_create_sql(sql)
        if transformed_sql:
            # ensure CREATE TABLE "name"
            transformed_sql = re.sub(r'CREATE\s+TABLE\s+("?)(%s)\1' % re.escape(name),
                                     f'CREATE TABLE "{name}"', transformed_sql, flags=re.I)
            create_list.append((name, transformed_sql, fk_alters))

    # 1) create all tables (DDL in autocommit)
    for name, ddl, fk_alters in create_list:
        print(f"\nProcessing table: {name}")
        try:
            # check if table exists in postgres
            with dst.connect() as conn:
                conn.execute(text(f'SELECT 1 FROM "{name}" LIMIT 1'))
            print(f"  Table {name} exists on Postgres; skipping DDL creation.")
        except Exception:
            create_table_if_not_exists(name, ddl)

    # 2) copy rows table-by-table
    for name, ddl, fk_alters in create_list:
        print(f"\nCopying rows for table: {name}")
        copy_rows(name)

    # 3) add FK constraints after data is present
    for name, ddl, fk_alters in create_list:
        if fk_alters:
            print(f"\nAdding FK constraints for table: {name}")
            add_fk_constraints(dst, name, fk_alters)

    # 4) reset sequences
    print("\nResetting sequences for serial id columns (if any)...")
    reset_serials()

    src_conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()


