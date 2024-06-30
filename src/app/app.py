import app.constants as c
from app.helpers import *

# from device.device import Device
from frame.connect.connect import ConnectFrame
# from frame.control.control import ControlFrame
from frame.values.values import ValuesFrame

import customtkinter as tk

class App:
    def __init__(self):
        self.__root = tk.CTk()
        self.__root.title(c.APP_NAME)
        self.__root.geometry(c.APP_GEOMETRY)
        
        self.__frame1 = tk.CTkFrame(self.__root)
        self.__frame2 = tk.CTkFrame(self.__root)
        
        # self.__device = Device()
        self.__connect_frame = ConnectFrame(self.__frame2)
        # self.__control_frame = ControlFrame()
        self.__values_frame = ValuesFrame(self.__frame2, width=950, height=230)
    
    def run(self):
        self.__frame1.grid(row=0, column=0)
        self.__frame2.grid(row=1, column=0)
        
        self.__connect_frame.mygrid(row=0, column=0)
        self.__values_frame.mygrid(row=0, column=1)
        
        self.__root.mainloop()
    
    def __del__(self):
        pass