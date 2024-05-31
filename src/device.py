from pymodbus.client import ModbusSerialClient

class Device:
    def __init__(self):
        pass

    def connect(self, method, port, baudrate, bytesize, parity, stopbits):

        self.__client = ModbusSerialClient(
            method=method,
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits
        )

        self.__client.connect()

    def disconnect(self):
        self.__client.close()
        