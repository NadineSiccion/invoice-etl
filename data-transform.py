#%%
import pandas as pd
import os
from pathlib import Path

#%%
# read latest CSV from the folder csv
BASE_DIR = Path.cwd()
CSV_DIR = BASE_DIR / "csv"
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

# CLEANING







# %%
# DEBUGGING CODE
print(os.getcwd())
# %%
