import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import re

# --- Folder paths ---
folder = Path(__file__).parent / 'TRANSLOKACE_PRESTAVBA_DLBCL'
seznam = Path(__file__).parent / 'seznam_dlbcl.csv'
timestamp = datetime.now().strftime("%d%m%Y")
output_file = Path(__file__).parent / f'merged_data_rearrangement_dlbcl_{timestamp}.xlsx'

# Read the input file
sample_table = pd.read_csv(seznam, sep=',', encoding='utf-8', names=['Run', 'Sample'], header=None)
files = list(folder.glob('*.xlsx'))

# sort of columns
columns_sort = ['run', 'sample', 'diagnosis', 'comments', 'in FASTQs', 'duplicated', 'mapped', 'on target',	
                'usable', 'rearrangement class', 'locus', 'V gene',	'D gene', 'J gene',	
                '%locus', '%class', 'fragments', 'locus sum', 'segmentation', 'junction', 'junction nt seq',	
                'sequence context',]

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
            #sheet_df = sheet_df.applymap(strip_html)
            sheet_df = sheet_df.map(strip_html)
            # Přidat sloupce sample, diagnosis a run
            sheet_df['sample'] = sheet_base
            sheet_df['diagnosis'] = 'DLBCL'
            sheet_df['run'] = run_name
            sheet_df['V gene'] = ''
            sheet_df['D gene'] = ''
            sheet_df['J gene'] = ''

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
                # Prefer 'gene partner' values for 'J gene'
                #sheet_df['J gene'] = sheet_df['gene partner'].apply(lambda x: extract_gene_type(x, 'J'))
                # Update 'V gene' and 'D gene' if 'gene partner' has relevant info
                #sheet_df['V gene'] = sheet_df['V gene'].fillna(sheet_df['gene partner'].apply(lambda x: extract_gene_type(x, 'V')))
                #sheet_df['D gene'] = sheet_df['D gene'].fillna(sheet_df['gene partner'].apply(lambda x: extract_gene_type(x, 'D')))
                partner_V = sheet_df['gene partner'].map(lambda x: extract_gene_type(x, 'V'))
                partner_D = sheet_df['gene partner'].map(lambda x: extract_gene_type(x, 'D'))
                partner_J = sheet_df['gene partner'].map(lambda x: extract_gene_type(x, 'J'))

                sheet_df['V gene'] = sheet_df['V gene'].fillna(partner_V)
                sheet_df['D gene'] = sheet_df['D gene'].fillna(partner_D)
                sheet_df['J gene'] = sheet_df['J gene'].fillna(partner_J)

            #print(f'filter columns: \n {sheet_df.columns}')

            # Filtrovat na SV ve sloupci 11 (index 10)
            #if sheet_df.shape[1] > 10:
            #    sheet_df = sheet_df[sheet_df.iloc[:, 10] == 'R']
            if 'class1' in sheet_df.columns:
                sheet_df = sheet_df[sheet_df['class1'] == 'R']
            merged_df = pd.concat([merged_df, sheet_df], ignore_index=True)
            print(f'Added sheet: {sheet_name} (base: {sheet_base}) from file: {file.name}')

# Do something with the merged DataFrame
print(merged_df.head())

# Rename columns
merged_df = merged_df.rename(columns={
    'class2': 'rearrangement class',
    '%': '%locus',
    'event1': 'segmentation'
})

# Přeskládat sloupce: run, sample, diagnosis, ostatní
exclude_cols = ['gene', 'gene partner', 'report','QC','clonal','class1','coord','coord partner', 'depth(s)','event2','event3','event comments','generic BAM','special BAM',]
#cols = ['run', 'sample', 'diagnosis'] + [col for col in merged_df.columns if col not in ['run', 'sample', 'diagnosis'] + exclude_cols]
cols = [col for col in merged_df.columns if col not in exclude_cols]
cols_sort = [col for col in columns_sort if col in cols]
final_df = merged_df[cols_sort]

# save the merged dataframe to an Excel file
final_df.to_excel(output_file, index=False)
print(f'Merged data saved to {output_file}')
