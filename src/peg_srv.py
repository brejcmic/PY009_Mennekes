""" SERVER Rodičovská třída serveru

    Modul nabízí rodičovskou třídu pro řízení ethernetových serverů. Vždy je nutné doplnit funkce 'kill' a 'threadfun'.
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------

# vlakno pro nezavisly beh serveru
import threading

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

class  BasicServer:
    """
    Třída pro řízení činnosti web serveru
    """

    def __init__(self):
        """
        Inicializace serveru.
        """
        # zalozeni objektu vlakna
        self.__thread = None
        self.__thread_has_started = False
        self.__thread_kill_requested = False

        # prirazeni funkce stop serveru
        self._server_stop = lambda: peg_msg.errormsg("Server nema funkci stop.")

    def __del__(self):
        """
        Destruktor objektu modbus serveru.
        """
        self.kill()

    def _threadfun(self):
        """
        Hlavni vlakno serveru. Funkce pouze spusti novy server.

        Returns
        -------
            None
        """
        peg_msg.errormsg("Server nema definovanu funkci vlakna.")

    def restart(self):
        """
        Restart serveru.

        Returns
        -------
            None
        """

        if self.is_alive():
            self.kill()

        if not self.is_alive():
            self.__thread = threading.Thread(target=self._threadfun, daemon=True)
            self.__thread.start()
            self.__thread_has_started = self.__thread.is_alive()

    def is_alive(self) -> bool:
        """
        Informace, zda je modbus server (jeho vlakno) v chodu.

        Returns
        -------
            True pokud server bezi, jinak False.
        """
        # pokus o cteni hlavicky ze serveru
        return self.__thread and self.__thread_has_started and self.__thread.is_alive()

    def kill(self):
        """
        Ukončení činnosti vlákna serveru

        Returns
        -------
            None
        """
        if self.is_alive():
            self.__thread_kill_requested = True
            self._server_stop()
            self.__thread.join(timeout=10.0)
            self.__thread_kill_requested = False

    def get_kill_request(self):
        """
        Získání požadavku na ukončení procesu.

        Returns
        -------
        kill_req: bool
            True pokud je požadavek vystaven, jinak False.
        """
        return self.__thread_kill_requested
