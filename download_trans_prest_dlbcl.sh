#!/bin/bash

# TRANSLOKACE PRESTAVBA DLBCL

DEST="/mnt/hdd2/anna/LYNX/TRANSLOKACE_PRESTAVBA_DLBCL"
SERVER="keeper@lynx.ceitec.muni.cz"
#LIST="seznam_trans_prest-test.csv"
LIST="seznam_trans_prest.csv"

# oddělovač na čárku
while IFS=',' read -r run; do
  if [[ -z "$run" ]]; then
    echo "Chyba u : $run" >&2
    continue
  fi

  outfile="$DEST/${run}.gathered.xlsx"
  if [ -f "$outfile" ]; then
    echo "$run existuje, přeskočeno."
    continue
  fi

  echo "Kopírování $run z $run..."
  remote_path="/media/shared_new/lynx/lynx-app-full/storage/cmbgtfnbrno/$run/${run}--gathered/${run}.gathered.xlsx"
  scp "$SERVER:$remote_path" "$outfile"

  if [ $? -ne 0 ]; then
    echo "Chyba u $run ($remote_path)" >&2
  else
    echo "$run je OK."
  fi
done < "$LIST"

