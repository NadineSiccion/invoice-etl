import subprocess, pandas, sqlalchemy, sqlite3, logging.config, sys
from pathlib import Path
from configs import setuplogging

def run_extract():
    try:
        subprocess.run(['python', 
        r'.\scripts\extract.py'],
        check=True)
    except Exception as sube:
        print(f"ERROR: {sube}")
        sys.exit()
    subprocess.run("pause")

def run_transform():
    try:
        subprocess.run(['python', 
        r'.\scripts\transform.py'],
        check=True)
    except Exception as sube:
        print(f"ERROR: {sube}")
        sys.exit()
    subprocess.run("pause")

def run_load():
    try:
        subprocess.run(['python', 
            r'.\scripts\load-sql.py'],
            check=True)
    except Exception as sube:
        print(f"ERROR: {sube}")
        sys.exit()
    subprocess.run("pause")


def run_test_env():
    try:
        subprocess.run(['python',
            r'.\scripts\warehouse_cli.py'],
            check=True)
    except Exception as sube:
        print(f"ERROR: {sube}")
        sys.exit()
    subprocess.run("pause")


def main():
    print("🚀 Starting ETL pipeline...\n")
    print("Running extract...")
    run_extract()

    print("Running transform...")
    run_transform()

    print("Running load...")
    run_load()

    answer = input("Would you like to make test queries to the data? [Y/N]: ")
    if (answer.strip().lower() == 'y'):
        print("Excellent! Please refer to the data schema shown in the README.md for details.")
        run_test_env()
    elif (answer.strip().lower() == 'n'):
        pass
    else:
        print("Please input y or n")

    print("Program complete!")
    # print("The Extract process uses a macro-enabled Excel workbook and VBA scripts.\n", 
    #     "which may require elevated permissions. ")

main()