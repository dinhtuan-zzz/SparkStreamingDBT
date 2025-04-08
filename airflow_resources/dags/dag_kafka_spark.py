from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from src.api_data_collector import stream


start_date = datetime.today() - timedelta(days=1)

default_args = {
    "owner": "airflow",
    "start_date": start_date,
    "retries": 1,  # number of retries before failing the task
    "retry_delay": timedelta(seconds=5),
}


with DAG(
    dag_id="kafka_spark_dag",
    default_args=default_args,
    schedule="*/10 * * * *",
    catchup=False,
    tags=['setup', 'python'],
    description='DAG run python file which fetch data from API to Kafka topic.'
) as dag:

    kafka_stream_task = PythonOperator(
        task_id="kafka_data_stream",
        python_callable=stream,
        dag=dag,
    )
    
