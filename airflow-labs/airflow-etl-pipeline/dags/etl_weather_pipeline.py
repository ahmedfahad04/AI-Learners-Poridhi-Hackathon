from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.decorators import task
from airflow.utils.dates import days_ago
import requests
import json

#Latitude and longitude for the desired location (London in this case)
LATITUDE= '52.52'
LONGITUDE= '13.41'
POSTGRES_CONN_ID= 'postgres_default'
API_CONN_ID= 'open_meteo_api'

default_args= {
    'owner': 'airflow',
    'start_date': days_ago(1)
}

def extract_weatherdata():
        """Extract weather data from Open meteo api using airflow connection"""

        #Use http hook to get connection details from airflow connection
        http_hook= HttpHook(http_conn_id=API_CONN_ID, method='GET')

        ##Build api endpoint
        ## https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current_weather=true
        endpoint= f'/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true'

        #Make the request via httphook
        response= http_hook.run(endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}")
        
    
def transform_weatherdata(weather_data):
        """Transform the extracted weather data"""
        current_weather= weather_data['current_weather']
        transformed_data={
            'latitude' : float(LATITUDE),
            'longitude': float(LONGITUDE),
            "temperature": current_weather['temperature'],
            'windspeed': current_weather['windspeed'],
            'winddirection': current_weather['winddirection'],
            'weathercode': current_weather['weathercode'],

        }
        return transformed_data
    
    
def load_weatherdata(transformed_data):
        """Load transformed data to postgres"""

        pg_hook= PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn= pg_hook.get_conn()
        cursor= conn.cursor()

        #create table if it doesn't exist
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS weather_data (
            latitude FLOAT,
            longitude FLOAT,
            temperature INT,
            windspeed INT,
            winddirection INT,
            weathercode INT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );"""
        )

        #Insert transformed data into the table
        cursor.execute(
            """INSERT INTO weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                transformed_data['latitude'],
                transformed_data['longitude'],
                transformed_data['temperature'],
                transformed_data['windspeed'],
                transformed_data['winddirection'],
                transformed_data['weathercode'],
            )
        )
        conn.commit()
        cursor.close()
        conn.close()


with DAG(dag_id='etl_weather_pipeline',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False
        ) as dag:
        
        extract_task= PythonOperator(
               task_id='extract_weather',
               python_callable=extract_weatherdata
        )

        transform_task= PythonOperator(
               task_id='transform_weatherdata',
               python_callable=transform_weatherdata,
               op_args=[extract_task.output]
        )

        load_task= PythonOperator(
               task_id='load_weatherdata',
               python_callable=load_weatherdata,
               op_args=[transform_task.output]
        )
        
        #DAG workflow
        
        extract_task >> transform_task >> load_task