import yaml
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta


# Параметры DAG
default_args = {
    'owner': 'airflow_admin',
    'start_date': days_ago(1),
    'retries': 0,
    'retry_delay': timedelta(seconds=5)
}

with DAG(
        dag_id='dbt_openmetadata_test_dag',
        default_args=default_args,
        schedule_interval=timedelta(seconds=5),
        catchup=False,
        max_active_runs=1
) as dag:

    generate_dbt_docs = BashOperator(
        task_id='generate_dbt_docs',
        bash_command="cd /usr/app/dbt/newproj/postgres_dbt && dbt run && dbt test && dbt docs generate",
        do_xcom_push=True
    )

    ingest_dbt_metadata = BashOperator(
        task_id='ingest_dbt_metadata',
        bash_command="metadata ingest -c /opt/airflow/dags/om_ingestion/dbt_pg_ingestion.yml",
        do_xcom_push=True
    )

    generate_dbt_docs >> ingest_dbt_metadata
