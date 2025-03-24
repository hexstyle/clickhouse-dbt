"""
This file has been generated from dag_runner.j2
"""
from airflow import DAG
from openmetadata_managed_apis.workflows import workflow_factory

workflow = workflow_factory.WorkflowFactory.create("/opt/airflow/dag_generated_configs/be97d0ad-666e-4189-81fd-c8a4bbfa4da6.json")
workflow.generate_dag(globals())
dag = workflow.get_dag()