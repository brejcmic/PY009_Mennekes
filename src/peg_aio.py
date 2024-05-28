""" ANALOG INPUTS OUTPUTS Přístup k analogovým vstupům a výstupům

    Modul inicializuje sběrnici ADC a PWM periferie zpřístupňuje jejich nastavení a čtení.
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------

# knihovna pro adc
import Adafruit_BBIO.ADC as ADC

# časování smyčky
import time

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
class Aio:

    def __init__(self):
        """
        Nastavení funkce analogových vstupů a výstupů pro CP a PP signály.
        """
        # konstatny
        # slovník názvů analogových výstupů
        self.ANALOG_OUTPUTS = {
            'CP1': '/dev/bone/pwm/1/a/',
            'CP2': '/dev/bone/pwm/1/b/'
        }

        self.__ANALOG_OUTPUT_DUTY = {
            'CP1': 100,
            'CP2': 100
        }
        self.__ANALOG_OUTPUT_PERIOD = {
            'CP1': 1000000,
            'CP2': 1000000
        }

        # slovník názvů analogových vstupů
        self.ANALOG_INPUTS = {
            'PP1': 'P9_39',
            'CP1': 'P9_40',
            'PP2': 'P9_37',
            'CP2': 'P9_38'
        }

        # měřítka: násobek, normování, povolení jmenovatele pro dělič
        self.__ANALOG_SCALES = {
            'PP1': {'scale': 500.0, 'idle': 0.9, 'div': True},
            'CP1': {'scale': 12, 'idle': 0.95, 'div': False},
            'PP2': {'scale': 500.0, 'idle': 0.9, 'div': True},
            'CP2': {'scale': 12, 'idle': 0.95, 'div': False},
        }

        # inicializace adc
        ADC.setup()

        for key in self.__ANALOG_SCALES:
            idle = ADC.read(self.ANALOG_INPUTS[key])
            if idle > self.__ANALOG_SCALES[key]['idle']:
                self.__ANALOG_SCALES[key]['idle'] = idle

        peg_msg.validmsg("Pocatecni kalibrace analogovych vstupu:")
        for key in self.__ANALOG_SCALES:
            peg_msg.infomsg("{0}: scale={1}, idle={2}".format(key,
                                                              self.__ANALOG_SCALES[key]['scale'],
                                                              self.__ANALOG_SCALES[key]['idle']))

        # inicializace pwm
        for key in self.ANALOG_OUTPUTS:
            with open(self.ANALOG_OUTPUTS[key] + 'period', 'w') as period:
                # udaj je v ns
                period.write(str(self.__ANALOG_OUTPUT_PERIOD[key]))

            self.set_output(name=key, duty=100)

            with open(self.ANALOG_OUTPUTS[key] + 'polarity', 'w') as polarity:
                # udaj muze byt bud 'normal' nebo 'inversed'
                polarity.write('inversed')

            with open(self.ANALOG_OUTPUTS[key] + 'enable', 'w') as enable:
                # udaj je bud 0 nebo 1
                enable.write('1')

    def __del__(self):
        """
        Destrukce objektu analogových vstupů a výstupů.

        Returns
        -------
            None
        """

        for key in self.ANALOG_OUTPUTS:
            with open(self.ANALOG_OUTPUTS[key] + 'enable', 'w') as enable:
                # udaj je bud 0 nebo 1
                enable.write('0')

    def check_calibration(self):
        """
        Kontrola kalibrace vstupů. Pokud je vstup v idle (hodnota > 80%), pak je proveden kalibrační krok, který
        přičte ke kalibrační hodnotě 1/16 rozdílu  aktuální hodnoty a uloženého offsetu.

        Returns
        -------
            None
        """
        for key in self.ANALOG_INPUTS:
            val = ADC.read(self.ANALOG_INPUTS[key])
            if val > 0.8:
                idle = self.__ANALOG_SCALES[key]['idle'] * 15 + val
                self.__ANALOG_SCALES[key]['idle'] = idle / 16

    def set_output(self, name: str, duty: int):
        """
        Nastavení střídy na analogovém výstupu.

        Parameters
        ----------
        name : str
            Název analogového výstupu,
        duty : int
            nastavovaná střída.

        Returns
        -------
            None
        """
        if name in self.ANALOG_OUTPUTS and 0 <= duty <= 100:
            self.__ANALOG_OUTPUT_DUTY[name] = duty
            duty_in_ns = int(duty * self.__ANALOG_OUTPUT_PERIOD[name] / 100)

            with open(self.ANALOG_OUTPUTS[name] + 'duty_cycle', 'w') as duty_cycle:
                # udaj je v ns, musi byt mene nez perioda
                duty_cycle.write(str(duty_in_ns))



    def get_output(self, name: str) -> int:
        """
        Získání nastavení střídy na analogovém výstupu.

        Parameters
        ----------
        name : str
            Název analogového výstupu,

        Returns
        -------
        duty : int
            nastavená střída.
        """
        if name in self.__ANALOG_OUTPUT_DUTY:
            return self.__ANALOG_OUTPUT_DUTY[name]
        else:
            return -1

    def get_input(self, name: str) -> float:
        """
        Získání hodnoty analogového vstupu.

        Parameters
        ----------
        name : str
            Název analogového vstupu,

        Returns
        -------
            aktuální hodnota analogového vstupu.
        """
        if name in self.ANALOG_INPUTS and name in self.__ANALOG_SCALES:
            val = ADC.read(self.ANALOG_INPUTS[name]) / self.__ANALOG_SCALES[name]['idle']
            if val > 0.99:
                val = 0.99

            # pro mereni rezistoru na PP
            if self.__ANALOG_SCALES[name]['div']:
                val = val / (1 - val)

            # pro -12 V na CP
            if -1 < self.get_output(name) < 2:
                val = 1

            return val * self.__ANALOG_SCALES[name]['scale']
        else:
            return -1

    def test(self):
        """
        Otestovani funkcí modulu.

        Returns
        -------
            None
        """
        if __name__ != '__main__':
            return

        peg_msg.warningmsg("Nastavovani strid po 1 s")
        for duty in range(6):
            self.set_output('CP1', int(20 * duty))
            peg_msg.infomsg("Strida CP1 nastavena na {0}".format(self.get_output('CP1')))
            self.set_output('CP2', int(100 - 20 * duty))
            peg_msg.infomsg("Strida CP2 nastavena na {0}".format(self.get_output('CP2')))
            time.sleep(2)

        self.set_output('CP1', 5)
        self.set_output('CP2', 5)
                                   
        peg_msg.warningmsg("Vypis stavu vstupu po dobu 40 s")
        for step in range(20):
            peg_msg.warningmsg("Cteni", step + 1)
            for key in self.ANALOG_INPUTS:
                peg_msg.infomsg("{0} = {1}".format(key, self.get_input(key)))
            time.sleep(2)


# ----------------------------------------------------------------------------------------------------------------------
# Test modulu
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    peg_msg.infomsg("Test cinnosti analogovych vstupu a vystupu")
    peg_msg.infomsg("==========================================")

    dbg_aio = Aio()
    dbg_aio.test()

