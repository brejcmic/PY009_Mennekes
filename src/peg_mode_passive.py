""" MODE PASSIVE (EXTERNAL) Pasivní ovládání jednotky mennekes pomocí externí aplikace.

    Modul tohoto režimu nezasahuje do běhu jednotky, pouze poskytuje prázdné funkce odpovídající modulům režimu
    řízení.
    Z tohoto modul by měly být odvozeny ostatní režimy.
"""

# ----------------------------------------------------------------------------------------------------------------------
# Import knihoven
# ----------------------------------------------------------------------------------------------------------------------
# hlaseni na konzoli
try:
    import peg_msg
except ImportError:
    from src import peg_msg

try:
    from peg_global_scope import singleton_modbus_datastore
except ImportError:
    from src.peg_global_scope import singleton_modbus_datastore


# ----------------------------------------------------------------------------------------------------------------------
# Konstanty modulu
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Hlavní třída modulu
# ----------------------------------------------------------------------------------------------------------------------
class PassiveMode:
    __COLORS = {
        "black":    (False, False, False),
        "red":      (True, False, False),
        "green":    (False, True, False),
        "blue":     (False, False, True),
        "yellow":   (True, True, False),
        "cyan":     (False, True, True),
        "magenta":  (True, False, True),
        "white":    (True, True, True),
    }

    def __int__(self, channel: int, idname: str = "PASSIVE"):
        """
        Inicializace objektu režimu. Vždy je třeba zadat číslo kanálu, podle kterého se identifikuje offset
        modbus registrů. Pro zadané hodnoty <= 1 se uvažuje kanál 1, pro ostatní hodnoty kanál 2.

        Parameters
        ----------
        channel : int
            číslo kanálu (1 nebo 2), ke kterému režim náleží,
        idname : str
            název režimu, který lze použít jako index ve slovníku.
        """
        self.__idname = idname
        if channel < 2:
            self.__channel = 1
        else:
            self.__channel = 2
        peg_msg.warningmsg("Jednotka se provozuje v rezimu: {0}".format(self.__idname))

    def __del__(self):
        """
        Likvidace objektu režimu
        """
        peg_msg.validmsg("Ukonceni cinnosti rezimu: {0}".format(self.__idname))

    def get_id(self) -> str:
        """
        Získání identifikačního názvu režimu.

        Returns
        -------
        idname : str
            název režimu.
        """
        return self.__idname

    def get_channel(self) -> int:
        """
        Získání informace o aktuálně nastaveném kanálu.

        Returns
        -------
        channel : int
            číslo kanálu (nabíjecího konektoru).
        """
        return self.__channel

    def poll(self):
        """
        Vybavení zásahu stavového automatu tohoto režimu.
        """
        pass

    def _is_error(self) -> bool:
        """
        Čtení stavu HW vstupu, na kterém se detekuje porucha kanálu. Pokud je při volání funkce porucha aktivní, pak
        tato funkce zajistí odpojení silového obvodu a přenastavení signálu control pilot do stavu chyby.

        Přenastavení zpět po opravě chybového stavu je nutné provést voláním příslušných funkcí.

        Returns
        -------
        is_active : bool
            True pokud je  porucha aktivní.
        """

        is_active = not singleton_modbus_datastore.get_di_state("IN{0}P2_STOK".format(self.__channel))

        if is_active:
            self._set_control_pilot_to_error()
            self._set_output_switch_off()

        return is_active

    def _is_vehicle_connected(self):
        """
        Informace, zda je ke konektoru připojeno vozidlo.

        Returns
        -------
        vehicle_is_present : bool
            True, pokud je na konektoru detekováno vozidlo a konektor není v chybě.
        """
        if self._is_error():
            return False

        resistance = singleton_modbus_datastore.get_ir_state("PP_RESISTANCE{0}".format(self.__channel))
        cp_voltage = singleton_modbus_datastore.get_ir_state("CP_VOLTAGE{0}".format(self.__channel))

        return (90 < resistance < 1600) and (2 < cp_voltage < 10)

    def _set_leds(self, color: str) -> None:
        """
        Nastavení barvy výstupních LED. Parametr barvy musí být jedním z následujících názvů:

        - "black",
        - "red",
        - "green",
        - "blue",
        - "yellow",
        - "cyan"
        - "magenta",
        - "white"

        Parameters
        ----------
        color : str
            platný název barvy, pokud není platný, nastavuje se "black"
        """
        color = color.lower()
        if color in self.__COLORS:
            singleton_modbus_datastore.set_co_state("LED_RED{0}".format(self.__channel),
                                                    self.__COLORS[color][0])
            singleton_modbus_datastore.set_co_state("LED_GREEN{0}".format(self.__channel),
                                                    self.__COLORS[color][1])
            singleton_modbus_datastore.set_co_state("LED_BLUE{0}".format(self.__channel),
                                                    self.__COLORS[color][2])
        else:
            singleton_modbus_datastore.set_co_state("LED_RED{0}".format(self.__channel),
                                                    False)
            singleton_modbus_datastore.set_co_state("LED_GREEN{0}".format(self.__channel),
                                                    False)
            singleton_modbus_datastore.set_co_state("LED_BLUE{0}".format(self.__channel),
                                                    False)

    def _set_control_pilot_to_active(self) -> bool:
        """
        Spuštění signálu na vodiči CP se střídou odpovídající aktuální hodnotě změřeného rezistoru na vodiči PP a
        maximální povolené hodnotě proudu tohoto kanálu.

        Funkce nemusí nutně nastavit výstupní střídu na hodnotu menší než 100% pokud:

        - měřený odpor na PP je menší než 90 ohm,
        - měřený odpor na PP je větší než 1600 ohm,
        - je zadaná hodnota maximálního proudu kanálu méně jak 6 A,
        - je zadaná hodnota maximálního proudu kanálu více jak 80 A.

        Pokud je detekována HW chyba, pak navíc dojde k rozpojení výstupního stykače a k přenastavení střídy do
        na hodnotu 0 %.

        Pokud dojde k nastavení hodnoty 100 % (idle), pak funkce vrací stav False.

        Returns
        -------
        is_active : bool
            True pro aktivní signál odpovídající proudu, který je více jak 0.
        """

        if self._is_error():
            return False

        # limit proudu dle PP
        resistance = singleton_modbus_datastore.get_ir_state("PP_RESISTANCE{0}".format(self.__channel))
        if resistance > 1600:
            current_limit = 0
        elif resistance > 1400:
            current_limit = 10
        elif resistance > 660:
            current_limit = 16
        elif resistance > 200:
            current_limit = 32
        elif resistance > 90:
            current_limit = 63
        else:
            current_limit = 0

        # nastaveni hodnoty stridy
        if 6 <= current_limit < 51:
            duty = round(current_limit / 0.6)
        elif 51 <= current_limit <= 80:
            duty = round((current_limit / 2.5) + 64)
        else:
            duty = 100

        singleton_modbus_datastore.set_hr_state("CP_DUTY{0}".format(self.__channel), duty)

        return duty < 100

    def _set_control_pilot_to_idle(self) -> bool:
        """
        Nastavení cp signálu do nečinného stavu, tj. 100% střída. Nečinný stav nebude nastaven v případě, že je
        detekována HW chyba daného kanálu. V případě chyby se vždy nastaví střída 0 %.

        Returns
        -------
        idle_is_active : bool
            True pro nastavený idle stav, jinak False při chybě.
        """
        if self._is_error():
            return False

        singleton_modbus_datastore.set_hr_state("CP_DUTY{0}".format(self.__channel), 100)
        return True

    def _set_control_pilot_to_error(self) -> None:
        """
        Nastavení cp signálu do stavu odpovídajícímu chybě stanice, tj. 0% střída.

        Returns
        -------
            None
        """
        singleton_modbus_datastore.set_hr_state("CP_DUTY{0}".format(self.__channel), 0)

    def _set_output_switch_on(self) -> bool:
        """
        Sepnutí stykače napájecího konektoru pro zahájení dodávky energie. Funkce neprovede sepnutí, pokud je
        detekována porucha konektoru.

        Returns
        -------
        is_switched_on : bool
            True, pokud byl výstupní stykač nastaven na sepnutí.
        """
        if self._is_error():
            return False

        singleton_modbus_datastore.set_co_state("POWER_SW{0}".format(self.__channel), True)
        return True

    def _set_output_switch_off(self) -> None:
        """
        Rozepnutí stykače napájecího konektoru pro zamezení toku energie. K povelu rozepnutí dojde vždy při volání
        této funkce.

        Returns
        -------
            None
        """
        singleton_modbus_datastore.set_co_state("POWER_SW{0}".format(self.__channel), False)

