#!/bin/bash
set -euo pipefail

source ../venv/bin/activate
echo "RUNNING MERGE SCRIPTS..."
printf "\n--- CNA ---\n"
python3 merge_cna.py
printf "\n --- SNV ---\n"
python3 merge_snv.py
printf "\n--- TRANSLOCATION ---\n"
python3 separate_transl.py
printf "\n"
printf "\n--- REARRANGEMENT ---\n"
python3 separate_rearrang.py
printf "\n"

echo "Results downloaded into /mnt/hdd2/anna/LYNX/output"