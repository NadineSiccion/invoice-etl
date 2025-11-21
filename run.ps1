# STEP 1 Check if Python3 is installed
if (Get-Command python -ErrorAction SilentlyContinue) {
    "Python is installed."
}
else {
    "Python not found."
    "Ending program..."
    Pause
    Exit-PSHostProcess
}

# STEP 2: Check if .venv folder exists in project folder
$venvExists = test-path -path "./.venv"

# If not, make .venv folder
if (!$venvExists) {
    ".venv does not exist."
    "Creating new virtual environment... This may take upto 3 minutes..."
    python.exe -m venv .venv
} else {
    ".venv exists."
}

# STEP 3: Activate .venv
"Activating virtual environment..."
"& ""$PSScriptRoot/.venv/Scripts/Activate.ps1"""

# STEP 4: Install dependencies 
"Intalling dependencies... This may take up to 7 minutes..."
try { python.exe -m pip install -r requirements.txt }
catch {
    "ERROR: An error has occurred while installing dependencies."
    Pause
    Exit-PSHostProcess
}

Pause
Clear-Host
"Dependencies have been installed."
Clear-Host

# Step 5: Extract procedure
Write-Host "========== EXTRACT PROCEDURE ==========" -ForegroundColor Yellow
"*SKIPPING* EXTRACT IS RECOMMENDED."
"*Only perform extract if you meet the following requirements:*"

$SkipExtract = Read-Host "Would you like to skip the extract phase (y recommended)? (y/n) "
""

if ($SkipExtract.toLower().Trim() -eq 'n') {
    $ExtractConfirm = "Are you sure you want to run the Extract script? (y/n)"
    if ($ExtractConfirm.toLower().Trim() -eq 'y') {
        "Running Extract script..."
        python.exe ./scripts/extract.py
        "Extract script complete!"
    }
} elseif ($SkipExtract.toLower().Trim() -eq 'y') {
    "Skipping Extract script. We will use a pre-loaded csv file for the transform script."
} else {
    "Please only enter y or n."
}
Pause
Clear-Host

# Step 5: Transform Procedure
Write-Host "========== TRANSFORM PROCEDURE ==========" -ForegroundColor Yellow
"The Transform script will take in the CSV output of the Extract script and turn it into 1 fact table, 2 dimension tables, and 1 flat file found in the 'output' folder under its respectivev timestamp."
""
"We will now run the Transform script."
Pause
python.exe ./scripts/transform.py

if ($LastExitCode -ne 0) {
    "ERROR: An error has occurred. Terminating script..."
    Pause
    Exit-PSHostProcess
}


"Transform script complete!"
Pause
Clear-Host

# Step 6: Load Procedure
Write-Host "========== LOAD PROCEDURE ==========" -ForegroundColor Yellow
"Originally, the load procedure would load these tables to a project in Google BigQuery."
"To avoid giving confidential information, the tables will be loaded locally to a file named 'warehouse.db' iwhtin the project folder."
""
"We will now run the Load script."
Pause
python.exe ./scripts/load.py
"Load script complete! The tables have been loaded to 'warehouse.db'."
Pause
Clear-Host

# Step 7: Warehouse_cli
Write-Host "========== Test It ==========" -ForegroundColor Yellow
"Test the 'warehouse' based on the schema in 'db-diagram-invoice-load.png' using SQLite queries!"
""
"We will run the script that allows you to run queries on it."
Pause
python.exe ./scripts/warehouse_cli.py