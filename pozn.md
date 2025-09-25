online verze excel max pocet radku 1 048 576
- 1 run = 465 radku * 16 samplu => 140 runu

komentáře se průběžně doplňují -> vždy aktualizovat všechny zdrojové soubory

cesta na keeperu: 
- /media/shared_new/lynx/lynx-app-full/storage/cmbgtfnbrno

ID vzorků 
- nejsou unikátní, mohou se opakovat, unikátní je kombinace s Run

pozor na desetinné čárky a tečky - někde je potřeba zachovat čárky, jinde lepší změny na čárky

někdy se objeví html značka v souboru ze keeperu (vyřešeno ve skriptu)

sloupce af, eur_af, gnomad_af, gnomad_nfe_af, max_af
- místo prázdných hodnot doplnit 0,000 kvůli filtrování

v class:
- R - přestavba
- SV - translokace
- SV-R - translokace imunoglobulinových genů, měly by se dublovat s přestavbami
- VAR - identifikované varianty tímto algoritmem, měly by se dublovat se SNV výsledky druhé pipeliny

Ve sloupci class2 jsou upřesňující hodnoty pro class1:
- pro class1=R - druh přestavby (e.g. VD:Vb-Db, VJ:Vb-(Db)-Jb)
- pro class1=SV - asi jenom translocation
- pro class1=SV-R - druh přestavby
- pro class1=VAR - deletion, insertion, substitution, SNV

Přejmenování sloupců:
- probes -> bins
- gene -> LPD genes
- více viz soubor LYNX sloupecky.xlsx

Dopočítání:
- length = end - start
- Pro cytoband se používá soubor cytoBand_hg38.txt a kód:
x.cyt_start = this.state.cytobands.filter(y => y.CHR === x.chromosome & Number(y.from) <= Number(x.start.replace(/,/g, '')) & Number(y.to) > Number(x.start.replace(/,/g, '')))[0].arm
x.cyt_end = this.state.cytobands.filter(y => y.CHR === x.chromosome & Number(y.from) <= Number(x.end.replace(/,/g, '')) & Number(y.to) > Number(x.end.replace(/,/g, '')))[0].arm
- ve skriptu přepsáno do Pythonu

Zkratky názvů diagnóz:
- https://bloodcancer.org.uk/understanding-blood-cancer/blood-cancer-types/