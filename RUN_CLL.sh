#!/bin/bash
source /mnt/hdd2/anna/LYNX/venv/bin/activate
bash download_cns_CLL.sh &
python merge_cna_CLL.py &
bash download_snv_CLL.sh &
python merge_snv_CLL.py &
wait