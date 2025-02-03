from datetime import timedelta

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import (
    BranchPythonOperator,
    PythonOperator,
)
from airflow.operators.subdag_operator import SubDagOperator
from airflow.utils.dates import days_ago


def choose_branch(**kwargs):
    # Logic to choose branch
    if kwargs["execution_date"].day % 2 == 0:
        return "even_day_task"
    else:
        return "odd_day_task"


def print_hello():
    print("Hello World")


def subdag(parent_dag_name, child_dag_name, args):
    dag_subdag = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        schedule_interval="@daily",
        start_date=args["start_date"],  # Add start_date here
    )

    with dag_subdag:
        task1 = DummyOperator(task_id="subdag_task1")
        task2 = DummyOperator(task_id="subdag_task2")

        task1 >> task2

    return dag_subdag


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": days_ago(2),  # Add start_date here
}

dag = DAG(
    "complex_dag",
    default_args=default_args,
    description="A complex DAG example",
    schedule_interval=timedelta(minutes=3),
    start_date=days_ago(2),
    tags=["example"],
)

start = DummyOperator(task_id="start", dag=dag)

branching = BranchPythonOperator(
    task_id="branching",
    python_callable=choose_branch,
    provide_context=True,
    dag=dag,
)

even_day_task = DummyOperator(task_id="even_day_task", dag=dag)
odd_day_task = DummyOperator(task_id="odd_day_task", dag=dag)

subdag_task = SubDagOperator(
    task_id="subdag_task",
    subdag=subdag("complex_dag", "subdag_task", default_args),
    dag=dag,
)

end = DummyOperator(task_id="end", dag=dag)

start >> branching
branching >> [even_day_task, odd_day_task]
even_day_task >> subdag_task
odd_day_task >> subdag_task
subdag_task >> end
