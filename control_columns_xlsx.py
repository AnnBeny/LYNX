import pandas as pd
from pathlib import Path

folder = Path(__file__).parent / 'TRANSLOKACE_PRESTAVBA_ALL'
columns_to_check = ['comments']
files = list(folder.glob('*.xlsx'))

for col in columns_to_check:
    print(f"\n====== Sloupec: {col} ======")
    total_nonempty = 0
    all_unique_values = set()

    for file in files:
        xls = pd.ExcelFile(file)
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            # filtr na rearrangement!!!
            #if 'class1' in df.columns:
            #    df = df[df['class1'] == 'R']
            # filtr na translocation!!!
            if df.shape[1] in df.columns:
                df = df[df['class1'].isin(['SV', 'SV-R'])]
            if col in df.columns:
                nonempty_vals = df[col].dropna()
                nonempty_vals = nonempty_vals[nonempty_vals.astype(str).str.strip() != '']
                count = len(nonempty_vals)
                if count > 0:
                    total_nonempty += count
                    all_unique_values.update(nonempty_vals.astype(str))
                    print(f"- {file.name} | {sheet} : {count} neprázdných hodnot")

    print(f"\nCelkově neprázdných hodnot: {total_nonempty}")
    print(f"Ukázka unikátních hodnot: {list(all_unique_values)[:10]}")
