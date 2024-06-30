import frame.values.constants as c
from frame.values.helpers import *

import customtkinter as tk

class ValuesLine:
    def __init__(self, root, group: str, physical_address: str, logical_address: str, value: str, name: str, description: str, note: str) -> None:
        self.__root = root
        self.__group = group
        self.__physical_address = physical_address
        self.__logical_address = logical_address
        self.__value = value
        self.__name = name
        self.__description = description
        self.__note = note
        
        self.__items()
        
    def __items(self) -> None:
        self.__label_group = tk.CTkLabel(self.__root, text=self.__group)
        self.__label_physical_address = tk.CTkLabel(self.__root, text=self.__physical_address)
        self.__label_logical_address = tk.CTkLabel(self.__root, text=self.__logical_address)
        
        if self.__group == c.NAME_1 or self.__group == c.NAME_2:
            self.__entry_value = tk.CTkEntry(self.__root, placeholder_text=self.__value)
        else:
            self.__label_value = tk.CTkLabel(self.__root, text=self.__value)
            
        self.__entry_name = tk.CTkEntry(self.__root, placeholder_text=self.__name)
        self.__entry_description = tk.CTkEntry(self.__root, placeholder_text=self.__description)
        self.__entry_note = tk.CTkEntry(self.__root, placeholder_text=self.__note)
        
    def _mygrid(self, row: int) -> None:
        self.__row = row
        
        self.__label_group.grid(row=self.__row, column=0, sticky="w")
        self.__label_physical_address.grid(row=self.__row, column=1, sticky="w")
        self.__label_logical_address.grid(row=self.__row, column=2, sticky="w")
        
        if self.__group == c.NAME_1 or self.__group == c.NAME_2:
            self.__entry_value.grid(row=self.__row, column=3, sticky="w")
        else:
            self.__label_value.grid(row=self.__row, column=3, sticky="w")
            
        self.__entry_name.grid(row=self.__row, column=4, sticky="w")
        self.__entry_description.grid(row=self.__row, column=5, sticky="w")
        self.__entry_note.grid(row=self.__row, column=6, sticky="w")
    
class ValuesFrame(tk.CTkScrollableFrame):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.__lines = []
        
        for _ in range(10):
            line = ValuesLine(
                self,
                group='',
                physical_address='',
                logical_address='',
                value='',
                name='',
                description='',
                note=''
            )
            
            self.__lines.append(line)
            
    def read(self, values: dict) -> None:
        self.__lines = []
        self.__values = values
        
        for _ in range(len(self.__values["group"])):
            line = ValuesLine(
                self,
                self.__values["group"][_],
                self.__values["physical_address"][_],
                self.__values["logical_address"][_],
                self.__values["value"][_],
                self.__values["name"][_],
                self.__values["description"][_],
                self.__values["note"][_]
            )
            
            self.__lines.append(line)
            
    def mygrid(self, row: int, column: int) -> None:
        self.__row = row
        self.__column = column
        
        self.grid(row=self.__row, column=self.__column, sticky="w")
        
        for _ in range(len(self.__lines)):
            self.__lines[_]._mygrid(_)