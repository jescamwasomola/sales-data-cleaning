"""Generates a SYNTHETIC messy retail sales dataset (Tanzania-style shop data).
Data is simulated for portfolio practice; seed fixed so results are reproducible."""
import numpy as np, pandas as pd, random
rng = np.random.default_rng(42); random.seed(42)
N = 10000
cities = ["Dar es Salaam","Arusha","Mwanza","Dodoma","Mbeya","Zanzibar"]
products = {"Rice 5kg":14000,"Cooking Oil 3L":18000,"Sugar 2kg":7500,"Wheat Flour 2kg":6000,
            "Soap Bar":1500,"Tea Leaves 500g":5000,"Laundry Powder 1kg":6500,"Bottled Water 1.5L":1200}
methods = ["Cash","M-Pesa","Tigo Pesa","Airtel Money","Card"]
dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0,365,N), unit="D")
prod = rng.choice(list(products), N)
qty = rng.integers(1,20,N)
price = np.array([products[p] for p in prod])
df = pd.DataFrame({
 "Order_ID":[f"ORD-{100000+i}" for i in range(N)],
 "Order_Date":dates, "Customer_Name":[f"Customer {rng.integers(1,1500)}" for _ in range(N)],
 "City":rng.choice(cities,N), "Product":prod, "Quantity":qty,
 "Unit_Price_TZS":price, "Payment_Method":rng.choice(methods,N,p=[.4,.3,.12,.1,.08])})
df["Total_TZS"] = df.Quantity*df.Unit_Price_TZS

# ---- inject mess ----
def idx(frac): return rng.choice(N, int(N*frac), replace=False)
# 1 mixed date formats (stored as text)
d = df.Order_Date.dt.strftime("%Y-%m-%d").astype(object)
i = idx(.15); d.iloc[i] = df.Order_Date.iloc[i].dt.strftime("%d/%m/%Y")
i = idx(.10); d.iloc[i] = df.Order_Date.iloc[i].dt.strftime("%d-%b-%Y")
df["Order_Date"] = d
# 2 city typos / case / spaces
m = {"Dar es Salaam":["dar es salaam","DAR ES SALAAM","Dar-es-Salaam","Dar es salaam "],
     "Arusha":["arusha","ARUSHA "," Arusha"],"Mwanza":["mwanza","Mwanza ","MWANZA"],
     "Dodoma":["dodoma","Dodoma ","DODOMA"],"Mbeya":["mbeya","MBEYA"],"Zanzibar":["zanzibar","Zanzibar ","ZNZ"]}
for j in idx(.20):
    df.at[j,"City"] = random.choice(m[df.at[j,"City"]])
# 3 payment method variants
pm = {"M-Pesa":["mpesa","M-PESA","M Pesa"],"Cash":["cash","CASH "],"Tigo Pesa":["tigopesa","Tigo pesa"],
      "Airtel Money":["airtel money","AirtelMoney"],"Card":["card","CARD"]}
for j in idx(.15):
    df.at[j,"Payment_Method"] = random.choice(pm[df.at[j,"Payment_Method"]])
# 4 product whitespace/case
for j in idx(.08):
    df.at[j,"Product"] = random.choice([df.at[j,"Product"].lower(), df.at[j,"Product"]+" "])
# 5 customer name case/space
for j in idx(.10):
    df.at[j,"Customer_Name"] = random.choice([df.at[j,"Customer_Name"].upper(), "  "+df.at[j,"Customer_Name"]])
# 6 missing values
df["Customer_Name"] = df["Customer_Name"].astype(object); df["City"]=df["City"].astype(object)
df["Payment_Method"]=df["Payment_Method"].astype(object)
df.loc[idx(.04),"Customer_Name"]=np.nan
df.loc[idx(.03),"City"]=np.nan
df.loc[idx(.03),"Payment_Method"]=np.nan
df["Quantity"]=df["Quantity"].astype(float); df.loc[idx(.02),"Quantity"]=np.nan
df["Unit_Price_TZS"]=df["Unit_Price_TZS"].astype(object)
df.loc[idx(.02),"Unit_Price_TZS"]=np.nan
# 7 price stored as text with currency
for j in idx(.06):
    v=df.at[j,"Unit_Price_TZS"]
    if pd.notna(v): df.at[j,"Unit_Price_TZS"]=random.choice([f"TZS {int(v):,}",f"{int(v):,}/=",f"{int(v)} TSh"])
# 8 invalid quantities (negative / zero / extreme)
for j in idx(.01): df.at[j,"Quantity"]=random.choice([-3,-1,0,0])
for j in idx(.005): df.at[j,"Quantity"]=random.choice([999,500,1200])
# total recalculated mismatch for some rows
df["Total_TZS"]=df["Total_TZS"].astype(float)
for j in idx(.02): df.at[j,"Total_TZS"]=df.at[j,"Total_TZS"]*random.choice([0.1,10])
# 9 duplicates
dups = df.sample(int(N*.05), random_state=1)
df = pd.concat([df,dups]).sample(frac=1, random_state=7).reset_index(drop=True)
df.to_csv("messy_sales_data.csv", index=False)
print(df.shape)
