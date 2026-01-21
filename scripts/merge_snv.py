from html.entities import html5
from io import StringIO
from bs4 import BeautifulSoup
import re, html
import sys
import pandas as pd
import numpy as np
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
#diagnosis = sys.argv[1] if len(sys.argv) > 1 else "MM" # default MM if not provided
DIAGNOSIS = DIAGNOSIS.upper()
dx_upper = DIAGNOSIS.upper()
dx_lower = DIAGNOSIS.lower()

# ---- Folder with files ----
folder = root / dx_upper
csv_file = root / f'seznam_{dx_lower}.csv'
timestamp = datetime.now().strftime("%d%m%Y")
output_file = root / 'output' / f'merged_data_snv_{dx_lower}_{timestamp}.xlsx'

# Read the samples and run from seznam.csv
sample_table = pd.read_csv(csv_file, sep=',', header=None, names=['Run', 'Sample'])
sample_table['Run'] = sample_table['Run'].astype(str).str.strip()
sample_table['Sample'] = sample_table['Sample'].astype(str).str.strip()

sample_table['Filename'] = sample_table['Run'] + "_" + sample_table['Sample']

print(f"sample_table shape: {sample_table}")

# Get all files
files = list(folder.glob('*.mutect2.cons.filt.norm.vep.csv'))
cyto_file = root / "cytoBand_hg38.txt"
cyto = pd.read_csv(cyto_file, sep="\t")
print(f"Found {len(files)} files in {folder}")

# sort of columns
columns_sort = ['comments', 'gene_symbol', 'genome_build', 'Chromosome', 'Start_Position', 'Variant_Classification', 'Variant_Type', 'Reference_Allele', 
                'Tumor_Seq_Allele2', 'HGVSc', 'HGVSp', 'feature_type', 'Transcript_ID', 'MANE_SELECT', 'MANE_PLUS_CLINICAL', 'Exon_Number', 'tumor_DP', 
                'tumor_AD_ref', 'tumor_AD_alt', 'tumor_AF', 'normal_DP', 'normal_AD_ref', 'normal_AD_alt', 'normal_AF', 'strand_bias', 'alt_transcripts', 
                'Codons', 'Existing_variation', 'BIOTYPE', 'CANONICAL', 'SIFT', 'PolyPhen', 'clinvar', 'IMPACT', 'af', 'eur_af', 'gnomadg_af', 'gnomad_af', 
                'gnomadg_nfe_af', 'gnomad_nfe_af', 'max_af', 'max_af_pops', 'pubmed'
]

# normalize allele frequency columns because of comma vs dot
def normalize_af_cols(df, cols, dec_places=4):
    def _norm_series(s):
        s = s.astype(str).str.strip()

        # if the column is empty, return it as is
        multi_mask = s.str.contains(',')

        # simple values → to float → back to text with dot
        single = pd.to_numeric(s[~multi_mask].str.replace(',', '.', regex=False),
                                errors='coerce')
        single = single.map(
            lambda x: f"{x:.{dec_places}f}" if not np.isnan(x) else ''
        )

        out = s.copy()
        out.update(single)
        return out

    for c in cols:
        df[c] = _norm_series(df[c])

    return df

# ---- Merge files ----
merged_dataframes = []

for file in files:
    print(f'\n{"-"*40}\n')

    print(f"Processing {file.name}")

    #sample_name = file.stem.replace('.csv', '').replace('.vep', '').replace('.norm', '').replace('.filt', '').replace('.cons', '').replace('.mutect2', '')
    #print(f"Sample name extracted: {sample_name}")

    filename_stem = file.stem
    sample_name = filename_stem.split('.')[0]
    print(f"Processing {filename_stem}")

    match = sample_table[sample_table['Filename'] == sample_name]

    #match = sample_table[sample_table['Sample'] == sample_name]
    #print(f"Matching sample: {match}")

    with open(file, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # Remove HTML tags from the entire text
    soup = BeautifulSoup(raw_text, "lxml")
    cleaned_text = soup.get_text(separator="\n")
    cleaned_text = html.unescape(cleaned_text)
    cleaned_text = re.sub(r'[ \t\u00A0]+', ' ', cleaned_text).strip()
    # cleaned_text = re.sub(r'<div><div[^>]*>([^<]+)</div></div>', r'\1', raw_text)
    
    '''
    def strip_html_text(val):
        if pd.isna(val):
            return val
        val = re.sub(r'<[^>]*>', '', str(val))
        val = html5().unescape(val)
        #val = html.unescape(val) 
        val = re.sub(r'\s+', ' ', val).strip() 
        return val
    '''

    run = match.iloc[0]['Run']

    df = pd.read_csv(file, sep='\t')
    print(f"\nDataFrame shape after reading {file.name}: {df.shape}")
    print(f"DataFrame columns after reading {file.name}: {df.columns.tolist()}")
    #df = pd.read_csv(file, sep=',', encoding='utf-8')
    #df = pd.read_csv(StringIO(cleaned_text), sep=',', dtype=str, low_memory=False)

    #df['Chromosome'] = df['Chromosome'].astype(str).str.strip()

    #df = pd.read_csv(file, sep=',', dtype={'Chromosome': str}, low_memory=False)
    #print(df['Chromosome'].dtype)

    print(f"\nDataFrame shape after reading {file.name}: {df.shape}")
    
    df = pd.read_csv(StringIO(cleaned_text), sep=',', dtype=str, low_memory=False)
    
    print(f"\nDataFrame head after cleaning HTML from {file.name}:")
    print(df.head(0)) 
    
    for col in columns_sort:
        if col not in df.columns:
            df[col] = ''
    df = df[[col for col in columns_sort if col in df.columns]]

    df.insert(loc=0, column='run', value=run)
    #df.insert(loc=1, column='sample', value=sample_name)
    df.insert(loc=1, column='sample', value=match.iloc[0]['Sample'])
    df.insert(loc=2, column='diagnosis', value=DIAGNOSIS)

    print(f"\nDataFrame head after processing {file.name}:")
    print(df.head(0))

    merged_dataframes.append(df)

final_df = pd.concat(merged_dataframes, ignore_index=True)
print("\nFinal merged DataFrame head:")
print(final_df.head(0))

# connect two columns, version with ends 'g' is the newer
#final_df['gnomadg_af'].replace('', np.nan, inplace=True)
final_df['gnomadg_af'] = final_df['gnomadg_af'].replace('', np.nan)
final_df['gnomadg_af'] = final_df['gnomadg_af'].fillna(final_df['gnomad_af'])

#final_df['gnomadg_nfe_af'].replace('', np.nan, inplace=True)
final_df['gnomadg_nfe_af'] = final_df['gnomadg_nfe_af'].replace('', np.nan)
final_df['gnomadg_nfe_af'] = final_df['gnomadg_nfe_af'].fillna(final_df['gnomad_nfe_af'])

final_df.drop(columns=['gnomad_af', 'gnomad_nfe_af'], inplace=True)

cols_to_fix = ['tumor_AF', 'af', 'eur_af', 'gnomadg_af', 'gnomadg_nfe_af', 'max_af']
final_df = normalize_af_cols(final_df, cols_to_fix)

# ---- Save merged data ----
final_df.to_excel(output_file, index=False)
print(f"Merged {final_df.shape[0]} files into {output_file.name}")

# control number of rows 
# wc -l *.mutect2.cons.filt.norm.vep.csv
# soubory majici hlavicku zacinajici chromosome nepocita prvni radek - potreba pricist +1
# porovnat s unique_heads.txt ze skriptu columns.sh
