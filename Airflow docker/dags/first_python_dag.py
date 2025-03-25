from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {"owner": "Fahad", "retries": 5, "retry_delay": timedelta(minutes=5)}


# def greet(name, age):
#     print(f"Hello world! My name is {name}, " f"I am {age} years old. ")


def greet(ti, age):  # ti -> task instance
    name = ti.xcom_pull(task_ids="get_name")
    print(f"Hello world! My name is {name}, " f"I am {age} years old. ")


def get_name():
    return "Ahmed Fahad"


with DAG(
    default_args=default_args,
    dag_id="First_dag_with_python_operator_v02",
    description="first dag creation with python operator",
    start_date=datetime(2024, 10, 12, 4),
    schedule="@daily",
) as dag:
    task1 = PythonOperator(
        task_id="greet",
        python_callable=greet,
        op_kwargs={"name ": "Ahmed Fahad", "age": 20},
    )
    task2 = PythonOperator(task_id="get_name", python_callable=get_name)
    task2 >> task1
