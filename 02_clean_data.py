"""Cleaning messy_sales_data.csv with pandas and write a cleaning log."""
import pandas as pd, numpy as np, re
raw = pd.read_csv("messy_sales_data.csv", dtype=str)
df = raw.copy()
log = []
def add(issue, column, affected, fix):
    log.append({"Issue": issue, "Column": column, "Rows_Affected": int(affected), "Fix_Applied": fix})

rows_before = len(df)

# 1. Exact duplicate rows
n = df.duplicated().sum(); df = df.drop_duplicates().reset_index(drop=True)
add("Duplicate rows (exact copies)", "All", n, "Removed duplicates, kept first occurrence")

# 2. Whitespace
for c in ["Customer_Name","City","Product","Payment_Method"]:
    s = df[c].dropna(); n = (s != s.str.strip()).sum()
    df[c] = df[c].str.strip()
    if n: add("Leading/trailing spaces", c, n, "Stripped whitespace")

# 3. City standardisation
city_map = {"dar es salaam":"Dar es Salaam","dar-es-salaam":"Dar es Salaam","arusha":"Arusha","mwanza":"Mwanza",
            "dodoma":"Dodoma","mbeya":"Mbeya","zanzibar":"Zanzibar","znz":"Zanzibar"}
new = df.City.str.lower().map(city_map).where(df.City.notna())
n = ((new != df.City) & df.City.notna()).sum(); df["City"] = new
add("Inconsistent city names (case, hyphens, abbreviations e.g. ZNZ)", "City", n, "Mapped to 6 standard city names")

# 4. Payment method standardisation
pm_map = {"cash":"Cash","mpesa":"M-Pesa","m-pesa":"M-Pesa","m pesa":"M-Pesa","tigopesa":"Tigo Pesa","tigo pesa":"Tigo Pesa",
          "airtel money":"Airtel Money","airtelmoney":"Airtel Money","card":"Card"}
new = df.Payment_Method.str.lower().map(pm_map).where(df.Payment_Method.notna())
n = ((new != df.Payment_Method) & df.Payment_Method.notna()).sum(); df["Payment_Method"] = new
add("Inconsistent payment method labels (e.g. mpesa / M Pesa / M-PESA)", "Payment_Method", n, "Mapped to 5 standard methods")

# 5. Product & customer name casing
prods = ["Rice 5kg","Cooking Oil 3L","Sugar 2kg","Wheat Flour 2kg","Soap Bar","Tea Leaves 500g","Laundry Powder 1kg","Bottled Water 1.5L"]
pmap = {p.lower():p for p in prods}
new = df.Product.str.lower().map(pmap); n = (new != df.Product).sum(); df["Product"] = new
add("Product names in wrong case", "Product", n, "Standardised to official product list")
new = df.Customer_Name.str.title().where(df.Customer_Name.notna())
n = ((new != df.Customer_Name) & df.Customer_Name.notna()).sum(); df["Customer_Name"] = new
add("Customer names in UPPERCASE", "Customer_Name", n, "Converted to Title Case")

# 6. Dates in 3 formats
d = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
for fmt in ["%Y-%m-%d","%d/%m/%Y","%d-%b-%Y"]:
    p = pd.to_datetime(df.Order_Date, format=fmt, errors="coerce")
    d = d.fillna(p)
n_non_iso = (~df.Order_Date.str.match(r"^\d{4}-\d{2}-\d{2}$")).sum()
add("Dates stored as text in 3 different formats", "Order_Date", n_non_iso, "Parsed all to a real date (YYYY-MM-DD)")
add("Dates that could not be parsed", "Order_Date", d.isna().sum(), "None found" if d.isna().sum()==0 else "Flagged")
df["Order_Date"] = d

# 7. Price text -> number
def price(v):
    if pd.isna(v): return np.nan
    return float(re.sub(r"[^\d.]", "", v))
n = df.Unit_Price_TZS.dropna().str.contains(r"[^\d.]").sum()
df["Unit_Price_TZS"] = df.Unit_Price_TZS.map(price)
add("Prices stored as text with currency symbols (TZS, /=, TSh, commas)", "Unit_Price_TZS", n, "Stripped symbols, converted to numeric")
df["Quantity"] = pd.to_numeric(df.Quantity, errors="coerce")
df["Total_TZS"] = pd.to_numeric(df.Total_TZS, errors="coerce")

# 8. Missing values
n = df.Unit_Price_TZS.isna().sum()
price_ref = df.groupby("Product").Unit_Price_TZS.agg(lambda s: s.mode().iloc[0])
df["Unit_Price_TZS"] = df.Unit_Price_TZS.fillna(df.Product.map(price_ref))
add("Missing unit price", "Unit_Price_TZS", n, "Filled with the most common price for that product")
for c, fill in [("Customer_Name","Unknown"),("City","Unknown"),("Payment_Method","Unknown")]:
    n = df[c].isna().sum(); df[c] = df[c].fillna(fill)
    add("Missing values", c, n, f"Filled with '{fill}' (kept row, flagged)")
n = df.Quantity.isna().sum(); df = df[df.Quantity.notna()]
add("Missing quantity (cannot be inferred)", "Quantity", n, "Removed rows")

# 9. Invalid / outlier quantities
n = (df.Quantity <= 0).sum(); df = df[df.Quantity > 0]
add("Zero or negative quantity", "Quantity", n, "Removed rows (invalid orders)")
n = (df.Quantity > 100).sum(); df = df[df.Quantity <= 100]
add("Extreme quantity outliers (>100 units per order)", "Quantity", n, "Removed rows (likely data-entry errors)")

# 10. Total mismatch
calc = df.Quantity * df.Unit_Price_TZS
n = (~np.isclose(df.Total_TZS, calc)).sum()
df["Total_TZS"] = calc
add("Total does not equal Quantity x Unit Price", "Total_TZS", n, "Recalculated Total_TZS = Quantity x Unit_Price_TZS")

df["Quantity"] = df.Quantity.astype(int)
df["Unit_Price_TZS"] = df.Unit_Price_TZS.astype(int); df["Total_TZS"] = df.Total_TZS.astype(int)
df = df.sort_values("Order_Date").reset_index(drop=True)
rows_after = len(df)
logdf = pd.DataFrame(log)
logdf = logdf[logdf.Rows_Affected > 0].reset_index(drop=True)
df.to_csv("clean_sales_data.csv", index=False)
logdf.to_csv("cleaning_log.csv", index=False)
summary = dict(rows_before=rows_before, rows_after=rows_after)
import json; json.dump(summary, open("summary.json","w"))
print(summary); print(logdf.to_string())
print(df.isna().sum().sum(), "missing after;", df.duplicated().sum(), "dups after")
print(df.dtypes)
