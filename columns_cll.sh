#!/bin/bash

DEST="/mnt/hdd2/anna/LYNX/CLL"
OUTFILE_cns="$DEST/heads_cns_CLL.txt"
OUTFILE_snv="$DEST/heads_snv_CLL.txt"

# --- cns ---
> "$OUTFILE_cns"

for file in "$DEST"/*.cns; do
    echo "Soubor $file" >> "$OUTFILE_cns"
    head -n 1 "$file" >> "$OUTFILE_cns"
    echo >> "$OUTFILE_cns"
done

for file in "$DEST"/*.cns; do
    head -n 1 "$file"
done | sort | uniq -c > "$DEST/unique_heads_cns.txt"

# --- snv ---
> "$OUTFILE_snv"

for file in "$DEST"/*.csv; do
    echo "Soubor $file" >> "$OUTFILE_snv"
    head -n 1 "$file" >> "$OUTFILE_snv"
    echo >> "$OUTFILE_snv"
done

for file in "$DEST"/*.csv; do
    head -n 1 "$file"
done | sort | uniq -c > "$DEST/unique_heads_snv.txt"