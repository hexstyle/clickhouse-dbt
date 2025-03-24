import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta


default_args = {
    'owner': 'airflow_admin',
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
        dag_id='fill_vitrina_dag',
        default_args=default_args,
        schedule_interval=timedelta(seconds=15),
        catchup=False,
        max_active_runs=1
) as dag:

    # 1) Выполняем преобразования в Postgres
    fill_vitrina_postgres = BashOperator(
        task_id='fill_vitrina_postgres',
        bash_command="""
            cd /usr/app/dbt/postgres
            set -x
            dbt run --target dev --models vitrina1_pg
        """
    )

    # 2) Переносим готовые данные в ClickHouse (создаём/обновляем vitrina1, логируем в sync_log)
    fill_vitrina_clickhouse = BashOperator(
        task_id='fill_vitrina_clickhouse',
        bash_command="""
            cd /usr/app/dbt/clickhouse
            set -x
            dbt run --target clickhouse_target --models vitrina1_ch
        """
    )

    fill_vitrina_postgres >> fill_vitrina_clickhouse


