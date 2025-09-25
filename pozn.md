<ul>
<li>
online verze excel max pocet radku 1 048 576
<ul><li>1 run = 465 radku * 16 samplu => 140 runu</li></ul>
</li>

<li>
komentáře se průběžně doplňují -> vždy aktualizovat všechny zdrojové soubory
</li>

<li>
cesta na keeperu: 
<ul><li>/media/shared_new/lynx/lynx-app-full/storage/cmbgtfnbrno</li></ul>
</li>

<li>
ID vzorků 
<ul><li>nejsou unikátní, mohou se opakovat, unikátní je kombinace s Run</li></ul>
</li>

<li>
pozor na desetinné čárky a tečky - někde je potřeba zachovat čárky, jinde lepší změny na čárky
</li>

<li>
někdy se objeví html značka v souboru ze keeperu (vyřešeno ve skriptu)
</li>

<li>
sloupce af, eur_af, gnomad_af, gnomad_nfe_af, max_af
<ul><li>místo prázdných hodnot doplnit 0,000 kvůli filtrování</li></ul>
</li>

<li>
v class:
<ul><li>R - přestavba</li></ul>
<ul><li>SV - translokace</li></ul>
<ul><li>SV-R - translokace imunoglobulinových genů, měly by se dublovat s přestavbami</li></ul>
<ul><li>VAR - identifikované varianty tímto algoritmem, měly by se dublovat se SNV výsledky druhé pipeliny</li></ul>
</li>

<li>
Ve sloupci class2 jsou upřesňující hodnoty pro class1:
<ul><li>pro class1=R - druh přestavby (e.g. VD:Vb-Db, VJ:Vb-(Db)-Jb)</li></ul>
<ul><li>pro class1=SV - asi jenom translocation</li></ul>
<ul><li>pro class1=SV-R - druh přestavby</li></ul>
<ul><li>pro class1=VAR - deletion, insertion, substitution, SNV</li></ul>
</li>

<li>
Přejmenování sloupců:
<ul><li>probes -> bins</li></ul>
<ul><li>gene -> LPD genes</li></ul>
<ul><li>více viz soubor LYNX sloupecky.xlsx</li></ul>
</li>

<li>
Dopočítání:
<ul><li>length = end - start</li></ul>
<ul><li>Pro cytoband se používá soubor cytoBand_hg38.txt a kód:
x.cyt_start = this.state.cytobands.filter(y => y.CHR === x.chromosome & Number(y.from) <= Number(x.start.replace(/,/g, '')) & Number(y.to) > Number(x.start.replace(/,/g, '')))[0].arm
x.cyt_end = this.state.cytobands.filter(y => y.CHR === x.chromosome & Number(y.from) <= Number(x.end.replace(/,/g, '')) & Number(y.to) > Number(x.end.replace(/,/g, '')))[0].arm</li></ul>
<ul><li>ve skriptu přepsáno do Pythonu</li></ul>
</li>

<li>
Zkratky názvů diagnóz:
<ul><li>https://bloodcancer.org.uk/understanding-blood-cancer/blood-cancer-types/</li></ul>
</li>
</ul>