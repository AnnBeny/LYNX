from __future__ import annotations
from asyncio import run
from pathlib import Path
import pathlib
from random import sample
from unicodedata import name
import pandas as pd
import time
import re
from datetime import datetime
import sys, logging, warnings
from logging.handlers import RotatingFileHandler

# cesty
DIR_LYNX = Path(__file__).parents[1]
DIR_ALL  = DIR_LYNX / "MM"
DIR_TRANS = DIR_LYNX / "MM"
DIR_OUTPUT = DIR_LYNX / "output"
SAMPLE_LIST = DIR_LYNX / "seznam_mm.csv"
LOG_DIR = DIR_LYNX / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)   
LOG_FILE = LOG_DIR / f"controls_update_{datetime.now():%Y%m%d_%H%M%S}.log"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=2, encoding='utf-8')
fh.setFormatter(fmt)
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(fmt)
logger.addHandler(fh)
logger.addHandler(ch)

warnings.simplefilter("default")
logging.captureWarnings(True)

def log_df(df, name, n=5):
    logger.info(f"{name} shape: {df.shape}")
    if df.shape[0] <= n:
        logger.info(f"\n{df}")
    else:
        logger.info(f"\n{df.head(n//2)}\n...\n{df.tail(n//2)}")

def latest_by_glob(pattern: str) -> Path | None:
    files = sorted(DIR_OUTPUT.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None

MERGED_FILES = {
    "SNV":              latest_by_glob("merged_data_snv_mm_*.xlsx"),
    "CNA":              latest_by_glob("merged_data_cna_mm_*.xlsx"),
    "TRANSLOCATIONS":   latest_by_glob("merged_data_translocations_mm_*.xlsx"),
    "REARRANGEMENT":    latest_by_glob("merged_data_rearrangement_mm_*.xlsx"),
}

TODAY = datetime.now().strftime("%d%m%Y")

# MERGED_FILES = {
#     "SNV":  DIR_OUTPUT / f"merged_data_snv_mm_{TODAY}.xlsx",
#     "CNA":  DIR_OUTPUT / f"merged_data_cna_mm_{TODAY}.xlsx",
#     "TRANSLOCATIONS": DIR_OUTPUT / f"merged_data_translocations_mm_{TODAY}.xlsx",
#     "REARRANGEMENT":  DIR_OUTPUT / f"merged_data_rearrangement_mm_{TODAY}.xlsx",
# }

# nacteni seznamu vzorku ze seznam_mm.csv
def load_sample_list(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath, header=None, names=["Run","Sample"], dtype=str)
    df["Run"] = df["Run"].str.strip()
    df["Sample"] = df["Sample"].str.strip()
    df["order"] = range(len(df))
    return df
sample_list = load_sample_list(SAMPLE_LIST)
print(f"{sample_list}, {len(sample_list)} vzorku ze seznamu.")

# spojeni run a sample do jednoho stringu 
def run_sample () -> pd.DataFrame:
    for index, row in sample_list.iterrows():
        pair_key = f"{row['Run']}_{row['Sample']}"
        #print(f"{pair_key}")
    return sample_list
sample_run_sample = run_sample()
#print(f"{sample_run_sample}, {len(sample_run_sample)} spojenych run a sample.")

# z merged vypsat unikatni run a sample
def find_run_sample_in_merged(merged_df: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame(columns=["Run", "Sample"])
    if "run" in merged_df.columns and "sample" in merged_df.columns:
        unique_pairs = merged_df[["run", "sample"]].drop_duplicates()
        unique_pairs.columns = ["Run", "Sample"]
        result = unique_pairs
    return result
merge_unique_cna = find_run_sample_in_merged(pd.read_excel(MERGED_FILES["CNA"]))
merge_unique_snv = find_run_sample_in_merged(pd.read_excel(MERGED_FILES["SNV"]))
merge_unique_translocations = find_run_sample_in_merged(pd.read_excel(MERGED_FILES["TRANSLOCATIONS"]))
merge_unique_rearrangement = find_run_sample_in_merged(pd.read_excel(MERGED_FILES["REARRANGEMENT"]))
print(f"{merge_unique_cna}, {len(merge_unique_cna)} unikatnich run a sample v merged souboru CNA.")
print(f"{merge_unique_snv}, {len(merge_unique_snv)} unikatnich run a sample v merged souboru SNV.")
print(f"{merge_unique_translocations}, {len(merge_unique_translocations)} unikatnich run a sample v merged souboru TRANSLOCATIONS.")
print(f"{merge_unique_rearrangement}, {len(merge_unique_rearrangement)} unikatnich run a sample v merged souboru REARRANGEMENT.")

# porovnat kombinaci run-sample se seznam_mm.csv, jestli neco v merge nechybi
def compare_run_sample_with_list(merge_unique: pd.DataFrame, sample_list: pd.DataFrame) -> pd.DataFrame:
    missing = pd.merge(sample_list, merge_unique, on=["Run", "Sample"], how="left", indicator=True)
    missing = missing[missing['_merge'] == 'left_only']
    return missing[['Run', 'Sample']]
compare_run_sample_cna = compare_run_sample_with_list(merge_unique_cna, sample_list)
print(f"{compare_run_sample_cna}, {len(compare_run_sample_cna)} chybejicich run a sample v merged souboru CNA.")
compare_run_sample_snv = compare_run_sample_with_list(merge_unique_snv, sample_list)
print(f"{compare_run_sample_snv}, {len(compare_run_sample_snv)} chybejicich run a sample v merged souboru SNV.")
compare_run_sample_translocations = compare_run_sample_with_list(merge_unique_translocations, sample_list)
print(f"{compare_run_sample_translocations}, {len(compare_run_sample_translocations)} chybejicich run a sample v merged souboru TRANSLOCATIONS.")
compare_run_sample_translocations.to_excel(f"{DIR_LYNX}/missing_translocations.xlsx", index=False)
compare_run_sample_rearrangement = compare_run_sample_with_list(merge_unique_rearrangement, sample_list)
print(f"{compare_run_sample_rearrangement}, {len(compare_run_sample_rearrangement)} chybejicich run a sample v merged souboru REARRANGEMENT.")
compare_run_sample_rearrangement.to_excel(f"{DIR_LYNX}/missing_rearrangement.xlsx", index=False)

# najit vzorky ve složce MM v souborech xlsx, které nemají v translocations class1 R a jsou v seznam_mm.csv
def find_no_translocations_in_excel_files(directory: str | Path, combined_df: pd.DataFrame, sample_list: pd.DataFrame) -> pd.DataFrame:
    directory = Path(directory)
    combined_df = pd.DataFrame()
    for filepath in directory.glob("*.xlsx"):
        xls = pd.ExcelFile(filepath)
        run_name = filepath.stem.replace('.gathered.xlsx', '')
        run_name = run_name.replace('.gathered', '')
        sample_row = sample_list[sample_list['Run'] == run_name]
        if sample_row.empty:
            print(f'No sample found for run {run_name}. Skipping file {filepath.name}.')
            continue
        samples = sample_row['Sample'].values
        for sheet_name in xls.sheet_names:
            sheet_base = sheet_name
            if sheet_base.endswith('_R1'):
                sheet_base: str = sheet_base.removesuffix('_R1')
            if sheet_base in samples:
                df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
                if 'class1' in df.columns:
                    df_r = df[df['class1'] == 'SV']
                    if df_r.empty:
                        new_row = {'run': run_name, 'sample': sheet_base}
                        combined_df = pd.concat([combined_df, pd.DataFrame([new_row])], ignore_index=True)
    print(f"{combined_df}, {len(combined_df)} radku bez SV v class1 ve složce {directory}.")
    return combined_df
no_translocations = find_no_translocations_in_excel_files(DIR_ALL, merge_unique_translocations, sample_list)
print(f"{no_translocations}, {len(no_translocations)} radku bez SV v class1 ve složce {DIR_ALL}.")
no_translocations.to_excel(f"{DIR_LYNX}/no_class1_SV_mm.xlsx", index=False)


# spocitat pocet radku na sample v jednotlivych merged souborech
def count_rows_per_sample_in_merged(merged_files: dict[str, Path]) -> pd.DataFrame:
    rows_per_sample_all = []
    for file_type, xlsx in merged_files.items():
        try:
            df = pd.read_excel(xlsx)
        except Exception as e:
            print(f"Nelze načíst {xlsx.name}: {e}")
            continue

        needed = {"sample"}
        missing = needed - set(df.columns)
        if missing:
            print(f"{xlsx.name}: chybí sloupce {missing} → přeskočeno.")
            continue

        has_run = "run" in df.columns
        group_cols = ["sample"] if not has_run else ["run", "sample"]

        counts = df.groupby(group_cols, dropna=False).size().reset_index(name="n_rows")
        counts.insert(0, "file", xlsx.name)
        counts.insert(1, "file_type", file_type)

        rows_per_sample_all.append(counts)

    if rows_per_sample_all:
        result = pd.concat(rows_per_sample_all, ignore_index=True)
        print(result.to_string(index=False))
        return result
    else:
        return pd.DataFrame()
rows_per_sample_merged = count_rows_per_sample_in_merged(MERGED_FILES)
rows_per_sample_merged.to_excel(f"{DIR_LYNX}/rows_per_sample_by_merged_file_mm.xlsx", index=False)
print(f"{rows_per_sample_merged}, {len(rows_per_sample_merged)} radku s počtem řádků na sample v merged souborech.")
# spocitat pocet radku na sample v jednotlivych souborech ve slozce MM
files = list(DIR_ALL.glob("*.xlsx"))
seznam_csv = DIR_LYNX / "seznam_mm.csv"
seznam = pd.read_csv(seznam_csv, header=None, names=["Run","Sample"], dtype=str)
seznam["Run"] = seznam["Run"].str.strip()
seznam["Sample"] = seznam["Sample"].str.strip()
seznam["order"] = range(len(seznam))
rows_per_sample_all = []
print(f"\nPočet řádků na sample v jednotlivých souborech ve složce MM:")
for xlsx in files:
    try:
        df = pd.read_excel(xlsx)
    except Exception as e:
        print(f"Nelze načíst {xlsx.name}: {e}")
        continue

    needed = {"sample"}
    missing = needed - set(df.columns)
    if missing:
        print(f"{xlsx.name}: chybí sloupce {missing} → přeskočeno.")
        continue

    has_run = "run" in df.columns
    group_cols = ["sample"] if not has_run else ["run", "sample"]

    counts = df.groupby(group_cols, dropna=False).size().reset_index(name="n_rows")
    counts.insert(0, "file", xlsx.name)

    rows_per_sample_all.append(counts)
if rows_per_sample_all:
    result = pd.concat(rows_per_sample_all, ignore_index=True)
    print(result.to_string(index=False))
else:
    print("Žádné výsledky (zkontroluj vstupní soubory/sloupce).")
print(f"{result}, {len(result)} radku s počtem řádků na sample v souborech ve složce MM.")
result.to_excel(f"{DIR_LYNX}/rows_per_sample_by_file_mm.xlsx", index=False)


# počet řádků v souborech ve složce MM
total_rows = {}
for xlsx in files:
    try:
        df = pd.read_excel(xlsx)
    except Exception as e:
        print(f"Nelze načíst {xlsx.name}: {e}")
        continue
    total_rows[xlsx.name] = len(df)
print(f"\nPočet řádků v jednotlivých souborech ve složce MM:")
for filename, n_rows in total_rows.items():
    print(f"{filename}: {n_rows} řádků")
    continue
total_rows[xlsx.name] = len(df)
print(f"\nPočet řádků v jednotlivých souborech:")
for filename, n_rows in total_rows.items():
    print(f"{filename}: {n_rows} řádků")
    total_rows[xlsx.name] = len(df)
print(f"\nPočet řádků v jednotlivých souborech:")
for filename, n_rows in total_rows.items():
    print(f"{filename}: {n_rows} řádků")

# počet řádků v souborech csv a cns ve složce MM
total_rows_csv_cns = {}
for filepath in DIR_ALL.glob("*"):
    if filepath.suffix.lower() in [".csv", ".cns"]:
        try:
            if filepath.suffix.lower() == ".csv":
                df = pd.read_csv(filepath)
            elif filepath.suffix.lower() == ".cns":
                df = pd.read_csv(filepath, sep="\t")
        except Exception as e:
            print(f"Nelze načíst {filepath.name}: {e}")
            continue
        total_rows_csv_cns[filepath.name] = len(df)
print(f"\nPočet řádků v jednotlivých csv a cns souborech ve složce MM:")
for filename, n_rows in total_rows_csv_cns.items():
    print(f"{filename}: {n_rows} řádků")
df_total_rows_csv_cns = pd.DataFrame(list(total_rows_csv_cns.items()), columns=["file", "n_rows"])
df_total_rows_csv_cns.to_excel(f"{DIR_LYNX}/total_rows_csv_cns.xlsx", index=False)



