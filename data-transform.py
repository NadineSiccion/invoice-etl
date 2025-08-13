#%%
import pandas as pd
import os
from pathlib import Path

#%%
# Paths
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
print(df.head(10))

# %%
# CLEANING

# # all the column names are fine
# add index-1 (since 0-base index already exists)
# df = df.reset_index() # turns index into a normal column

# set up DESCRIPTION2 Series
desc_2 = ['N/A']
desc_2[1:] = df['DESCRIPTION'][0:-1]
df = df.assign(DESCRIPTION2=desc_2)
print(df.head())

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

# %%
category_s = pd.Series([get_category(desc1, desc2) for desc1, desc2 in zip(df["DESCRIPTION"], df["DESCRIPTION2"])])
df["CATEGORY"] = category_s
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
