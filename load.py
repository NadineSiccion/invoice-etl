# %%
# import pandas as pd
import os
from pathlib import Path
from google.cloud import bigquery
# from pandas_gbq import to_gbq
from google.oauth2 import service_account
# import pandas_gbq

# Code for logging
import atexit
import json
import logging.config
import pathlib
def setup_logging():
    config_file = pathlib.Path("2-stderr-json-file.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


# Setup logging
logger = logging.getLogger(__name__)  # __name__ is a common choice
setup_logging()
logging.basicConfig(level="Running load.py...")

# Paths and resources
BASE_DIR = Path.cwd()
OUT_DIR = BASE_DIR / "out"

# Set ADC path dynamically in Python
key_path = BASE_DIR / 'gcp_credentials.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path.as_posix()

# Get latest timestamp
csv_files = os.listdir(OUT_DIR)
if ".gitignore"  in csv_files:
    csv_files.remove(".gitignore")
csv_files.sort()
for file in csv_files:
    print(file)
source_timestamp = csv_files[-1]
logger.info(f'👀 Latest CSV is {source_timestamp}')
print(f'👀 Latest CSV is {source_timestamp}')


# Set up Google BigQuery API Connection
credentials = service_account.Credentials.from_service_account_file(
    BASE_DIR/'gcp_credentials.json')
client = bigquery.Client()

project_id = "invoice-project-467712"
dataset_id = "invoice_dataset"
table_id = "dim_file"
# table_id = dataset_id+"."+destination_table
logger.info("Credentials set based on Private Key JSON.")
print("✅ Credentials set based on Private Key JSON.")


# Set up client and table (start with dim_file)
table_ref = client.dataset(dataset_id).table(table_id)

# Define Job Config 
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,  # Skip header row
    autodetect=True,
    schema = [
        bigquery.SchemaField("file_key", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("file_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("start_date", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("end_date", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("issue_date", "DATE")
    ],
    write_disposition=bigquery.WriteDisposition.WRITE_EMPTY,
)

# https://cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.client.Client#google_cloud_bigquery_client_Client_load_table_from_dataframe

# Identify target path of fact_transactions
source_name = source_timestamp + '_dim_file.csv'
RESULT_DIR = OUT_DIR / source_timestamp
source_path = RESULT_DIR / source_name

# Load from local csv
with open(source_path, "rb") as source_file:
    load_job = client.load_table_from_file(
        source_file,
        table_ref,
        job_config=job_config
    )

load_job.result()  # Wait for the job to complete

logger.info(f"✅ Table has been successfully loaded.")
print(f"✅ Table has been successfully loaded.")

