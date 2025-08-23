# %%
import pandas as pd
import os
from pathlib import Path
# from google.cloud import bigquery
# from pandas_gbq import to_gbq
from google.oauth2 import service_account
import pandas_gbq


# Code for logging
import atexit
import json
import logging.config
import pathlib

logger = logging.getLogger(__name__)  # __name__ is a common choice
def setup_logging():
    config_file = pathlib.Path("2-stderr-json-file.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)

setup_logging()
logging.basicConfig(level="INFO")


# Load most recent out as a DataFrame
BASE_DIR = Path.cwd()
OUT_DIR = BASE_DIR / "out"

csv_files = os.listdir(OUT_DIR)
if ".gitignore" in csv_files:
    csv_files.remove(".gitignore")
csv_files.sort()
for file in csv_files:
    print(file)
latest_csv = csv_files[-1]
logger.info(f'Latest CSV is {latest_csv}')

df = pd.read_csv(OUT_DIR/latest_csv)
print(df.head())
print(df.tail())


# Set up BigQuery
# bigquery_client = bigquery.Client()
credentials = service_account.Credentials.from_service_account_file(
    BASE_DIR/'invoice-project-467712-privatekey.json')
logger.info("Credentials set based on Private Key JSON.")

project_id = "invoice-project-467712"
dataset_id = "invoice_dataset"
destination_table = "invoice_table"

table_id = dataset_id+"."+destination_table

pandas_gbq.to_gbq(df, table_id, project_id=project_id, if_exists='replace', credentials=credentials)
logger.info(f"Table has been successfully loaded into {project_id+"."+dataset_id+"."+table_id}.")
print(f"Table has been successfully loaded into {project_id+"."+dataset_id+"."+table_id}.")

# df = pandas_gbq.read_gbq(sql, project_id="YOUR-PROJECT-ID", credentials=credentials)