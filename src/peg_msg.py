# Tisk informacnich zprav na konzoli

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------
# cteni aktualniho data a casu
import datetime
import collections

# ----------------------------------------------------------------------------------------------------------------------
# Konstanty modulu
# ----------------------------------------------------------------------------------------------------------------------
# cesta pro nacteni testovaciho souboru, pokud neni definovana (None) tak se soubor nevytvari.
POSTMORT_FILE = None

# fronta zprav postmort pro zobrazeni
POSTMORT_QUEUE = collections.deque(maxlen=15)

# GLOBALNI PROMENNE MODULU
# ----------------------------------------------------------------------------------------------------------------------
# zamek pro vypisy paralelnich vlaken
lock = False


# ----------------------------------------------------------------------------------------------------------------------
# Globální funkce modulu
# ----------------------------------------------------------------------------------------------------------------------
# Tisk chyboveho hlaseni
def errormsg(msg: str) -> None:
    """
    Tisk chyboveho hlaseni na prikazovou radku

    Parameters
    ----------
    msg : str
        informacni zprava chyby
    """
    global lock
    while lock:
        pass
    lock = True
    print("[\x1b[31mFAILED\x1b[0m] {0}".format(insertspaces(msg)))
    print2postmort("FAILED {0}".format(msg))
    lock = False


# Tisk potvrzeni
def validmsg(msg: str) -> None:
    """
    Tisk potvrzujiciho hlaseni na prikazovou radku

    Parameters
    ----------
    msg : str
        informacni zprava potvrzeni
    """
    global lock
    while lock:
        pass
    lock = True
    print("[\x1b[32m  OK  \x1b[0m] {0}".format(insertspaces(msg)))
    print2postmort("--OK-- {0}".format(msg))
    lock = False


# Tisk varovani
def warningmsg(msg: str, num: int = None) -> None:
    """
    Tisk varovneho hlaseni na prikazovou radku

    Parameters
    ----------
    msg : str
        informacni zprava varovani
    num : int
        nepovinne cislo, ktere se objevi v zavorce u zpravy
    """
    global lock
    while lock:
        pass
    lock = True
    if num:
        print("[\x1b[33m{0: ^6}\x1b[0m] {1}".format(num, insertspaces(msg)))
    else:
        print("[\x1b[33m//////\x1b[0m] {0}".format(insertspaces(msg)))
    print2postmort("-WARN- {0}".format(msg))
    lock = False


# Ziskani vstupu z prikazove radky
def inputmsg(msg: str) -> str:
    """
    Tisk dotazu a ziskani odpovedi z prikazove radky

    Parameters
    ----------
    msg : str
        informacni zprava varovani

    Returns
    -------
    instr : str
        vstup z prikazove radky
    """
    global lock
    while lock:
        pass
    lock = True
    ret = input("[\x1b[33m  ??  \x1b[0m] {0}".format(insertspaces(msg)))
    lock = False
    return ret


# Tisk informacniho hlaseni - pouze spravne odsazeni
def infomsg(msg: str):
    """
    Tisk informacni zpravy. Funkce pouze zajistuje spravne odsazeni od kraje u prvniho radku.

    Parameters
    ----------
    msg : str
        informacni zprava potvrzeni
    """
    global lock
    while lock:
        pass
    lock = True
    print("         {0}".format(insertspaces(msg)))
    print2postmort("       {0}".format(insertspaces(msg, 29)))
    lock = False


# preformatovani textu tak, aby obsahoval spravny pocet mezer za novou radkou
def insertspaces(msg: str, cnt: int = 9) -> str:
    """
    Vlozeni spravneho poctu mezer do retezce za symbol nove radky.

    Parameters
    ----------
    msg : str
        formatovana zprava
    cnt : int
        pocet vkladanych mezer, v zakladu 9

    Returns
    -------
    formated_text : str
        text s vlozenymi mezerami.
    """
    spaces = " " * cnt
    return msg.replace("\n", "\n" + spaces)


def print2postmort(msg: str):
    """
    Provedeni zapisu do souboru postmortu. Provadi se jen pokud je definovana cesta k souboru postmortu.

    Parameters
    ----------
    msg : str
        zapisovana zprava

    Returns
    -------
        None
    """
    # cteni casu
    now = datetime.datetime.now()
    pmmsg = "[{0}] {1}\n".format(now.strftime('%Y-%m-%d %H:%M:%S'), msg)
    # zapis zpravy do fronty
    POSTMORT_QUEUE.append(pmmsg)
    # zapis zpravy do souboru
    if POSTMORT_FILE is not None:
        try:
            with open(POSTMORT_FILE, "at", encoding="utf-8") as file:
                file.write(pmmsg)
                file.flush()
                file.close()
        except IOError:
            pass


def tailpostmort():
    """
    Funkce vraci textovy retezec obsahujici poslednich 15 zapisu postmortu.

    Returns
    -------
    txt : str
        textovy retezec s poslednimi 15 zapisy do postmortu.
    """
    if len(POSTMORT_QUEUE) == 0:
        return "Neprobehla zadna diagnosticka zprava."
    else:
        ret = ""
        for msg in POSTMORT_QUEUE:
            ret = ret + str(msg)
        return ret


# ----------------------------------------------------------------------------------------------------------------------
# Test modulu
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':

    print(tailpostmort())

    for i in range(20):
        validmsg("Zprava cislo {0}".format(i))

    print(tailpostmort())
