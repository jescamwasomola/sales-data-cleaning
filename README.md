# Sales Data Cleaning Project (Python + Excel)

Turning a messy 10,500-row retail sales dataset into a clean, analysis-ready file.

 **Note:** The dataset is **synthetic**, created to practise
 realistic data-quality problems. It is not real company data.

## The Problem
Raw sales data often arrives with duplicates, inconsistent labels, text-formatted
numbers and missing values, which makes reporting unreliable.

## What I Did
Built a reproducible pandas pipeline that detects and fixes 19 types of issues
and records every fix in a cleaning log.

| Issue | Rows affected | Fix |
|---|---|---|
| Duplicate rows | 500 | Removed |
| Dates in 3 different formats | 2,332 | Parsed to a real date |
| Prices as text (TZS, /=, TSh) | 587 | Converted to numeric |
| Inconsistent city names | 1,514 | Standardised to 6 cities |
| Inconsistent payment labels | 1,458 | Standardised to 5 methods |
| Missing unit price | 200 | Filled with product's most common price |
| Zero/negative quantity | 100 | Removed |
| Extreme quantity outliers | 50 | Removed |
| Wrong totals | 194 | Recalculated (Qty x Price) |

Full list: `cleaning_log.csv`

## Results
- **10,500 rows → 9,651 clean rows**
- **0** missing values and **0** duplicates remaining
- Excel report with Summary, Raw_Data, Clean_Data and Cleaning_Log sheets

## Project Files
| File | Purpose |
|---|---|
| `01_generate_messy_data.py` | Creates the messy dataset (seed 42, reproducible) |
| `02_clean_data.py` | Cleaning pipeline and log |
| `03_build_excel.py` | Builds the Excel report |
| `Sales_Data_Cleaning_Project.xlsx` | Final report |
| `messy_sales_data.csv` / `clean_sales_data.csv` | Before and after |

## How to Run
```bash
pip install pandas numpy openpyxl
python 01_generate_messy_data.py
python 02_clean_data.py
python 03_build_excel.py
```

## Tools
Python (pandas, NumPy), openpyxl, Microsoft Excel

## Author
**Jesca Mwasomola**, Data Science student, EASTC, Dar es Salaam  
Available for data cleaning and analysis work on Upwork.
