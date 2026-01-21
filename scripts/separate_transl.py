import pandas as pd
import sys
import argparse
from pathlib import Path
from datetime import datetime
import re

root = Path(__file__).parents[1]

# parameters for choosing of input data
def choose(prompt, options, default=None):
    print(prompt)
    for i, opt in enumerate(options, start=1):
        print(f"{i}. {opt}")
    choice = input(f"Enter choice (1-{len(options)}): ").strip()
    if not choice and default is not None:
        return default
    try:
        index = int(choice)
        # allow choice up to len(options)
        if 1 <= index <= len(options):
            return options[index-1]
    except ValueError:
        pass
    print("Invalid choice. Please try again.")
    return choose(prompt, options, default)

DIAGNOSIS = choose("Select diagnosis:", ["ALL","DLBCL","CLL","MM"], default="ALL")

#parser = argparse.ArgumentParser(description="Process some integers.")
#parser.add_argument("diagnosis", choices=["ALL", "DLBCL", "CLL", "MM"], default="ALL", nargs="?", help="Diagnosis type")
#args = parser.parse_args()

# python separate_rearrang.py [ALL|DLBCL|CLL|MM]
#diagnosis = args.diagnosis
DIAGNOSIS = DIAGNOSIS.upper()
dx_upper = DIAGNOSIS.upper()
dx_lower = DIAGNOSIS.lower()

print(f"Diagnosis: {dx_upper}, List: seznam_{dx_lower}.csv, Input file: {dx_upper}")

# --- Folder paths ---
#folder = root / f'TRANSLOKACE_PRESTAVBA_{dx_upper}'
folder = root / f'{dx_upper}'
seznam = root / f'seznam_{dx_lower}.csv'
timestamp = datetime.now().strftime("%d%m%Y")
output_file = root / 'output' / f'merged_data_translocations_{dx_lower}_{timestamp}.xlsx'

print(f"Diagnosis: {dx_upper}, List: {seznam}, Input file: {folder}, Output file: {output_file}")

# Read the input file
sample_table = pd.read_csv(seznam, sep=',', encoding='utf-8', names=['Run', 'Sample'], header=None,  dtype=str)
files = list(folder.glob('*.xlsx'))

print(f"Sample table shape: {sample_table.shape}")
print(f"Found {len(files)} files in {folder}")

# Sort of columns
columns_sort = ['run', 'sample', 'diagnosis', 'comments', 'in FASTQs', 'duplicated', 'mapped', 'on target', 
                'usable', 'gene', 'gene partner', 'coord', 'coord partner', 'frequency', '%class', 
                'fragments', 'depth(s)', 'gene / gene partner', 'sequence context']

# --- Merge all sheets from the first file ---
merged_df = pd.DataFrame()

for file in files:
    print(f'{"-"*150}')
    
    print(f'Processing file: \n {file.name}')

    xls = pd.ExcelFile(file)
    print(f'Found sheets: \n {xls.sheet_names}')

    # Extract run name from the file name
    run_name = file.stem.replace('.gathered.xlsx', '')
    run_name = run_name.replace('.gathered', '')
    #print(f"Looking for run_name: {run_name} in {sample_table['Run'].tolist()}")

    # Get sample for this run
    sample_row = sample_table[sample_table['Run'] == run_name]
    if sample_row.empty:
        print(f'No sample found for run {run_name}. Skipping file {file.name}.')
        continue
    samples = sample_row['Sample'].values

    for sheet_name in xls.sheet_names:
        sheet_base = sheet_name
        if sheet_base.endswith('_R1'):
            #sheet_base = sheet_base[:-3]
            sheet_base: str = sheet_base.removesuffix('_R1')
        if sheet_base in samples:
            sheet_df = pd.read_excel(xls, sheet_name=sheet_name)
            # Remove HTML tags from all cells
            def strip_html(val):
                if isinstance(val, str):
                    return re.sub(r'<[^>]*>', '', val)
                return val
            sheet_df = sheet_df.map(strip_html)
            # Add columns sample, diagnosis and run
            sheet_df['sample'] = sheet_base
            sheet_df['diagnosis'] = DIAGNOSIS
            sheet_df['run'] = run_name

            # Filterovat SV (SV-R) in column 11 (index 10)
            if sheet_df.shape[1] > 10:
                #sheet_df = sheet_df[sheet_df.iloc[:, 10].isin(['SV', 'SV-R'])]
                sheet_df = sheet_df[sheet_df.iloc[:, 10].isin(['SV'])]
            merged_df = pd.concat([merged_df, sheet_df], ignore_index=True)
            print(f'Added sheet: {sheet_name} (base: {sheet_base}) from file: {file.name}')

print(merged_df.head())

# Rename columns
merged_df = merged_df.rename(columns={
    '%': 'frequency',
    'event1': 'gene / gene partner'
})

# Rearrange columns: run, sample, diagnosis, others
#cols = ['run', 'sample', 'diagnosis'] + [col for col in merged_df.columns if col not in ['run', 'sample', 'diagnosis']]
cols_sort = [col for col in columns_sort]
final_df = merged_df[cols_sort]

# Save the merged dataframe to an Excel file
final_df.to_excel(output_file, index=False)
print(f'Merged data saved to {output_file}')
