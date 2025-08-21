#%%
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

# Code for Logging
import atexit
import json
import logging.config
import logging.handlers
import pathlib
import mylogger

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

logger.debug("debug message", extra={"x": "hello"})
logger.info("info message")
logger.warning("warning message")
logger.error("error message")
logger.critical("critical message")

#%% Paths
BASE_DIR = Path.cwd()
CSV_DIR = BASE_DIR / "csv"

# read latest CSV from the folder csv
csv_files = os.listdir(CSV_DIR)

if ".gitignore" in csv_files:
    csv_files.remove(".gitignore")
csv_files.sort()
for file in csv_files:
    print(file)

latest_csv = csv_files[-1]
print(f'Latest CSV is {latest_csv}')

# create df
df = pd.read_csv(CSV_DIR/latest_csv)
print(df.head())
print(df.tail())

# %% CLEANING

# # all the column names are fine
# add index-1 (since 0-base index already exists)
# df = df.reset_index() # turns index into a normal column

# Set up DESCRIPTION2 column
desc_2 = ['N/A']
desc_2[1:] = df['DESCRIPTION'][0:-1]
df = df.assign(DESCRIPTION2=desc_2)
print(df.head())
print(df.tail())



# Set up Category column
# Make new custom column called category based on Description and DESCRITPION2
def get_category(desc1, desc2):
    if "Coverage Period" in desc1 and "Jobs for" in desc2 :
        return "Jobs" 
    elif "SMS Messages Sent" in desc1 and "Initial 20 jobs are" in desc2 :
        return "SMS" 
    elif "Coverage Period" in desc1 and "SMS Messages Sent" in desc2 :
        return "Addon Forms" 
    elif "This amount will be debited from your Stripe" in desc1 and "ServiceM8 Stripe Application Fee" in desc2 :
        return "stripe"
    # in the future, add an elif for the following logic
    # not ([desc] = "" or [desc] = "stripe") then [desc] else "!Uncategorized")
category_s = pd.Series([get_category(desc1, desc2) for desc1, desc2 in zip(df["DESCRIPTION"], df["DESCRIPTION2"])])
df["CATEGORY"] = category_s
print(df.head())
print(df.tail())


# Set up primary key column
def get_primary_key(filename:str, category:str):
    return (str(filename)+str(category)).lower()
primary_s = pd.Series([get_primary_key(file, cat) for file, cat in zip(df['Source.Name'], df['CATEGORY'])])
df['PRIMARY'] = primary_s
print(df.head())
print(df.tail())

# Clean and export
df = df[df['UNIT PRICE'].notna() & df['CATEGORY'].notnull()]
df = df.drop(['DESCRIPTION', 'DESCRIPTION2'], axis=1)
df = df[['PRIMARY', 'Source.Name', 'CATEGORY', 'QTY', 'UNIT PRICE', 'PRICE (AUD)']]
print(df.head())
print(df.tail())

outname = datetime.now().strftime(r'%Y%M%d%H%M%S') + '_transformed.csv'
df.to_csv(BASE_DIR / 'out' / outname, index=False)


# In column DESCRIPTION, apply Str.replace("Coverage Period", "Coverage Period +") so you can split by plus sign
# Split DESCRIPTION by plus "+" sign and name the new column "Coverage from".
# Split "Coverage from" by " to " and name the new column "Coverage to"
# Replace all 3 letter month abbreviation to its 2-digit numerica value (Feb -> 02)
# Make a new filename column which will allow you to alphebatize the list in chronological order







# %%
# DEBUGGING CODE
# df = df.assign(index1=df['index']+1)


# %%
print(df.head())
print(df.tail())
