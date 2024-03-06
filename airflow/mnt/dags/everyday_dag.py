from airflow import DAG
from airflow.utils import timezone
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id = "everyday_dag",
    start_date = timezone.datetime(2024, 1, 30),
    schedule_interval = "0 0 * * *",
    tags = ["everyday"],
) as dag:

    task_1 = EmptyOperator(
        task_id = "task_1"
    )
    task_2 = EmptyOperator(
        task_id = "task_2"
    )
    
    task_1 >> task_2