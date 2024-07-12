from pymodbus.client import ModbusSerialClient

class Device:
    def __init__(self) -> None:
        self._create()
        
    def _create(self) -> None:
        self.__client = None
        
        self.__number_of_coils = 0
        self.__number_of_discrete_inputs = 0
        self.__number_of_input_registers = 0
        self.__number_of_holding_registers = 0
        
        self.data = {
            "Coil": {
                "group": [], 
                "physical_address": [],
                "logical_address": [],
                "value": [],
                "name": [],
                "description": [],
                "notes": []
            },
            "Discrete input": {
                "group": [],
                "physical_address": [],
                "logical_address": [],
                "value": [],
                "name": [],
                "description": [],
                "notes": []
            },
            "Input register": {
                "group": [],
                "physical_address": [],
                "logical_address": [],
                "value": [],
                "name": [],
                "description": [],
                "notes": []
            },
            "Holding register": {
                "group": [],
                "physical_address": [],
                "logical_address": [],
                "value": [],
                "name": [],
                "description": [],
                "notes": []
            }
        }
        
        self.is_connected = False
        
    def _clear_data(self) -> None:
        for category in self.data:
            for attribute in self.data[category]:
                self.data[category][attribute] = []
    
    def connect(self, method, port, baudrate, bytesize, parity, stopbits) -> None:
        self.__method = method
        self.__port = port
        self.__baudrate = baudrate
        self.__bytesize = bytesize
        self.__parity = parity
        self.__stopbits = stopbits
        
        self.__client = ModbusSerialClient(
            method=self.__method,
            port=self.__port,
            baudrate=self.__baudrate,
            bytesize=self.__bytesize,
            parity=self.__parity,
            stopbits=self.__stopbits
        )

        self.is_connected = self.__client.connect()
        
        if self.is_connected:
            self.check_space()
            self.prepare_table()
    
    def disconnect(self) -> None:
        self.__client.close()
        self.is_connected = False
        
    def __read_until_failure(self, read_method):
        address = 0
        
        while True:
            try:
                response = read_method(address=address, count=1, slave=1)
                try:
                    response.bits[0]
                except:
                    response.registers[0]
            except:
                break
            address += 1
            
        return address
        
    def check_space(self) -> None:
        self.__number_of_coils = self.__read_until_failure(
            self.__client.read_coils
        )
        self.__number_of_discrete_inputs = self.__read_until_failure(
            self.__client.read_discrete_inputs
        )
        self.__number_of_input_registers = self.__read_until_failure(
            self.__client.read_input_registers
        )
        self.__number_of_holding_registers = self.__read_until_failure(
            self.__client.read_holding_registers
        )
        
    def prepare_table(self) -> None:
        self._clear_data()
        
        self.__enter_data("Coil", length=self.__number_of_coils)
        self.__enter_data("Discrete input", length=self.__number_of_discrete_inputs)
        self.__enter_data("Input register", length=self.__number_of_input_registers)
        self.__enter_data("Holding register", length=self.__number_of_holding_registers)
        
    def __calculate_item(self, item):
        value1 = item // 128
        value2 = item % 128
        
        return value1, value2
    
    def __read_item(self, read_method, item, bits: bool) -> list:
        address = 0
        max_count = 128
        response = []
        
        value1, value2 = self.__calculate_item(item)
        
        for _ in range(value1):
            curr_response = read_method(address=address, count=max_count, slave=1)
            if bits:
                list_response = curr_response.bits
            else:
                list_response = curr_response.registers
            
            for i in range(len(list_response)):
                response.append(list_response[i])
            
            address += max_count
            
        curr_response = read_method(address=address, count=value2, slave=1)
        if bits:
            list_response = curr_response.bits
        else:
            list_response = curr_response.registers
        
        for i in range(len(list_response)):
            response.append(list_response[i])
        
        return response
    
    
    def __enter_data(self, name, response: list=None, length: int=None) -> None:
        if length is None and response is None:
            return
        
        if length is None:
            length = len(response)
        
        for i in range(length):
            self.data[name]["group"].append(name)
            self.data[name]["physical_address"].append(i)    
            self.data[name]["logical_address"].append(i+1)
            
            if response is not None:
                self.data[name]["value"].append(response[i])
            else:
                self.data[name]["value"].append("None")
                
            self.data[name]["name"].append("None")
            self.data[name]["description"].append("None")
            self.data[name]["notes"].append("None")
        
    def read(self) -> None:
        self._clear_data()

        coil_response = self.__read_item(
            self.__client.read_coils,
            self.__number_of_coils,
            True
        )
        
        self.__enter_data("Coil", coil_response)
        
        discrete_inputs_response = self.__read_item(
            self.__client.read_discrete_inputs,
            self.__number_of_discrete_inputs,
            True
        )
        
        self.__enter_data("Discrete input", discrete_inputs_response)
        
        input_registers_response = self.__read_item(
            self.__client.read_input_registers,
            self.__number_of_input_registers,
            False
        )
        
        self.__enter_data("Input register", input_registers_response)
        
        holding_registers_response = self.__read_item(
            self.__client.read_holding_registers,
            self.__number_of_holding_registers,
            False
        )
        
        self.__enter_data("Holding register", holding_registers_response)
        
    def __correct_values(self, data: dict) -> None:
        for i in range(len(data["group"])):
            if data["group"][i] == "Coil":
                if str(data["value"][i]) == "True":
                    data["value"][i] = True
                elif str(data["value"][i]) == "False":
                    data["value"][i] = False
                else:
                    continue
            elif data["group"][i] == "Holding register":
                data["value"][i] = int(data["value"][i])
        
    def __write_item(self, write_method, item, data: list) -> None:
        address = 0
        max_count = 128
        
        value1, value2 = self.__calculate_item(item)
        
        for _ in range(value1):
            write_method(address=address, values=data[address:address+max_count], unit=1)
            address += max_count
            
        write_method(address=address, values=data[address:address+value2], unit=1)
            
    def write(self, data: dict) -> None:
        self.__correct_values(data)
        curr_data = {
            "Coil": [],
            "Holding register": []
        }
        
        for i in range(len(data["group"])):
            if data["group"][i] == "Coil":
                curr_data["Coil"].append(data["value"][i])
            elif data["group"][i] == "Holding register":
                curr_data["Holding register"].append(data["value"][i])
        
        self.__write_item(
            self.__client.write_coils,
            self.__number_of_coils,
            curr_data["Coil"]
        )
        
        self.__write_item(
            self.__client.write_registers,
            self.__number_of_holding_registers,
            curr_data["Holding register"]
        )