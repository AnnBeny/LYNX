import pandas as pd
import numpy as np
import re
from io import StringIO
from pathlib import Path

# ---- Folder with files ----
folder = Path(__file__).parent / 'CLL'
csv_file = Path(__file__).parent / 'seznam_cll.csv'
output_file = Path(__file__).parent / 'merged_data_snv_cll.xlsx'

# Read the samples and run from seznam.csv
sample_table = pd.read_csv(csv_file, sep=',', header=None, names=['Run', 'Sample'])
sample_table['Run'] = sample_table['Run'].astype(str).str.strip()
sample_table['Sample'] = sample_table['Sample'].astype(str).str.strip()

print(f"sample_table shape: {sample_table}")

# Get all files
files = list(folder.glob('*.mutect2.cons.filt.norm.vep.csv'))
print(f"Found {len(files)} files in {folder}")

# sort of columns
columns_sort = ['comments', 'gene_symbol', 'genome_build', 'Chromosome', 'Start_Position', 'Variant_Classification', 'Variant_Type', 'Reference_Allele', 
                'Tumor_Seq_Allele2', 'HGVSc', 'HGVSp', 'feature_type', 'Transcript_ID', 'MANE_SELECT', 'MANE_PLUS_CLINICAL', 'Exon_Number', 'tumor_DP', 
                'tumor_AD_ref', 'tumor_AD_alt', 'tumor_AF', 'normal_DP', 'normal_AD_ref', 'normal_AD_alt', 'normal_AF', 'strand_bias', 'alt_transcripts', 
                'Codons', 'Existing_variation', 'BIOTYPE', 'CANONICAL', 'SIFT', 'PolyPhen', 'clinvar', 'IMPACT', 'af', 'eur_af', 'gnomadg_af', 'gnomad_af', 
                'gnomadg_nfe_af', 'gnomad_nfe_af', 'max_af', 'max_af_pops', 'pubmed'
]

# ---- Merge files ----
merged_dataframes = []

for file in files:
    print(f"Processing {file.name}")

    sample_name = file.stem.replace('.csv', '').replace('.vep', '').replace('.norm', '').replace('.filt', '').replace('.cons', '').replace('.mutect2', '')
    print(f"Sample name extracted: {sample_name}")

    match = sample_table[sample_table['Sample'] == sample_name]
    #print(f"Matching sample: {match}")

    with open(file, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    cleaned_text = re.sub(r'<div><div[^>]*>([^<]+)</div></div>', r'\1', raw_text)

    if match.empty:
        print(f"No matching sample found for {file.name}, skipping.")
        continue

    run = match.iloc[0]['Run']

    #print(f"Number of cleaned lines: {len(cleaned_lines)}")
    #print(f"First 5 cleaned lines: {cleaned_lines[:5]}")

    # <div><div class=t-td" role="gridcell" style="flex-grow: 103.409; flex-basis: auto; transition-behavior: normalnormalnormalnormal; transition-duration: 0.3s0s0s0s; transition-timing-function: easeeaseeaseease; transition-delay: 0s0s0s0s; border-right: 1px solid rgba(000.02); cursor: auto; width: 103.409px; max-width: 300px;">polym</div></div>

    #df = pd.read_csv(file, sep='\t')
    df = pd.read_csv(StringIO(cleaned_text), sep=",")
    #print(df.head(10))
    #df = pd.read_csv(file, sep=',')
    #print(f"DataFrame shape after reading {file.name}: {df.shape}")
    
    for col in columns_sort:
        if col not in df.columns:
            df[col] = ''
    df = df[[col for col in columns_sort if col in df.columns]]

    df.insert(loc=0, column='run', value=run)
    df.insert(loc=1, column='sample', value=sample_name)
    df.insert(loc=2, column='diagnosis', value='CLL')

    merged_dataframes.append(df)

final_df = pd.concat(merged_dataframes, ignore_index=True)

# connect two columns, version with ends 'g' is the newer
#final_df['gnomadg_af'] = final_df['gnomadg_af'].replace('', np.nan)
#final_df['gnomadg_af'] = final_df['gnomadg_af'].fillna(final_df['gnomad_af'])

#final_df['gnomadg_nfe_af'] = final_df['gnomadg_nfe_af'].replace('', np.nan)
#final_df['gnomadg_nfe_af'] = final_df['gnomadg_nfe_af'].fillna(final_df['gnomad_nfe_af'])

#final_df.drop(columns=['gnomad_af', 'gnomad_nfe_af'], inplace=True)

# ---- Save merged data ----
final_df.to_excel(output_file, index=False)
print(f"Merged {final_df.shape[0]} files into {output_file.name}")


# control number of rows 
# wc -l *.mutect2.cons.filt.norm.vep.csv
# soubory majici hlavicku zacinajici chromosome nepocita prvni radek - potreba pricist +1
# porovnat s unique_heads.txt ze skriptu columns.sh
