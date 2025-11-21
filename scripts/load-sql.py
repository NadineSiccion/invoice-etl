import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import logging.config
from configs import setuplogging

# Paths and resources
BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "output"
CONFIG_DIR = BASE_DIR / "scripts" / "configs"
LOG_CONFIG_FILE = CONFIG_DIR / "log_config.json"
# KEY_PATH = CONFIG_DIR / "gcp_credentials.json"

# Setup logging
logger = logging.getLogger(__name__)  # __name__ is a common choice
setuplogging.setup_logging(LOG_CONFIG_FILE)
logging.basicConfig(level="Running load.py...")

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

SOURCE_DIR = OUT_DIR / source_timestamp

# Connect to SQLite
# Output will be loaded to a .db file in the Project directory
engine = create_engine("sqlite:///warehouse.db", echo=True)

# Load CSVs into DataFrames
filename = source_timestamp + "_fact_transactions.csv"
fact_transaction = pd.read_csv(SOURCE_DIR / filename)

filename = source_timestamp + "_dim_file.csv"
dim_file = pd.read_csv(SOURCE_DIR / filename)

filename = source_timestamp + "_dim_category.csv"
dim_category = pd.read_csv(SOURCE_DIR / filename)

# Write DataFrames to SQL tables
fact_transaction.to_sql("fact_transaction", engine, if_exists="replace", index=False)
dim_file.to_sql("dim_file", engine, if_exists="replace", index=False)
dim_category.to_sql("dim_category", engine, if_exists="replace", index=False)
print("All DataFrames loaded into warehouse.db")