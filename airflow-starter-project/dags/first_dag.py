from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {"owner": "Fahad", "retries": 5, "retry_delay": timedelta(minutes=2)}

with DAG(
    dag_id="Our_first_dag",
    default_args=default_args,
    description="This is our first dag that we write",
    start_date=datetime(2024, 10, 12, 2),
    schedule="@daily",
) as dag:
    task1 = BashOperator(
        task_id="first_task", bash_command="hello world, this is the first task"
    )
    task2 = BashOperator(
        task_id="second_task",
        bash_command="I'm the second task and I'll be running after the first task",
    )
    task1.set_downstream(task2)
