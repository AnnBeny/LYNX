### control_row_counts.py
spočítá počet řádků na vzorek a run pro xlsx soubory cna, snv, rearrangement, translocations u DLBCL

### control_sample_counts.py
spočítá počet vzorků každého runu pro xlsx soubory cna, snv, rearrangement, translocations u DLBCL

### cytoBand_hg38.txt
souřadnice cytogenetických pásem hg38, používané pro mapování genomových variant na chromozomální oblasti typu 1p36.33 nebo 5q21.1

### download_*.sh
stáhnou zdrojové soubory ze serveru LYNX - kluci dají přístup na keeper@lynx.ceitec.muni.cz
- download_cns_CLL.sh
- download_snv_CLL.sh
- download_cns_DLBCL.sh
- download_snv_DLBCL.sh
- download_trans_prest_dlbcl.sh

### merge_*.py
spojí všechny soubory jednotlivých vzorků do jednoho souboru
- merge_cna_CLL.py
- merge_snv_CLL.py
- merge_cna_DLBCL.py
- merge_snv_DLBCL.py

### separate_*.py
vezme všechny stažené soubory pro přestavby/translokace

### RUN_*.sh
spustí všechny skripty pro CLL/DLBCL najednou

---

## Postup
- vytvořit seznam vzorků **seznam_*.csv**
  | Run     | Sample   |
  |---------|----------|
- v terminálu zkontrolovat neviditelné znaky, které tam přidává excel **cat -A seznam_*.csv**
- a vymazat je **sed -i '1s/^\xEF\xBB\xBF//' seznam_*.csv**
- stáhnout soubory z Lynx serveru skriptem **download_*.sh**
- pokud něco spadne, opravit název v seznamu vzorků seznam_*.csv
- zjistit názvy sloupců ve stažených souborech skriptem **column.sh**, přidat chybějící sloupce do skriptu **merge_*.py**
