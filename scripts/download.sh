#!/bin/bash

# ./download.sh [cns|snv|trans] [ALL|DLBCL|CMM]

DATA_KIND="${1:-}"
DX="${2:-}"

# Choice menu for data type
if [[ -z "${DATA_KIND:-}" ]]; then
  PS3="Vyber typ dat (1-3): "
  select opt in "cns" "snv" "translocations_rearrangement"; do
    case "$REPLY" in 1|2|3) DATA_KIND="$opt"; break ;; *) echo "Neplatný výběr."; ;; esac
  done
fi

# Choice menu for diagnosis
if [[ -z "${DX:-}" ]]; then
  PS3="Vyber diagnózu (1-4): "
  select opt in "ALL" "DLBCL" "CLL" "MM"; do
    case "$REPLY" in 1|2|3|4) DX="$opt"; break ;; *) echo "Neplatný výběr."; ;; esac
  done
fi

echo "CHOICES: DATA_KIND=$DATA_KIND  DX=$DX"

#set -euo pipefail

# lc = lowercase
# uc = uppercase
# ucfirst = Uppercase first letter
lc() { printf '%s' "${1,,}"; }

KIND_LO="${DATA_KIND,,}"   # cns/snv/trans
DX_UP="${DX^^}"            # ALL/DLBCL/CLL
DX_LO="${DX,,}"            # all/dlbcl/cll

ROOT="/mnt/hdd2/anna/LYNX"
STAMP="$(date +%F)"
DEST="$ROOT/raw_$(lc "$DX")_$(lc "$DATA_KIND")_$STAMP"
SERVER="keeper@lynx.ceitec.muni.cz"
#SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
LIST="$ROOT/seznam_$(lc "$DX").csv"

echo "OUTPUT=$DEST"
#echo "BASH_SOURCE=$BASH_SOURCE"
#echo "SCRIPT_DIR=$SCRIPT_DIR"
#echo "ROOT=$ROOT"
#echo "DATE=$STAMP"
#echo "SERVER=$SERVER"
#echo "SCRIPT_DIR=$SCRIPT_DIR"
#echo "LIST=$LIST"
#echo "SNAP=$SNAP"

mkdir -p "$DEST"

err=0
declare -a downloaded=()
declare -a skipped=()
declare -a failures=()

# --- CNS ----
if [[ "$DATA_KIND" == "cns" ]]; then
    while IFS=',' read -r run sample; do
        if [[ -z "$run" || -z "$sample" ]]; then
            echo "Chyba u : $run,$sample" >&2
            continue
        fi

        outfile="$DEST/${run}_${sample}.call.cns"
        if [ -f "$outfile" ]; then
            echo "$run/$sample existuje, přeskočeno."
            skipped+=("$run/$sample -> $(basename "$outfile")")
            continue
        fi

        echo "Kopírování $sample z $run..."
        remote_path="/media/shared_new/lynx/lynx-app-full/storage/cmbgtfnbrno/$run/$run/samples/$sample/cnv/${sample}.call.cns"
        if scp "$SERVER:$remote_path" "$outfile"; then
            echo "$sample je OK."
            downloaded+=("$run/$sample -> $(basename "$outfile")")
        else
            echo "Chyba u $sample ($remote_path)" >&2
            failures+=("$run/$sample ($remote_path)")
            ((err++))
        fi
    done < "$LIST"
# --- SNV ----
elif [[ "$DATA_KIND" == "snv" ]]; then
    while IFS=',' read -r run sample; do
        if [[ -z "$run" || -z "$sample" ]]; then
            echo "Chyba u : $run,$sample" >&2
            continue
        fi

        outfile="$DEST/${run}_${sample}.mutect2.cons.filt.norm.vep.csv"
        if [ -f "$outfile" ]; then
            echo "$run/$sample existuje, přeskočeno."
            skipped+=("$run/$sample -> $(basename "$outfile")")
            continue
        fi

        echo "Kopírování $sample z $run..."
        remote_path="/media/shared_new/lynx/lynx-app-full/storage/cmbgtfnbrno/$run/$run/samples/$sample/variants/mutect2/${sample}.mutect2.cons.filt.norm.vep.csv"
        if scp "$SERVER:$remote_path" "$outfile"; then
            echo "$sample je OK."
            downloaded+=("$run/$sample -> $(basename "$outfile")")
        else
            echo "Chyba u $sample ($remote_path)" >&2
            failures+=("$run/$sample ($remote_path)")
            ((err++))
        fi
    done < "$LIST"
# --- TRANSLOCATIONS REARRANGEMENT ----
elif [[ "$DATA_KIND" == "translocations_rearrangement" ]]; then
    # awk -F',' 'NR>1{print $1}' "$LIST" | sort -u | while read -r run; do
    #     if [[ -z "$run" ]]; then
    #         echo "Chyba u : $run" >&2
    #         continue
    #     fi
    
    while read -r run; do
        [[ -z "$run" ]] && { echo "Chyba u : $run" >&2; continue; }

        outfile="$DEST/${run}.gathered.xlsx"
        if [ -f "$outfile" ]; then
            echo "$run existuje, přeskočeno."
            skipped+=("$run -> $(basename "$outfile")")
            continue
        fi

        echo "Kopírování $run z $run..."
        remote_path="/media/shared_new/lynx/lynx-app-full/storage/cmbgtfnbrno/$run/${run}--gathered/${run}.gathered.xlsx"
        if scp "$SERVER:$remote_path" "$outfile"; then
            echo "$run je OK."
            downloaded+=("$run -> $(basename "$outfile")")
        else
            echo "Chyba u $run ($remote_path)" >&2
            failures+=("$run ($remote_path)")
            ((err++))
        fi
    done < <(awk -F',' 'NR>1{print $1}' "$LIST" | sort -u)
else
    echo "Neznámý TYPE: $DATA_KIND (použij cns|snv|trans)" >&2; exit 2
fi

# --- SYMLINKS ----
echo "Creating symlinks in $ROOT/$DX ..."
# Use DX as-is (DX is already uppercase: ALL, DLBCL, CLL...)
ACTIVE="$ROOT/$DX"
printf "ACTIVE=%s\n" "$ACTIVE"
mkdir -p "$ACTIVE"

# Create symlinks based on data type
if [[ "$DATA_KIND" == "cns" ]]; then
    for file in "$DEST"/*.call.cns; do
        ln -sf "$file" "$ACTIVE/$(basename "$file")"
    done
elif [[ "$DATA_KIND" == "snv" ]]; then
    for file in "$DEST"/*.mutect2.cons.filt.norm.vep.csv; do
        ln -sf "$file" "$ACTIVE/$(basename "$file")"
    done
elif [[ "$DATA_KIND" == "translocations_rearrangement" ]]; then
    for file in "$DEST"/*.gathered.xlsx; do
        ln -sf "$file" "$ACTIVE/$(basename "$file")"
    done
fi

[[ "$err" -eq 0 ]] || echo "Hotovo s chybami: $err" >&2

echo "Aktualizováno: $ACTIVE (symlinky)  a  manifest: $DEST/manifest.tsv"

SUMMARY_FILE="$DEST/download_summary.log"
{
    echo "===== Shrnutí stahování ($(date +%F' '%T)) ====="
    echo "DATA_KIND: $DATA_KIND"
    echo "Diagnóza: $DX"
    echo
    if ((${#downloaded[@]})); then
        echo "Stažené položky (${#downloaded[@]}):"
        printf '  - %s\n' "${downloaded[@]}"
    else
        echo "Stažené položky: nic nového."
    fi
    echo
    if ((${#skipped[@]})); then
        echo "Přeskočené položky (${#skipped[@]}):"
        printf '  - %s\n' "${skipped[@]}"
    else
        echo "Přeskočené položky: žádné."
    fi
    echo
    if ((${#failures[@]})); then
        echo "Chyby (${#failures[@]}):"
        printf '  - %s\n' "${failures[@]}"
    else
        echo "Chyby: žádné."
    fi
    echo
    if (( err == 0 )); then
        echo "Výsledek: HOTOVO [OK]"
    else
        echo "Výsledek: HOTOVO s chybami ($err) [WARN]"
    fi
} | tee "$SUMMARY_FILE"
echo "Souhrnný log uložen do: $SUMMARY_FILE"
