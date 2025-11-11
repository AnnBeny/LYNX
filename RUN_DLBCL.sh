#!/bin/bash
source /mnt/hdd2/anna/LYNX/venv/bin/activate
bash ../scripts/download_cns_DLBCL.sh &
python ../scripts/merge_cna_DLBCL.py &
bash ../scripts/download_snv_DLBCL.sh &
python ../scripts/merge_snv_DLBCL.py &
python ../scripts/separate_rearrang_dlbcl.py &
python ../scripts/separate_transl_dlbcl.py &
wait