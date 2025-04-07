from __future__ import annotations
import pendulum
from datetime import timedelta
from airflow.models.dag import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

TARGET_CONTAINER_NAME = "spark-server"
SPARK_COMMAND = "./spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2 ./kafkaToDelta.py"
DOCKER_HOST_URL = "tcp://docker-proxy:2375"

VARIABLE_NAME='task_a_completed_status'
VARIABLE_VALUE_SUCCESS='true'

with DAG(
    dag_id='sparkStreaming_dag',
    schedule='@once',
    start_date=pendulum.datetime(2025, 1, 1, tz='Asia/Ho_Chi_Minh'),
    catchup=False,
    default_args=default_args,
    tags=['setup', 'bash'],
    description='DAG run one-time task to run spark streaming job to read data from Kafka topic.'
) as dag:
    spark_streaming_task = BashOperator(
        task_id="pyspark_consumer",
        bash_command=f"""docker exec {TARGET_CONTAINER_NAME} {SPARK_COMMAND} && \
                echo "spark-submit completed." 
        """,
        env={
            'DOCKER_HOST':DOCKER_HOST_URL
        },
        append_env=True,
        dag=dag,
    )

