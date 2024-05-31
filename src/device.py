from pymodbus.client import ModbusSerialClient

class Device:
    def __init__(self):
        self.__client = ModbusSerialClient(port="")

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
        