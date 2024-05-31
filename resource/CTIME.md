PY009 Mennekes
==============

Pro naklonovaní repozitáře spusťte git-bash v místě, kde má repozitář 
existovat. Do příkazové řádky následně zapište:

    git clone /v/GIT_repozitare/PY009_Mennekes/.git

**POZOR:** některé soubory jsou ignorovány v .gitignore.

Implementace ovládacího programu pro desku Mennekes a zařízení beaglebone.


REV. 1.1
--------

- přidána kontrola kalibrace analogových vstupů. U vstupu AIN0 se po čase 
projevuje pokles hodnoty. Důvod jevu není známý.
- funkce spi.xfer2 nahrazena funkcí spi.writebytes pro 16 bitů. V jiném 
nastavení nebo při použití xfer2 občas dochází k výpadku odeslání jednoho
byte hodnoty.