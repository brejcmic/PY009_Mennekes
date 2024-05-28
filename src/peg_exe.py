""" EXECUTION Výkonná funkce programu

    Modul nabízí inicialiční třídu a její funkci 'execute', která zajišťuje vykonnávání funkcí programu, tj. propojení
    činností mezi jednotlivými moduly.

    Aktálně spojuje činnost modulů:
        - peg_aio
        - peg_dio
        - peg_das
        - peg_elm
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------

# casovani tiku counteru
import time

# import pristupu k modbus datum
try:
    from peg_global_scope import singleton_modbus_datastore as modbus_datastore
except (ImportError, ModuleNotFoundError):
    from src.peg_global_scope import singleton_modbus_datastore as modbus_datastore

# import typu elektromeru
try:
    from peg_global_scope import ELECTROMETER_TYPES
except (ImportError, ModuleNotFoundError):
    from src.peg_global_scope import ELECTROMETER_TYPES

# import typu pripojeni LED
try:
    from peg_global_scope import LED_COMMON_ELECTRODE
except (ImportError, ModuleNotFoundError):
    from src.peg_global_scope import LED_COMMON_ELECTRODE

# analogove vstupy a vystupy
try:
    import peg_aio
except (ImportError, ModuleNotFoundError):
    from src import peg_aio

# digitalni vstupy a vystupy
try:
    import peg_dio
except (ImportError, ModuleNotFoundError):
    from src import peg_dio

# hlaseni na konzoli
try:
    import peg_msg
except (ImportError, ModuleNotFoundError):
    from src import peg_msg

# cteni elektromeru
try:
    import peg_elm
except (ImportError, ModuleNotFoundError):
    from src import peg_elm


# ----------------------------------------------------------------------------------------------------------------------
# Hlavní třída modulu
# ----------------------------------------------------------------------------------------------------------------------
class Execution:
    """
    Třída slouží pouze jako zapouzdření dat nutných pro vybavení výkonné funkce přípravku Mennekes
    """
    def __init__(self):
        """
        Inicializace pravidelneho kroku programové smyčky.
        """

        # digitalní vstupy a vystupy
        self.__dio = peg_dio.Dio()

        # analogove vstupy a vystupy
        self.__aio = peg_aio.Aio()
        self.__aio_calibration_div_cnt = 0

        # pocitadlo cinnosti
        self.__counter = 0xFFFF
        self.__counter_step_start_time = time.time()
        
        # nastaveni maxima pocitadla
        modbus_datastore.set_hr_state(name='COUNTER_TOP', value=self.__counter)

        # tvorba seznamu elektromeru
        self.__electrometer = []
        for channel_raw_num, electrometer_type in enumerate(ELECTROMETER_TYPES):
            if 'pulse' in electrometer_type:
                elem = peg_elm.ElectrometerPulse(channel_num=(channel_raw_num + 1), dio=self.__dio)
            elif 'schrack_mgrzk' in electrometer_type:
                elem = peg_elm.ElectrometerSchrackMGRZK465(channel_num=(channel_raw_num + 1))
            else:
                elem = peg_elm.Electrometer(channel_num=(channel_raw_num + 1))
                elem.disable()
                peg_msg.warningmsg("Zaveden elektromer bez podpory vycitani hodnoty.")
            self.__electrometer.append(elem)
            elem.start()

        # nastaveni typu kontrolnich vystupu (zamky jsou invertovany)
        self.__ctr_output_inverted = dict(self.__dio.DIGITAL_OUTPUTS_CTRL)
        for key in self.__ctr_output_inverted:
            self.__ctr_output_inverted[key] = "LOCK" in key

        # nastaveni typu spojeni LED
        self.__led_common_anode = dict(self.__dio.DIGITAL_OUTPUTS_LEDS)
        for key in self.__led_common_anode:
            if "1" in key:
                self.__led_common_anode[key] = "anode" in LED_COMMON_ELECTRODE[0]
            else:
                self.__led_common_anode[key] = "anode" in LED_COMMON_ELECTRODE[1]

    def __del__(self):
        """
        Ukonceni cinnosti spustenych vlaken.

        Returns
        -------
            None
        """
        self.__dio.kill()

    def execute(self) -> int:
        """
        Výkonná funkce programu.

        Returns
        -------
        error_num: int
            číslo chyby nebo 0 pokud chyba nenastala.
        """

        # kontrola behu hlavniho vlakna digitalnich vstupu a vystupu
        if not self.__dio.is_alive():
            peg_msg.warningmsg("Restart vlakna digitalnich vstupu a vystupu.")
            self.__dio.restart()

        # prepis stavu digitalnich vstupu
        for key in self.__dio.DIGITAL_INPUTS:
            modbus_datastore.set_di_state(key, self.__dio.get_input(name=key))

        # prepis stavu LED
        for key in self.__dio.DIGITAL_OUTPUTS_LEDS:
            name = 'LED_{0}'.format(key)
            val = modbus_datastore.get_co_state(name=name)
            val = val != self.__led_common_anode[key]
            self.__dio.set_output(key, val)
            val = self.__dio.get_output(name=key) != self.__led_common_anode[key]
            modbus_datastore.set_di_state(name, val)

        # prepis stavu kontrolnich pinu
        for key in self.__dio.DIGITAL_OUTPUTS_CTRL:
            val = modbus_datastore.get_co_state(name=key) != self.__ctr_output_inverted[key]
            self.__dio.set_output(key, val)
            val = self.__dio.get_output(name=key) != self.__ctr_output_inverted[key]
            modbus_datastore.set_di_state(key, val)

        # prepis stavu analogovych vstupu
        for key in self.__aio.ANALOG_INPUTS:
            if 'CP' in key:
                name = 'CP_VOLTAGE' + key[2]
                modbus_datastore.set_ir_state(name=name, value=round(self.__aio.get_input(key)))
            elif 'PP' in key:
                name = 'PP_RESISTANCE' + key[2]
                modbus_datastore.set_ir_state(name=name, value=round(self.__aio.get_input(key)))
            else:
                pass

        # prepis stavu analogovych vystupu
        for key in self.__aio.ANALOG_OUTPUTS:
            name = 'CP_DUTY' + key[2]
            self.__aio.set_output(key, modbus_datastore.get_hr_state(name=name))
            modbus_datastore.set_ir_state(name=name, value=self.__aio.get_output(key))

        # prepis stavu pocitadel a jejich pripadne nulovani:
        for key in self.__dio.DIGITAL_INPUTS:
            name = key + '_CNT_CLR'
            if modbus_datastore.get_co_state(name=name):
                self.__dio.clr_input_counter(key)

            val = self.__dio.get_input_counter(key)
            name = key + '_CNT_L'
            modbus_datastore.set_ir_state(name=name, value=(val & 0xFFFF))
            name = key + '_CNT_H'
            modbus_datastore.set_ir_state(name=name, value=((val >> 16) & 0xFFFF))

        # prepis stavu elektromeru a jejich pripadne nulovani
        for channel_raw_num in range(len(self.__electrometer)):
            key = "ELECTROMETER{0}".format(channel_raw_num + 1)
            name = key + '_CLR'
            if modbus_datastore.get_co_state(name=name):
                self.__electrometer[channel_raw_num].reset()

            val = self.__electrometer[channel_raw_num].read()
            name = key + '_L'
            modbus_datastore.set_ir_state(name=name, value=val[0])
            name = key + '_H'
            modbus_datastore.set_ir_state(name=name, value=val[1])

        # rekalibrace analogových vstupů
        if self.__aio_calibration_div_cnt > 0:
            self.__aio_calibration_div_cnt = self.__aio_calibration_div_cnt - 1
        else:
            self.__aio.check_calibration()
            self.__aio_calibration_div_cnt = 9

        # inkrementace pocitadla exekuce
        now = time.time()
        if (now - self.__counter_step_start_time) > 1:
            self.__counter = self.__counter + 1

            counter_top = modbus_datastore.get_hr_state(name="COUNTER_TOP")
            if self.__counter > counter_top:
                self.__counter = 0
            self.__counter_step_start_time = now
            
        modbus_datastore.set_ir_state(name="COUNTER", value=self.__counter)

        return 0
