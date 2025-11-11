#!/bin/bash
source /mnt/hdd2/anna/LYNX/venv/bin/activate
bash ../scripts/download_cns_CLL.sh &
python ../scripts/merge_cna_CLL.py &
bash ../scripts/download_snv_CLL.sh &
python ../scripts/merge_snv_CLL.py &
wait