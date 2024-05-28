""" MODBUS DATASTORE Přístup k datum modbusu, tj. globální data aplikace

    Modul inicializuje paměťový prostor pro data protokolu modbus. Čtení a nastavování hodnot dat je zpřístupňováno
    podle jmen konkrétních registrů.
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------
# datovy prostor slave
from pymodbus.datastore import ModbusSlaveContext

# bloky registru, sequential = bez mezer
from pymodbus.datastore import ModbusSequentialDataBlock

# export json
import json

# hlaseni na konzoli
try:
    import peg_msg
except ImportError:
    from src import peg_msg

# ----------------------------------------------------------------------------------------------------------------------
# Konstanty modulu
# ----------------------------------------------------------------------------------------------------------------------
DEFAULT_IDENTIFICATION = {
    "VendorName": "PEG spol. s r.o.",
    "ProductCode": "PYxxx",
    "VendorUrl": "peg.cz",
    "ProductName": "Debug",
    "ModelName": "Debug",
    "MajorMinorRevision": "0.1"
}

# pametovy prostor logickych vstupu
# =================================
DEFAULT_DIGITAL_INPUTS = {
    'TEST_DI': {
        'address': 1,
        'description': 'Testovací digitální vstup.'
    }
}

# pametovy prostor civek
# ======================
DEFAULT_COILS = {
    'TEST_CO': {
        'address': 1,
        'description': 'Testovací cívka'
    }
}
# pametovy prostor holding registru
# =================================
DEFAULT_HOLDING_REGISTERS = {
    'TEST_HR': {
        'address': 1,
        'description': 'Testovací holding registr'
    }
}
# pametovy prostor vstupnich registru
# ===================================
DEFAULT_INPUT_REGISTERS = {
    'TEST_IR': {
        'address': 1,
        'description': 'Testovací input registr'
    }
}

# predpis pro generovani webove stranky index.html
# ================================================
TEMPLATE_INDEX_HTML = """{{% extends 'base_diagnostics.html' %}}

{{% block head %}}
<title>{0}</title>
{{% endblock %}}

{{% block coils %}}
{1}
{{% endblock %}}

{{% block digital_inputs %}}
{2}
{{% endblock %}}

{{% block holding_registers %}}
{3}
{{% endblock %}}

{{% block input_registers %}}
{4}
{{% endblock %}}
"""

# predpis pro generovani skriptu readdata pro webovou stranku
# ===========================================================
TEMPLATE_READDATA_JS = """{{% extends 'base_diagnostics.js' %}}

{{% block register_ids %}}
{0}
{{% endblock %}}

{{% block read_coils %}}
{1}
{{% endblock %}}

{{% block read_digital_inputs %}}
{2}
{{% endblock %}}

{{% block read_holding_registers %}}
{3}
{{% endblock %}}

{{% block read_input_registers %}}
{4}
{{% endblock %}}
"""


# ----------------------------------------------------------------------------------------------------------------------
# Datové třídy modulu
# ----------------------------------------------------------------------------------------------------------------------
class DataStoreInfo:
    """
    Třída pro správu informací o paměťovém prostoru
    """

    def __init__(self, descr: dict):
        """
        Založení objektu s iformacemi o paměťových místech. Slovník musí obsahovat nasledující položky:
        {
            '<název registru>': {
                'address': <logická adresa registru>,
                'description': <popis registru>,
            },
        }

        Parameters
        ----------
        descr : dict
            slovníkový popis dat.
        """
        # obecne informace
        self.__start_address = 0xFFFF
        self.__count = 0
        # detailni informace pomoci slovniku
        self.__descr = descr

        # zjistovani pocatecni adresy = minimalni adresa
        # zjisteni celkove delky pameti pro cteni = maximalni adresa - minimalni adresa
        for key in self.__descr:
            if self.__descr[key]['address'] < self.__start_address:
                self.__start_address = self.__descr[key]['address']
            if self.__descr[key]['address'] > self.__count:
                self.__count = self.__descr[key]['address']

        self.__count = self.__count - self.__start_address + 1

        # kontrola dat a vyvolani vyjimky
        if self.__start_address < 0 or self.__count < 0:
            raise ValueError('Inicializacni data obsahuji zapornou adresu nebo neplatny pocet.')

    def getstartaddress(self) -> int:
        """
        Funkce vrati pocatecni logickou adresu pametoveho uloziste.

        Returns
        -------
        startaddress : int
            pocatecni adresa pametoveho uloziste.
        """
        return self.__start_address

    def getlen(self):
        """
        Funkce vrati delku pametoveho uloziste.

        Returns
        -------
        len : int
            delka pametoveho uloziste v poctu registru.
        """
        return self.__count

    def getlist(self):
        """
        Funkce vrati seznam jmen registru.

        Returns
        -------
        reglist : list
            seznam nazvu registru.
        """
        return self.__descr.keys()

    def getaddress(self, name: str):
        """
        Ziskani udaje logické adresy dat v pametovem prostoru modbus na zaklade jmena registru.

        Parameters
        ----------
        name : str
            nazev registru,

        Returns
        -------
        address : int
            logická adresa dat nebo -1 pokud registr s timto jmenem neexistuje.
        """
        if name in self.__descr:
            return self.__descr[name]['address']
        else:
            return -1

    def getdescription(self, name: str):
        """
        Ziskani popisu dat.

        Parameters
        ----------
        name : str
            nazev registru,

        Returns
        -------
        description : str
            popis dat nebo retezec "NA" pokud registr neexistuje
        """
        if name in self.__descr:
            return self.__descr[name]['description']
        else:
            return "NA"


# ----------------------------------------------------------------------------------------------------------------------
# Hlavní třída modulu
# ----------------------------------------------------------------------------------------------------------------------
class DataStore:
    """
    Třída zajišťuje vytvoření paměťového prostoru registrů pro potřeby aplikace modbus serveru.

    Datový prostor umožňuje následující:
        - číst všechy registry a bity modbusu,
        - nastavovat výhradně vstupní registry a digitální vstupy.
    """

    def __init__(self,
                 identification: dict = None,
                 coils: dict = None,
                 digital_inputs: dict = None,
                 holding_registers: dict = None,
                 input_registers: dict = None):
        """
        Inicializace paměťového prostoru.

        Pokud se předává slovníkový popis registrů, tak uspořádání slovníku musí mít následující tvar:

        {
            '<název registru>': {
                'address': <logická adresa registru>,
                'description': <popis registru>,
            },
        }

        Počáteční hodnota fyzické adresy je 0, logická adresa je o 1 větší. Slovníky používají logickou adresu.
        """

        # tvorba pameti
        # pamet pro informace o datech
        self.__identification = identification or DEFAULT_IDENTIFICATION

        # inicializace pameti
        coils = coils or DEFAULT_COILS
        digital_inputs = digital_inputs or DEFAULT_DIGITAL_INPUTS
        holding_registers = holding_registers or DEFAULT_HOLDING_REGISTERS
        input_registers = input_registers or DEFAULT_INPUT_REGISTERS
        self.__di = DataStoreInfo(descr=digital_inputs)
        self.__co = DataStoreInfo(descr=coils)
        self.__ir = DataStoreInfo(descr=input_registers)
        self.__hr = DataStoreInfo(descr=holding_registers)

        # tvorba obsahu pametoveho prostoru modbusu
        self.__slave_context = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(self.__di.getstartaddress(), [0] * self.__di.getlen()),
            co=ModbusSequentialDataBlock(self.__co.getstartaddress(), [0] * self.__co.getlen()),
            ir=ModbusSequentialDataBlock(self.__ir.getstartaddress(), [0] * self.__ir.getlen()),
            hr=ModbusSequentialDataBlock(self.__hr.getstartaddress(), [0] * self.__hr.getlen()),
            zero_mode=False
        )

    def get_context(self):
        """
        Ziskani reference na objekt datoveho prostoru registru.

        Returns
        -------
        slave_context : ModbusSlaveContext
            Reference modbus pametoveho prostoru.
        """
        return self.__slave_context

    def get_di_state(self, name: str) -> bool:
        """
        Získání stavu digitálního vstupu dle jeho jména.

        Parameters
        ----------
        name : str
            Jméno digitálního vstupu,

        Returns
        -------
        state : bool
            stav digitálního vstupu, při neexistenci jména False.
        """
        # získání fyzické adresy datového místa
        address = self.__di.getaddress(name=name) - 1
        return address >= 0 and self.__slave_context.getValues(0x02, address)[0] > 0

    def get_co_state(self, name: str) -> bool:
        """
        Získání stavu cívky dle jejího jména.

        Parameters
        ----------
        name : str
            Jméno cívky,

        Returns
        -------
        state : bool
            stav cívky, při neexistenci jména False.
        """
        # získání fyzické adresy datového místa
        address = self.__co.getaddress(name=name) - 1
        return address >= 0 and self.__slave_context.getValues(0x01, address)[0] > 0

    def get_ir_state(self, name: str) -> int:
        """
        Získání hodnoty vstupního registru dle jeho jména.

        Parameters
        ----------
        name : str
            Jméno registru,

        Returns
        -------
        state : int
            vždy hodnota 0-65535, pro neexistující jméno vrací 0.
        """
        # získání fyzické adresy datového místa
        address = self.__ir.getaddress(name=name) - 1
        if address >= 0:
            return self.__slave_context.getValues(0x04, address)[0]
        else:
            return 0

    def get_hr_state(self, name: str) -> int:
        """
        Získání hodnoty holding registru dle jeho jména.

        Parameters
        ----------
        name : str
            Jméno registru,

        Returns
        -------
        state : int
            vždy hodnota 0-65535, pro neexistující jméno vrací 0.
        """
        # získání fyzické adresy datového místa
        address = self.__hr.getaddress(name=name) - 1
        if address >= 0:
            return self.__slave_context.getValues(0x03, address)[0]
        else:
            return 0

    def set_di_state(self, name: str, state: bool):
        """
        Nastavení hodnoty digitálního vstupu dle jeho jména.

        Parameters
        ----------
        name : str
            Jméno digitálního vstupu,

        state: bool
            nastavovaný stav.

        Returns
        -------
            None
        """
        # získání fyzické adresy datového místa
        address = self.__di.getaddress(name=name) - 1
        if address >= 0:
            if state:
                self.__slave_context.setValues(0x02, address, values=[0x01])
            else:
                self.__slave_context.setValues(0x02, address, values=[0x00])

    def set_co_state(self, name: str, state: bool):
        """
        Nastavení hodnoty cívky dle jejího jména.

        Parameters
        ----------
        name : str
            Jméno cívky,

        state: bool
            nastavovaný stav.

        Returns
        -------
            None
        """
        # získání fyzické adresy datového místa
        address = self.__co.getaddress(name=name) - 1
        if address >= 0:
            if state:
                self.__slave_context.setValues(0x01, address, values=[0x01])
            else:
                self.__slave_context.setValues(0x01, address, values=[0x00])

    def set_ir_state(self, name: str, value: int):
        """
        Nastavení hodnoty vstupního registru dle jeho jména.

        Hodnoty musí být z platného rozsahu 0-65535. Při platném jméně se zapíše vždy LSB 16 bitů hodnoty.

        Parameters
        ----------
        name : str
            Jméno vstupního registru,

        value: int
            nastavovaná hodnota.

        Returns
        -------
            None
        """
        # získání fyzické adresy datového místa
        address = self.__ir.getaddress(name=name) - 1
        if address >= 0:
            value = value & 0xFFFF
            self.__slave_context.setValues(0x04, address, values=[value])

    def set_hr_state(self, name: str, value: int):
        """
        Nastavení hodnoty paměťového registru dle jeho jména.

        Hodnoty musí být z platného rozsahu 0-65535. Při platném jméně se zapíše vždy LSB 16 bitů hodnoty.

        Parameters
        ----------
        name : str
            Jméno paměťového registru,

        value: int
            nastavovaná hodnota.

        Returns
        -------
            None
        """
        # získání fyzické adresy datového místa
        address = self.__hr.getaddress(name=name) - 1
        if address >= 0:
            value = value & 0xFFFF
            self.__slave_context.setValues(0x03, address, values=[value])

    def get_product_identification(self):
        """
        Ziskani identifikace produktu.

        Returns
        -------
        identification: dict
            slovnik s identifikaci produktu
        """
        return self.__identification

    def get_file_data(self, filename: str):
        """
        Vraci data dotazovaneho souboru nebo prazdny retezec.

        Parameters
        ----------
        filename : str
            nazev souboru, jehoz obsah je pozadovan,

        Returns
        -------
        filedata : str
            obsah souboru nebo prazdny retezec.
        """
        valsdict = {}

        if filename == "co.json":
            memory = self.get_context()
            vals = memory.getValues(0x01,
                                    self.__co.getstartaddress() - 1,
                                    self.__co.getlen())

            for key in self.__co.getlist():
                valsdict[key + '_co'] = int(vals[self.__co.getaddress(key) - self.__co.getstartaddress()])
            filedata = json.dumps(valsdict, ensure_ascii=False, indent=2, sort_keys=False)
        elif filename == "di.json":
            memory = self.get_context()
            vals = memory.getValues(0x02,
                                    self.__di.getstartaddress() - 1,
                                    self.__di.getlen())

            for key in self.__di.getlist():
                valsdict[key + '_di'] = int(vals[self.__di.getaddress(key) - self.__di.getstartaddress()])
            filedata = json.dumps(valsdict, ensure_ascii=False, indent=2, sort_keys=False)
        elif filename == "hr.json":
            memory = self.get_context()
            vals = memory.getValues(0x03,
                                    self.__hr.getstartaddress() - 1,
                                    self.__hr.getlen())

            for key in self.__hr.getlist():
                valsdict[key + '_hr'] = vals[self.__hr.getaddress(key) - self.__hr.getstartaddress()]
            filedata = json.dumps(valsdict, ensure_ascii=False, indent=2, sort_keys=False)
        elif filename == "ir.json":
            memory = self.get_context()
            vals = memory.getValues(0x04,
                                    self.__ir.getstartaddress() - 1,
                                    self.__ir.getlen())

            for key in self.__ir.getlist():
                valsdict[key + '_ir'] = vals[self.__ir.getaddress(key) - self.__ir.getstartaddress()]
            filedata = json.dumps(valsdict, ensure_ascii=False, indent=2, sort_keys=False)
        elif filename == "index.html":
            filedata = self.__get_html_index()
        elif filename == "readdata.js":
            filedata = self.__get_html_readdata()
        else:
            filedata = ""

        return filedata

    def __get_html_index(self):
        """
        Funkce generuje retezec odpovidajici webove strance index.html.

        Returns
        -------
        page : str
            vygenerovany retezec webove stranky.
        """
        tableco = ""
        tabledi = ""
        tablehr = ""
        tableir = ""

        template = '<tr>\n'\
                   '\t<td> {0} </td>\n'\
                   '\t<td> {1} </td>\n'\
                   '\t<td id="{2}"> 0 </td>\n'\
                   '\t<td> "{3}" </td>\n'\
                   '</tr>\n'

        for key in self.__co.getlist():
            tableco = tableco + template.format(self.__co.getaddress(key),
                                                key,
                                                key + '_co',
                                                self.__co.getdescription(key))
        for key in self.__di.getlist():
            tabledi = tabledi + template.format(self.__di.getaddress(key),
                                                key,
                                                key + '_di',
                                                self.__di.getdescription(key))
        for key in self.__hr.getlist():
            tablehr = tablehr + template.format(self.__hr.getaddress(key),
                                                key,
                                                key + '_hr',
                                                self.__hr.getdescription(key))
        for key in self.__ir.getlist():
            tableir = tableir + template.format(self.__ir.getaddress(key),
                                                key,
                                                key + '_ir',
                                                self.__ir.getdescription(key))

        if "ProductName" in self.__identification:
            product_name = self.__identification["ProductName"]
        else:
            product_name = "Zarizeni PEG"

        return TEMPLATE_INDEX_HTML.format(product_name, tableco, tabledi, tablehr, tableir)

    def __get_html_readdata(self):
        """
        Funkce generuje retezec odpovidajici souboru javascriptu readdata.js, ktery se pouziva v html strance
        index.html pro obnovu predavanych hodnot.

        Returns
        -------
        script : str
            vygenerovany retezec skriptu pro webovou stranku.
        """
        elementids = ""
        templateid = '{0} = document.getElementById("{0}");\n'

        datacovals = ""
        datadivals = ""
        datahrvals = ""
        datairvals = ""
        templateval = 'datavalue = data["{0}"];\n'\
                      'if (!isNaN(datavalue)) datavalue = datavalue.toFixed(0);\n'\
                      '{0}.innerHTML = datavalue;\n'

        for key in self.__co.getlist():
            elementids = elementids + templateid.format(key + '_co')
            datacovals = datacovals + templateval.format(key + '_co')
        for key in self.__di.getlist():
            elementids = elementids + templateid.format(key + '_di')
            datadivals = datadivals + templateval.format(key + '_di')
        for key in self.__hr.getlist():
            elementids = elementids + templateid.format(key + '_hr')
            datahrvals = datahrvals + templateval.format(key + '_hr')
        for key in self.__ir.getlist():
            elementids = elementids + templateid.format(key + '_ir')
            datairvals = datairvals + templateval.format(key + '_ir')

        return TEMPLATE_READDATA_JS.format(elementids, datacovals, datadivals, datahrvals, datairvals)

    def test(self):
        """
        Otestovani funkcí modulu.

        Returns
        -------
            None
        """
        if __name__ != '__main__':
            return

        peg_msg.warningmsg("Stavy registru, cteni stavu a zapis noveho stavu")

        peg_msg.infomsg("Digitalni vstupy, cteni a zapis ini -> not(ini):")
        names = self.__di.getlist()
        for name in names:
            inival = self.get_di_state(name=name)
            self.set_di_state(name=name, state=(not inival))
            newval = self.get_di_state(name=name)
            if not inival and newval != inival:
                peg_msg.validmsg("\t{0} : {1} -> {2}".format(name, inival, newval))
            else:
                peg_msg.errormsg("\t{0} : {1} -> {2}".format(name, inival, newval))

        peg_msg.infomsg("Civky, cteni a zapis ini -> not(ini):")
        names = self.__co.getlist()
        for name in names:
            inival = self.get_co_state(name=name)
            self.set_co_state(name=name, state=(not inival))
            newval = self.get_co_state(name=name)
            if not inival and newval != inival:
                peg_msg.validmsg("\t{0} : {1} -> {2}".format(name, inival, newval))
            else:
                peg_msg.errormsg("\t{0} : {1} -> {2}".format(name, inival, newval))

        peg_msg.infomsg("Vstupni registry, cteni a zapis ini -> inv(adresa):")
        names = self.__ir.getlist()
        for name in names:
            inival = self.get_ir_state(name=name)
            self.set_ir_state(name=name, value=(~self.__ir.getaddress(name=name)))
            newval = self.get_ir_state(name=name)
            if newval == (~self.__ir.getaddress(name=name) & 0xFFFF):
                peg_msg.validmsg("\t{0} : {1} -> {2}".format(name, inival, newval))
            else:
                peg_msg.errormsg("\t{0} : {1} -> {2}".format(name, inival, newval))

        peg_msg.infomsg("Holding registry, cteni a zapis ini -> adresa:")
        names = self.__hr.getlist()
        for name in names:
            inival = self.get_hr_state(name=name)
            self.set_hr_state(name=name, value=(self.__hr.getaddress(name=name)))
            newval = self.get_hr_state(name=name)
            if newval == (self.__hr.getaddress(name=name) & 0xFFFF):
                peg_msg.validmsg("\t{0} : {1} -> {2}".format(name, inival, newval))
            else:
                peg_msg.errormsg("\t{0} : {1} -> {2}".format(name, inival, newval))

        peg_msg.warningmsg("Tisk souboru index.html")
        peg_msg.infomsg(self.get_file_data('index.html'))

        peg_msg.warningmsg("Tisk souboru readdata.js")
        peg_msg.infomsg(self.get_file_data('readdata.js'))

        peg_msg.warningmsg("Tisk souboru di.json")
        peg_msg.infomsg(self.get_file_data('di.json'))

        peg_msg.warningmsg("Tisk souboru co.json")
        peg_msg.infomsg(self.get_file_data('co.json'))

        peg_msg.warningmsg("Tisk souboru ir.json")
        peg_msg.infomsg(self.get_file_data('ir.json'))

        peg_msg.warningmsg("Tisk souboru hr.json")
        peg_msg.infomsg(self.get_file_data('hr.json'))


# ----------------------------------------------------------------------------------------------------------------------
# Test modulu
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    peg_msg.infomsg("Test pametoveho prostoru pro modbus SERVER")
    peg_msg.infomsg("==========================================")
    dbg_datastore = DataStore()
    dbg_datastore.test()

    peg_msg.validmsg("Konec testu pametoveho prostoru pro modbus SERVER")
