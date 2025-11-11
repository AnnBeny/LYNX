#!/bin/bash
source /mnt/hdd2/anna/LYNX/venv/bin/activate
mkdir -p /mnt/hdd2/anna/LYNX/ALL &
mkdir -p /mnt/hdd2/anna/LYNX/TRANSLOKACE_PRESTAVBA_ALL &
bash ../scripts/download_cns_ALL.sh &
python ../scripts/merge_cna_ALL.py &
bash ../scripts/download_snv_ALL.sh &
python ../scripts/merge_snv_ALL.py &
python ../scripts/separate_rearrang_all.py &
python ../scripts/separate_transl_all.py &
wait