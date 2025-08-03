# Invoice-ETL-Project
This project is a mock case based on a real life solution I have needed to solve in my work experience. Exporting, transforming and loading messy invoice data using MS Power Query, Python, and laoding it as a database to a BigQuery Sandbox.

# Problem
Company XYZ was prospecting a new call/SMS platforming service to replace their current one. A financial analysis regarding the pricing of the Company's SMS automated messages in their current software (Software A) needed to be done. This information is available in their past invoices, as well as other information that could be useful for future analysis. **However**, the past invoices are all stored in **PDF format**, making it hard to parse. And when parsed with Excel's Data Import feature, the **rows detected do not align with the relevant information**, making analysis with the imported data impossible.

# Solution (and How I Got There)
To solve this issue, I apply the ETL framework so our low-code financical analysts can perform analysis on the data using Excel.

## Extraction
* PDFs are downloaded from the Past Invoice section of Company A's account. These PDFs are uploaded to a common SharePoint Folder. The format of these Invoices have been consistent for several years.
* The common SharePoint folder is set as the Data Source for Power Query. Power Query is able to automatically parse data from the second table of each PDF and append them onto one Query.
* I have tried many other PDF extraction options and Power Query has come up with the best results. So I have automated this solution using batch and VBA scripts which is run by running the `download_recent_csv.bat` file.
* The extracted data is very messy and cannot be used for data analysis as is. [image] 

## Transformation

## Load

# Requirements
The following are required to run this project:
* Computer running Windows 10/11 OS
* Microsoft Office Excel installed to the laptop.

# How to Use
* Enable the use of Macros in the `SM8 Invoice Analysis.xlsm` file.
* Export - Run the `download_recent_csv.bat`.