from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
import json
import requests
from datetime import timedelta, datetime

# S3 buckets
raw_bucket = "dhrsrapidapi"   # where raw JSON goes
s3_bucket = "cleaned-data-zone-csv-bucket-dhrs"  # cleaned zone bucket

# RapidAPI headers
headers = {
    "x-rapidapi-key": "76554e94d6msh27d9e9a6c0e3ec5p18478cjsn464f74f73eb6",
    "x-rapidapi-host": "zillow-com4.p.rapidapi.com"
}

def extract_zillow_data(**kwargs):
    url = kwargs['url']
    headers = kwargs['headers']
    querystring = kwargs['querystring']
    execution_timestamp = kwargs['ts_nodash']

    # Call API
    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()
    response_data = response.json()

    # Save raw JSON locally
    output_file_path = f"/home/ubuntu/response_data_{execution_timestamp}.json"
    cleaned_filename = f"response_data_{execution_timestamp}.csv"  # expected cleaned file

    with open(output_file_path, "w") as output_file:
        json.dump(response_data, output_file, indent=4)

    # Return raw file path + expected cleaned file name
    return [output_file_path, cleaned_filename]

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['rauhlsiddharthdh@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=15)
}

with DAG(
    dag_id='zillow_analytics_dag',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='@daily',   # ✅ FIXED
    catchup=False,
) as dag:

    # 1. Extract Zillow data
    extract_zillow_data_var = PythonOperator(
        task_id='tsk_extract_zillow_data',
        python_callable=extract_zillow_data,
        op_kwargs={
            'url': 'https://zillow-com4.p.rapidapi.com/properties/search-coordinates',
            'querystring': {
                "location": "Houston, TX", "eastLng": "-94.517205", "westLng": "-96.193233",
                "southLat": "29.170258", "northLat": "29.657524", "status": "forSale",
                "sort": "relevance", "sortType": "asc", "priceType": "listPrice", "listingType": "agent"
            },
            'headers': headers
        }
    )

    # 2. Load raw JSON to raw bucket
    load_to_s3 = BashOperator(
        task_id='tsk_load_to_s3',
        bash_command='aws s3 mv {{ ti.xcom_pull(task_ids="tsk_extract_zillow_data")[0] }} s3://'
                     + raw_bucket + '/',
    )

    # 3. Wait for cleaned CSV in cleaned-data-zone
    is_file_in_s3_available = S3KeySensor(
        task_id='tsk_is_file_in_s3_available',
        bucket_key='{{ ti.xcom_pull(task_ids="tsk_extract_zillow_data")[1] }}',
        bucket_name=s3_bucket,
        aws_conn_id='aws_s3_conn',
        wildcard_match=False,
        timeout=60*60*6,   # 6 hours
        poke_interval=300  # every 5 min
    )

    # 4. Load into Redshift
    transfer_s3_to_redshift = S3ToRedshiftOperator(
        task_id="tsk_transfer_s3_to_redshift",
        aws_conn_id='aws_s3_conn',
        redshift_conn_id='conn_id_redshift',
        s3_bucket=s3_bucket,
        s3_key='{{ ti.xcom_pull(task_ids="tsk_extract_zillow_data")[1] }}',   # ✅ FIXED
        schema="PUBLIC",
        table="zillowdata",
        copy_options=[
            "CSV",
            "IGNOREHEADER 1",
            "TRUNCATECOLUMNS",
            "BLANKSASNULL",
            "EMPTYASNULL",
            "TIMEFORMAT 'auto'",
            "ACCEPTINVCHARS"
        ],
    )

    extract_zillow_data_var >> load_to_s3 >> is_file_in_s3_available >> transfer_s3_to_redshift
