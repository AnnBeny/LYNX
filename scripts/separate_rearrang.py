import pandas as pd
import sys
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

# python separate_rearrang.py [ALL|DLBCL|CLL|MM]
#diagnosis = sys.argv[1] if len(sys.argv) > 1 else "MM" # default MM if not provided
DIAGNOSIS = DIAGNOSIS.upper()
dx_upper = DIAGNOSIS.upper()
dx_lower = DIAGNOSIS.lower()

# --- Folder paths ---
#folder = root / f'TRANSLOKACE_PRESTAVBA_{dx_upper}'
folder = root / f'{dx_upper}'
seznam = root / f'seznam_{dx_lower}.csv'
timestamp = datetime.now().strftime("%d%m%Y")
output_file = Path(__file__).parents[1] / 'output' / f'merged_data_rearrangement_{dx_lower}_{timestamp}.xlsx'

print(f"Diagnosis: {dx_upper}, List: {seznam}, Input file: {folder}, Output file: {output_file}")

# Read the input file
sample_table = pd.read_csv(seznam, sep=',', encoding='utf-8', names=['Run', 'Sample'], header=None, dtype=str)
files = list(folder.glob('*.xlsx'))

print(f"Sample table shape: {sample_table.shape}")
print(f"Found {len(files)} files in {folder}")

# Sort of columns
columns_sort = ['run', 'sample', 'diagnosis', 'comments', 'in FASTQs', 'duplicated', 'mapped', 'on target',
                'usable', 'rearrangement class', 'locus', 'V gene', 'D gene', 'J gene',
                '%locus', '%class', 'fragments', 'locus sum', 'segmentation', 'junction', 'junction nt seq',
                'sequence context']

# --- Merge all sheets from the first file ---
merged_df = pd.DataFrame()

for file in files:
    print(f'\n{"-"*40}\n')

    print(f'Processing file: \n {file.name}')

    xls = pd.ExcelFile(file)
    print(f'Found sheets: \n {xls.sheet_names}')

    # Extract run name from the file name
    run_name = file.stem.replace('.gathered.xlsx', '')
    run_name = run_name.replace('.gathered', '')
    if run_name not in sample_table['Run'].values:
        print(f'Run {run_name} not found in sample table. Skipping file {file.name}.')
        continue

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
            print(f'Processing sheet: {sheet_df.columns} from file: {file.name}')
            # Remove HTML tags from all cells
            def strip_html(val):
                if isinstance(val, str):
                    return re.sub(r'<[^>]*>', '', val)
                return val
            #sheet_df = sheet_df.applymap(strip_html)
            sheet_df = sheet_df.map(strip_html)
            print(f'Columns after HTML stripping: \n {sheet_df.columns}')
            # Add columns sample, diagnosis and run
            sheet_df['sample'] = sheet_base
            sheet_df['diagnosis'] = 'MM'
            sheet_df['run'] = run_name
            sheet_df['V gene'] = ''
            sheet_df['D gene'] = ''
            sheet_df['J gene'] = ''
            print(f'Columns after adding sample, diagnosis, run: \n {sheet_df.columns}')

            # Rename columns to match the desired output
            sheet_df = sheet_df.rename(columns={'%locus': '%'})
            print(f'Columns after renaming: \n {sheet_df.columns}')

            # Change column types to string to avoid issues with NaN
            #sheet_df['comments'] = sheet_df['comments'].astype(str)
            sheet_df['comments'] = sheet_df['comments'].apply(lambda x: str(x) if pd.notnull(x) else '')
            print(f'Comments column types after conversion: {sheet_df["comments"].dtype}')

            # Function to extract gene type based on position 4
            def extract_gene_type(gene, gene_type):
                if isinstance(gene, str) and len(gene) >= 4:
                    if gene[3] == gene_type:
                        return gene
                return None

            # Process 'gene' column (column 12)
            #if 'gene' in sheet_df.columns:
            #    sheet_df['V gene'] = sheet_df['gene'].apply(lambda x: extract_gene_type(x, 'V'))
            #    sheet_df['D gene'] = sheet_df['gene'].apply(lambda x: extract_gene_type(x, 'D'))
            #    sheet_df['J gene'] = sheet_df['gene'].apply(lambda x: extract_gene_type(x, 'J'))
            sheet_df['V gene'] = sheet_df['gene'].map(lambda x: extract_gene_type(x, 'V'))
            sheet_df['D gene'] = sheet_df['gene'].map(lambda x: extract_gene_type(x, 'D'))
            sheet_df['J gene'] = sheet_df['gene'].map(lambda x: extract_gene_type(x, 'J'))

            # Process 'gene partner' column (column 13)
            if 'gene partner' in sheet_df.columns:
                partner_V = sheet_df['gene partner'].map(lambda x: extract_gene_type(x, 'V'))
                partner_D = sheet_df['gene partner'].map(lambda x: extract_gene_type(x, 'D'))
                partner_J = sheet_df['gene partner'].map(lambda x: extract_gene_type(x, 'J'))

                sheet_df['V gene'] = sheet_df['V gene'].fillna(partner_V)
                sheet_df['D gene'] = sheet_df['D gene'].fillna(partner_D)
                sheet_df['J gene'] = sheet_df['J gene'].fillna(partner_J)
            print(f'Columns after processing gene and gene partner: \n {sheet_df.columns}')

            #print(f'filter columns: \n {sheet_df.columns}')

            # Filter R in column 11 (index 10) = class1
            if 'class1' in sheet_df.columns:
                sheet_df = sheet_df[sheet_df['class1'] == 'R']
            merged_df = pd.concat([merged_df, sheet_df], ignore_index=True)
            print(f'Merged dataframe shape: {merged_df.columns}')
            print(f'Added sheet: {sheet_name} (base: {sheet_base}) from file: {file.name}')

print(merged_df.head())
print(f'Columns before merge and rename: \n {merged_df.columns}')

# Rename columns
merged_df = merged_df.rename(columns={
    'class2': 'rearrangement class',
    '%': '%locus',
    'event1': 'segmentation'
})

print(f'Columns after merge and rename: \n {merged_df.columns}')

# Rearrange columns: run, sample, diagnosis, others
exclude_cols = ['gene', 'gene partner', 'report','QC','clonal','class1','coord','coord partner', 'depth(s)','event2','event3','event comments','generic BAM','special BAM',]
#cols = ['run', 'sample', 'diagnosis'] + [col for col in merged_df.columns if col not in ['run', 'sample', 'diagnosis'] + exclude_cols]
cols = [col for col in merged_df.columns if col not in exclude_cols]
print(f'Columns after exclusion: \n {cols}')
cols_sort = [col for col in columns_sort if col in cols]
print(f'Final sorted columns: \n {cols_sort}')
final_df = merged_df[cols_sort]
print(f'Final dataframe shape: {final_df}')

# save the merged dataframe to an Excel file
final_df.to_excel(output_file, index=False)
print(f'Merged data saved to {output_file}')
