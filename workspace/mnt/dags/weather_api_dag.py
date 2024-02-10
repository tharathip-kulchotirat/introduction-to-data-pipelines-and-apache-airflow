from airflow import DAG
from airflow.utils import timezone
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable

def _get_weather_data():
    # เอา import ไว้ใน function เพราะว่ามันจะมี Process ของ Airflow ที่จะอ่าน script นี้ตลอดเวลา แปลว่ามันจะมีการ import ไปทำซ้ำๆ ตลอดเวลา ทำให้เกิดปัญหาเรื่อง memory ขึ้นมา ดังนั้นเราจึงเอาไว้ใน function แทน
    import requests
    from uuid import uuid4
    import json
    import datetime
    
    # Get API Key from Variable
    api_key = Variable.get("weather_key")
    # Get data from Weather API
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Bangkok&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    print(data)
    
    # Write data to file
    now = datetime.datetime.now()
    with open(f"weather_{now}.json", "w") as f:
        json.dump(data, f)
    
    
    # Prepare credentials and configuration for JSONBin API
    x_master_key = Variable.get("x_master_key")
    x_collection_id = Variable.get("x_collection_id")
    api_url = "https://api.jsonbin.io/v3/b"
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": x_master_key,
        "X-Collection-Id": x_collection_id,
        "X-Bin-Name": f"weather_{uuid4()}",
    }
    
    # Read data from file
    with open(f"weather_{now}.json", "r") as f:
        data = json.load(f)
    
    # Upload data to JSONBin API
    response = requests.post(api_url, json=data, headers=headers)
    print(response.json())

with DAG(
    dag_id = "weather_api_dag",
    start_date = timezone.datetime(2024, 2, 3),
    schedule = "@hourly",
    catchup = False,
) as dag:

    start = EmptyOperator(
        task_id = "start"
    )
    
    get_weather_data = PythonOperator(
        task_id = "get_weather_data",
        python_callable = _get_weather_data,
    )
    
    end = EmptyOperator(
        task_id = "end"
    )
    
    start >> get_weather_data >> end