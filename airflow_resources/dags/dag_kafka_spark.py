from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

from src.api_data_collector import stream


start_date = datetime.today() - timedelta(days=1)
TARGET_CONTAINER_NAME = "spark-server"
SPARK_COMMAND = "./spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2 ./kafkaToDelta.py"
DOCKER_HOST_URL = "tcp://docker-proxy:2375"

default_args = {
    "owner": "airflow",
    "start_date": start_date,
    "retries": 1,  # number of retries before failing the task
    "retry_delay": timedelta(seconds=5),
}


with DAG(
    dag_id="kafka_spark_dag",
    default_args=default_args,
    schedule_interval="*/10 * * * *",
    catchup=False,
) as dag:

    kafka_stream_task = PythonOperator(
        task_id="kafka_data_stream",
        python_callable=stream,
        dag=dag,
    )
    
    spark_stream_task = BashOperator(
        task_id="pyspark_consumer",
        bash_command=f"docker exec {TARGET_CONTAINER_NAME} {SPARK_COMMAND}",
        env={
            'DOCKER_HOST':DOCKER_HOST_URL
        },
        append_env=True,
        dag=dag,
    ) 


    kafka_stream_task >> spark_stream_task
