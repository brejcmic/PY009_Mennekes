""" MODBUS Implementace modbus TCP serveru

    Modul inicializuje server protokolu modbus na předávané ip adrese. Součástí jsou i obslužné funkce pro spouštění
    a zastavování vlákna serveru.
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------
# informace o zarizeni
from pymodbus.device import ModbusDeviceIdentification

# pametovy prostor na serveru, tj. pamet slavu
from pymodbus.datastore import ModbusServerContext

# casovani debugu
import time

# hlaseni na konzoli
try:
    import peg_msg
except ImportError:
    from src import peg_msg

# datovy prostor modbusu
try:
    import peg_das
except ImportError:
    from src import peg_das

# zakladni ovladani serveru
try:
    from peg_srv import BasicServer
except ImportError:
    from src.peg_srv import BasicServer

# zavedeni startovaci funkce serveru
try:
    from pymodbus.server import StartTcpServer
except ImportError:
    # modbus verze <= 2.5.3
    try:
        from pymodbus.server.sync import StartTcpServer
    except ImportError:
        StartTcpServer = lambda: peg_msg.errormsg("Funkce 'StartTcpServer' pro start modbus serveru neni definovana")

try:
    from pymodbus.server import ServerStop
except ImportError:
    # modbus verze <= 2.5.3
    ServerStop = lambda: peg_msg.errormsg("Funkce 'kill' neni definovana pro modbus knihovnu 'pymodbus' verze <= 2.5.3")

# ----------------------------------------------------------------------------------------------------------------------
# Konstanty modulu
# ----------------------------------------------------------------------------------------------------------------------
# pocatecni IP adresa, pokud neni prenastavena
DEFAULT_IP = "127.0.0.1"

# komunikacni port
DEFAULT_PORT = 502

# ----------------------------------------------------------------------------------------------------------------------
# Hlavní třída modulu
# ----------------------------------------------------------------------------------------------------------------------
class ModbusServer(BasicServer):
    """
    Třída pro řízení činnosti modbus serveru
    """

    def __init__(self, datastore: peg_das.DataStore, host=DEFAULT_IP, port=DEFAULT_PORT):

        # inicializace zakladu serveru
        super().__init__()
        self._server_stop = ServerStop

        # nastaveni identity zarizeni
        info_name= datastore.get_product_identification()
        info= {
            0x00: info_name["VendorName"],
            0x01: info_name["ProductCode"],
            0x02: info_name["MajorMinorRevision"],
            0x03: info_name["VendorUrl"],
            0x04: info_name["ProductName"],
            0x05: info_name["ModelName"]
        }
        self.__identity = ModbusDeviceIdentification(info=info)

        # preulozeni zadanych hodnot
        self.__ipaddr = (host, port)
        # inicializace pametoveho prostoru
        self.__datastore = datastore
        # inicializace obsahu serveru, single = je jen jeden slave prostor, tj. vsechna id jsou mapovana sem
        self.__context = ModbusServerContext(slaves=self.__datastore.get_context(), single=True)

    def _threadfun(self):
        """
        Hlavni vlakno modbus serveru. Funkce pouze spusti novy server.

        Returns
        -------
            None
        """
        # informace o volani vlakna
        peg_msg.validmsg("Start vlakna modbus serveru.")
        try:
            StartTcpServer(context=self.__context,
                           identity=self.__identity,
                           address=self.__ipaddr)
        finally:
            if self.get_kill_request():
                peg_msg.validmsg("Vlakno modbus serveru rizene ukonceno - signal kill")
            else:
                peg_msg.errormsg("Vlakno modbus serveru neocekavane ukoncilo cinnost")

    def get_address(self) -> str:
        """
        Funkce vrati retezec obsahujici ip adresu serveru ve formatu <ip>:<port>.

        Returns
        -------
        ip_address : str
            ip adresa serveru.
        """
        return "{0}:{1}".format(self.__ipaddr[0], self.__ipaddr[1])

    def test(self):
        """
        Otestovani funkcí modulu.

        Returns
        -------
            None
        """
        if __name__ != '__main__':
            return

        peg_msg.warningmsg("Spousteni serveru")
        peg_msg.infomsg("IP adresa: {0}".format(self.get_address()))
        self.kill()
        self.restart()

        time.sleep(5)
        peg_msg.warningmsg("Restart serveru")
        self.restart()

        delay = 180
        peg_msg.warningmsg("Zacina odpocet doby {0} sekund do vypnuti serveru".format(delay))

        time.sleep(delay)
        peg_msg.warningmsg("Vypinani serveru")
        self.kill()


# ----------------------------------------------------------------------------------------------------------------------
# Test modulu
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    peg_msg.infomsg("Test cinnosti modbus serveru")
    peg_msg.infomsg("==========================================")

    # zalozeni datoveho prostoru
    dbg_datastore = peg_das.DataStore()

    # zalozeni serveru
    dbg_server = ModbusServer(datastore=dbg_datastore)
    dbg_server.test()
