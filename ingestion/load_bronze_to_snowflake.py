"""
Loader script — Bronze JSON -> Snowflake raw table
Reads all bronze JSON files, flattens the nested rate object into rows,
and loads them into a raw table in Snowflake for dbt to build on top of.
 
Requires environment variables (put these in a local .env file, never commit it):
    SNOWFLAKE_ACCOUNT
    SNOWFLAKE_USER
    SNOWFLAKE_PASSWORD
    SNOWFLAKE_WAREHOUSE
    SNOWFLAKE_DATABASE
    SNOWFLAKE_SCHEMA
 
Usage:
    python load_bronze_to_snowflake.py --bronze-dir data/bronze/exchange_rates
"""
import argparse
import json
import logging
import os
from pathlib import Path

import snowflake.connector
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent/".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

RAW_TABLE = "RAW_EXCHANGE_RATES"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {RAW_TABLE} (
    base_currency STRING,
    target_currency STRING,
    rate FLOAT,
    rate_date STRING,
    ingested_at TIMESTAMP_NTZ,
    source_file STRING
    )
    """

INSERT_SQL = f"""
INSERT INTO {RAW_TABLE}
    (base_currency, target_currency, rate, rate_date, ingested_at, source_file)
VALUES (%s, %s, %s, %s, %s, %s)
"""

def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )

def flatten_bronze_file(file_path: Path) -> list[tuple]:
    """FLatten one bronze JSON file into (base, target, rate, date, ingested_at, filename) rows."""
    with open(file_path) as f:
        payload = json.load(f)

    base_currency = payload["base_currency"]
    ingested_at = payload["ingested_at"]
    raw = payload["raw_response"]
    rate_date = raw.get("time_last_update_utc", "")
    rates = raw.get("rates", {})

    rows = [
        (base_currency, target, rate, rate_date, ingested_at, file_path.name)
        for target, rate in rates.items()
    ]
    return rows

def load_bronze_dir(bronze_dir: str) -> int:
    json_files = list(Path(bronze_dir).rglob("*.json"))
    logger.info(f"Found {len(json_files)}bronze files under {bronze_dir}")

    all_rows = []
    for file_path in json_files:
        all_rows.extend(flatten_bronze_file(file_path))

    if not all_rows:
        logger.info("no rows to load")
        return 0
    
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(CREATE_TABLE_SQL)
        cur.executemany(INSERT_SQL, all_rows)
        conn.commit()
        logger.info(f"Loaded {len(all_rows)} rows into {RAW_TABLE}")
    finally:
        conn.close()

    return len(all_rows)

def main():
    parser = argparse.ArgumentParser(description="Load bronze JSON file into Snowflake")
    parser.add_argument(
        "--bronze-dir",
        default="data/bronze/exchange_rates",
        help="Directory containing bronze JSON files",
    )
    args = parser.parse_args()

    load_bronze_dir(args.bronze_dir)

if __name__== "__main__":
    main()
