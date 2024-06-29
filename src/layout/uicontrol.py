import customtkinter as tk

class MyControlFrame(tk.CTkFrame):
    def __init__(self, master, device, myconnectionframe, mycontrol) -> None:
        super().__init__(master)
        self.device = device
        self.myconnectionframe = myconnectionframe
        self.mycontrol = mycontrol
        
        self.label_status = tk.CTkLabel(self, text="Status", width=330, bg_color="red")
        
        self.button_connect = tk.CTkButton(self, text="Connect", width=100, command=self.connect_pressed)
        self.button_disconnect = tk.CTkButton(self, text="Disconnect", width=100, command=self.disconnect_pressed)
    
        self.button_save = tk.CTkButton(self, text="Save", width=75)
        self.button_saveas = tk.CTkButton(self, text="Save as", width=75)
        
        self.button_load = tk.CTkButton(self, text="Load", width=75)
        
        self.button_write = tk.CTkButton(self, text="Write", width=75, command=self.write_pressed)
        self.button_read = tk.CTkButton(self, text="Read", width=75, command=self.read_pressed)
        self.entry_readinterval = tk.CTkEntry(self, placeholder_text="Interval", width=75)
    
    def draw_frame(self, row, column) -> None:
        self.grid(row=row, column=column, sticky="w")
        
        self.label_status.grid(row=0, column=0, sticky="w")
        
        self.button_connect.grid(row=0, column=1, sticky="w")
        self.button_disconnect.grid(row=0, column=2, sticky="w")
        
        self.button_save.grid(row=0, column=4, sticky="w")
        self.button_saveas.grid(row=0, column=7, sticky="w")
        
        self.button_load.grid(row=0, column=8, sticky="w")
        
        self.button_write.grid(row=0, column=11, sticky="w")
        self.button_read.grid(row=0, column=12, sticky="w")
        self.entry_readinterval.grid(row=0, column=13, sticky="w")
        
        print("MyControlFrame drawn")
        
    def connect_pressed(self) -> None:
        self.device.connect(self.myconnectionframe.get_parameters())
        
    def disconnect_pressed(self) -> None:
        self.device.disconnect()
        
    def read_pressed(self) -> None:
        self.device.read_values_device()
        self.mycontrol.update_values(self.device.data["value"])
        
        for i in range(len(self.device.data["group"])):
            print(self.device.data["group"][i], self.device.data["value"][i])
            
    def write_pressed(self) -> None:
        self.device.write_values_device(self.mycontrol.get_values())