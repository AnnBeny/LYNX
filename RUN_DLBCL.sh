#!/bin/bash
source /mnt/hdd2/anna/LYNX/venv/bin/activate
bash download_cns_DLBCL.sh &
python merge_cna_DLBCL.py &
bash download_snv_DLBCL.sh &
python merge_snv_DLBCL.py &
python separate_rearrang_dlbcl.py &
python separate_transl_dlbcl.py &
wait