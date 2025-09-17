import pandas as pd
import sys
from pathlib import Path
from datetime import datetime


# ---- Folder with files ----
folder = Path(__file__).parent / 'DLBCL'
csv_file = Path(__file__).parent / 'seznam_dlbcl.csv'
timestamp = datetime.now().strftime("%d%m%Y")
output_file = Path(__file__).parent / f'merged_data_cna_dlbcl_{timestamp}.xlsx'

# Read the samples and run from seznam.csv
sample_table = pd.read_csv(csv_file, sep=',', header=None, names=['Run', 'Sample'])
sample_table['Run'] = sample_table['Run'].astype(str).str.strip()
sample_table['Sample'] = sample_table['Sample'].astype(str).str.strip()

print(f"sample_table shape: {sample_table}")

# Get all files
files = list(folder.glob('*.call.cns'))
cyto = pd.read_csv("cytoBand_hg38.txt", sep="\t")
print(f"Found {len(files)} files in {folder}")

# sort of columns
columns_sort = ['run', 'sample', 'diagnosis', 'comments', 'chromosome', 'start', 'end', 'cyt_start', 'cyt_end', 'length',
                 'gene', 'log2', 'baf', 'cn', 'cn1', 'cn2', 'depth', 'loh', 'probes', 'var num', 'weight'
]

# ---- Merge files ----
merged_dataframes = []

def get_cytoband(pos, chrom, cyto_df):
    match = cyto_df[
        (cyto_df['CHR'] == chrom) &
        (cyto_df['from'] <= pos) &
        (cyto_df['to'] > pos)
    ]
    return match['arm'].values[0] if not match.empty else None

for file in files:
    print(f"Processing {file.name}")

    sample_name = file.stem.replace('.call.cns', '')
    sample_name = file.stem.replace('.call', '')
    print(f"Sample name extracted: {sample_name}")

    match = sample_table[sample_table['Sample'] == sample_name]
    #print(f"Matching sample: {match}")

    if match.empty:
        print(f"No matching sample found for {file.name}, skipping.")
        continue

    run = match.iloc[0]['Run']

    df = pd.read_csv(file, sep='\t')
    #print(f"DataFrame shape after reading {file.name}: {df.shape}")

    if 'comments' not in df.columns:
        df.insert(loc=3, column='comments', value='')

    for col in columns_sort:
        if col not in df.columns:
            df[col] = ''

    df['run'] = run
    df['sample'] = sample_name
    df['diagnosis'] = 'DLBCL'

    df = df[[col for col in columns_sort if col in df.columns]]

    # Rename columns
    df = df.rename(columns={
        'probes': 'bins',
        'gene': 'LPD genes'
    })

    # cytoBand
    df['cyt_start'] = df.apply(lambda x: get_cytoband(x['start'], x['chromosome'], cyto), axis=1)
    df['cyt_end'] = df.apply(lambda x: get_cytoband(x['end'], x['chromosome'], cyto), axis=1)

    df['start'] = pd.to_numeric(df['start'], errors='coerce')
    df['end'] = pd.to_numeric(df['end'], errors='coerce')
    df['length'] = df['end'] - df['start']

    merged_dataframes.append(df)

merged_dataframes = [df for df in merged_dataframes if not df.empty]

if not merged_dataframes:
    print("No dataframes to merge. Exiting.")
    sys.exit()

final_df = pd.concat(merged_dataframes, ignore_index=True)

# ---- Save merged data ----
final_df.to_excel(output_file, index=False)
print(f"Merged {final_df.shape[0]} files into {output_file.name}")


# control number of rows 
# wc -l *.call.cns
# soubory majici hlavicku zacinajici chromosome nepocita prvni radek - potreba pricist +1
# porovnat s unique_heads.txt ze skriptu columns.sh
