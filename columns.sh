#!/bin/bash

DEST="/mnt/hdd2/anna/LYNX/DLBCL"
OUTFILE="$DEST/heads_cns_dlbcl.txt"

> "$OUTFILE"

for file in "$DEST"/*.cns; do
    echo "Soubor $file" >> "$OUTFILE"
    head -n 1 "$file" >> "$OUTFILE"
    echo >> "$OUTFILE"
done

for file in "$DEST"/*.cns; do
    head -n 1 "$file"
done | sort | uniq -c > "$DEST/unique_heads.txt"