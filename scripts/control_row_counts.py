from pathlib import Path
from datetime import datetime
import pandas as pd
import glob

root = Path(__file__).parents[1]
print(f"Root directory: {root}")

# choosing diagnosis
def choose(prompt, options, default=None):
    print(prompt)
    for i, opt in enumerate(options, start=1):
        print(f"{i}. {opt}")
    choice = input(f"Vyber číslo (1-{len(options)}): ").strip()
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

DIAGNOSIS = choose("Vyber diagnózu:", ["ALL","DLBCL","CLL","MM"], default="all")
dg_lower = DIAGNOSIS.lower()
dg_upper = DIAGNOSIS.upper()

# paths
DIR_OUTPUT = root / "output"
DIR_ALL  = root / f"{dg_upper}"
SAMPLE_LIST = root / f"seznam_{dg_lower}.csv"
cnv_files = glob.glob(str(DIR_ALL / "*.call.cns"))
#print(f"\ncnv_files: {cnv_files}  found {len(cnv_files)} files.")
snv_files = glob.glob(str(DIR_ALL / "*.mutect2.cons.filt.norm.vep.csv"))
rear_trans_files = glob.glob(str(DIR_ALL / "*.gathered.xlsx"))

# 10 latest files
files = glob.glob(str(DIR_OUTPUT / f"merged_data_*_{dg_lower}_*.xlsx"))
files.sort(key=lambda p: Path(p).stat().st_mtime, reverse=False)
choose_files = files[-9:]

# seznam
seznam = pd.read_csv(SAMPLE_LIST, header=None, names=["run","sample"], dtype=str)
seznam["run"] = seznam["run"].str.strip()
seznam["sample"] = seznam["sample"].str.strip()

seznam["order"] = range(len(seznam))
print(f"Načten seznam ze {SAMPLE_LIST}, počet záznamů: {len(seznam)}")
print(seznam.head(5).to_string(index=False))

rows_per_sample_all = []
result = []

#selected_file = DIR_OUTPUT / "merged_data_snv_dlbcl_15012026.xlsx"  # default value in case of no selection

# control excel files
print(f"\nPočet řádků na sample v jednotlivých {dg_upper} souborech:")

while True:
    # select file
    source = Path(choose("Vyber soubor ke kontrole řádků na sample:", [Path(f).name for f in choose_files]))
    selected_file = DIR_OUTPUT / source
    print(f"\n--- Vybrán soubor: {selected_file.name} ---")
    print(f"\nZpracovávám...")
    try:
        df = pd.read_excel(selected_file)
    except Exception as e:
        print(f"Nepodařilo se načíst {selected_file.name}: {e}")
        continue

    # check columns run and sample
    if "run" not in df.columns or "sample" not in df.columns:
        print("  -> chybí sloupce run/sample, přeskočeno")
        continue

    group_cols = ["run","sample"]
    counts = df.groupby(group_cols, dropna=False).size().reset_index(name="n_rows")
    #counts.insert(0, "file", selected_file.name)

    rows_per_sample_all.append(counts)
    print(counts.to_string(index=False))
    print(f"Počet unikátních run+sample v merged: {len(counts)}")

    # export
    n_unique = len(counts)
    sum_rows = int(counts["n_rows"].sum())
    file_name = selected_file.name

    break

# excel merge
df_excel_total = rows_per_sample_all[0]["n_rows"].sum() if rows_per_sample_all else 0
print(f"\nCelkem řádků v merged souboru: {df_excel_total}")

counts_rows = counts.copy()

result = pd.DataFrame([{
    "file": file_name,
    "n_unique_samples": n_unique,
    "total_rows": sum_rows
}]
)

final =pd.concat([counts_rows, result], axis=1)

cnv_rows = []
snv_rows = []
trans_rows = []

# cnv
if "cna" in selected_file.name:
    for file in cnv_files:
        #print(f"Processing file: {file}")
        df = pd.read_csv(file, sep="\t")
        n = len(df)
        cnv_rows.append({"file": Path(file).name, "total_rows": n})
    # print("\nCelkový počet řádků v CNV souborech:")
    df_cnv_rows = pd.DataFrame(cnv_rows)
    #print(df_cnv_rows.to_string(index=False))
    print(f"\nPočet CNV souborů: {len(df_cnv_rows)}")
    df_cnv_total = df_cnv_rows["total_rows"].sum()
    print(f"Celkem řádků ve všech CNV souborech: {df_cnv_total}")

    compare = df_excel_total == df_cnv_total
    if compare:
        print(f"\n-> Počet řádků v {selected_file.name} souboru ODPOVÍDÁ počtu řádků v CNV {dg_upper} souborech.")
    else:   
        print(f"\n-> POZOR: Počet řádků v {selected_file.name} souboru NEODPOVÍDÁ počtu řádků v CNV {dg_upper} souborech!")

# snv
elif "snv" in selected_file.name:
    for file in snv_files:
        #print(f"Processing file: {file}")
        df = pd.read_csv(file, sep="\t")
        n = len(df)
        snv_rows.append({"file": Path(file).name, "total_rows": n})
    # print("\nCelkový počet řádků v SNV souborech:")
    df_snv_rows = pd.DataFrame(snv_rows)
    #print(df_snv_rows.to_string(index=False))
    print(f"\nPočet SNV {dg_upper} souborů: {len(df_snv_rows)}")
    df_snv_total = df_snv_rows["total_rows"].sum()
    print(f"Celkem řádků ve všech SNV {dg_upper} souborech: {df_snv_total}")
    compare = df_excel_total == df_snv_total
    if compare:
        print(f"\nPočet řádků v {selected_file.name} souboru ODPOVÍDÁ počtu řádků v SNV {dg_upper} souborech.")
    else:   
        print(f"\nPOZOR: Počet řádků v {selected_file.name} souboru NEODPOVÍDÁ počtu řádků v SNV {dg_upper} souborech!")

# u translokací a přestaveb se porovnání řádků nedělá, protože se tam po stažení z keeperu ještě rozpočítávají řádky a je jich pak v merge celkově míň

# translocations
elif "translocations" in selected_file.name:
    print(f"\nPočet soborů {dg_upper} s translokacemi: {len(rear_trans_files)}")
    #df = pd.read_excel(selected_file)
    for file in rear_trans_files:
        print(f"Processing file: {file}")
        df_rear_trans = pd.ExcelFile(file)
        for sheet_name in df_rear_trans.sheet_names:
            sheet_base = sheet_name
            sheet_base: str = sheet_base.removesuffix('_R1')
            if sheet_base in seznam['sample'].values:
                sheet_df = pd.read_excel(df_rear_trans, sheet_name=sheet_name)
                sheet_df = sheet_df[sheet_df['class1'] == 'R']
                n = len(sheet_df)
                print(f"  Sheet: {sheet_name}, Rows: {n}")
                trans_rows.append({"file": Path(file).name, "sheet": sheet_name, "total_rows": n})
    # print("\nCelkový počet řádků v TRANSLOCATION souborech:")
    df_trans_rows = pd.DataFrame(trans_rows)
    print(f"\nPočet soborů {dg_upper} s translokacemi: {len(df_trans_rows)}")
    df_trans_total = df_trans_rows["total_rows"].sum()
    print(f"Celkem řádků ve všech TRANSLOCATION {dg_upper} souborech: {df_trans_total}")

# rearrangements
elif "rearrangement" in selected_file.name:
    print(f"\nPočet soborů {dg_upper} s přestavbami: {len(rear_trans_files)}")
    #df = pd.read_excel(selected_file)
    for file in rear_trans_files:
        print(f"Processing file: {file}")
        df_rear_trans = pd.ExcelFile(file)
        for sheet_name in df_rear_trans.sheet_names:
            sheet_base = sheet_name
            sheet_base: str = sheet_base.removesuffix('_R1')
            if sheet_base in seznam['sample'].values:
                sheet_df = pd.read_excel(df_rear_trans, sheet_name=sheet_name)
                sheet_df = sheet_df[sheet_df['class1'] == 'SV']
                n = len(sheet_df)
                print(f"  Sheet: {sheet_name}, Rows: {n}")
                trans_rows.append({"file": Path(file).name, "sheet": sheet_name, "total_rows": n})
    # print("\nCelkový počet řádků v TRANSLOCATION souborech:")
    df_trans_rows = pd.DataFrame(trans_rows)
    print(f"\nPočet soborů {dg_upper} s translokacemi: {len(df_trans_rows)}")
    df_trans_total = df_trans_rows["total_rows"].sum()
    print(f"Celkem řádků ve všech TRANSLOCATION {dg_upper} souborech: {df_trans_total}")

# export final
final.to_excel(DIR_OUTPUT / f"control_summary_{Path(file_name).stem}.xlsx", index=False)
print(f"\nVšechny výstupy byly uloženy do: {DIR_OUTPUT}")