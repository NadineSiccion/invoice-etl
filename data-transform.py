#%%
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import re

# Code for Logging 
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

''' 
logger.debug("debug message", extra={"x": "hello"})
logger.info("info message")
logger.warning("warning message")
logger.error("error message")
logger.critical("critical message")
'''
month_substrings = {
    'jan': '01',
    'feb': '02',
    'mar': '03',
    'apr': '04',
    'may': '05',
    'jun': '06',
    'jul': '07',
    'aug': '08',
    'sep': '09',
    'oct': '10',
    'nov': '11',
    'dec': '12'
}

# Create DataFrame out of the latest CSV
def get_latest_csv_path(csv_dir) -> str:
    csv_files = os.listdir(csv_dir)
    if ".gitignore" in csv_files:
        csv_files.remove(".gitignore")
    csv_files.sort()
    for file in csv_files:
        print(file)
    return csv_files[-1]

# Helper Functions
def change_month_to_number(name) -> str:
    for substr, num in month_substrings.items():
        if substr in name:
            name = name.replace(substr, num, 1)  # Replace only the first occurrence
    return name

# Processes the date arrays extracted from the extract_start_end_dates function
def turn_date_arr_to_date(date_arr:list[str]) -> datetime.date:
    out = []
    # Day
    pattern = r"\D+"  # \D matches any non-digit character
    match = re.search(pattern, date_arr[0])
    if match:
        # print(match.group())
        out = [date_arr[0].replace(match.group(0), "").zfill(2)]
    elif len(date_arr[0]) == 2:
        out.append(date_arr[0])
    else:
        raise Exception("Issue in day input for turn_date_arr_to_date.") 
    
    # Month
    if len(date_arr[1]) == 2:
        out.append(date_arr[1])
    else:
        for month_sub in list(month_substrings.keys()):
            if month_sub in date_arr[1].lower():
                out.append(str(month_substrings[month_sub]).zfill(2))
    
    # Year
    out.append(date_arr[2])
    
    # Convert to datetime
    output = datetime(int(out[2]), int(out[1]), int(out[0])).date()
    # print('Extracted date:', output)
    return output

def get_new_filename(source_name, month_map):
    str_arr = source_name[:-4].split("-")
    str_arr[1] = month_map[str_arr[1][0:2]]
    new_name = str_arr[2]+str_arr[1]+str_arr[0]
    return new_name

def get_transaction_key_key(source_name:str, category:str):
    name = str(source_name).lower().replace('.pdf', '').replace('-','')
    name = change_month_to_number(name)
    return (name + str(category)).lower()

# Set up Category column
def get_category(desc1:str, desc2:str) -> str:
    if "Coverage Period" in desc1 and "Jobs for" in desc2 :
        return "jobs" 
    elif "SMS Messages Sent" in desc1 and "Initial 20 jobs are" in desc2 :
        return "sms" 
    elif "Coverage Period" in desc1 and "SMS Messages Sent" in desc2 :
        return "addon_forms" 
    elif "This amount will be debited from your Stripe" in desc1 and "ServiceM8 Stripe Application Fee" in desc2 :
        return "stripe"
    else:
        return "uncategorized"
    # in the future, add an elif for the following logic
    # not ([desc] = "" or [desc] = "stripe") then [desc] else "!Uncategorized")

def make_file_key_list(filenames) -> list:
    output = [change_month_to_number(filename.lower().replace('.pdf', '')) 
              for filename in filenames]
    return output

# Dimension Table functions
def extract_issue_date_from_file_key(string:str) -> datetime:
    arr = string.split("-")
    output = datetime(int(arr[2]), int(arr[1]), int(arr[0])).date()
    return output

def extract_start_end_dates(desc_col, file_name_col) -> dict:
    out_dict = {'start_dates': [], 'end_dates': []}

    for desc in desc_col:
        if 'Coverage Period' in desc:
            temp = desc.split(' ')
            start_date = temp[2:5]
            end_date = temp[6:9]
            out_dict['start_dates'].append(turn_date_arr_to_date(start_date))        
            out_dict['end_dates'].append(turn_date_arr_to_date(end_date))
        else:
            out_dict['start_dates'].append(None)        
            out_dict['end_dates'].append(None)
    
    return out_dict


def make_dim_file(
    df:pd.DataFrame,
    file_key_col,
    file_name_col,
    start_date_col,
    end_date_col,
    issue_date_col) -> pd.DataFrame:
    
    temp_df = df[[file_key_col,
            file_name_col,
            start_date_col,
            end_date_col,
            issue_date_col]]
    
    temp2_df = temp_df.copy()
    
    temp_df = temp_df.drop_duplicates(ignore_index=True)
    temp2_df = temp2_df.drop_duplicates('file_key', keep='first', ignore_index=True)

    return temp2_df


    

def get_category_dict(path) -> dict:
    with open(path, 'r') as file:
        category_dict = json.load(file)
    return category_dict

def get_category_key_list(category_dict:dict, category_col) -> list:
    key_list = []
    category_names = list(category_dict.keys())

    for item in category_col:
        if item.lower().strip() in category_names:
            for name in category_names:
                key_list.append(category_dict[name])
        else:
            key_list.append("-1")
    return key_list

def make_dim_category(category_dict) -> pd.DataFrame:
    int_list = [int(num) for num in list(category_dict.keys())]
    
    output = pd.DataFrame({'category_key': int_list,
     'category_name': list(category_dict.values())})
    return output

# %%
# Initialize logging
setup_logging()
logging.basicConfig(level="INFO")

# Initilize Paths
BASE_DIR = Path.cwd()
CSV_DIR = BASE_DIR / "csv"
CATEGORY_PATH = BASE_DIR / "categories.json"

# EXPORT
# Get CSV
latest_csv = get_latest_csv_path(CSV_DIR)
logger.info(f'👀 Latest CSV is {latest_csv}')
print(f'👀 Latest CSV is {latest_csv}')

# Create initial DataFrame
df = pd.read_csv(CSV_DIR/latest_csv)
logger.info("☑ Initial DataFrame created.")
print("☑ Initial DataFrame created.")

# CLEANING
# Set up DESCRIPTION2 column
desc_2 = ['N/A']
desc_2[1:] = df['DESCRIPTION'][0:-1]
df = df.assign(DESCRIPTION2=desc_2)
logger.info("☑ Set up DESCRIPTION2 column.")
print("☑ Set up DESCRIPTION2 column.")

# Add category_name column
category_name_list = [get_category(desc1, desc2) for desc1, desc2 in zip(df["DESCRIPTION"], df["DESCRIPTION2"])]
df['category_name'] = pd.Series(category_name_list)
logger.info("☑ Set up category_name column.")
print("☑ Set up category_name column.")

# Add file_key column
file_keys_list = make_file_key_list(df['Source.Name'])
df['file_key'] = pd.Series(file_keys_list)
logger.info("☑ Set up file_key column.")
print("☑ Set up file_key column.")

# Add category_key column
category_dict = get_category_dict(CATEGORY_PATH)
category_key_list = get_category_key_list(category_dict, df['category_name'])
df['category_key'] = pd.Series(category_key_list)
logger.info("☑ Set up category_key column.")
print("☑ Set up category_key column.")

# Add issue_date column
df['issue_date'] = pd.Series([
    extract_issue_date_from_file_key(fk) 
    for fk in df['file_key']])

# Add start_date and end_date columns
coverage_dict = extract_start_end_dates(df['DESCRIPTION'], df['Source.Name'])
df['start_date'] = pd.Series(coverage_dict['start_dates'])
df['end_date'] = pd.Series(coverage_dict['end_dates'])

# Set up transaction_keys column
transaction_key_s = pd.Series([get_transaction_key_key(file, cat) for file, cat in zip(df['Source.Name'], df['category_name'])])
df['transaction_key'] = transaction_key_s
logger.info("☑ Set up transaction_key column.")
print("☑ Set up transaction_key column.")

# %%
print("👇👇 Before cleaning:")
df.head()
df.tail()

# %%
# Clean data for exporting as csv
df = df.loc[df['UNIT PRICE'].notna() & df['category_name'].notnull()].reset_index(drop=True)
df = df.drop(['DESCRIPTION', 'DESCRIPTION2'], axis=1)
df.rename(columns={'Source.Name': 'file_name', 'QTY':'quantity', 'UNIT PRICE':'unit_price', 'PRICE (AUD)': 'total_price_aud'}, inplace=True)
df = df[['transaction_key', 'file_key', 'file_name', 'start_date', 'end_date', 'issue_date', 'category_key', 'category_name', 'quantity', 'unit_price', 'total_price_aud']]

logger.info('DataFrame has successfully been transformed and cleaned.')
print("👇👇 After cleaning:")
df.head()

out_timestamp = datetime.now().strftime(r'%Y%M%d%H%M%S')
# %%
# Checking directories
result_dir = BASE_DIR / 'out' / out_timestamp
if not result_dir.parents[0].exists():
    print(f'👀 Directory: "{result_dir.parents[0].relative_to(BASE_DIR).as_posix()}" does not exist.')
    logging.info(f'👀 Directory: "{result_dir.parents[0].relative_to(BASE_DIR).as_posix()}" does not exist.')
    
    result_dir.parents[0].mkdir()
    
    print(f'✅ Directory: {result_dir.parents[0].relative_to(BASE_DIR).as_posix()}" created made.')
    logging.info(f'✅ Directory: {result_dir.parents[0].relative_to(BASE_DIR).as_posix()}" created made.')
else:
    print(f'✅ Directory: "{result_dir.parents[0].relative_to(BASE_DIR).as_posix()}" exists!')
    logging.info(f'✅ Directory: "{result_dir.parents[0].relative_to(BASE_DIR).as_posix()}" exists!')

if not result_dir.exists():
    print(f'👀 Directory: "{result_dir.relative_to(BASE_DIR).as_posix()}" does not exist.')
    logging.info(f'👀 Directory: "{result_dir.relative_to(BASE_DIR).as_posix()}" does not exist.')
    result_dir.mkdir()
    print(f'✅ Directory: "{result_dir.relative_to(BASE_DIR).as_posix()}" made.')
    logging.info(f'✅ Directory: "{result_dir.relative_to(BASE_DIR).as_posix()}" made.')
else:
    print(f'✅ Directory: "{result_dir.relative_to(BASE_DIR).as_posix()}" already exists!')
    logging.info(f'✅ Directory: "{result_dir.relative_to(BASE_DIR).as_posix()}" already exists!')

# %%

# Export csv to a folder in "out" folder
outname = out_timestamp + '_transformed.csv'
df.to_csv(result_dir / outname, index=False)
print(f'☑ DataFrame has been output as CSV file in {BASE_DIR / 'out' / outname}.')
logger.info(f'☑ DataFrame has been output as CSV file in {BASE_DIR / 'out' / outname}.')

# Set up fact_transactions
fact_transactions = df[['transaction_key', 'file_key', 'category_key', 'quantity', 'unit_price', 'total_price_aud']]
logging.info("☑ fact_transactions df made")
print("☑ fact_transactions df made")

# %%
# Set up dim_file df
dim_file = make_dim_file(df, 'file_key', 'file_name', 'start_date', 'end_date', 'issue_date')
dim_file.head()
logging.info("☑ dim_file df made")
print("☑ dim_file df made")

# %%
# Set up dim_category df
dim_category = make_dim_category(get_category_dict(CATEGORY_PATH))
dim_category.head()
logging.info("☑ dim_category df made")
print("☑ dim_category df made")


# %%
fact_transactions.tail()
# %%
dim_category.tail()
# %%
dim_file.tail()

# %%
# Save dfs to a directory
outname = out_timestamp + 'fact_transactions.csv'
fact_transactions.to_csv(result_dir / outname, index=False)
print(f'☑ fact_transactions has been output as CSV file in {result_dir}.')
logger.info(f'☑ fact_transactions has been output as CSV file in {result_dir}.')

outname = out_timestamp + 'dim_category.csv'
dim_category.to_csv(result_dir / outname, index=False)
print(f'☑ dim_category has been output as CSV file in {result_dir}.')
logger.info(f'☑ dim_category has been output as CSV file in {result_dir}.')

outname = out_timestamp + 'dim_file.csv'
dim_file.to_csv(result_dir / outname, index=False)
print(f'☑ dim_file has been output as CSV file in {result_dir}.')
logger.info(f'☑ dim_file has been output as CSV file in {result_dir}.')
# %%
