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

# Initialize logging
logging.basicConfig(level="INFO")

''' 
logger.debug("debug message", extra={"x": "hello"})
logger.info("info message")
logger.warning("warning message")
logger.error("error message")
logger.critical("critical message")
'''

#%%
# Initilize Paths
BASE_DIR = Path.cwd()
CSV_DIR = BASE_DIR / "csv"
CATEGORY_PATH = BASE_DIR / "categories.json"

# Create DataFrame out of the latest CSV
def get_latest_csv_path(csv_dir) -> str:
    csv_files = os.listdir(csv_dir)
    if ".gitignore" in csv_files:
        csv_files.remove(".gitignore")
    csv_files.sort()
    for file in csv_files:
        print(file)
    return csv_files[-1]

latest_csv = get_latest_csv_path(CSV_DIR)
print(f'Latest CSV is {latest_csv}')
logger.info('Latest CSV is {latest_csv}')

df = pd.read_csv(CSV_DIR/latest_csv)
print(df.head())
print(df.tail())
logger.info("Initial DataFrame created.")

# %% 

def change_month_to_number(name):
    for substr, num in month_substrings.items():
        if substr in name:
            name = name.replace(substr, num, 1)  # Replace only the first occurrence
    return name

# CLEANING
# Set up DESCRIPTION2 column
desc_2 = ['N/A']
desc_2[1:] = df['DESCRIPTION'][0:-1]
df = df.assign(DESCRIPTION2=desc_2)
print(df.head())
print(df.tail())

# TODO: Parse start and end dates, put it in as a column.
#%%

def extract_date(arr:list) -> datetime.date:
    out = []

    # Day
    pattern = r"\D+"  # \D matches any non-digit character
    match = re.search(pattern, arr[0])
    if match:
        print(match.group())
        out = [arr[0].replace(match.group(0), "").zfill(2)]
    else:
        raise Exception("Issue in day input for extract_date.") 
    
    # Month
    for month_sub in list(month_substrings.keys()):
        if month_sub in arr[1].lower():
            out.append(str(month_substrings[month_sub]).zfill(2))
    
    # Year
    out.append(arr[2])
    
    # Convert to datetime
    output = datetime(int(out[2]), int(out[1]), int(out[0])).date()
    # print('Extracted date:', output)
    return output

#%%
def make_dim_file(df:pd.DataFrame) -> pd.DataFrame:
    coverage_dict = {'file_key': [], 
                     'file_name':[], 
                     'start_dates': [], 
                     'end_dates': []}

    for desc, src_name in zip(df['DESCRIPTION'], df['Source.Name']):
        print('desc:' + desc)
        if 'Coverage Period' in desc:
            temp = desc.split(' ')
            start_date = temp[2:5]
            end_date = temp[6:9]
            coverage_dict['start_dates'].append(extract_date(start_date))        
            coverage_dict['end_dates'].append(extract_date(end_date))
        else:
            coverage_dict['start_dates'].append(None)        
            coverage_dict['end_dates'].append(None)
        coverage_dict['file_key'].append(change_month_to_number(src_name.lower()))
        coverage_dict['file_name'].append(src_name)
    
    print([
        len(coverage_dict['file_key']),
        len(coverage_dict['file_name']),
        len(coverage_dict['start_dates']),
        len(coverage_dict['end_dates'])
        ])
    print(coverage_dict['file_key'])
        
    coverage_df = pd.DataFrame(coverage_dict)
    return coverage_df

dim_coverages = make_dim_file(df)
dim_coverages.head()
#%%

# Set up Category column
def get_category(desc1, desc2):
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
category_s = pd.Series([get_category(desc1, desc2) for desc1, desc2 in zip(df["DESCRIPTION"], df["DESCRIPTION2"])])
df["CATEGORY"] = category_s
print(df.head())
print(df.tail())

def get_new_filename(source_name, month_map):
    str_arr = source_name[:-4].split("-")
    str_arr[1] = month_map[str_arr[1][0:2]]
    new_name = str_arr[2]+str_arr[1]+str_arr[0]
    return new_name




# Make the transaction keys


# Make the category

# %% Set up Primary key column / Transaction ID

#%%
def get_primary_key(source_name:str, category:str):
    name = str(source_name).lower().replace('.pdf', '').replace('-','')
    name = change_month_to_number(name)
    return (name + str(category)).lower()

primary_s = pd.Series([get_primary_key(file, cat) for file, cat in zip(df['Source.Name'], df['CATEGORY'])])
df['PRIMARY'] = primary_s
print(df.head())
print(df.tail())
logger.info("Primary keys made")


# Clean data and export csv to "out" folder
df = df[df['UNIT PRICE'].notna() & df['CATEGORY'].notnull()]
df = df.drop(['DESCRIPTION', 'DESCRIPTION2'], axis=1)
df = df[['PRIMARY', 'Source.Name', 'CATEGORY', 'QTY', 'UNIT PRICE', 'PRICE (AUD)']]
df.rename(columns={'PRIMARY':'transaction_key', 'Source.Name': 'file_name', 'CATEGORY': 'category_name', 'QTY':'quantity', 'UNIT PRICE':'unit_price', 'PRICE (AUD)': 'total_price_aud'}, inplace=True)
logger.info('DataFrame has successfully been transformed and cleaned.')

print(df.head())
print(df.tail())

outname = datetime.now().strftime(r'%Y%M%d%H%M%S') + '_transformed.csv'
df.to_csv(BASE_DIR / 'out' / outname, index=False)
logger.info(f'DataFrame has been output as CSV file in {BASE_DIR / 'out' / outname}.')

# %%
# DEBUGGING CODE
# df = df.assign(index1=df['index']+1)

# %%
print(df.head())
print(df.tail())

# %%

def make_dim_category(path) -> pd.DataFrame:
    with open(path, 'r') as file:
        data = json.load(file)
    
    int_list = [int(num) for num in list(data.keys())]
    
    output = pd.DataFrame({'category_key': int_list,
     'category_name': list(data.values())})
    return output

dim_category = make_dim_category(CATEGORY_PATH)
dim_category.head()
print(dim_category)
logging.info("dim_category df made")
    
# %%
# TODO: def make_dim_file


#%% debug cell
test = [1,2,3,4,5,6]
print(test[0:2])
# %%
