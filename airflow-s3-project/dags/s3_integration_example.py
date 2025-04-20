from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import (
    S3CreateBucketOperator,
    S3DeleteBucketOperator,
)
from airflow.providers.amazon.aws.transfers.local_to_s3 import (
    LocalFilesystemToS3Operator,
)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 10, 6),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "s3_integration_example",
    default_args=default_args,
    description="A simple DAG to demonstrate S3 integration",
    schedule=timedelta(days=1),
)

create_bucket = S3CreateBucketOperator(
    task_id="create_bucket",
    bucket_name="my-airflow-bucket-{}".format(datetime.now().strftime("%Y%m%d%H%M%S")),
    region_name="ap-southeast-1",
    aws_conn_id="aws_default",
    dag=dag,
)

upload_file = LocalFilesystemToS3Operator(
    task_id="upload_file",
    filename="/home/fahad/AWS/local_Files.txt",
    dest_key="local_file.txt",
    dest_bucket='{{ task_instance.xcom_pull(task_ids="create_bucket") }}',
    aws_conn_id="aws_default",
    dag=dag,
)

# delete_bucket = S3DeleteBucketOperator(
#     task_id="delete_bucket",
#     bucket_name='{{ task_instance.xcom_pull(task_ids="create_bucket") }}',
#     force_delete=True,
#     aws_conn_id="aws_default",
#     dag=dag,
# )

create_bucket >> upload_file 
