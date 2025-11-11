#!/bin/bash

DX="${1:-}"

# Choice menu for diagnosis
if [[ -z "${DX:-}" ]]; then
  PS3="Vyber diagnózu (1-4): "
  select opt in "ALL" "DLBCL" "CLL" "MM"; do
    case "$REPLY" in 1|2|3|4) DX="$opt"; break ;; *) echo "Neplatný výběr."; ;; esac
  done
fi
echo "CHOICES: DX=$DX"

ROOT="/mnt/hdd2/anna/LYNX"
DEST="$ROOT/$DX"
echo "DEST=$DEST"
OUTFILE_cns="$ROOT/heads_cns_$DX.txt"
OUTFILE_snv="$ROOT/heads_snv_$DX.txt"
OUTFILE_tr_re="$ROOT/heads_trans_rear_$DX.txt"

# --- cns ---
> "$OUTFILE_cns"

for file in "$DEST"/*.cns; do
    echo "Soubor $file" >> "$OUTFILE_cns"
    head -n 1 "$file" >> "$OUTFILE_cns"
    echo >> "$OUTFILE_cns"
done

for file in "$DEST"/*.cns; do
    head -n 1 "$file"
done | sort | uniq -c > "$ROOT/unique_heads_cns_$DX.txt"

# --- snv ---
> "$OUTFILE_snv"

for file in "$DEST"/*.csv; do
    echo "Soubor $file" >> "$OUTFILE_snv"
    head -n 1 "$file" >> "$OUTFILE_snv"
    echo >> "$OUTFILE_snv"
done

for file in "$DEST"/*.csv; do
    head -n 1 "$file"
done | sort | uniq -c > "$ROOT/unique_heads_snv_$DX.txt"

# --- translocations, rearrangements ---
> "$OUTFILE_tr_re"

for file in "$DEST"/*.xlsx; do
    echo "Soubor $file" >> "$OUTFILE_tr_re"
    head -n 1 "$file" >> "$OUTFILE_tr_re"
    echo >> "$OUTFILE_tr_re"
done

for file in "$DEST"/*.xlsx; do
    head -n 1 "$file"
done | sort | uniq -c > "$ROOT/unique_heads_trans_rear_$DX.txt"