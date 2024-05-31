# import knihoven
import threading
import time

# pymodbus
from pymodbus.client.serial import ModbusSerialClient

# elektrometer - class pro zavedení společného rozhraní všem zařízením
class Electrometer:
    # init - pro zalozeni elektrometru je potreba zadat cislo kanalu
    # pokud je kanal 1 nebo mensi je to kanal 1
    # pokud je kanal 2 nebo vetsi je to kanal 2
    def __init__(self, channel_num: int):
        self.__consumption = [0, 0] # spotreba
        self.__alive = False # ! POZOR - kdyz nastane chyba tak alive = False
        self.__enabled = True # ! POZOR - kdyz je enabled - program bezi a vyzaduje funkcost
        self.__period = 5 # ! POZOR - perioda cas na neco
        self.__watchdog_period = self.__period + 4 # ! POZOR - kontrola po casovym useku
        self.__watchdog = time.time() # ! POZOR - zaznamenavani casu

        # nastaveni kanalu
        if channel_num > 1:
            self.__channel_num = 2
        else:
            self.__channel_num = 1

        self.__reset_req = True

    # destruktor - obecneho zařízení elektroměru
    def __del__(self):
        self.disable()

    # spusteni elektrometru
    def start(self):
        # pokud uz neni zapnuty a je povoleny
        if not self.__alive and self.__enabled:
            self.__alive = True
            self.__watchdog = time.time()
            self.__thread = threading.Thread(target=self.__run)
            self.__thread.daemon = True
            self.__thread.start()
    
    # povoleni
    def enable(self):
        self.__enabled = True

    # zakazani
    def disable(self):
        self.__enabled = False

    # zjisteni stavu - bezi nebo nebezi
    def is_alive(self):
        # pokud je elektrometr bezi nebo je cas mensi nez watchdog
        return self.__alive or time.time() < self.__watchdog
    
    # zjisteni spotreby
    def read(self):
        return self.__consumption
    
    # ziskani kanalu
    def get_channel_num(self):
        return self.__channel_num
    
    # restartovani hodnot a vynuceni resetu
    def reset(self):
        self.__consumption = [0, 0]
        self.__reset_req = True

    # ziskani stavu resetu
    def _get_reset(self):
        return self.__reset_req
    
    # potvrzeni resetu
    def _reset_ack(self):
        self.__reset_req = False

    # aktualizace hodnoty spotreby
    def _update_consumption(self):
        low = 0
        high = 0
        return [low, high]

    # casove vlakno pro periodickou aktualiuzaci spotreby
    def __task(self):
        self._alive = True
        self.__consumption = self._update_consumption()
        self.start()

# rozsiruje o clienta pro modbus
# komunikace pomoci seriove linky RS485 (protokol modbus)
# typ: 3f MGRKZ 465
class ElectrometerSchrackMGRZK465(Electrometer):
    # rozsireny init s deklaraci client_portu
    def __init__(self, channel_num: int):
        # zavolani zdedeneho konstruktoru
        super().__init__(channel_num)

        if self.get_channel_num() > 1:
            client_port = '/dev/tty.GOGTWSBUDDY02'
        else:
            client_port = '/dev/tty.GOGTWSBUDDY02'

        self.__client = ModbusSerialClient(
            method='rtu',
            port=client_port,
            baudrate=115200,
            bytesize=8,
            parity='N',
            stopbits=1
        )
        
        self.__client.connect()

    # rozsireny destruktoru       
    def __del__(self):
        super().disable()
        self.__client.close()

    # aktualizace hodnoty spotreby
    def _update(self):
        # registr pro reset
        if self._get_reset():
            self.__client.write_register(address=13, value=0x01, unit=33)
            self._ack_reset()

        # zap
        data = self.__client.read_input_registers(address=426, count=2, unit=33)

        if data.isError():
            low = 0
            high = 0
            print("Data error")
        else:
            val = int(((int(data.registers[0]) << 16) + int(data.registers[1])) / 10)
            low = val & 0xFFFF
            high = (val >> 16) & 0xFFFF

        return [low, high]
    
# test modulu
if __name__ == "__main__":

    client = ModbusSerialClient(
        method='rtu',
        port= '/dev/cu.usbserial-AJ03LLWP',
        baudrate=115200,
        bytesize=8,
        parity='N',
        stopbits=1
    )

    # zapis
    for i in range(0, 32):
        check_coil = client.write_coil(address=i, value=0, unit=1)
        print(check_coil)

    for i in range(0, 64):
        check_holding = client.write_register(address=i, value=i, unit=1)
        print(check_holding)

    # cteni
    data_input = client.read_input_registers(address=0, count=32, slave=1)
    data_coil = client.read_coils(address=0, count=32, slave=1)
    data_discrete = client.read_discrete_inputs(address=0, count=32, slave=1)
    data_holding = client.read_holding_registers(address=0, count=64, slave=1)

    print(data_coil)
    print(data_coil.bits)
    print(data_discrete)
    print(data_discrete.bits)
    print(data_holding)
    print(data_holding.registers)
    print(data_input)
    print(data_input.registers)