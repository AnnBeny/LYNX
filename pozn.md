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
pozor na desetinné čárky a tečky - někde je potřeba zachovat tečky, jinde lepší změny na čárky
</li>

<li>
někdy se objeví html značka v souboru z keeperu (řešeno ve skriptu, ale někdy to nefunguje a musí se to opravit ručně!)
html < br > a < div > se objevuje i v komentářích, ale nevadí při merge, stačí smazat až ve výsledných souborech+
v některych souborech celý řádek  jen html kod (i na LYNX)
</li>

<h5>SNV</h5>
<li>
sloupce af, eur_af, gnomad_af, gnomad_nfe_af, max_af
<ul><li>místo prázdných hodnot doplnit 0,000 kvůli filtrování</li></ul>
<ul><li>místo teček čárky</li></ul>
ve sloupci tumor_AF, strand_bias, MANE_SELECT nechat tečky
sloupce duplicated, mapped, on_target 
    <ul><li>tečky na čárky</ul></li>
    <ul><li>nastavit buňky na procenta</ul></li>
</li>
<br>
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
<ul><li>více viz soubor LYNX sloupecky.xlsx (nasdílená tab od Toma)</li></ul>
<ul><li>%locus v tab s přejmenováním jako %, ale na LYNX UI odpovídá sloupci 'frequency'
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