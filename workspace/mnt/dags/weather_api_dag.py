from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils import timezone

import requests
import json


def _get_weather_data(**context):
    # API_KEY = os.environ.get("WEATHER_API_KEY")
    API_KEY = Variable.get("weather_key")

    name = Variable.get("name")
    print(f"Hello, {name}")

    print(context)
    print(context["execution_date"])
    ds = context["ds"]
    print(ds)

    payload = {
        "q": "bangkok",
        "appid": API_KEY,
        "units": "metric"
    }
    url = f"https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(url, params=payload)
    print(response.url)

    data = response.json()
    print(data)

    timestamp = context["execution_date"]
    with open(f"/opt/airflow/dags/weather_data_{timestamp}.json", "w") as f:
        json.dump(data, f)

    return f"/opt/airflow/dags/weather_data_{timestamp}.json"


def _load_data_to_postgres(**context):
    ti = context["ti"]
    file_name = ti.xcom_pull(task_ids="get_weather_data", key="return_value")
    print(file_name)

    pg_hook = PostgresHook(
        postgres_conn_id="my_postgres_conn",
        schema="postgres"
    )
    connection = pg_hook.get_conn()
    cursor = connection.cursor()

    sql = """
        CREATE TABLE IF NOT EXISTS weathers (
            temp FLOAT NOT NULL
        )
    """
    cursor.execute(sql)
    connection.commit()

    sql = """
        INSERT INTO weathers (temp) VALUES (31.39)
    """
    cursor.execute(sql)
    connection.commit()


default_args = {
    "email": ["kuang.acad@gmail.com"],
    # "retries": 1,
}
with DAG(
    "weather_api_dag",
    default_args=default_args,
    schedule="@hourly",
    start_date=timezone.datetime(2024, 2, 3),
    catchup=False,
):
    start = EmptyOperator(task_id="start")

    get_weather_data = PythonOperator(
        task_id="get_weather_data",
        python_callable=_get_weather_data,
    )

    load_data_to_postgres = PythonOperator(
        task_id="load_data_to_postgres",
        python_callable=_load_data_to_postgres,
    )

    end = EmptyOperator(task_id="end")

    start >> get_weather_data >> load_data_to_postgres >> end