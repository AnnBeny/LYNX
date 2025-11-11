from pathlib import Path
import pandas as pd

# soubory na kontrolu
files = [
    #Path("/mnt/hdd2/anna/LYNX/output/merged_data_translocations_dlbcl_04092025.xlsx"),
    #Path("/mnt/hdd2/anna/LYNX/output/merged_data_rearrangement_dlbcl_04092025.xlsx"),
    Path("/mnt/hdd2/anna/LYNX/output/merged_data_snv_mm_03112025.xlsx"),
    Path("/mnt/hdd2/anna/LYNX/output/merged_data_cna_mm_30102025.xlsx")
]
dest = Path("/mnt/hdd2/anna/LYNX/output/")

for xlsx in files:
    print(f"\nSoubor: {xlsx.name}")
    df = pd.read_excel(xlsx)

    if "run" not in df.columns or "sample" not in df.columns:
        print("  -> chybí sloupce run/sample, přeskočeno")
        continue

    counts = df.groupby("run")["sample"].nunique().reset_index()
    counts.rename(columns={"sample": "n_samples"}, inplace=True)

    print(counts.to_string(index=False))
    print(f"  Celkem unikátních vzorků: {df['sample'].nunique()}")
    counts.to_excel(dest / f"control_sample_counts_{xlsx.name}", index=False)