# scripts/copy_sqlite_to_postgres.py
import os
from sqlalchemy import create_engine, MetaData, Table, select, text
from sqlalchemy.exc import IntegrityError

# path to your sqlite file (relative or absolute)
SQLITE_URL = "sqlite:///digi_aata.db"
POSTGRES_URL = os.getenv("DATABASE_URL")  # from .env or environment

if not POSTGRES_URL:
    raise SystemExit("Please set DATABASE_URL environment variable (postgresql+psycopg2://...)")

src_engine = create_engine(SQLITE_URL)
dst_engine = create_engine(POSTGRES_URL)

src_meta = MetaData()
dst_meta = MetaData()

# reflect source (sqlite) schema
src_meta.reflect(bind=src_engine)
# reflect target schema (may be empty)
dst_meta.reflect(bind=dst_engine)

with src_engine.connect() as src_conn, dst_engine.connect() as dst_conn:
    for table_name, src_table in src_meta.tables.items():
        print(f"\nProcessing table: {table_name}")
        # if table does not exist in Postgres, create it using the SQLite definition
        if table_name not in dst_meta.tables:
            print(f"  Creating table {table_name} on Postgres...")
            # create a new Table object bound to dst_meta with same columns
            src_table.metadata = dst_meta
            try:
                src_table.create(bind=dst_engine)
                dst_meta.reflect(bind=dst_engine)  # refresh
            except Exception as e:
                print(f"  Could not create table {table_name}: {e}")
                continue

        # read all rows from sqlite
        rows = src_conn.execute(select(src_table)).mappings().all()
        if not rows:
            print("  No rows to copy.")
            continue

        dst_table = dst_meta.tables[table_name]
        # transform rows into list of dicts (SQLAlchemy core will convert types automatically)
        data = [dict(r) for r in rows]

        # attempt bulk insert; if fails for unique constraints, insert row-by-row
        try:
            print(f"  Inserting {len(data)} rows into Postgres.{table_name} ...")
            dst_conn.execute(dst_table.insert(), data)
            dst_conn.commit()
            print("  Bulk insert OK.")
        except IntegrityError as ie:
            print("  Bulk insert failed (IntegrityError), trying row-by-row ...")
            dst_conn.execute(text("BEGIN"))
            for row in data:
                try:
                    dst_conn.execute(dst_table.insert().values(**row))
                except Exception as e:
                    print(f"    Skipped row due to insert error: {e}")
            dst_conn.commit()

    # optional: reset serial sequences for typical 'id' primary keys
    print("\nResetting sequences for serial id columns (if any)...")
    for table in dst_meta.tables.values():
        if 'id' in table.c:
            seq_sql = text(
                "SELECT setval(pg_get_serial_sequence(:table, 'id'), COALESCE((SELECT MAX(id) FROM \"{}\"), 1), false)".format(table.name)
            )
            try:
                dst_conn.execute(seq_sql, {"table": table.name})
            except Exception:
                # some tables may not use serials - ignore
                pass

print("\nDone.")

