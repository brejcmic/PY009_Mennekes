from pymodbus.client.serial import ModbusSerialClient
import pandas as pd

class MyDevice:
    def __init__(self) -> None:
        self.values: dict = {}
        
    def update(self) -> None:
        self.read_csv("resource/data.csv")
        
    def connect(self, parameters) -> None:
        self.client = ModbusSerialClient(
            method=parameters["method"],
            port="/dev/cu.usbserial-"+parameters["port"],
            baudrate=int(parameters["baudrate"]),
            bytesize=int(parameters["bytesize"]),
            parity=parameters["parity"],
            stopbits=int(parameters["stopbits"])
        )
        
        self.client.connect()
        
        print("Device connected")
        
    def disconnect(self) -> None:
        self.client.close()
        
        print("Device disconnected")
        
    def read_csv(self, file_path) -> None:
        self.data = pd.read_csv(file_path, sep=';')
        
        print("CSV read")
        
    def read_values_device(self) -> None:
        for i in range(len(self.data["group"])):
            if self.data["group"][i] == "Coil":
                response = self.client.read_coils(
                    address=self.data["logical_address"][i],
                    count=1,
                    slave=1
                )
                self.data["value"][i] = response.bits[0]
                
                if self.data["value"][i]:
                    self.data["value"][i] = "True"
                else:
                    self.data["value"][i] = "False"
            elif self.data["group"][i] == "Digital input":
                response = self.client.read_discrete_inputs(
                    address=self.data["logical_address"][i],
                    count=1,
                    slave=1
                )
                self.data["value"][i] = response.bits[0]
                if self.data["value"][i]:
                    self.data["value"][i] = "True"
                else:
                    self.data["value"][i] = "False"
            elif self.data["group"][i] == "Input register":
                response = self.client.read_input_registers(
                    address=self.data["logical_address"][i],
                    count=1,
                    slave=1
                )
                self.data["value"][i] = response.registers[0]
            elif self.data["group"][i] == "Holding register":
                response = self.client.read_holding_registers(
                    address=self.data["logical_address"][i],
                    count=1,
                    slave=1
                )
                self.data["value"][i] = response.registers[0]
        
        print("Values read")
        
    def write_values_device(self, values) -> None:
        for i in range(len(values)):
            if values[i]["group"] == "Coil" and (values[i]["value"] == "True" or values[i]["value"] == "False"):
                self.client.write_coils(
                    address=values[i]["logical_address"],
                    values=values[i]["value"],
                    slave=1
                )
            elif values[i]["group"] == "Holding register":
                self.client.read_holding_registers(
                    address=self.data[i]["logical_address"],
                    values=values[i]["value"],
                    slave=1
                )
        
        print("Values written")
