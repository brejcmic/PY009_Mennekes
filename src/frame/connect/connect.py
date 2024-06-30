import frame.connect.constants as c
from frame.connect.helpers import *

import customtkinter as tk

class ConnectLine:
    def __init__(self, root, description: str, options: list, custom: bool, refresh: bool) -> None:
        self.__root = root
        self.__description = description
        self.__options = options
        self.__selected = tk.StringVar()
        self.__custom = custom
        self.__refresh = refresh
        
        self.__items()
        
    def __items(self) -> None:
        self.__label_description = tk.CTkLabel(self.__root, text=self.__description, width=c.DESCRIPTION_WIDTH, height=c.ITEMS_HEIGHT)
        
        self.__optionmenu_options = tk.CTkOptionMenu(self.__root, variable=self.__selected, values=self.__options, width=c.OPTIONS_WIDTH, height=c.ITEMS_HEIGHT)
        self.__optionmenu_options.set(self.__options[0])
        
        if self.__custom:
            self.__entry_custom = tk.CTkEntry(self.__root, width=c.CUSTOM_ENTRY_WIDTH, height=c.ITEMS_HEIGHT)
            self.__switch_custom = tk.CTkSwitch(self.__root, text='', command=self.__toggle_switch_custom, width=c.CUSTOM_SWITCH_WIDTH, height=c.ITEMS_HEIGHT)
            
        if self.__refresh:
            self.__button_refresh = tk.CTkButton(self.__root, text='Refresh', width=c.REFRESH_WIDTH, height=c.ITEMS_HEIGHT)
        
    def _mygrid(self, row: int) -> None:
        self.__row = row
         
        self.__label_description.grid(row=self.__row, column=0, sticky="w")
        
        self.__optionmenu_options.grid(row=self.__row, column=1, sticky="w")
        
        if self.__custom:
            self.__switch_custom.grid(row=self.__row, column=2, sticky="w")
        if self.__refresh:
            self.__button_refresh.grid(row=self.__row, column=3, sticky="w")
            
    def __toggle_switch_custom(self) -> None:
        if self.__switch_custom.get():
            self.__entry_custom.grid(row=self.__row, column=1, sticky="w")
            self.__optionmenu_options.grid_forget()
        else:
            self.__optionmenu_options.grid(row=self.__row, column=1, sticky="w")
            self.__entry_custom.grid_forget()
    
class ConnectFrame(tk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master)
        
        self.__method = ConnectLine(self, *c.METHOD_PARAMETERS)
        self.__port = ConnectLine(self, *c.PORT_PARAMETERS)
        self.__baudrate = ConnectLine(self, *c.BAUDRATE_PARAMETERS)
        self.__databits = ConnectLine(self, *c.DATABITS_PARAMETERS)
        self.__parity = ConnectLine(self, *c.PARITY_PARAMETERS)
        self.__stopbits = ConnectLine(self, *c.STOPBITS_PARAMETERS)

    def mygrid(self, row: int, column: int) -> None:
        self.__row = row
        self.__column = column
        
        self.grid(row=self.__row, column=self.__column, sticky="w")
        
        self.__method._mygrid(row)
        self.__port._mygrid(row + 1)
        self.__baudrate._mygrid(row + 2)
        self.__databits._mygrid(row + 3)
        self.__parity._mygrid(row + 4)
        self.__stopbits._mygrid(row + 5)