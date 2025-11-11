#!/usr/bin/env python3
"""
Quick script to check if ingestion worked
"""


import duckdb


def check_ingestion():
    """Check if the ingestion job populated the database."""

    try:
        # Connect to database
        conn = duckdb.connect('analytics.duckdb')
        print("Ingestion Status Check")
        print("=" * 40)

        # Check if schemas exist
        schemas = conn.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('raw', 'staging', 'marts', 'metadata')").fetchall()
        print(f"Custom schemas found: {len(schemas)}")
        for schema in schemas:
            print(f"  - {schema[0]}")

        # Check if raw.gl_records table exists
        try:
            table_check = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'raw' AND table_name = 'gl_records'").fetchone()
            if table_check[0] > 0:
                print("\nraw.gl_records table: EXISTS")

                # Check record count
                count_result = conn.execute("SELECT COUNT(*) FROM raw.gl_records").fetchone()
                total_records = count_result[0] if count_result else 0
                print(f"Total records: {total_records}")

                if total_records > 0:
                    # Check by source
                    source_counts = conn.execute("SELECT source, COUNT(*) FROM raw.gl_records GROUP BY source").fetchall()
                    print("Records by source:")
                    for source, count in source_counts:
                        print(f"  - {source}: {count} records")

                    # Check latest ingestion
                    latest = conn.execute("SELECT MAX(ingested_at) FROM raw.gl_records WHERE source = 'fastapi'").fetchone()
                    if latest[0]:
                        print(f"Latest FastAPI ingestion: {latest[0]}")

                    # Sample data
                    print("\nSample records:")
                    sample = conn.execute("SELECT gl_entry_id, account_name, net_amount, ingested_at FROM raw.gl_records LIMIT 3").fetchall()
                    for record in sample:
                        print(f"  ID: {record[0]}, Account: {record[1]}, Amount: {record[2]}, Ingested: {record[3]}")

                    print("\nSUCCESS: Data found in database!")
                else:
                    print("\nWARNING: Table exists but no records found")
                    print("Try running the ingestion job in Dagster UI")
            else:
                print("\nERROR: raw.gl_records table not found")

        except Exception as e:
            print(f"\nERROR checking raw.gl_records: {e}")

        # Check other tables
        print("\nAll tables in database:")
        all_tables = conn.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog') ORDER BY table_schema, table_name").fetchall()
        for schema, table in all_tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {schema}.{table}").fetchone()[0]
            print(f"  {schema}.{table}: {count} records")

        conn.close()

    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        print("Try copying database first: docker cp dakota_duckdb:/app/data/analytics.duckdb ./analytics.duckdb")

if __name__ == "__main__":
    check_ingestion()
