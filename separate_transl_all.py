# do coor se přidavaji jmena genu asi z gene_partner - opravit
# coord partner, depth, event3  jsou prazdne - ma být ?
# event comments asi smichane s něčim jinym


import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import re

# --- Folder paths ---
folder = Path(__file__).parent / 'TRANSLOKACE_PRESTAVBA_ALL'
seznam = Path(__file__).parent / 'seznam_all.csv'
timestamp = datetime.now().strftime("%d%m%Y")
output_file = Path(__file__).parent / f'merged_data_translocations_all_{timestamp}.xlsx'

# Read the input file
sample_table = pd.read_csv(seznam, sep=',', encoding='utf-8', names=['Run', 'Sample'], header=None,  dtype=str)
files = list(folder.glob('*.xlsx'))

# sort of columns
columns_sort = ['run', 'sample', 'diagnosis', 'comments', 'in FASTQs', 'duplicated', 'mapped', 'on target', 
                'usable', 'gene', 'gene partner', 'coord', 'coord partner', 'frequency', '%class', 
                'fragments', 'depth(s)', 'gene / gene partner', 'sequence context']

# --- Merge all sheets from the first file ---
merged_df = pd.DataFrame()

for file in files:
    print(f'Processing file: \n {file.name}')

    xls = pd.ExcelFile(file)
    print(f'Found sheets: \n {xls.sheet_names}')

    # Extract run name from the file name
    run_name = file.stem.replace('.gathered.xlsx', '')
    run_name = run_name.replace('.gathered', '')
    #print(f"Looking for run_name: {run_name} in {sample_table['Run'].tolist()}")

    if run_name not in sample_table['Run'].values:
        print(f'Run {run_name} not found in sample table. Skipping file {file.name}.')
        continue

    # Získat sample pro tento run
    sample_row = sample_table[sample_table['Run'] == run_name]
    if sample_row.empty:
        print(f'No sample found for run {run_name}. Skipping file {file.name}.')
        continue
    samples = sample_row['Sample'].values

    for sheet_name in xls.sheet_names:
        sheet_base = sheet_name
        if sheet_base.endswith('_R1'):
            sheet_base = sheet_base[:-3]
        if sheet_base in samples:
            sheet_df = pd.read_excel(xls, sheet_name=sheet_name)
            # Odstranit HTML tagy ze všech buněk
            def strip_html(val):
                if isinstance(val, str):
                    return re.sub(r'<[^>]*>', '', val)
                return val
            sheet_df = sheet_df.map(strip_html)
            # Přidat sloupce sample, diagnosis a run
            sheet_df['sample'] = sheet_base
            sheet_df['diagnosis'] = 'ALL'
            sheet_df['run'] = run_name

            # Filtrovat na SV nebo SV-R ve sloupci 11 (index 10)
            if sheet_df.shape[1] > 10:
                sheet_df = sheet_df[sheet_df.iloc[:, 10].isin(['SV', 'SV-R'])]
            merged_df = pd.concat([merged_df, sheet_df], ignore_index=True)
            print(f'Added sheet: {sheet_name} (base: {sheet_base}) from file: {file.name}')

# Do something with the merged DataFrame
print(merged_df.head())

# Rename columns
merged_df = merged_df.rename(columns={
    '%': 'frequency',
    'event1': 'gene / gene partner'
})

# Přeskládat sloupce: run, sample, diagnosis, ostatní
#cols = ['run', 'sample', 'diagnosis'] + [col for col in merged_df.columns if col not in ['run', 'sample', 'diagnosis']]
cols_sort = [col for col in columns_sort]
final_df = merged_df[cols_sort]

# save the merged dataframe to an Excel file
final_df.to_excel(output_file, index=False)
print(f'Merged data saved to {output_file}')
