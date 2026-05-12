import pandas as pd
import os

url = "https://en.wikipedia.org/wiki/List_of_circulating_currencies"
output_path = "../databank/currencies_and_fractions.csv"

tables = pd.read_html(url)

def flatten_columns(cols):
    if isinstance(cols, pd.MultiIndex):
        return [' '.join(map(str, tup)).strip().lower() for tup in cols]
    else:
        return [str(c).strip().lower() for c in cols]

target_table = None
for t in tables:
    cols = flatten_columns(t.columns)
    has_country    = any("state" in c or "territory" in c for c in cols)
    has_currency   = any("currency" in c for c in cols)
    has_fractional = any("fractional" in c and "unit" in c for c in cols)
    has_iso        = any("iso" in c and "code" in c for c in cols)
    has_symbol     = any("symbol" in c or "abbrev" in c for c in cols)
    if has_country and has_currency and has_fractional and has_iso and has_symbol:
        target_table = t
        target_table.columns = cols
        break

if target_table is None:
    raise ValueError("Could not find a table with the required columns.")

# find actual column names dynamically
country_col    = next(c for c in target_table.columns if "state" in c or "territory" in c)
currency_col   = next(c for c in target_table.columns if "currency" in c)
fractional_col = next(c for c in target_table.columns if "fractional" in c and "unit" in c)
iso_col        = next(c for c in target_table.columns if "iso" in c and "code" in c)
symbol_col     = next(c for c in target_table.columns if "symbol" in c or "abbrev" in c)

df = target_table[[country_col, currency_col, fractional_col, iso_col, symbol_col]].copy()

df.columns = ["country", "currency", "fractional_unit", "iso_code", "symbol_or_abbreviation"]

df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else "")

os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False, encoding="utf-8")

print(f"Saved {len(df)} rows with columns: country, currency, fractional_unit, iso_code, symbol_or_abbreviation → {output_path}")
