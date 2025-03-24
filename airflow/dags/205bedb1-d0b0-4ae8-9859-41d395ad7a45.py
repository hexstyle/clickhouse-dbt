"""
This file has been generated from dag_runner.j2
"""
from airflow import DAG
from openmetadata_managed_apis.workflows import workflow_factory

workflow = workflow_factory.WorkflowFactory.create("/opt/airflow/dag_generated_configs/205bedb1-d0b0-4ae8-9859-41d395ad7a45.json")
workflow.generate_dag(globals())
dag = workflow.get_dag()