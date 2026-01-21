import pandas as pd
import sys
import logging
from pathlib import Path
from datetime import datetime

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

# python merge_cna.py [ALL|DLBCL|CMM]
DIAGNOSIS = DIAGNOSIS.upper()
dx_upper = DIAGNOSIS.upper()
dx_lower = DIAGNOSIS.lower()

# logging configuration
parent_dir = Path(__file__).resolve().parent.parent
log_dir = parent_dir / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_path = parent_dir / f"cnv_{dx_lower}.log"

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logging.info("Spuštění skriptu")

# ---- Folder with files ----
folder = root / dx_upper
csv_file = root / f'seznam_{dx_lower}.csv'
timestamp = datetime.now().strftime("%d%m%Y")
output_file = root / 'output' / f'merged_data_cna_{dx_lower}_{timestamp}.xlsx'

# Read the samples and run from seznam.csv
sample_table = pd.read_csv(csv_file, sep=',', header=None, names=['Run', 'Sample'])
sample_table['Run'] = sample_table['Run'].astype(str).str.strip()
sample_table['Sample'] = sample_table['Sample'].astype(str).str.strip()

#sample_table['Filename'] = sample_table['Run'] + "_" + sample_table['Sample']
sample_table['Filename'] = sample_table['Run'].astype(str) + "_" + sample_table['Sample'].astype(str)


print(f"sample_table shape: {sample_table}")

# Get all files
files = list(folder.glob('*.call.cns'))
cyto_file = root / "cytoBand_hg38.txt"
cyto = pd.read_csv(cyto_file, sep="\t")
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

    #sample_name = file.stem.replace('.call.cns', '')
    #sample_name = file.stem.replace('.call', '')
    #print(f"Sample name extracted: {sample_name}")
    
    filename_stem = file.stem.replace('.call', '')
    print(f"Processing {filename_stem}")

    # match = sample_table[sample_table['Sample'] == sample_name]
    match = sample_table[sample_table['Filename'] == filename_stem]
    #print(f"Matching sample: {match}")

    if match.empty:
        print(f"No matching sample found for {file.name}, skipping.")
        continue

    run = match.iloc[0]['Run']
    sample_name = match.iloc[0]['Sample']

    df = pd.read_csv(file, sep='\t')
    #print(f"DataFrame shape after reading {file.name}: {df.shape}")

    if 'comments' not in df.columns:
        df.insert(loc=3, column='comments', value='')

    for col in columns_sort:
        if col not in df.columns:
            df[col] = ''

    df['run'] = run
    df['sample'] = sample_name
    df['diagnosis'] = dx_upper

    df = df[[col for col in columns_sort if col in df.columns]]

    # Rename columns
    df = df.rename(columns={
        'probes': 'bins',
        'gene': 'LPD genes'
    })

    # cytoBand
    # axis=1 applies the function to each row, lambda x represents the row, get_cytoband is called with the appropriate parameters, x['start'] and x['chromosome'] extract the values from the row
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
print("Log vytvořen:", log_path.name)

# control number of rows 
# awk 'tolower($1) ~ /^(comments|chromosome)$/ { next }  NF { count[FILENAME]++ }  END {for (f in count) {printf "%s\t%d\n", f, count[f]}  }' *.call.cns | sort - pro jednotlive soubory
# wc -l *.call.cns - pro všechny dohromady
# soubory majici hlavicku zacinajici chromosome nepocita prvni radek - potreba pricist +1
# porovnat s unique_heads.txt ze skriptu columns.sh
