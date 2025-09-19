#!/bin/bash

DEST="/mnt/hdd2/anna/LYNX/ALL"
SERVER="keeper@lynx.ceitec.muni.cz"
#LIST="seznam_dlbcl-test.csv"
LIST="seznam_all.csv"

# oddělovač na čárku
while IFS=',' read -r run sample; do
  if [[ -z "$run" || -z "$sample" ]]; then
    echo "Chyba u : $run,$sample" >&2
    continue
  fi

  outfile="$DEST/${run}_${sample}.mutect2.cons.filt.norm.vep.csv"
  if [ -f "$outfile" ]; then
    echo "$run/$sample existuje, přeskočeno."
    continue
  fi

  echo "Kopírování $sample z $run..."
  remote_path="/media/shared_new/lynx/lynx-app-full/storage/cmbgtfnbrno/$run/$run/samples/$sample/variants/mutect2/${sample}.mutect2.cons.filt.norm.vep.csv"
  scp "$SERVER:$remote_path" "$outfile"

  if [ $? -ne 0 ]; then
    echo "Chyba u $sample ($remote_path)" >&2
  else
    echo "$sample je OK."
  fi
done < "$LIST"

