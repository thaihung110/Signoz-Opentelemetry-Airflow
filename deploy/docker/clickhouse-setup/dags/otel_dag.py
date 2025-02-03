import random
import time
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def simulate_api_call():
    """Simulate an API call with random latency"""
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("api_call") as span:
        try:
            # Add custom attributes to the span
            span.set_attribute("service.name", "external_api")

            # Simulate API latency
            latency = random.uniform(0.1, 2.0)
            time.sleep(latency)

            # Add latency as a span attribute
            span.set_attribute("latency_seconds", latency)

            # Simulate API response
            response = {
                "status": "success",
                "latency": latency,
                "timestamp": datetime.now().isoformat(),
            }

            # Set span status to success
            span.set_status(Status(StatusCode.OK))

            return response

        except Exception as e:
            # Set span status to error and record the exception
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


def process_data():
    """Process some data with custom metrics"""
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("data_processing") as span:
        try:
            # Add custom attributes
            span.set_attribute("processor.name", "data_processor")

            # Simulate data processing
            processed_items = random.randint(100, 1000)
            processing_time = random.uniform(0.5, 3.0)
            time.sleep(processing_time)

            # Add processing metrics as span attributes
            span.set_attribute("processed_items", processed_items)
            span.set_attribute("processing_time", processing_time)

            return {
                "processed_items": processed_items,
                "processing_time": processing_time,
            }

        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


def database_operation():
    """Simulate database operations"""
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("database_operation") as span:
        try:
            # Add database-specific attributes
            span.set_attribute("db.system", "postgresql")
            span.set_attribute("db.operation", "query")

            # Simulate database query time
            query_time = random.uniform(0.2, 1.5)
            time.sleep(query_time)

            # Add query metrics
            span.set_attribute("db.query_time", query_time)

            return {"status": "success", "query_time": query_time}

        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


with DAG(
    "test_opentelemetry",
    default_args=default_args,
    description="Test OpenTelemetry Integration with Signoz",
    schedule_interval=timedelta(minutes=2),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["test", "opentelemetry", "monitoring"],
) as dag:

    # Start the workflow
    start = BashOperator(
        task_id="start",
        bash_command='echo "Starting OpenTelemetry test workflow"',
    )

    # Simulate API call
    api_task = PythonOperator(
        task_id="api_call",
        python_callable=simulate_api_call,
    )

    # Process data
    process_task = PythonOperator(
        task_id="process_data",
        python_callable=process_data,
    )

    # Database operation
    db_task = PythonOperator(
        task_id="database_operation",
        python_callable=database_operation,
    )

    # End the workflow
    end = BashOperator(
        task_id="end",
        bash_command='echo "Completed OpenTelemetry test workflow"',
    )

    # Define task dependencies
    start >> api_task >> process_task >> db_task >> end
