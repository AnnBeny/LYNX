#!/bin/bash

DEST="/mnt/hdd2/anna/LYNX/TRANSLOKACE_PRESTAVBA_DLBCL"
OUTFILE="$DEST/translocations_dlbcl.txt"

> "$OUTFILE"

for file in "$DEST"/*.xlsx; do
    echo "Soubor $file" >> "$OUTFILE"
    head -n 1 "$file" >> "$OUTFILE"
    echo >> "$OUTFILE"
done

for file in "$DEST"/*.xlsx; do
    head -n 1 "$file"
done | sort | uniq -c > "$DEST/unique_heads.txt"