#!/bin/bash
source /mnt/hdd2/anna/LYNX/venv/bin/activate
mkdir -p /mnt/hdd2/anna/LYNX/ALL &
mkdir -p /mnt/hdd2/anna/LYNX/TRANSLOKACE_PRESTAVBA_ALL &
bash download_cns_ALL.sh &
python merge_cna_ALL.py &
bash download_snv_ALL.sh &
python merge_snv_ALL.py &
python separate_rearrang_all.py &
python separate_transl_all.py &
wait