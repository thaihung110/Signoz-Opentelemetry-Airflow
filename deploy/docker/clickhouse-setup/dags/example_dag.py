import random
from datetime import timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago


# Function to simulate API data loading
def load_data(**kwargs):
    data = random.randint(1, 100)  # Simulate random data
    kwargs["ti"].xcom_push(key="data", value=data)
    print(f"Loaded data: {data}")


# Function to process data
def process_data(**kwargs):
    data = kwargs["ti"].xcom_pull(key="data", task_ids="load_data_task")
    print(f"Processing data: {data}")
    return data


# Function to decide branch based on data
def decide_branch(**kwargs):
    data = kwargs["ti"].xcom_pull(key="data", task_ids="load_data_task")
    if data % 2 == 0:
        return "even_branch_task"
    else:
        return "odd_branch_task"


# Function for even branch
def even_branch(**kwargs):
    print("Data is even. Executing even branch tasks.")


# Function for odd branch
def odd_branch(**kwargs):
    print("Data is odd. Executing odd branch tasks.")


# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

# Define the DAG
dag = DAG(
    "sample_dag",
    default_args=default_args,
    description="A complex DAG example",
    schedule_interval=timedelta(minutes=2),
    start_date=days_ago(1),
    catchup=False,
)

# Task 1: Load data
load_data_task = PythonOperator(
    task_id="load_data_task",
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

# Task 2: Process data
process_data_task = PythonOperator(
    task_id="process_data_task",
    python_callable=process_data,
    provide_context=True,
    dag=dag,
)

# Task 3: Decide branch
decide_branch_task = BranchPythonOperator(
    task_id="decide_branch_task",
    python_callable=decide_branch,
    provide_context=True,
    dag=dag,
)

# Task 4a: Even branch
even_branch_task = PythonOperator(
    task_id="even_branch_task",
    python_callable=even_branch,
    provide_context=True,
    dag=dag,
)

# Task 4b: Odd branch
odd_branch_task = PythonOperator(
    task_id="odd_branch_task",
    python_callable=odd_branch,
    provide_context=True,
    dag=dag,
)

# Task 5: Trigger another DAG
trigger_other_dag_task = TriggerDagRunOperator(
    task_id="trigger_other_dag_task",
    trigger_dag_id="another_dag",  # Replace with the actual DAG ID to trigger
    dag=dag,
)

# Define the task pipeline
load_data_task >> process_data_task >> decide_branch_task

decide_branch_task >> even_branch_task >> trigger_other_dag_task

decide_branch_task >> odd_branch_task >> trigger_other_dag_task
