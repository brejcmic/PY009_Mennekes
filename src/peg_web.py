""" WEB Webová vizualizace programu

    Modul pouze zajišťuje tvorbu webového přístupu pomocí framework FLASK.
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------
# casovani debugu
import time

# import framework
from flask import render_template

#import wsqi
from waitress import serve

# zakladni ovladani serveru
try:
    from peg_srv import BasicServer
except (ImportError, ModuleNotFoundError):
    from src.peg_srv import BasicServer

# import pristupu k flask aplikaci
try:
    from peg_global_scope import singleton_flask_app as app
except (ImportError, ModuleNotFoundError):
    from src.peg_global_scope import singleton_flask_app as app

# import pristupu k modbus datum
try:
    from peg_global_scope import singleton_modbus_datastore as modbus_datastore
except (ImportError, ModuleNotFoundError):
    from src.peg_global_scope import singleton_modbus_datastore as modbus_datastore

# hlaseni na konzoli
try:
    import peg_msg
except (ImportError, ModuleNotFoundError):
    from src import peg_msg

# ----------------------------------------------------------------------------------------------------------------------
# Konstanty modulu
# ----------------------------------------------------------------------------------------------------------------------
# pocatecni IP adresa, pokud neni prenastavena
DEFAULT_IP = "0.0.0.0"

# komunikacni port
DEFAULT_PORT = 8080

# ----------------------------------------------------------------------------------------------------------------------
# Globální metody
# ----------------------------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/readdata.js')
def read_data():
    return render_template('readdata.js')


@app.route('/postmort.html')
def postmort():
    return "<!DOCTYPE html>\n<html>\n<body>\n<pre>\n" + peg_msg.tailpostmort() + "</pre>\n</body>"


@app.route('/co.json')
def read_coils():
    return modbus_datastore.get_file_data('co.json')


@app.route('/di.json')
def read_digital_inputs():
    return modbus_datastore.get_file_data('di.json')


@app.route('/hr.json')
def read_holding_registers():
    return modbus_datastore.get_file_data('hr.json')


@app.route('/ir.json')
def read_input_registers():
    return modbus_datastore.get_file_data('ir.json')


# ----------------------------------------------------------------------------------------------------------------------
# Hlavní třída modulu
# ----------------------------------------------------------------------------------------------------------------------
class WebServer(BasicServer):
    """
    Třída pro řízení činnosti web serveru
    """
    def __init__(self, host=DEFAULT_IP, port=DEFAULT_PORT):
        # inicializace zakladu serveru
        super().__init__()
        self._server_stop = lambda: peg_msg.errormsg("Web server neposkytuje funkci 'stop' pro ukonceni.")

        # preulozeni zadanych hodnot
        self.__ipaddr = (host, port)

    def _threadfun(self):
        """
        Hlavni vlakno web serveru. Funkce pouze spusti novy server.

        Returns
        -------
            None
        """
        peg_msg.validmsg("Start vlakna web serveru.")
        try:
            serve(app=app, listen=self.get_address(), threads=6)
        finally:
            if self.get_kill_request():
                peg_msg.validmsg("Vlakno web serveru rizene ukonceno - signal kill")
            else:
                peg_msg.errormsg("Vlakno web serveru neocekavane ukoncilo cinnost")

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

        delay = 180
        divider = 6
        peg_msg.warningmsg("Zacina odpocet doby {0} sekund do vypnuti serveru".format(delay))

        step = delay / divider
        for div in range(divider):
            time.sleep(step)
            peg_msg.infomsg("Zbyva {0}".format(round(delay - (div + 1) * step)))
        time.sleep(1)
        peg_msg.warningmsg("Vypinani serveru")
        self.kill()



# ----------------------------------------------------------------------------------------------------------------------
# Test modulu
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':

    dbg_web = WebServer()
    dbg_web.test()

