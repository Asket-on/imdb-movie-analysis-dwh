from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="imdb_daily_dwh_pipeline",
    default_args=default_args,
    description="End-to-End IMDb Movie Analysis DWH Pipeline (Ingestion -> Staging -> Marts -> DQ Tests)",
    schedule="0 4 * * *",  # Daily at 04:00 UTC
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["data-engineering", "dbt", "postgres", "imdb", "portfolio"],
) as dag:

    # Step 1: Extract and load raw IMDb datasets into PostgreSQL raw_imdb schema
    extract_and_load_raw = BashOperator(
        task_id="extract_and_load_raw",
        bash_command="python /opt/airflow/src/ingest_imdb.py --sample",
        doc_md="""
        ### Extract & Load Raw IMDb Data
        Downloads official compressed TSV datasets or generates deterministic sample data,
        cleans standard IMDb null representations (`\\N`), and batch-loads into PostgreSQL `raw_imdb` schema.
        """,
    )

    # Step 2: Run dbt staging models
    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command="dbt run --profiles-dir /opt/airflow/dbt_imdb --project-dir /opt/airflow/dbt_imdb --select staging",
        doc_md="Transforms raw tables into cleaned staging views with normalized data types.",
    )

    # Step 3: Execute data quality tests on staging schema
    dbt_test_staging = BashOperator(
        task_id="dbt_test_staging",
        bash_command="dbt test --profiles-dir /opt/airflow/dbt_imdb --project-dir /opt/airflow/dbt_imdb --select staging",
        doc_md="Verifies primary key uniqueness and non-null constraints on staging models.",
    )

    # Step 4: Run dbt intermediate and analytical mart tables
    dbt_run_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command="dbt run --profiles-dir /opt/airflow/dbt_imdb --project-dir /opt/airflow/dbt_imdb --select intermediate marts",
        doc_md="Builds intermediate joined tables and final analytical data marts.",
    )

    # Step 5: Execute data quality assertions on analytical marts
    dbt_test_marts = BashOperator(
        task_id="dbt_test_marts",
        bash_command="dbt test --profiles-dir /opt/airflow/dbt_imdb --project-dir /opt/airflow/dbt_imdb --select intermediate marts",
        doc_md="Verifies business rules and data quality constraints on final analytical tables.",
    )

    # Define execution graph sequence
    extract_and_load_raw >> dbt_run_staging >> dbt_test_staging >> dbt_run_marts >> dbt_test_marts
