""" GLOBAL_SCOPE Globální proměnné a konstanty programu

    Modul obsahuje konstanty, proměnné a objekty, které mohou být přístupné z jiných modulů. Objekty jsou považovány
    za singletony.
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------
# import cteni cest
from os.path import dirname

# import framework pro web
from flask import Flask

# cteni a zapis konfiguracniho souboru
import getopt
import configparser

# datovy prostor modbusu
try:
    import peg_das
except (ImportError, ModuleNotFoundError):
    from src import peg_das

# modbus server
try:
    import peg_mdb
except (ImportError, ModuleNotFoundError):
    from src import peg_mdb

# hlaseni na konzoli
try:
    import peg_msg
except ImportError:
    from src import peg_msg

# ----------------------------------------------------------------------------------------------------------------------
# Konstanty modulu
# ----------------------------------------------------------------------------------------------------------------------
# napoveda
# ========
USAGE = """
--------------------------------------------------------------------------------
Program py009_mennekes slouzi pro ovladani hw periferii DPS 'Mennekes 
Controller' a 'Mennekes Driver' pomoci protokolu Modbus TCP.

Pouziti:
      py009_mennekes [OPTIONS]

Parametry:
-h, --help          
                Tisk teto napovedy.
-i [IP_ADDRESS], --ipaddr=[IP_ADDRESS]
                Zadani ip adresy, na ktere maji byt dostupne servery webu a
                modbusu.
-r [CONFIG_FILE], --read=[CONFIG_FILE]
                Nacteni parametru konfigurace z predavaneho souboru.
-w [CONFIG_FILE], --write=[CONFIG_FILE]
                Zapis noveho konfiguracniho souboru. Po volani se program 
                ukonci.
"""

# predpis konfiguracniho souboru
# ==============================
CFG_TEMPLATE = """[PRODUCT_IDENTIFICATION]
{0}

[PCB_REVISION]
# revize dps, ktere program obsluhuje
{1}

[ELECTROMETERS]
# 'type' musi byt jedna z nasledujicich hodnot: 
#   pulse ... signal pulsu elektromeru je pripojeny na vstup IN1P0_ELEM 
#   schrack_mgrzk465 ... elektromer schrack MGRZK 465 s protokolem modbus
#     pripojeny pomoci rs485
{2}

[LEDS]
# Typ pripojeni signalizacnich LED podle spolecne elektrody. Povolene
# hodnoty jsou:
#   cathode ... spolecna katoda
#   anode ... spolecna anoda
{3}
"""

# typy hodnot v konfiguracnim souboru
# ===================================
CFG_KEY_CLASS = {
    "ModelName": str,
    "driver": float,
    "controller": float,
    "ch1_type": str,
    "ch2_type": str,
    "ch1_common_electrode": str,
    "ch2_common_electrode": str,
}

# revize DPS jako float
# =====================
PCB_REVISION = {
    "driver": 1.2,
    "controller": 3.0
}

# typ pripojeni elektromeru
# =========================
# - pulse,
# - schrack_mgrzk465
ELECTROMETER_TYPES = ["pulse", "pulse"]

# typ pripojeni signalizacnich LED
# ================================
# cathode, anode
LED_COMMON_ELECTRODE = ["cathode", "cathode"]

# Aktualni verze programu
# =======================
PRODUCT_IDENTIFICATION = {
    "VendorName": "PEG spol. s r.o.",
    "ProductCode": "PY009",
    "MajorMinorRevision": "1.3",
    "VendorUrl": "peg.cz",
    "ProductName": "Mennekes",
    "ModelName": "WallBox"
}

# IP adresa zarizeni a otevrene porty
# ===================================
IP_ADDRESS = "0.0.0.0"
PORT_MODBUS = 502
PORT_WEB = 8080

# pametovy prostor civek
# ======================
COILS = {
    'DISABLE_LOCK12': {
        'address': 1,
        'description': 'povolení funkce budiče zámku konektorů'
    },
    'POWER_SW1': {
        'address': 2,
        'description': 'povel pro relé na kanálu 1 - hlavního stykače'
    },
    'OPEN_LOCK1': {
        'address': 3,
        'description': 'povel pro otevření zámku kanálu 1'
    },
    'CLOSE_LOCK1': {
        'address': 4,
        'description': 'povel pro zavření zámku kanálu 1'
    },
    'LED_RED1': {
        'address': 5,
        'description': 'povel pro svícení červenou LED na kanálu 1'
    },
    'LED_GREEN1': {
        'address': 6,
        'description': 'povel pro svícení zelenou LED na kanálu 1'
    },
    'LED_BLUE1': {
        'address': 7,
        'description': 'povel pro svícení modrou LED na kanálu 1'
    },
    'IN1P0_ELEM_CNT_CLR': {
        'address': 8,
        'description': 'nulování počítadla náběžných hran pro vstup IN1P0, logická 1 drží počítadlo v nule'
    },
    'IN1P1_LOCK_CNT_CLR': {
        'address': 9,
        'description': 'nulování počítadla náběžných hran pro vstup IN1P1, logická 1 drží počítadlo v nule'
    },
    'IN1P2_STOK_CNT_CLR': {
        'address': 10,
        'description': 'nulování počítadla náběžných hran pro vstup IN1P2, logická 1 drží počítadlo v nule'
    },
    'IN1P3_BTON_CNT_CLR': {
        'address': 11,
        'description': 'nulování počítadla náběžných hran pro vstup IN1P3, logická 1 drží počítadlo v nule'
    },
    'ELECTROMETER1_CLR': {
        'address': 12,
        'description': 'nulování stavu elektroměru kanálu 1'
    },
    'POWER_SW2': {
        'address': 22,
        'description': 'povel pro relé na kanálu 2 - hlavního stykače'
    },
    'OPEN_LOCK2': {
        'address': 23,
        'description': 'povel pro otevření zámku kanálu 2'
    },
    'CLOSE_LOCK2': {
        'address': 24,
        'description': 'povel pro zavření zámku kanálu 2'
    },
    'LED_RED2': {
        'address': 25,
        'description': 'povel pro svícení červenou LED na kanálu 2'
    },
    'LED_GREEN2': {
        'address': 26,
        'description': 'povel pro svícení zelenou LED na kanálu 2'
    },
    'LED_BLUE2': {
        'address': 27,
        'description': 'povel pro svícení modrou LED na kanálu 2'
    },
    'IN2P0_ELEM_CNT_CLR': {
        'address': 28,
        'description': 'nulování počítadla náběžných hran pro vstup IN2P0, logická 1 drží počítadlo v nule'
    },
    'IN2P1_LOCK_CNT_CLR': {
        'address': 29,
        'description': 'nulování počítadla náběžných hran pro vstup IN2P1, logická 1 drží počítadlo v nule'
    },
    'IN2P2_STOK_CNT_CLR': {
        'address': 30,
        'description': 'nulování počítadla náběžných hran pro vstup IN2P2, logická 1 drží počítadlo v nule'
    },
    'IN2P3_BTON_CNT_CLR': {
        'address': 31,
        'description': 'nulování počítadla náběžných hran pro vstup IN2P3, logická 1 drží počítadlo v nule'
    },
    'ELECTROMETER2_CLR': {
        'address': 32,
        'description': 'nulování stavu elektroměru kanálu 2'
    },
}

# pametovy prostor logickych vstupu
# =================================
DIGITAL_INPUTS = {
    'DISABLE_LOCK12': {
        'address': 1,
        'description': 'stav povolení funkce budiče zámku konektorů'
    },
    'POWER_SW1': {
        'address': 2,
        'description': 'stav relé kanálu 1 - stav hlavního stykače'
    },
    'OPEN_LOCK1': {
        'address': 3,
        'description': 'stav povelu pro otevření zámku kanálu 1'
    },
    'CLOSE_LOCK1': {
        'address': 4,
        'description': 'stav povelu pro zavření zámku kanálu 1'
    },
    'LED_RED1': {
        'address': 5,
        'description': 'stav povelu pro svícení červenou LED na kanálu 1'
    },
    'LED_GREEN1': {
        'address': 6,
        'description': 'stav povelu pro svícení zelenou LED na kanálu 1'
    },
    'LED_BLUE1': {
        'address': 7,
        'description': 'stav povelu pro svícení modrou LED na kanálu 1'
    },
    'IN1P0_ELEM': {
        'address': 8,
        'description': 'stav digitálního vstupu IN1P0, pulsy elektroměru kanálu 1'
    },
    'IN1P1_LOCK': {
        'address': 9,
        'description': 'stav digitálního vstupu IN1P1, stav zámku kanálu 1'
    },
    'IN1P2_STOK': {
        'address': 10,
        'description': 'stav digitálního vstupu IN1P2, detekce vnější chyby kanálu 1'
    },
    'IN1P3_BTON': {
        'address': 11,
        'description': 'stav digitálního vstupu IN1P3, tlačítko spuštění kanálu 2'
    },
    'POWER_SW2': {
        'address': 22,
        'description': 'stav relé kanálu 2 - stav hlavního stykače'
    },
    'OPEN_LOCK2': {
        'address': 23,
        'description': 'stav povelu pro otevření zámku kanálu 2'
    },
    'CLOSE_LOCK2': {
        'address': 24,
        'description': 'stav povelu pro zavření zámku kanálu 2'
    },
    'LED_RED2': {
        'address': 25,
        'description': 'stav povelu pro svícení červenou LED na kanálu 2'
    },
    'LED_GREEN2': {
        'address': 26,
        'description': 'stav povelu pro svícení zelenou LED na kanálu 2'
    },
    'LED_BLUE2': {
        'address': 27,
        'description': 'stav povelu pro svícení modrou LED na kanálu 2'
    },
    'IN2P0_ELEM': {
        'address': 28,
        'description': 'stav digitálního vstupu IN2P0, pulsy elektroměru kanálu 2'
    },
    'IN2P1_LOCK': {
        'address': 29,
        'description': 'stav digitálního vstupu IN2P1, stav zámku kanálu 2'
    },
    'IN2P2_STOK': {
        'address': 30,
        'description': 'stav digitálního vstupu IN2P2, detekce vnější chyby kanálu 2'
    },
    'IN2P3_BTON': {
        'address': 31,
        'description': 'stav digitálního vstupu IN2P3, tlačítko spuštění kanálu 2'
    },
}

# pametovy prostor holding registru
# =================================
HOLDING_REGISTERS = {
    'COUNTER_TOP': {
        'address': 1,
        'description': 'testovací - counter v input registrech čítá s periodou 1 s od 0 do této hodnoty'
    },
    'CP_DUTY1': {
        'address': 2,
        'description': 'zadání hodnoty střídy signálu CP na kanálu 1'
    },
    'CP_DUTY2': {
        'address': 22,
        'description': 'zadání hodnoty střídy signálu CP na kanálu 2'
    },
}
# pametovy prostor vstupnich registru
# ===================================
INPUT_REGISTERS = {
    'COUNTER': {
        'address': 1,
        'description': 'testovací - pocitadlo do hodnoty counter_top s pretecenim, inkrementace po 1 s'
    },
    'CP_DUTY1': {
        'address': 2,
        'description': 'hodnota střídy signálu CP na kanálu 1 v jednotkách %'
    },
    'CP_VOLTAGE1': {
        'address': 3,
        'description': 'hodnota kladného maxima signálu CP na kanálu 1 v jednotkách V'
    },
    'PP_RESISTANCE1': {
        'address': 4,
        'description': 'hodnota připojeného odporu na vodiči PP u kanálu 1 v jednotkách ohm'
    },
    'IN1P0_ELEM_CNT_L': {
        'address': 5,
        'description': 'stav počítadla náběžných hran vstupu IN1P0, nižší byte'
    },
    'IN1P0_ELEM_CNT_H': {
        'address': 6,
        'description': 'stav počítadla náběžných hran vstupu IN1P0, vyšší byte'
    },
    'IN1P1_LOCK_CNT_L': {
        'address': 7,
        'description': 'stav počítadla náběžných hran vstupu IN1P1, nižší byte'
    },
    'IN1P1_LOCK_CNT_H': {
        'address': 8,
        'description': 'stav počítadla náběžných hran vstupu IN1P1, vyšší byte'
    },
    'IN1P2_STOK_CNT_L': {
        'address': 9,
        'description': 'stav počítadla náběžných hran vstupu IN1P2, nižší byte'
    },
    'IN1P2_STOK_CNT_H': {
        'address': 10,
        'description': 'stav počítadla náběžných hran vstupu IN1P2, vyšší byte'
    },
    'IN1P3_BTON_CNT_L': {
        'address': 11,
        'description': 'stav počítadla náběžných hran vstupu IN1P3, nižší byte'
    },
    'IN1P3_BTON_CNT_H': {
        'address': 12,
        'description': 'stav počítadla náběžných hran vstupu IN1P3, vyšší byte'
    },
    'ELECTROMETER1_L': {
        'address': 13,
        'description': 'stav elektroměru kanálu 1 v jednotkách Wh, nižší byte'
    },
    'ELECTROMETER1_H': {
        'address': 14,
        'description': 'stav elektroměru kanálu 1 v jednotkách Wh, vyšší byte'
    },
    'CP_DUTY2': {
        'address': 22,
        'description': 'hodnota střídy signálu CP na kanálu 2 v jednotkách %'
    },
    'CP_VOLTAGE2': {
        'address': 23,
        'description': 'hodnota kladného maxima signálu CP na kanálu 2 v jednotkách V'
    },
    'PP_RESISTANCE2': {
        'address': 24,
        'description': 'hodnota připojeného odporu na vodiči PP u kanálu 2'
    },
    'IN2P0_ELEM_CNT_L': {
        'address': 25,
        'description': 'stav počítadla náběžných hran vstupu IN2P0, nižší byte'
    },
    'IN2P0_ELEM_CNT_H': {
        'address': 26,
        'description': 'stav počítadla náběžných hran vstupu IN2P0, vyšší byte'
    },
    'IN2P1_LOCK_CNT_L': {
        'address': 27,
        'description': 'stav počítadla náběžných hran vstupu IN2P1, nižší byte'
    },
    'IN2P1_LOCK_CNT_H': {
        'address': 28,
        'description': 'stav počítadla náběžných hran vstupu IN2P1, vyšší byte'
    },
    'IN2P2_STOK_CNT_L': {
        'address': 29,
        'description': 'stav počítadla náběžných hran vstupu IN2P2, nižší byte'
    },
    'IN2P2_STOK_CNT_H': {
        'address': 30,
        'description': 'stav počítadla náběžných hran vstupu IN2P2, vyšší byte'
    },
    'IN2P3_BTON_CNT_L': {
        'address': 31,
        'description': 'stav počítadla náběžných hran vstupu IN2P3, nižší byte'
    },
    'IN2P3_BTON_CNT_H': {
        'address': 32,
        'description': 'stav počítadla náběžných hran vstupu IN2P3, vyšší byte'
    },
    'ELECTROMETER2_L': {
        'address': 33,
        'description': 'stav elektroměru kanálu 2 v jednotkách Wh, nižší byte'
    },
    'ELECTROMETER2_H': {
        'address': 34,
        'description': 'stav elektroměru kanálu 2 v jednotkách Wh, vyšší byte'
    },
}

# ----------------------------------------------------------------------------------------------------------------------
# Globální singletony modulu
# ----------------------------------------------------------------------------------------------------------------------
# tvorba pametoveho prostoru modbusu
singleton_modbus_datastore = peg_das.DataStore(identification=PRODUCT_IDENTIFICATION,
                                               coils=COILS,
                                               digital_inputs=DIGITAL_INPUTS,
                                               holding_registers=HOLDING_REGISTERS,
                                               input_registers=INPUT_REGISTERS)

# tvorba objektu aplikace Flask
root_path = dirname(__file__)
singleton_flask_app = Flask(PRODUCT_IDENTIFICATION["ProductName"], root_path=root_path)


# ----------------------------------------------------------------------------------------------------------------------
# Globální funkce modulu
# ----------------------------------------------------------------------------------------------------------------------
# Ziskani parametru z prikazove radky
# argv ... seznam parametru prikazove radky
def getsettings(argv: list) -> None:
    """
    Funkce cte parametry z prikazove radky a zajistuje nastaveni nebo obslouzeni prislusnych pozadavku.

    Parameters
    ----------
    argv : list of str
        nactene retezce prikazove radky
    """

    # cteni vlajek prikazove radky
    try:
        opts, args = getopt.getopt(argv, "hr:w:", ["help", "read=", "write="])
    except getopt.GetoptError:
        peg_msg.errormsg(f"Nepodarilo precist parametry prikazove radky.")
        exit(1)

    rfilename = None
    wfilename = None

    # prochazeni vlajek
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            # tisk napovedy
            print(USAGE)
            exit(0)
        elif opt in ("-r", "--read"):
            # pozadavek cteni konfigurace ze souboru
            rfilename = str(arg)
        elif opt in ("-w", "--read"):
            # pozadavek na zapis konfigurace do souboru
            wfilename = str(arg)
        else:
            peg_msg.errormsg(f"Neplatna volba {opt}")
            exit(1)

    if rfilename:
        rconfig = configparser.ConfigParser()
        rconfig.read(rfilename)

        if "PRODUCT_IDENTIFICATION" in rconfig:
            if "ModelName" in rconfig["PRODUCT_IDENTIFICATION"]:
                PRODUCT_IDENTIFICATION["ModelName"] = CFG_KEY_CLASS["ModelName"](
                    rconfig["PRODUCT_IDENTIFICATION"]["ModelName"])
                peg_msg.validmsg("Cteni konfigurace PRODUCT_IDENTIFICATION: 'ModelName = {0}'".format(
                    PRODUCT_IDENTIFICATION["ModelName"]))

        if "PCB_REVISION" in rconfig:
            for key in PCB_REVISION:
                if key in rconfig["PCB_REVISION"]:
                    PCB_REVISION[key] = CFG_KEY_CLASS[key](rconfig["PCB_REVISION"][key])
                    peg_msg.validmsg("Cteni konfigurace PCB_REVISION: {0} = {1}".format(
                        key, PCB_REVISION[key]))

        if "ELECTROMETERS" in rconfig:
            if "ch1_type" in rconfig["ELECTROMETERS"]:
                ELECTROMETER_TYPES[0] = CFG_KEY_CLASS["ch1_type"](rconfig["ELECTROMETERS"]["ch1_type"])
                peg_msg.validmsg("Cteni konfigurace ELECTROMETERS: ch1_type = {0}".format(ELECTROMETER_TYPES[0]))
            if "ch2_type" in rconfig["ELECTROMETERS"]:
                ELECTROMETER_TYPES[1] = CFG_KEY_CLASS["ch2_type"](rconfig["ELECTROMETERS"]["ch2_type"])
                peg_msg.validmsg("Cteni konfigurace ELECTROMETERS: ch2_type = {0}".format(ELECTROMETER_TYPES[1]))

        if "LEDS" in rconfig:
            if "ch1_common_electrode" in rconfig["LEDS"]:
                LED_COMMON_ELECTRODE[0] = CFG_KEY_CLASS["ch1_common_electrode"](rconfig["LEDS"]["ch1_common_electrode"])
                peg_msg.validmsg("Cteni konfigurace LEDS: ch1_common_electrode = {0}".format(LED_COMMON_ELECTRODE[0]))
            if "ch2_common_electrode" in rconfig["LEDS"]:
                LED_COMMON_ELECTRODE[1] = CFG_KEY_CLASS["ch2_common_electrode"](rconfig["LEDS"]["ch2_common_electrode"])
                peg_msg.validmsg("Cteni konfigurace LEDS: ch2_common_electrode = {0}".format(LED_COMMON_ELECTRODE[1]))

    if wfilename:
        product_indetification_section = "\nModelName = {0}".format(PRODUCT_IDENTIFICATION["ModelName"])

        pcb_revision_section = ""
        for key in PCB_REVISION:
            pcb_revision_section = pcb_revision_section + "\n{0} = {1}".format(key, PCB_REVISION[key])

        electrometers_section = "\nch1_type = {0}\nch2_type = {1}"
        electrometers_section = electrometers_section.format(ELECTROMETER_TYPES[0], ELECTROMETER_TYPES[1])

        leds_section = "\nch1_common_electrode = {0}\nch2_common_electrode = {1}"
        leds_section = leds_section.format(LED_COMMON_ELECTRODE[0], LED_COMMON_ELECTRODE[1])

        wconfig = CFG_TEMPLATE.format(product_indetification_section,
                                      pcb_revision_section,
                                      electrometers_section,
                                      leds_section)

        try:
            with open(wfilename, 'w') as configfile:
                try:
                    configfile.write(wconfig)
                    peg_msg.validmsg("Zapis noveho konfiguracniho souboru: {0}".format(wfilename))
                except (IOError, OSError):
                    peg_msg.errormsg("Nepodarilo se zapsat konfiguracni soubor.")
        except (FileNotFoundError, PermissionError, OSError):
            peg_msg.errormsg("Nepodarilo se otevrit konfiguracni soubor pro zapis.")
        exit(0)


if __name__ == "__main__":
    getsettings(["-r", "config.ini"])
