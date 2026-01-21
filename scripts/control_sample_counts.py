from pathlib import Path
import pandas as pd
import glob

root = Path(__file__).parents[1]

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

DIAGNOSIS = choose("Vyber diagnózu:", ["all","dlbcl","cll","mm"], default="all")

# paths
folder = root / 'output'

# 10 latest files
files = glob.glob(str(folder / f"merged_data_*_{DIAGNOSIS}_*.xlsx"))
files.sort(key=lambda p: Path(p).stat().st_mtime, reverse=False)
choose_files = files[9:]

# main loop
while True:

    # select file
    source = Path(choose("Select file to control sample counts:", [Path(f).name for f in choose_files]))
    selected_file = folder / source
    print(f"\nSoubor: {selected_file.name}")
    print(f"\nZpracovávám...")
    df = pd.read_excel(selected_file)

    # check columns run and sample
    if "run" not in df.columns or "sample" not in df.columns:
        print("  -> chybí sloupce run/sample, přeskočeno")
        continue

    # count samples per run
    counts = df.groupby("run")["sample"].nunique().reset_index()
    counts.rename(columns={"sample": "n_samples"}, inplace=True)
    print(counts.to_string(index=False))
    print(f"  Celkem unikátních vzorků: {df['sample'].nunique()}")

    # save result
    counts.to_excel(folder.parent / f"control_sample_counts_{selected_file.name}", index=False)
    print(f"  Výsledek uložen do: control_sample_counts_{selected_file.name} ve složce {folder.parent}")

    # ask to continue
    again = choose("Chceš zkontrolovat další soubor?", ["Ano", "Ne"], default="Ne")
    if again.lower() != "ano":
        break