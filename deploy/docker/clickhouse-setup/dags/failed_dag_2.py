from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


def fail_task():
    raise Exception("This task is designed to fail.")


default_args = {
    "owner": "airflow",
    "retries": 0,  # No retries to avoid automatic retrying of the task
    "start_date": datetime(2025, 2, 4),
}

with DAG(
    dag_id="failed_task_dag_2",
    default_args=default_args,
    schedule_interval=timedelta(
        minutes=2
    ),  # This will run only when triggered manually
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id="fail_task",
        python_callable=fail_task,
    )
