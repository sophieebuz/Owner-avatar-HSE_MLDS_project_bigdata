import sys
sys.path.append("/opt/hadoop/airflow/dags/bol_theater/HSE_MLDS_project_bigdata")

from airflow.operators.python_operator import PythonOperator
from airflow.decorators import task
from airflow.models import DAG
from configs.airflow_args import airflow_args
from configs.constants import parsing_url
from configs.parquet_paths import parquet_paths
from configs.db_params import db_params
from parsing.load_data import load_performances, mock_load_performances
from processing.create_notifications_parquet import create_notifications_parquet
from processing.create_performances_parquet import create_performances_parquet
from processing.upload_data_to_mysql import upload_data_to_mysql
from telegram.send_push_message import send_push_messages


with DAG(
    dag_id="bolshoi_theater",
    catchup=False,
    default_args=airflow_args
) as dag:
    @task(task_id="load_data")
    def load_data(**kwargs):
        # не забыть удалить
        mock_load_performances(parsing_url, parquet_paths['parsing'])


    @task(task_id="process_data")
    def process_data(**kwargs):
        create_performances_parquet(parquet_paths)
        create_notifications_parquet(parquet_paths, db_params)


    @task(task_id="upload_data_to_database")
    def upload_data_to_database(**kwargs):
        upload_data_to_mysql(parquet_paths['performances'], db_params, 'bth_performances')
        upload_data_to_mysql(parquet_paths['notifications'], db_params, 'bth_notifications')
    
    # @task(task_id="send_push_message")
    # def send_push_message(**kwargs):
    #     send_push_messages()

    


    load_data() >> process_data() >> upload_data_to_database() 
    #>> send_push_message()
