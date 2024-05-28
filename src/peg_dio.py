""" DIGITAL INPUTS OUTPUTS Přístup k digitálním výstupům pomocí sběrnice SPI a čtení digitálních vstupů

    Modul inicializuje sběrnici SPI a zpřístupňuje funkce pro ovládání digitálních výstupů, které jsou na DPS Mennekes
    zapojené pomocí posuvných registrů. Dále zpřístupňuje čtení digitálních vstupů.

    Pro povolení SPI v Beaglebone je nutné buď zavolat příkaz config-pin:

    config-pin P9_17 spi_cs
    config-pin P9_18 spi
    config-pin P9_21 spi
    config-pin P9_22 spi_sclk

    nebo pro trvalé povolení editovat soubor /boot/uEnv.txt:

    ###Additional custom capes
    # 20190727 jc: enable SPI0 by default
    uboot_overlay_addr4=/lib/firmware/BB-SPIDEV0-00A0.dtbo

    Při editaci souboru /boot/uEnv.txt bude SPI funkční až po restartu. Řádky výše ukazují přidání overlay na slot 4,
    který je v původním souboru po instalaci volný.

    POZOR: pin P9_15 je používán u posuvných registrů jako vstup CLR. Tento pin musí mít vysokou úroveň, aby bylo
    možné výstupy zapisovat na požadované hodnoty.
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------

# knihovna pro spi
from Adafruit_BBIO.SPI import SPI

# knihovna pro GPIO
import Adafruit_BBIO.GPIO as GPIO

# časování smyčky
import time

# vlakno pro trvalou komunikaci spi
import threading

# identifikace verze produktu
try:
    from peg_global_scope import PCB_REVISION
except ImportError:
    from src.peg_global_scope import PCB_REVISION

# hlaseni na konzoli
try:
    import peg_msg
except ImportError:
    from src import peg_msg

# ----------------------------------------------------------------------------------------------------------------------
# Konstanty modulu
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Hlavní třída modulu
# ----------------------------------------------------------------------------------------------------------------------
class Dio:

    def __init__(self):
        """
        Inicializace komunikace spi a nastavení digitálních vstupů
        """
        # konstanty
        # slovník masek digitálních výstupů přístupných přes SPI
        self.DIGITAL_OUTPUTS_CTRL = {
            'POWER_SW1': 0x02,
            'OPEN_LOCK1': 0x08,
            'CLOSE_LOCK1': 0x04,
            'POWER_SW2': 0x10,
            'OPEN_LOCK2': 0x40,
            'CLOSE_LOCK2': 0x20,
            'DISABLE_LOCK12': 0x80
        }
        self.DIGITAL_OUTPUTS_LEDS = {
            'RED1': 0x04,
            'GREEN1': 0x08,
            'BLUE1': 0x10,
            'RED2': 0x20,
            'GREEN2': 0x40,
            'BLUE2': 0x80
        }
        self.__DIGITAL_OUTPUTS_CLR_PIN = "P9_15"
        self.__DIGITAL_OUTPUTS_DINEN_PIN = "P8_17"

        # slovník názvů digitálních vstupů
        if PCB_REVISION["controller"] < 2.0:
            self.DIGITAL_INPUTS = {
                'IN1P0_ELEM': 'P8_18',
                'IN1P1_LOCK': 'P8_17',
                'IN2P0_ELEM': 'P8_16',
                'IN2P1_LOCK': 'P8_15'
            }
            self.digital_inputs_inverted = True
        elif PCB_REVISION["controller"] < 3.0:
            self.DIGITAL_INPUTS = {
                'IN1P0_ELEM': 'P8_18',
                'IN1P1_LOCK': 'P8_17',
                'IN1P2_STOK': 'P8_16',
                'IN2P0_ELEM': 'P8_15',
                'IN2P1_LOCK': 'P9_25',
                'IN2P2_STOK': 'P9_27'
            }
            self.digital_inputs_inverted = True
        else:
            self.DIGITAL_INPUTS = {
                'IN1P0_ELEM': 'P8_41',
                'IN1P1_LOCK': 'P8_42',
                'IN1P2_STOK': 'P8_39',
                'IN1P3_BTON': 'P8_40',
                'IN2P0_ELEM': 'P8_45',
                'IN2P1_LOCK': 'P8_46',
                'IN2P2_STOK': 'P8_43',
                'IN2P3_BTON': 'P8_44'
            }
            self.digital_inputs_inverted = False

        # otevření sběrnice NUM = 0, CS = 0
        self.spi = SPI(0,0)

        # nastavení:
        #           - rychlost 5 kHz
        #           - mod CPOL = 1, CPHA = 0, u beaglebonu je to asi invertováno
        #           - počet bitů 16
        self.spi.msh = 5000
        self.spi.mode = 2
        self.spi.bpw = 16
        time.sleep(1)

        # počáteční hodnoty
        self.doleds = 0
        self.doctrl = 0
        
        # povolit zadávání vystupu posuvných registrů
        GPIO.setup(self.__DIGITAL_OUTPUTS_CLR_PIN, GPIO.OUT)
        GPIO.output(self.__DIGITAL_OUTPUTS_CLR_PIN, GPIO.HIGH)

        # povolení čtení digitalních vstupů (od verze C3.0)
        if PCB_REVISION["controller"] >= 3.0:
            GPIO.setup(self.__DIGITAL_OUTPUTS_DINEN_PIN, GPIO.OUT)
            GPIO.output(self.__DIGITAL_OUTPUTS_DINEN_PIN, GPIO.HIGH)

        # digitální vstupy a počítadla náběžných hran
        for val in self.DIGITAL_INPUTS.values():
            GPIO.setup(val, GPIO.IN)

        self.__DIGITAL_INPUT_COUNTERS = {}
        for key in self.DIGITAL_INPUTS:
            self.__DIGITAL_INPUT_COUNTERS[key] = 0

        for din in self.DIGITAL_INPUTS.values():
            GPIO.add_event_detect(din, GPIO.RISING, callback=self.__inc_inx_cnt)

        # nastaveni vlakna
        self.__thread = threading.Thread(target=self.__threadfun, daemon=True)
        self.__thread_has_started = False
        self.__thread_kill_requested = False
        

    def __del__(self):
        """
        Destrukce objektu digitálních vstupů a výstupů

        Především uzavření komunikace spi.

        Returns
        -------
            None
        """
        self.spi.close()
        GPIO.cleanup()

    def __threadfun(self):
        """
        Hlavní vlákno komunikace, které se stará o odesílání stavů výstupů.

        Returns
        -------
            None
        """

        txlist = [0, 0]
        divider = 0
        try:
            while not self.__thread_kill_requested:
                # nastavení výstupu
                if txlist[0] != self.doctrl or txlist[1] != self.doleds:
                    txlist[0] = self.doctrl
                    txlist[1] = self.doleds
                    # self.spi.xfer2(txlist) nefunguje spravne v dlouhem casovem horizontu. Obcas dochazi k odeslani
                    # pouze 1 byte.
                    self.spi.writebytes(txlist)
                    txlist[0] = self.doctrl
                    txlist[1] = self.doleds
                    divider = 0
                else:
                    divider = divider + 1
                # uspávání vlákna
                time.sleep(0.2)
        finally:
            if self.__thread_kill_requested:
                peg_msg.validmsg("Vlakno digitalnich IO rizene ukonceno - signal kill")
            else:
                peg_msg.errormsg("Vlakno digitalnich IO neocekavane ukoncilo cinnost")

    def __inc_inx_cnt(self, pin):
        """
        Inkrementace počítadla náběžných hran pro vstupy 0 - 3

        Returns
        -------
            None
        """
        for key in self.DIGITAL_INPUTS:
            if pin == self.DIGITAL_INPUTS[key]:
                self.__DIGITAL_INPUT_COUNTERS[key] = (self.__DIGITAL_INPUT_COUNTERS[key] + 1) & 0xFFFFFFFF
                break

    def restart(self):
        """
        Restart vlákna digitálních IO.

        Returns
        -------
            None
        """

        if self.is_alive():
            self.kill()

        if not self.is_alive():
            self.__thread = threading.Thread(target=self.__threadfun, daemon=True)
            self.__thread.start()
            self.__thread_has_started = self.__thread.is_alive()

    def is_alive(self) -> bool:
        """
        Informace, zda je čtení a zápis digitálních IO (vlákno) v chodu.

        Returns
        -------
            True pokud je vše v chodu, jinak False.
        """
        # pokus o cteni hlavicky ze serveru
        return self.__thread_has_started and self.__thread.is_alive()

    def kill(self):
        """
        Ukončení činnosti vlákna digitálních IO

        Returns
        -------
            None
        """
        if self.is_alive():
            self.__thread_kill_requested = True
            self.__thread.join(timeout=10.0)
            self.__thread_kill_requested = False

    def set_output(self, name: str, level: bool):
        """
        Nastavení logické úrovně zadanému digitálnímu výstupu.

        Parameters
        ----------
        name : str
            Název digitálního výstupu,
        level :
            logická hodnota, která se má zapsat.

        Returns
        -------
            None
        """
        if name in self.DIGITAL_OUTPUTS_CTRL:
            mask = self.DIGITAL_OUTPUTS_CTRL[name]
            if level:
                self.doctrl = self.doctrl | mask
            else:
                self.doctrl = self.doctrl & ~mask

        elif name in self.DIGITAL_OUTPUTS_LEDS:
            mask = self.DIGITAL_OUTPUTS_LEDS[name]
            if level:
                self.doleds = self.doleds & ~mask
            else:
                self.doleds = self.doleds | mask


        else:
            pass

    def get_output(self, name: str) -> bool:
        """
        Získání stavu digitálního výstupu.

        Parameters
        ----------
        name : str
            Název digitálního výstupu,

        Returns
        -------
        level : bool
            aktuální logický stav digitálního výstupu.
        """
        if name in self.DIGITAL_OUTPUTS_CTRL:
            mask = self.DIGITAL_OUTPUTS_CTRL[name]
            return (self.doctrl & mask) > 0

        elif name in self.DIGITAL_OUTPUTS_LEDS:
            mask = self.DIGITAL_OUTPUTS_LEDS[name]
            return (self.doleds & mask) == 0

        else:
            return False

    def get_input(self, name: str) -> bool:
        """
        Získání stavu digitálního vstupu.

        Parameters
        ----------
        name : str
            Název digitálního vstupu,

        Returns
        -------
            aktuální logický stav digitálního vstupu.
        """
        if name in self.DIGITAL_INPUTS:
            return GPIO.input(self.DIGITAL_INPUTS[name]) != self.digital_inputs_inverted

    def get_input_counter(self, name: str) -> int:
        """
        Získání stavu počítadla náběžných hran daného digitálního vstupu. Počítadlo přetéká na hodnotě 2^32

        Parameters
        ----------
        name : str
            Název digitálního vstupu,

        Returns
        -------
            stav počítadla náběžných hran.
        """
        if name in self.__DIGITAL_INPUT_COUNTERS:
            return self.__DIGITAL_INPUT_COUNTERS[name]
        else:
            return 0

    def clr_input_counter(self, name: str):
        """
        Vynulovani pocitadla nabeznych hran.

        Parameters
        ----------
        name : str
            Název digitálního vstupu.

        Returns
        -------
            None
        """
        if name in self.__DIGITAL_INPUT_COUNTERS:
            self.__DIGITAL_INPUT_COUNTERS[name] = 0

    def test(self):
        """
        Otestovani funkcí modulu.

        Returns
        -------
            None
        """
        if __name__ != '__main__':
            return

        peg_msg.warningmsg("Spusteni obsluzneho vlakna")
        self.restart()

        time.sleep(0.5)
        if self.is_alive():
            peg_msg.validmsg("Vlakno hlasi: alive")
        else:
            peg_msg.errormsg("Vlakno hlasi: not alive")
            return

        peg_msg.warningmsg("Sepnuti rele 1")
        self.set_output('POWER_SW1', True)
        time.sleep(4)
        
        peg_msg.warningmsg("Sepnuti rele 2")
        self.set_output('POWER_SW2', True)
        time.sleep(4)

        peg_msg.warningmsg("Rozepnuti rele 1")
        self.set_output('POWER_SW1', False)
        time.sleep(4)
        
        peg_msg.warningmsg("Rozepnuti rele 2")
        self.set_output('POWER_SW2', False)
        time.sleep(4)

        peg_msg.warningmsg("Vypis stavu vstupu po dobu 40 s")
        for step in range(20):
            peg_msg.warningmsg("Cteni", step + 1)
            for key in self.DIGITAL_INPUTS:
                peg_msg.infomsg("{0} = {1}".format(key, self.get_input(key)))
            time.sleep(2)

        peg_msg.warningmsg("Vypis poctu nabeznych hran:")
        for key in self.DIGITAL_INPUTS:
            peg_msg.infomsg("{0} = {1}".format(key, self.get_input_counter(key)))

# ----------------------------------------------------------------------------------------------------------------------
# Test modulu
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    peg_msg.infomsg("Test cinnosti digitalnich vstupu a vystupu")
    peg_msg.infomsg("==========================================")

    dbg_dio = Dio()
    dbg_dio.test()
