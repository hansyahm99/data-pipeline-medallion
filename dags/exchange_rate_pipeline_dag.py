"""
DAG: exchange_rate_pipeline
Orchestrates the full medallion pipeline:
    fetch (bronze JSON) >> load (Snowflake raw) >> dbt staging >> dbt silver >> dbt gold >> dbt test
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ingestion"))
from fetch_exchange_rates import fetch_rates, save_raw #noqa: E402
from load_bronze_to_snowflake import load_bronze_dir # noqa: E402

default_args = {
    "owner": "data-engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

BASE_CURRENCY = "USD"
BRONZE_DIR = "data/bronze/exchange_rates"
DBT_PROJECT_DIR = os.path.join(os.path.dirname(__file__), "..", "dbt_project")

def ingest_bronze(**context):
    data = fetch_rates(BASE_CURRENCY)
    save_raw(data, BRONZE_DIR, BASE_CURRENCY)

def load_to_snowflake(**context):
    load_bronze_dir(BRONZE_DIR)

with DAG(
    dag_id="exchange_rate_pipline",
    description="Daily exchange rate pipeline: bronze -> RAW -> staging -> silver -> gold",
    default_args=default_args,
    schedule="0 6 * * *",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["exchange-rate", "medallion", "portofoli"],
) as dag:

    t1_ingest_bronze = PythonOperator(
        task_id="ingest_bronze",
        python_callable=ingest_bronze,
    )

    t2_load_to_snowflake = PythonOperator(
        task_id="load_to_snowflake",
        python_callable=load_to_snowflake
    )

    t3_dbt_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --select staging",
    )

    t4_dbt_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --select silver",
    )

    t5_dbt_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --select gold",
    )

    t6_dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
    )

    t1_ingest_bronze >> t2_load_to_snowflake >> t3_dbt_staging >> t4_dbt_silver >> t5_dbt_gold >> t6_dbt_test