from pathlib import Path
import pandas as pd

# ====== CESTY ======
DIR_LYNX = Path("/mnt/hdd2/anna/LYNX")
DIR_ALL  = DIR_LYNX / "ALL"
DIR_TRANS = DIR_LYNX / "TRANSLOKACE_PRESTAVBA_ALL"

MERGED_FILES = {
    "SNV":  DIR_LYNX / "merged_data_snv_all_19092025.xlsx",
    "CNA":  DIR_LYNX / "merged_data_cna_all_19092025.xlsx",
    "TRANSLOCATIONS": DIR_LYNX / "merged_data_translocations_all_19092025.xlsx",
    "REARRANGEMENT":  DIR_LYNX / "merged_data_rearrangement_all_23092025.xlsx",
}

# ====== POMOCNÉ ČTEČKY ======
def read_csv_any(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=None, engine="python", dtype=str, on_bad_lines="skip")

def read_cns(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, comment="#")

def count_rows_xlsx_all_sheets(path: Path) -> int:
    total = 0
    xls = pd.ExcelFile(path)
    for sh in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sh)
        total += len(df)
    return total

def count_trans_rearr_in_folder(folder: Path) -> tuple[int,int]:
    trans_total = 0
    rearr_total = 0
    for x in sorted(folder.glob("*.xlsx")):
        xls = pd.ExcelFile(x)
        for sh in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sh, dtype=str)
            if "class1" not in df.columns:
                continue
            c = df["class1"].astype(str)
            trans_total  += (c.isin({"SV", "SV-R"})).sum()
            rearr_total  += (c == "R").sum()
    return trans_total, rearr_total

# ====== 1) ZDROJOVÉ POČTY Z ALL/ A TRANSLOKACE_PRESTAVBA_ALL/ ======
# SNV z CSV
snv_total_src = 0
csv_files = [p for p in DIR_ALL.glob("*.vep.csv")]
if not csv_files:
    print("[INFO] Ve složce ALL nejsou CSV soubory (ani .csv/.CSV).")
for p in sorted(csv_files):
    try:
        df = pd.read_csv(p, sep=None, engine="python", dtype=str, on_bad_lines="skip")
        snv_total_src += len(df)
    except Exception as e:
        print(f"[WARN] Nelze načíst CSV {p.name}: {e}")

# CNA z CNS
cna_total_src = 0
for p in sorted(DIR_ALL.glob("*.cns")):
    try:
        cna_total_src += len(read_cns(p))
    except Exception as e:
        print(f"[WARN] Nelze načíst CNS {p.name}: {e}")

# TRANS/REARR z TRANS složky
trans_total_src, rearr_total_src = count_trans_rearr_in_folder(DIR_TRANS)

# ====== 2) POČTY Z HOTOVÝCH 4 MERGED XLSX ======
merged_totals = {}
for key, path in MERGED_FILES.items():
    try:
        merged_totals[key] = count_rows_xlsx_all_sheets(path)
    except Exception as e:
        print(f"[WARN] Nelze načíst merged {key} ({path.name}): {e}")
        merged_totals[key] = None

# ====== 3) TISK PŘEHLEDU ======
print("\n=== ZDROJOVÉ POČTY (z jednotlivých vstupů) ===")
print(f"SNV (ALL/*.csv)  : {snv_total_src:,d}")
print(f"CNA (ALL/*.cns)  : {cna_total_src:,d}")
print(f"TRANSLOCATIONS (TRANSLOKACE*, class1 in SV,SV-R) : {trans_total_src:,d}")
print(f"REARRANGEMENT (TRANSLOKACE*, class1=='R')        : {rearr_total_src:,d}")

print("\n=== MERGED XLSX POČTY (hotové výsledky) ===")
for key in ["SNV","CNA","TRANSLOCATIONS","REARRANGEMENT"]:
    print(f"{key:15s}: {merged_totals.get(key)}")

print("\n=== ROZDÍLY (MERGED - SOURCE) ===")
def diff(label, merged, source):
    if merged is None:
        return "N/A (merged nelze načíst)"
    d = merged - source
    sign = "+" if d>=0 else "-"
    return f"{d:+,d}"
print("Translocations a Rearrangements se nemají rovnat, pže se tam některé sloupce rozpočítávají. Dá se porovnat s LYNXem na webu.")

print(f"SNV            : {diff('SNV',            merged_totals.get('SNV'),            snv_total_src)}")
print(f"CNA            : {diff('CNA',            merged_totals.get('CNA'),            cna_total_src)}")
print(f"TRANSLOCATIONS : {diff('TRANSLOCATIONS', merged_totals.get('TRANSLOCATIONS'), trans_total_src)}")
print(f"REARRANGEMENT  : {diff('REARRANGEMENT',  merged_totals.get('REARRANGEMENT'),  rearr_total_src)}")
