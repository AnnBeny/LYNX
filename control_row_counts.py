from pathlib import Path
import pandas as pd

# soubory na kontrolu
files = [
    Path("/mnt/hdd2/anna/LYNX/merged_data_translocations_all_19092025.xlsx"),
    Path("/mnt/hdd2/anna/LYNX/merged_data_rearrangement_all_23092025.xlsx"),
    Path("/mnt/hdd2/anna/LYNX/merged_data_cna_all_19092025.xlsx"),
    Path("/mnt/hdd2/anna/LYNX/merged_data_snv_all_19092025.xlsx")
]
folder_all = Path("/mnt/hdd2/anna/LYNX/ALL")
print(f"Načtení {len(files)} souborů.")

# files = list(Path("/mnt/hdd2/anna/LYNX").glob("*.xlsx"))

seznam_csv = Path("/mnt/hdd2/anna/LYNX/seznam_all.csv")
seznam = pd.read_csv(seznam_csv, header=None, names=["Run","Sample"], dtype=str)
seznam["Run"] = seznam["Run"].str.strip()
seznam["Sample"] = seznam["Sample"].str.strip()

seznam["order"] = range(len(seznam))

rows_per_sample_all = []

print(f"\nPočet řádků na sample v jednotlivých souborech:")

for xlsx in files:
    try:
        df = pd.read_excel(xlsx)
    except Exception as e:
        print(f"Nelze načíst {xlsx.name}: {e}")
        continue

    # kontrola sloupce
    needed = {"sample"}
    missing = needed - set(df.columns)
    if missing:
        print(f"{xlsx.name}: chybí sloupce {missing} → přeskočeno.")
        continue

    # přidat run
    has_run = "run" in df.columns
    group_cols = ["sample"] if not has_run else ["run", "sample"]

    # počet řádků na sample
    counts = df.groupby(group_cols, dropna=False).size().reset_index(name="n_rows")
    counts.insert(0, "file", xlsx.name)

    rows_per_sample_all.append(counts)

# merge
if rows_per_sample_all:
    result = pd.concat(rows_per_sample_all, ignore_index=True)
    # save
    #out_csv = Path("/mnt/hdd2/anna/LYNX/rows_per_sample_by_file.csv")
    #result.to_csv(out_csv, index=False)
    #print(f"Uloženo: {out_csv}")
    #print(result.head(20).to_string(index=False))
    print(result.to_string(index=False))
else:
    print("Žádné výsledky (zkontroluj vstupní soubory/sloupce).")

# počet řádků v souborech
total_rows = {}

for xlsx in files:
    try:
        df = pd.read_excel(xlsx)
    except Exception as e:
        print(f"Nelze načíst {xlsx.name}: {e}")
        continue

    total_rows[xlsx.name] = len(df)

print("\nCelkový počet řádků v souborech:")
for fname, n in total_rows.items():
    print(f"{fname}: {n}")

# kontrola proti seznamu
print("\nKontrola proti seznamu:")
seznam = seznam.rename(columns={"Run": "run", "Sample": "sample"})
# kontrola proti seznamu
if "run" in result.columns:
    merged = pd.merge(result, seznam, on=["run","sample"], how="right")
    missing_samples = merged[merged["n_rows"].isna()]
    if not missing_samples.empty:
        print("Sample ze seznamu chybí ve výsledcích:")
        print(missing_samples[["run","sample","order"]].to_string(index=False))
    else:
        print("Všechny samply ze seznamu jsou ve výsledcích.")
else:
    print("Ve výsledcích není sloupec 'run', nelze provést kontrolu proti seznamu.")



