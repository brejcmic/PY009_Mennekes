import customtkinter as tk

class MyConnectionLine():
    def __init__(self, master, description: str, parameter: list, custom: bool, refresh: bool) -> None:
        
        self.description = description
        self.parameter = parameter
        self.custom = custom
        self.refresh = refresh
        
        self.label_description = tk.CTkLabel(master, text=self.description, width=75, height=40)
        
        self.optionmenu_parameter = tk.CTkOptionMenu(master, values=self.parameter, width=150, height=40)
        self.optionmenu_parameter.set(self.parameter[0])
        
        if self.custom:
            self.entry_custom = tk.CTkEntry(master, width=150, height=40)
            self.switch_custom = tk.CTkSwitch(master, text="", width=50, height=40, command=self.toggle_switch_custom)
            
        if self.refresh:
            self.button_refresh = tk.CTkButton(master, text="Refresh", width=50, height=40)
        
        print(self.description + " MyConnectionLine created")
        
    def draw_line(self, row) -> None:
        
        self.row = row
        
        self.label_description.grid(row=self.row, column=0, sticky="w")
        self.optionmenu_parameter.grid(row=self.row, column=1, sticky="w")
        if self.custom:
            self.switch_custom.grid(row=self.row, column=2, sticky="w")
        if self.refresh:
            self.button_refresh.grid(row=self.row, column=3, sticky="w")
            
        print(self.description + " MyConnectionLine drawn")
        
    def toggle_switch_custom(self) -> None:
        if self.switch_custom.get():
            self.entry_custom.grid(row=self.row, column=1, sticky="w")
            self.optionmenu_parameter.grid_forget()
        else:
            self.optionmenu_parameter.grid(row=self.row, column=1, sticky="w")
            self.entry_custom.grid_forget()
            
        print(self.description + " MyConnectionLine switched")

class MyConnectionFrame(tk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master)
        
        self.method = MyConnectionLine(self, "Method", ["RTU", "ASCII", "Binary"], custom=True, refresh=False)
        self.port = MyConnectionLine(self, "Port", ["None"], custom=True, refresh=True)
        self.baudrate = MyConnectionLine(self, "Baudrate", ["9600", "19200", "38400"], custom=True, refresh=False)
        self.databits = MyConnectionLine(self, "Databits", ["8"], custom=True, refresh=False)
        self.parity = MyConnectionLine(self, "Parity", ["None", "Even", "Odd"], custom=True, refresh=False)
        self.stopbits = MyConnectionLine(self, "Stopbits", ["1", "2"], custom=True, refresh=False)
        
        print("MyConnectionFrame created")
        
    def draw_frame(self, row, column) -> None:
        self.grid(row=row, column=column, sticky="w")
        
        self.method.draw_line(row)
        self.port.draw_line(row+1)
        self.baudrate.draw_line(row+2)
        self.databits.draw_line(row+3)
        self.parity.draw_line(row+4)
        self.stopbits.draw_line(row+5)
        
        print("MyConnectionFrame drawn")