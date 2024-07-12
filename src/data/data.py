from PyQt6.QtWidgets import QFileDialog
import pandas as pd
import csv


class Data:
    def __init__(self) -> None:
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
        
        self.__current_file_path = None
        
    def read(self, file_path: str) -> None:
        self.__file_path = file_path
        
        idk_data = pd.read_csv(self.__file_path, sep=";")
        curr_data = idk_data.to_dict()
        
        for i in range(len(curr_data["group"])):
            if str(curr_data["group"][i]) == "Coil":
                self.data["Coil"]["group"].append(curr_data["group"][i])
                self.data["Coil"]["physical_address"].append(curr_data["physical_address"][i])
                self.data["Coil"]["logical_address"].append(curr_data["logical_address"][i])
                self.data["Coil"]["value"].append(curr_data["value"][i])
                self.data["Coil"]["name"].append(curr_data["name"][i])
                self.data["Coil"]["description"].append(curr_data["description"][i])
                self.data["Coil"]["notes"].append(curr_data["notes"][i])
            elif str(curr_data["group"][i]) == "Discrete input":
                self.data["Discrete input"]["group"].append(curr_data["group"][i])
                self.data["Discrete input"]["physical_address"].append(curr_data["physical_address"][i])
                self.data["Discrete input"]["logical_address"].append(curr_data["logical_address"][i])
                self.data["Discrete input"]["value"].append(curr_data["value"][i])
                self.data["Discrete input"]["name"].append(curr_data["name"][i])
                self.data["Discrete input"]["description"].append(curr_data["description"][i])
                self.data["Discrete input"]["notes"].append(curr_data["notes"][i])
            elif str(curr_data["group"][i]) == "Input register":
                self.data["Input register"]["group"].append(curr_data["group"][i])
                self.data["Input register"]["physical_address"].append(curr_data["physical_address"][i])
                self.data["Input register"]["logical_address"].append(curr_data["logical_address"][i])
                self.data["Input register"]["value"].append(curr_data["value"][i])
                self.data["Input register"]["name"].append(curr_data["name"][i])
                self.data["Input register"]["description"].append(curr_data["description"][i])
                self.data["Input register"]["notes"].append(curr_data["notes"][i])
            elif str(curr_data["group"][i]) == "Holding register":
                self.data["Holding register"]["group"].append(curr_data["group"][i])
                self.data["Holding register"]["physical_address"].append(curr_data["physical_address"][i])
                self.data["Holding register"]["logical_address"].append(curr_data["logical_address"][i])
                self.data["Holding register"]["value"].append(curr_data["value"][i])
                self.data["Holding register"]["name"].append(curr_data["name"][i])
                self.data["Holding register"]["description"].append(curr_data["description"][i])
                self.data["Holding register"]["notes"].append(curr_data["notes"][i])
        
    def write(self, file_path: str, data: dict) -> None:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            
            header = data.keys()
            writer.writerow(header)
            
            rows = zip(*data.values())
            writer.writerows(rows)
    
    def save(self, content, window) -> None:
        if not self.__current_file_path:
            self.saveas(content, window)
        else:
            self.write(self.__current_file_path, content)
            print(f"Content saved to: {self.__current_file_path}")
    
    def saveas(self, content, window) -> None:
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(window, "Save File", "", "CSV files (*.csv);;All files (*.*)")
        if file_path:
            self.__current_file_path = file_path
            self.write(self.__current_file_path, content)
            print(f"Content saved to: {self.__current_file_path}")
    
    def open(self, window) -> None:
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(window, "Open File", "", "CSV files (*.csv);;All files (*.*)")
        if file_path:
            self.read(file_path)
    