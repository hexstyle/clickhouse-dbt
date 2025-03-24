import yaml
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
try:
    from airflow.operators.python import PythonOperator
except ModuleNotFoundError:
    from airflow.operators.python_operator import PythonOperator
from metadata.config.common import load_config_file
from metadata.workflow.metadata import MetadataWorkflow


dbt_clickhouse_config = """
source:
  type: dbt
  serviceName: dbt_service_clickhouse
  serviceConnection:
    config:
      type: Clickhouse
      username: write_user
      password: write_pass
      hostPort: clickhouse1:8123
      databaseSchema: online_reporting
  sourceConfig:
    config:
      type: DBT
      dbtConfigSource:
        dbtConfigType: local
        dbtCatalogFilePath: "/usr/app/dbt/clickhouse/target/catalog.json"
        dbtManifestFilePath: "/usr/app/dbt/clickhouse/target/manifest.json"
        dbtRunResultsFilePath: "/usr/app/dbt/clickhouse/target/run_results.json"
sink:
  type: metadata-rest
  config: {}
workflowConfig:
  loggerLevel: DEBUG
  openMetadataServerConfig:
    hostPort: "http://openmetadata:8585/api"
    authProvider: openmetadata
    securityConfig:
      jwtToken: "eyJhbGciOiJSUzI1NiIsImtpZCI6ImdiMzg5YS05Zjc2LWdkanMtYTkyai0wMjQyYms5NDM1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJsb2NhbGhvc3QiLCJzdWIiOiJhaXJmbG93IiwiYXVkIjoibG9jYWxob3N0IiwiZXhwIjoxNzc2ODk1NDcyLCJpYXQiOjE3NDA4OTkwNzJ9.UWN_Fq7NTo8r1xD6m-5QsCzysS60SGNcvJ7i5iFjvmtogahJtbJtuDqs7H_3UOu4wvbm3HLmwkqVmQiD6trDkV3KOfriGmD3LUjRSztTptRmKaRJN5F37PxtFEfxXXbNKJnCMEle0et9XN1_aBC7Tf0EVeVrfWHAzK8sc9FrMll0g1cO3aWE0gNtvtPhkK7Zj_SawxQFzle1RkFzmcbEiI1vvGExU2BEZOS7DD2FpZ5zDizNdb0_6LMBlsxaW8H8yEP6tTOkTSVc5qPH6AwIdgtCwXFJV0SuQR6yKASm5TBDDwLL9AeRCZIAG2tWL1oyvo2U3IqkQ2MqSvSPwf-PaQ"
"""

dbt_postgres_config = """
source:
  type: dbt
  serviceName: dbt_service_postgres
  serviceConnection:
    config:
      type: PostgreSQL
      username: user
      authType:
        password: "password"
      hostPort: postgres:5432
      database: dwh
  sourceConfig:
    config:
      type: DBT
      dbtConfigSource:
        dbtConfigType: local
        dbtCatalogFilePath: "/usr/app/dbt/clickhouse/target/catalog.json"
        dbtManifestFilePath: "/usr/app/dbt/clickhouse/target/manifest.json"
        dbtRunResultsFilePath: "/usr/app/dbt/clickhouse/target/run_results.json"
sink:
  type: metadata-rest
  config: {}
workflowConfig:
  loggerLevel: DEBUG
  openMetadataServerConfig:
    hostPort: "http://openmetadata:8585/api"
    authProvider: openmetadata
    securityConfig:
      jwtToken: "eyJhbGciOiJSUzI1NiIsImtpZCI6ImdiMzg5YS05Zjc2LWdkanMtYTkyai0wMjQyYms5NDM1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJsb2NhbGhvc3QiLCJzdWIiOiJhaXJmbG93IiwiYXVkIjoibG9jYWxob3N0IiwiZXhwIjoxNzc2ODk1NDcyLCJpYXQiOjE3NDA4OTkwNzJ9.UWN_Fq7NTo8r1xD6m-5QsCzysS60SGNcvJ7i5iFjvmtogahJtbJtuDqs7H_3UOu4wvbm3HLmwkqVmQiD6trDkV3KOfriGmD3LUjRSztTptRmKaRJN5F37PxtFEfxXXbNKJnCMEle0et9XN1_aBC7Tf0EVeVrfWHAzK8sc9FrMll0g1cO3aWE0gNtvtPhkK7Zj_SawxQFzle1RkFzmcbEiI1vvGExU2BEZOS7DD2FpZ5zDizNdb0_6LMBlsxaW8H8yEP6tTOkTSVc5qPH6AwIdgtCwXFJV0SuQR6yKASm5TBDDwLL9AeRCZIAG2tWL1oyvo2U3IqkQ2MqSvSPwf-PaQ"
"""

def postgres_ingestion_workflow():
    workflow_config = yaml.safe_load(dbt_postgres_config)
    workflow = MetadataWorkflow.create(workflow_config)
    workflow.execute()
    workflow.raise_from_status()
    workflow.print_status()
    workflow.stop()
    
def clickhouse_ingestion_workflow():
    workflow_config = yaml.safe_load(dbt_clickhouse_config)
    workflow = MetadataWorkflow.create(workflow_config)
    workflow.execute()
    workflow.raise_from_status()
    workflow.print_status()
    workflow.stop()

default_args = {
    'owner': 'airflow_admin',
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

with DAG(
        dag_id='fill_openmetadata_dag',
        default_args=default_args,
        schedule_interval=timedelta(minutes=1),
        catchup=False,
        max_active_runs=1
) as dag:
    
    generate_dbt_clickhouse_docs = BashOperator(
        task_id='generate_dbt_clickhouse_docs',
        bash_command="cd /usr/app/dbt/clickhouse && dbt docs generate",
        do_xcom_push=True
    )

    ingest_dbt_clickhouse_metadata = PythonOperator(
        task_id="ingest_dbt_clickhouse_metadata",
        python_callable=clickhouse_ingestion_workflow,
    )

    generate_dbt_postgres_docs = BashOperator(
        task_id='generate_dbt_postgres_docs',
        bash_command="cd /usr/app/dbt/postgres && dbt docs generate",
        do_xcom_push=True
    )

    ingest_dbt_postgres_metadata = PythonOperator(
        task_id="ingest_dbt_postgres_metadata",
        python_callable=postgres_ingestion_workflow,
    )

    generate_dbt_clickhouse_docs >> generate_dbt_postgres_docs >> [ingest_dbt_clickhouse_metadata, ingest_dbt_postgres_metadata]
