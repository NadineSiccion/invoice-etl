@echo off
title Run ETL

:: Step 1: Run 'venv' to create a virtual environment in the same folder
echo Initializating vevn... This may take about 3 minutes...
python -m venv ve
if %errorlevel% neq 0 (
    echo Failed to create virtual environment.
    pause
    exit /b
)

:: Step 2: Activate the virtual environment
echo Running the virtual environment...
call ve\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b
)

:: Step 3: Install packages from requirements.txt
pip install -r requirements.txt
echo Installing requirements...
if %errorlevel% neq 0 (
    echo Failed to install packages from requirements.txt.
    pause
    exit /b
)

:: Step 4: Extract phase
echo Extract phase is optional, moving onto Transformation phase
:: echo Running run_macro.vbs... May take up to a minute...
:: wscript "./run_macro.vbs"
:: echo CSV downloaded. Check the csv folder.

:: Step 5: Transformation phase
echo Running Transformation phase...
python .\scripts\data-transform.py
echo Transformation phase complete
pause

:: Step 6: Load phase
echo Google BigQuery dataset cannot be accessed without proper credentials, this will be skipped.
:: python .\scripts\load.py
pause