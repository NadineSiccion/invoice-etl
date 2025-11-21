# 🚀 ETL Pipeline Project

This project demonstrates an **ETL (Extract–Transform–Load)** pipeline using **Python, Batch Scripts, and VBA**.
It was inspired by a **real business problem encountered during work**. While this exact solution was not implemented in production, it represents a working alternative that could have automated reporting workflows, improved data consistency, and saved significant time.

## 📖 Background

Company XYZ was prospecting new call/SMS platforms to replace their current one. Thus, a financial analysis regarding the costs of the Company's SMS automated messaging over the last 7 years must be done.

This information is available in their past invoices in Software A, as well as other information that could be useful for future analysis. **However**, all invoices are stored in **PDF format** with no easy way to extract the data for analysis.

The goal of this project is to show how such a scenario could be solved by:

-   **Extracting** from PDF files (Excel, CSV, system dumps).
-   **Transforming** it into a standardized format (a light star-schema).
-   **Loading** the data into a structured schema, resembling a lightweight **data warehouse**, for downstream analysis and visualization (originally for cloud, re-made for local storage).
-   **Running** practice queries in a SQLite environment.

## 🖼️ ETL Architecture

<img width="1175" height="327" alt="process diagram invoice etl-2" src="https://github.com/user-attachments/assets/9ae1f451-d800-49f7-90b0-e51ba9cc5553" />

## 🗄️ Data Warehouse Schema

<img width="771" height="503" alt="db diagram invoice etc" src="https://github.com/user-attachments/assets/7b00be05-c101-41f5-84a0-81e787adfefa" />

## 📂 Project Structure

```
etl-project/
├── README.md               # Project documentation
├── images/                 # Images showing architecture
├── input/                  # Contains csv from Extract script
│   ├── sample_invoices/    # Raw sample invoices
├── requirements.txt        # Python dependencies
├── output/                 # Processed results
├── scripts/
│   ├── extract.py          # Extract data (CSV, Excel, APIs, etc.)
│   ├── transform.py        # Clean & transform logic
│   ├── load-gcp.py         # Load into GCP schema (no creds)
│   ├── load-sql.py         # Load into local db file
│   ├── warehouse_cli.py    # Simulate sqlite env for testing
│   ├── run-macro.vbs       # Part of the Extract script
├── Export.xlsm             # Macro-enabled excel for Export phase
│   └── run_etl.bat         # Windows batch script to run the pipeline
├── log/                    # Log files
├── run.bat                 # Run ETL
└── run.ps1                 # Run ETL

```

---

## ⚙️ How It Works

1. **Extract**

    - Python scripts pull data from raw files and system exports.
    - Extracted files are stored in `/data/input/`.

2. **Transform**

    - Python validates and cleans data.
    - Example: date normalization, removing duplicates, mapping inconsistent department codes.

3. **Load**

    - Python writes the final dataset into `/data/output/`.
    - Data is structured according to the **warehouse schema** (fact + dimension tables).

4. **Excel/VBA Automation**

    - A VBA macro (`cleanup_module.bas`) can be imported into Excel to apply final formatting for business users.

5. **Orchestration**

    - `run_etl.bat` triggers the ETL pipeline end-to-end.

## 📦 Installation & Setup

### Requirements

-   Windows 10/11
-   Python 3
-   git bash

### 1. Clone Repository

```bash
git clone git@github.com:NadineSiccion/invoice-etl.git
cd etl-project
```

### 3. Run Pipeline

```bash
batch\run_etl.bat
```
