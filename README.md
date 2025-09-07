# Invoice-ETL-Project
This project is a mock solution based on a real world business problem encountered in my early career. Though not implemented, this repository covers its practical and hypothetical execution. 

![ETL Process Diagram](https://raw.githubusercontent.com/NadineSiccion/invoice-etl/refs/heads/main/imgs/process%20diagram%20invoice%20etl-2.png?token=GHSAT0AAAAAADKVD3JNBXA7FYNRZB2TSNUO2F5PBSA "ETL Process Diagram")

# Problem
Company XYZ was prospecting new call/SMS platforms to replace their current one. Thus, a financial analysis regarding the costs of the Company's SMS automated messaging over the last 7 years must be done.

This information is available in their past invoices in Software A, as well as other information that could be useful for future analysis. **However**, all invoices are stored in **PDF format** with no easy way to extract the data for analysis.

The objectives of this project are:
- Extract the data from the PDFs.
- Transform the data so it is safe for analysis.
- Load the data to a data warehouse to be accessed by analysts.

# Solution (and How I Got There)
My solution is illustrated in this diagram. Explanations for each part are found below.

![ETL Process Diagram](https://raw.githubusercontent.com/NadineSiccion/invoice-etl/refs/heads/main/imgs/process%20diagram%20invoice%20etl-2.png?token=GHSAT0AAAAAADKVD3JNBXA7FYNRZB2TSNUO2F5PBSA "ETL Process Diagram")

## Extraction
Monthly reports of the invoices of the past 7 years could only be downloaded as PDFs from the website.

- All the PDFs are to be saved into a single folder with a consistent naming pattern (we will use the existing naming convention which is `dd-MMM-YYYY.pdf`, ex. `02-Aug-2024.pdf`).
- Using Excel's VBA, PowerQuery extracts the values into a csv file. 
    - I found that PowerQuery is able to accurately extract the values with less setup costs than other software explored, with the caveat of the rows being misaligned in a preditable manner. 
- This csv will be transformed and cleaned in the next phase.
<!-- 
## Extraction
* PDFs are downloaded from the Past Invoice section of Company A's account. These PDFs are uploaded to a common SharePoint Folder. The format of these Invoices have been consistent for several years.
* The common SharePoint folder is set as the Data Source for Power Query. Power Query is able to automatically parse data from the second table of each PDF and append them onto one Query.
* I have tried many other PDF extraction options and Power Query has come up with the best results. So I have automated this solution using batch and VBA scripts which is run by running the `download_recent_csv.bat` file.
* The extracted data is very messy and cannot be used for data analysis as is. [image]  -->

## Transformation
With the invoice data collated and extracted into csv format, pandas is used to clean the values. A backup of this simple dataframe is saved locally as a CSV. 

Next, the data is be transformed into this structure to follow the principles of the Star Schema for scalable analysis:

![Database Diagram](https://raw.githubusercontent.com/NadineSiccion/invoice-etl/refs/heads/main/imgs/db%20diagram%20invoice%20etc.png?token=GHSAT0AAAAAADKVD3JNKAXGPWAKTTDFI5DW2F5O7XQ)

After transformation, the data will be loaded to the "data warehouse".

## Load
The transformed data is loaded onto Google BigQuery via authentication from Google Cloud API and the pandas-gbq library. With access, this data may be quiried from Google BigQuery for analysis. 

# How to Use
### Requirements
The following are required to run this project:
* Computer running Windows 10/11 OS
* Microsoft Office Excel installed to the laptop.

### Steps
* Clone this repository on your system.
* Enable the use of Macros in the `SM8 Invoice Analysis.xlsm` file.
* Export - Run the `download_recent_csv.bat`.
