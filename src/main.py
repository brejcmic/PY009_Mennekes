""" ELECTROMETERS Přístup k výsledkům měření elektroměrů

    Modul inicializuje příslušné zařízení elektroměru a poskytuje funkce pro čtení hodnoty a její reset. Zařízení
    buď

    - čtou počet pulsů na vstupech IN1P0_ELEM, IN2P0_ELEM,
    - nebo využívají sériovou linku RS485 na portech /dev/ttyS4 (CH1) a /dev/ttyS1 (CH2).
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------
# tvorba vlakna pro volani sama sebe
import threading

# casovani watchdog
import time

# digitalni vstupy a vystupy≤
try:
    from peg_dio import Dio
except (ImportError, ModuleNotFoundError):
    from src.peg_dio import Dio

# knihovna modbusu
try:
    modbus_version = 2
    from pymodbus.client.sync import ModbusSerialClient
except ImportError:
    # verze >=3
    from pymodbus import __version__ as raw_version
    modbus_version = int(raw_version[0])
    from pymodbus.client.serial import ModbusSerialClient

# ----------------------------------------------------------------------------------------------------------------------
# Datové třídy modulu
# ----------------------------------------------------------------------------------------------------------------------

class Electrometer:
    """
    Třída obecného zařízení elektroměru pro zavedení společného rozhraní všem zařízením
    """

    def __init__(self, channel_num: int):
        """
        Konstruktor obecného zařízení elektroměru. Hodnota spotřeby se ukládá do dvojice slov (16 bit) jako
        LITTLE ENDIAN. Při inicializaci je nutné zadat číslo kanálu (výstupu), na kterém elektroměr měří.

        Parameters
        ----------
        channel_num : int
            číslo kanálu, ke kterému elektroměr patří, hodnoty menší nž 2 patří kanálu 1, vyšší hodnoty kanálu 2
        """
        self.__consumption = [0, 0]
        self.__alive = False
        self.__enabled = True
        self.__period = 5
        self.__watchdog_period = self.__period + 4
        self.__watchdog = time.time()
        if channel_num > 1:
            self.__channel_num = 2
        else:
            self.__channel_num = 1
        self.__reset_req = True

    def __del__(self):
        """
        Destruktor obecneho zařízení elektroměru
        """
        self.disable()

    def start(self):
        """
        Start vlakna pristroje
        """
        if not self.__alive and self.__enabled:
            thread = threading.Timer(interval=self.__period, function=self.__task)
            thread.daemon = True
            thread.start()
            self.__watchdog = time.time() + self.__watchdog_period
            self.__alive = True

    def enable(self):
        """
        Povolení spouštění vlákna vyčítání údaje přístroje. Při inicializaci přístroje je v základu vždy povoleno.
        """
        self.__enabled = True

    def disable(self):
        """
        Zakázání spouštění vlákna vyčítání údaje přístroje. Při inicializaci přístroje je v základu vždy povoleno.
        """
        self.__enabled = False

    def is_alive(self):
        """
        Získání stavu života vlákna.

        Returns
        -------
        alive : bool
            true, pokud vlakno žije.
        """
        return self.__alive or time.time() < self.__watchdog

    def read(self) -> list[int]:
        """
        Čtení aktuální hodnoty odběru od posledního nulování.

        Returns
        -------
        consumption: List[int]
            aktuální odběr energie od nulování jako seznam dvou 16 bit hodnot (celková hodnota LITTLE ENDIAN).
        """
        return self.__consumption

    def get_channel_num(self):
        """
        Získání čísla výstupu, ke kterému elektroměr naleží
        """
        return self.__channel_num

    def reset(self):
        """
        Vynulování aktuální hodnoty počítadla elektroměru.
        """
        self.__consumption = [0, 0]
        self.__reset_req = True

    def _get_reset(self):
        """
        Získání stavu požadavku resetu hodnoty elektroměru.

        Returns
        -------
        reset_req: stav požadavku nulování.
        """
        return self.__reset_req

    def _ack_reset(self):
        """
        Potvrzení odbavení stavu požadavku resetu hodnoty elektroměru.
        """
        self.__reset_req = False

    def _update(self):
        """
        Funkce aktualizace hodnoty spotřeby.
        """
        low = 0
        high = 0
        return [low, high]

    def __task(self):
        """
        Časované vlákno pro periodickou aktualizaci hodnoty elektroměru
        """
        self.__alive = False
        self.__consumption = self._update()
        self.start()

class ElectrometerSchrackMGRZK465(Electrometer):
    """
    Třída elektroměru schrack, který komunikuje pomocí sériové linky RS485 s protokolem modbus.

    Typ: 3f MGRZK 465
    """

    def __init__(self, channel_num: int):
        """
        Objekt elektroměru Schrack MGRZK s rozhraním RS485 a protokolem modbus, který náleží ke kanálu channel_num.

        Parameters
        ----------
        channel_num : int
            číslo kanálu, ke kterému elektroměr patří, hodnoty menší nž 2 patří kanálu 1, vyšší hodnoty kanálu 2
        """
        super().__init__(channel_num=channel_num)

        if self.get_channel_num() > 1:
            client_port = '/dev/ttyS1'
        else:
            client_port = '/dev/ttyS4'

        self.__client = ModbusSerialClient(method='rtu',
                                           port=client_port,
                                           baudrate=19200,
                                           bytesize=8,
                                           parity='N',
                                           stopbits=2)
        self.__client.connect()

    def __del__(self):
        """
        Uzavreni komunikace
        """
        super().disable()
        self.__client.close()

    def _update(self):
        """
        Funkce aktualizace hodnoty spotřeby.
        """
        if self._get_reset():
            if modbus_version > 2:
                self.__client.write_register(address=13, value=0x01, slave=33)
            else:
                self.__client.write_register(address=13, value=0x01, unit=33)
            self._ack_reset()

        if modbus_version > 2:
            data = self.__client.read_input_registers(address=426, count=2, slave=33)
        else:
            data = self.__client.read_input_registers(address=426, count=2, unit=33)

        if data.isError():
            low = 0
            high = 0
        else:
            val = int(((int(data.registers[0]) << 16) + int(data.registers[1])) / 10)
            low = val & 0xFFFF
            high = (val >> 16) & 0xFFFF

        return [low, high]


# ----------------------------------------------------------------------------------------------------------------------
# Test modulu
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    test = Electrometer(channel_num=1)
    time.sleep(5)
    print(test.read())
    test2 = Electrometer(channel_num=2)
    time.sleep(5)
    print(test.read())
    print(test2.read())
    time.sleep(5)
    print(test.read())
    print(test2.read())
    print("Tady konci program")
