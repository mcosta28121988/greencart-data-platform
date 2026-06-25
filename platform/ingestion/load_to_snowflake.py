"""
Loads GreenCart simulator Parquet output into Snowflake RAW schema.

Expects the following environment variables to be set (via .env at repo root):
    SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PRIVATE_KEY_PATH,
    SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA,
    SNOWFLAKE_ROLE

Usage:
    python platform/ingestion/load_to_snowflake.py
"""

import os
import sys
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from snowflake.connector.pandas_tools import write_pandas

# Explicitly load .env from repo root regardless of where
# the script is called from
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

TABLES = [
    "customers",
    "products",
    "order_lines",
    "orders",
    "payments",
]

PARQUET_DIR = Path(__file__).resolve().parents[2] / "simulator" / "output"


def get_connection():
    key_path = os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]

    with open(key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=private_key_bytes,
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        role=os.environ["SNOWFLAKE_ROLE"],
    )


def load_table(conn, table: str) -> None:
    path = PARQUET_DIR / f"{table}.parquet"

    if not path.exists():
        print(f"  ERROR: {path} not found — run the simulator first")
        sys.exit(1)

    df = pd.read_parquet(path)

    # Snowflake column names must be uppercase
    df.columns = [col.upper() for col in df.columns]

    # Convert datetime columns to strings — Snowflake connector
    # handles string timestamps more reliably than Python datetime
    for col in df.select_dtypes(include=["datetime64[ns]"]).columns:
        df[col] = df[col].astype(str).replace("NaT", None)

    success, chunks, rows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name=table.upper(),
        auto_create_table=True,
        overwrite=True,
    )

    if success:
        print(f"  {table:<12} {rows:>6,} rows loaded")
    else:
        print(f"  {table:<12} FAILED after {chunks} chunks")
        sys.exit(1)


def main():
    print("GreenCart — loading simulator output to Snowflake RAW")
    print(f"Target: {os.environ['SNOWFLAKE_DATABASE']}.{os.environ['SNOWFLAKE_SCHEMA']}")
    print()

    conn = get_connection()

    try:
        for table in TABLES:
            load_table(conn, table)
    finally:
        conn.close()

    print()
    print("Done.")


if __name__ == "__main__":
    main()
