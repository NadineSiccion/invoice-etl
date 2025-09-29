# %%
# import pandas as pd
import os
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account

# Code for logging
import atexit
import json
import logging.config
from configs import mylogger

def setup_logging(config_file):
    config_file = config_file
    with open(config_file) as f_in:
        config = json.load(f_in)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


# Paths and resources
BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "output"
CONFIG_DIR = BASE_DIR / "scripts" / "configs"
LOG_CONFIG_FILE = CONFIG_DIR / "log_config.json"
KEY_PATH = CONFIG_DIR / "gcp_credentials.json"

# Setup logging
logger = logging.getLogger(__name__)  # __name__ is a common choice
setup_logging(LOG_CONFIG_FILE)
logging.basicConfig(level="Running load.py...")

# Set ADC path dynamically in Python
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH.as_posix()

# Get latest timestamp
dirs = OUT_DIR.iterdir()
dir_names = []
print(f"The directories found:")
for dir in dirs:
    if (dir.is_dir()) and not (dir.name == ".gitignore"):
        print(f'{dir.name}')
        dir_names.append(dir.name)
dir_names.sort()
source_timestamp = dir_names[-1]
logger.info(f'👀 Latest CSV is {source_timestamp}')
print(f'👀 Latest CSV is {source_timestamp}')



# if ".gitignore"  in csv_files:
#     csv_files.remove(".gitignore")
# csv_files.sort()
# for file in csv_files:
#     print(file)

# Set up Google BigQuery API Connection
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = bigquery.Client()

def load_to_gbq(target:str, table_schema) -> None:
    dataset_id = "invoice_dataset"
    table_id = target
    logger.info("Credentials set based on Private Key JSON.")
    print("✅ Credentials set based on Private Key JSON.")

    # Set up client and table (start with dim_file)
    table_ref = client.dataset(dataset_id).table(table_id)

    # Define Job Config 
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # Skip header row
        autodetect=True,
        schema = table_schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    # https://cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.client.Client#google_cloud_bigquery_client_Client_load_table_from_dataframe

    # Identify target path of fact_transactions
    source_name = source_timestamp + '_' + target + '.csv'
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

    logger.info(f"✅ Table {target} has been successfully loaded.")
    print(f"✅ Table {target} has been successfully loaded.")


# load dim_file
schema = [
    bigquery.SchemaField("file_key", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("file_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("start_date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("end_date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("issue_date", "DATE")
]
load_to_gbq("dim_file", schema)

# load fact_transactions
schema = [
    bigquery.SchemaField("transaction_key", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("file_key", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("category_key", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("quantity", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("unit_price", "FLOAT", mode="REQUIRED"),
    bigquery.SchemaField("total_price_aud", "FLOAT", mode="REQUIRED")
]
load_to_gbq("fact_transactions", schema)


# load dim_category
schema = [
    bigquery.SchemaField("category_key", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("category_name", "STRING", mode="REQUIRED")
]
load_to_gbq("dim_category", schema)