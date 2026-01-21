## Seznam skriptů

### columns.sh
vypíše názvy sloupečků - unikátní i u jednotlivých souborů

### control_row_counts.py
spočítá počet řádků na vzorek a run pro merged soubory a porovná s počtem řádků zdrojových souborů

### control_sample_counts.py
spočítá počet vzorků každého runu v merged souborech

### cytoBand_hg38.txt
souřadnice cytogenetických pásem hg38, používané pro mapování genomových variant na chromozomální oblasti typu 1p36.33 nebo 5q21.1

### download.sh
stáhne zdrojové soubory ze serveru LYNX - kluci dají přístup na keeper@lynx.ceitec.muni.cz

### merge_cna.py a merge_snv.py
spojí všechny soubory CNA/SNV jednotlivých vzorků do jednoho souboru

### separate_rearrang.py a separate_transl.py
vezme všechny stažené soubory pro přestavby/translokace, vybere listy s vybranýma vzorkama a spojí do jednoho excel souboru

---

## Postup
- vytvořit seznam vzorků dané diagnózy **seznam_*.csv** (např. seznam_dlbcl.csv), jeden sloupecek název runu, druhý název samplu, oddělený čárkou
  | Run     | Sample   |
  |---------|----------|
- v terminálu zkontrolovat neviditelné znaky, které tam přidává excel **cat -A seznam_*.csv**
- a vymazat je **sed -i '1s/^\xEF\xBB\xBF//' seznam_*.csv**
- a vymazat mezery na konci řádků **sed -i 's/[[:space:]]*$//' seznam_*.csv**
- stáhnout soubory z Lynx serveru skriptem **download.sh**
- pokud něco spadne, opravit název v seznamu vzorků seznam_*.csv
- zjistit názvy sloupců ve stažených souborech skriptem **column.sh**, přidat chybějící sloupce do skriptu **merge_*.py** nebo **separate_*.py**
- pomocí **control_*.py** skriptů zkontrolovat, jestli jsou tam všechny vzorky a sedí počet řádků (ne u translokací a přestaveb)
- upravit excely (změnit tečky na čárky, ...) podle poznámek **pozn.md**
