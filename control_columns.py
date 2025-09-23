import pandas as pd
from pathlib import Path

folder = Path(__file__).parent / 'ALL'
columns_to_check = ['normal_DP', 'normal_AD_ref', 'normal_AD_alt', 'normal_AF']
files = list(folder.glob('*.vep.csv'))

for col in columns_to_check:
    nonempty_count = 0
    unique_values = set()
    for file in files:
        df = pd.read_csv(file, sep=',')
        if col in df.columns:
            vals = df[col].dropna().unique()
            vals = [v for v in vals if str(v).strip() != '']
            if vals:
                nonempty_count += 1
                unique_values.update(vals)

    print(f"\nSloupec: {col}")
    print(f" V {nonempty_count} souborech je alespoň 1 neprázdná hodnota.")
    print(f" Ukázka hodnot: {list(unique_values)[:10]}")
