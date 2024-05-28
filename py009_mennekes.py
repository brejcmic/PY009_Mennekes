#!/usr/bin/python3

""" Hlavní ovládací program jednotky Mennekes

    Program slouží k ovládání vstupů a čtení výstupů pomocí protokolu modbus TCP.
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------

# časování
import time

# čtení příkazové řádky
import sys

# běh s účtem root
import ctypes

# nezávislost na cestách os
import os
import os.path

# hlášení na konzoli
from src import peg_msg

# identifikace produktu
from src.peg_global_scope import PRODUCT_IDENTIFICATION
from src.peg_global_scope import getsettings

# singletony
from src.peg_global_scope import singleton_modbus_datastore as modbus_datastore

# počáteční hodnoty adres
from src.peg_global_scope import IP_ADDRESS
from src.peg_global_scope import PORT_MODBUS
from src.peg_global_scope import PORT_WEB

# modbus server
from src.peg_mdb import ModbusServer

# web server
from src.peg_web import WebServer

# vykonna funkce
from src.peg_exe import Execution

# ----------------------------------------------------------------------------------------------------------------------
# Konstanty modulu
# ----------------------------------------------------------------------------------------------------------------------

# pozadovan beh programu s administratorskymi pravy
RUN_AS_ADMIN = False

# ----------------------------------------------------------------------------------------------------------------------
# Globální funkce
# ----------------------------------------------------------------------------------------------------------------------
def is_admin():
    """
    Funkce zkontroluje administratorska prava pro beh programu.

    Returns
    -------
    iamadmin : bool
        True pokud program bezi s administratorskymi pravy. False jinak.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        return False

# ----------------------------------------------------------------------------------------------------------------------
# Hlavní třída modulu
# ----------------------------------------------------------------------------------------------------------------------
class PY009Mennekes:
    """
        Trida hlavniho programu, zaklada vsechny objekty a spousti komunikaci.
    """

    def __init__(self, terminal_argv: list = None):
        """
        Inicializace origramu z prikazove radky

        Parameters
        ----------
        terminal_argv : list
            seznam parametru prikazove radky.
        """
        # kontrola, ze byl program susten s administratorskymi pravy
        if RUN_AS_ADMIN and not is_admin():
            # Nove spusteni programu s administratorskymi pravy
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            exit(0)

        # ulozeni aktualni cesty ke skriptu
        self.mydir = os.path.dirname(os.path.realpath(__file__))

        # precteni parametru prikazove radky
        if terminal_argv is None:
            getsettings(sys.argv[1:])
        else:
            getsettings(terminal_argv)

        # volani prikazu pro konzoli za ucelem spusteni funkce ANSI znaku
        os.system('echo "Program {0} {1}, verze {2}"'.format(
            PRODUCT_IDENTIFICATION['ProductCode'],
            PRODUCT_IDENTIFICATION['ProductName'],
            PRODUCT_IDENTIFICATION['MajorMinorRevision']))
        peg_msg.print2postmort("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        peg_msg.print2postmort("@@@@@@@@@@@@@@@@@@@@@@@@ START PROGRAMU @@@@@@@@@@@@@@@@@@@@@@@@")
        peg_msg.print2postmort("Program {0} {1}, verze {2}".format(
            PRODUCT_IDENTIFICATION['ProductCode'],
            PRODUCT_IDENTIFICATION['ProductName'],
            PRODUCT_IDENTIFICATION['MajorMinorRevision']))

        # kontrola aktualniho stavu webove stranky
        webfiles = {
            "index.html": modbus_datastore.get_file_data("index.html"),
            "readdata.js": modbus_datastore.get_file_data("readdata.js"),
        }

        for key in webfiles:
            filepath = self.mydir + "/src/templates/" + key
            try:
                filetext = open(filepath, "r", encoding="utf-8").read()
            except IOError:
                filetext = "File not found"

            if filetext != webfiles[key]:
                try:
                    file = open(filepath, "w", encoding="utf-8")
                    file.write(webfiles[key])
                    file.close()
                    peg_msg.validmsg("Vytvoreni noveho souboru {0}".format(key))
                except IOError:
                    peg_msg.validmsg("Nepodarilo se vygenerovat novy soubor {0}".format(key))
                    exit(1)

        # nastaveni pocatecni ip adresy serveru
        self.ipaddr = IP_ADDRESS

        # nastaveni pocatecnich portu
        self.port_web = PORT_WEB
        self.port_modbus = PORT_MODBUS

        # nastaveni pocatecnich hodnot strid v modbusu
        modbus_datastore.set_hr_state(name="CP_DUTY1", value=100)
        modbus_datastore.set_hr_state(name="CP_DUTY2", value=100)

        # tvorba objektu modbus serveru
        self.srvmdb = ModbusServer(datastore=modbus_datastore,
                                   host=self.ipaddr,
                                   port=self.port_modbus)

        # zalozeni objektu weboveho serveru
        self.srvweb = WebServer(host=self.ipaddr,
                                port=self.port_web)

        # zalozeni vykonneho objektu
        self.process = Execution()

        # povoleni behu programu v nekonecne smycce
        self.program_enable = True

    def __del__(self):
        """
        Destruktor programu se postara o uzavreni bezicich vlaken a vycisteni pameti.

        Returns
        -------
            None.
        """
        try:
            self.srvweb.kill()
        except AttributeError:
            pass

        try:
            self.srvmdb.kill()
        except AttributeError:
            pass

    def main(self):
        """
        Hlavni programova smycka se vykonava do okamziku ukonceni chybou nebo zasahu uzivatele.

        Returns
        -------
        errcode : int
            kod chyby pro prikazovou radku, bez chyby je 0.
        """

        peg_msg.warningmsg("Start modbus serveru")
        self.srvmdb.restart()
        time.sleep(2)
        if not self.srvmdb.is_alive():
            peg_msg.errormsg("Vlakno modbus serveru se nepodarilo spustit")
            exit(1)

        peg_msg.warningmsg("Start WEB serveru")
        self.srvweb.restart()
        time.sleep(2)
        if not self.srvweb.is_alive():
            peg_msg.errormsg("Vlakno WEB serveru se nepodarilo spustit")
            exit(1)

        # sousteni programove smycky
        peg_msg.validmsg("Spusteni hlavni programove smycky.")

        srvweb_errcnt = 0
        srvmdb_errcnt = 0
        while self.program_enable:
            # kontrola behu web serveru
            if not self.srvweb.is_alive():
                if srvweb_errcnt < 10:
                    srvweb_errcnt = srvweb_errcnt + 1
                else:
                    peg_msg.warningmsg('Restart weboveho serveru')
                    self.srvweb.restart()
                    srvweb_errcnt = 0
            else:
                srvweb_errcnt = 0

            # kontrola behu modbus serveru
            if not self.srvmdb.is_alive():
                if srvmdb_errcnt < 10:
                    srvmdb_errcnt = srvmdb_errcnt + 1
                else:
                    peg_msg.warningmsg('Restart modbus serveru')
                    self.srvmdb.restart()
                    srvmdb_errcnt = 0
            else:
                srvweb_errcnt = 0

            # vybaveni funkci pripravku
            self.process.execute()

            time.sleep(0.2)

    def kill(self):
        """
        Funkce zastavi vykonavani hlavni smycky programu.

        Returns
        -------
            None
        """
        peg_msg.warningmsg("Hlavni smycka programu ukoncena na zaklade ukonceni povoleni behu.")
        self.program_enable = False



# ----------------------------------------------------------------------------------------------------------------------
# Spusteni modulu
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # zalozeni vlakna programu
    program = PY009Mennekes()
    # hlavni programova smycka
    try:
        program.main()
    except KeyboardInterrupt:
        peg_msg.errormsg("Program ukoncen uzivatelem z klavesnice")

    program = None

    exit(0)

