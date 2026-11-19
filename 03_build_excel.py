import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
raw = pd.read_csv("messy_sales_data.csv", dtype=str)
clean = pd.read_csv("clean_sales_data.csv")
log = pd.read_csv("cleaning_log.csv")
F = "Arial"; hdr_fill = PatternFill("solid", fgColor="1F4E78")
def write(ws, df, widths=None):
    ws.append(list(df.columns))
    for r in df.itertuples(index=False): ws.append([None if pd.isna(v) else v for v in r])
    for c in ws[1]: c.font = Font(name=F, bold=True, color="FFFFFF"); c.fill = hdr_fill; c.alignment = Alignment(horizontal="center")
    for i, col in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(i)].width = (widths or {}).get(col, max(14, len(col)+4))
    ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
wb = Workbook()
s = wb.active; s.title = "Summary"
ws = wb.create_sheet("Raw_Data"); write(ws, raw)
wc = wb.create_sheet("Clean_Data"); write(wc, clean)
for r in range(2, len(clean)+2): wc.cell(r,2).number_format = "yyyy-mm-dd"
for col in "FGI":
    for r in range(2, len(clean)+2): wc[f"{col}{r}"].number_format = "#,##0"
wl = wb.create_sheet("Cleaning_Log"); write(wl, log, {"Issue":62,"Column":18,"Rows_Affected":15,"Fix_Applied":58})
for row in wl.iter_rows(min_row=2): 
    for c in row: c.font = Font(name=F)
for ws_ in (ws, wc):
    for row in ws_.iter_rows(min_row=2, max_row=60):
        for c in row: c.font = Font(name=F)

n_raw, n_clean, n_log = len(raw)+1, len(clean)+1, len(log)+1
s["A1"] = "Sales Data Cleaning Project"; s["A1"].font = Font(name=F, size=16, bold=True, color="1F4E78")
s["A2"] = "Note: dataset is SIMULATED (synthetic) for portfolio practice. Cleaning done with Python (pandas); see script."
s["A2"].font = Font(name=F, italic=True, size=10)
rows = [("Metric","Value"),
 ("Rows in raw data", f"=COUNTA(Raw_Data!A2:A{n_raw})"),
 ("Rows in clean data", f"=COUNTA(Clean_Data!A2:A{n_clean})"),
 ("Rows removed", "=B5-B6"),
 ("% of rows removed", "=B7/B5"),
 ("Total issue types fixed", f"=COUNTA(Cleaning_Log!A2:A{n_log})"),
 ("Total fixes applied (sum of rows affected)", f"=SUM(Cleaning_Log!C2:C{n_log})"),
 ("Missing values remaining in clean data", f'=COUNTBLANK(Clean_Data!A2:I{n_clean})'),
 ("Duplicate Order_IDs remaining", f"=SUMPRODUCT((COUNTIF(Clean_Data!A2:A{n_clean},Clean_Data!A2:A{n_clean})>1)*1)"),
 ("Total revenue, clean data (TZS)", f"=SUM(Clean_Data!I2:I{n_clean})")]
for i, (a, b) in enumerate(rows, 4):
    s.cell(i,1,a); s.cell(i,2,b)
    s.cell(i,1).font = Font(name=F, bold=(i==4)); s.cell(i,2).font = Font(name=F, bold=(i==4))
for c in (s["A4"], s["B4"]): c.fill = hdr_fill; c.font = Font(name=F, bold=True, color="FFFFFF")
for r in (5,6,7,9,10,11,12): s[f"B{r}"].number_format = "#,##0"
s["B8"].number_format = "0.0%"; s["B13"].number_format = "#,##0"
s.column_dimensions["A"].width = 46; s.column_dimensions["B"].width = 20
wb.save("Sales_Data_Cleaning_Project.xlsx")
