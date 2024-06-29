import customtkinter as tk

class MyValuesLine:
    def __init__(self, master, group: str, physical_address: str, logical_address: str, value: str, name: str, description: str, note: str) -> None:
        self.group = group
        self.physical_address = physical_address
        self.logical_address = logical_address
        self.value = value
        self.name = name
        self.description = description
        self.note = note
        
        self.label_group = tk.CTkLabel(master, text=self.group, width=75)
        self.label_physical_address = tk.CTkLabel(master, text=self.physical_address, width=50)
        self.label_logical_address = tk.CTkLabel(master, text=self.logical_address, width=50)
        
        if self.group == "Coil" or self.group == "Holding register":
            self.entry_value = tk.CTkEntry(master, width=100, placeholder_text=self.value)
        else:
            self.label_value = tk.CTkLabel(master, text=self.value, width=100)
            
        self.entry_name = tk.CTkEntry(master, placeholder_text=self.name, width=175)
        self.entry_description = tk.CTkEntry(master, placeholder_text=self.description, width=400)
        self.entry_note = tk.CTkEntry(master, placeholder_text=self.note, width=100)
        
        print(self.group + " MyValuesLine created")
        
    def draw_line(self, row) -> None:
        self.row = row
        
        self.label_group.grid(row=self.row, column=0, sticky="w")
        self.label_physical_address.grid(row=self.row, column=1, sticky="w")
        self.label_logical_address.grid(row=self.row, column=2, sticky="w")
        
        if self.group == "Coil" or self.group == "Holding register":
            self.entry_value.grid(row=self.row, column=3, sticky="w")
        else:
            self.label_value.grid(row=self.row, column=3, sticky="w")
        
        self.entry_name.grid(row=self.row, column=4, sticky="w")
        self.entry_description.grid(row=self.row, column=5, sticky="w")
        self.entry_note.grid(row=self.row, column=6, sticky="w")
        
        print(self.group + " MyValuesLine drawn")
        
    def update(self, value) -> None:
        self.value = value
        
        if self.group == "Coil" or self.group == "Holding register":
            self.entry_value.configure(placeholder_text=self.value)
        else:
            self.label_value.configure(text=self.value)
            
        print("MyValuesScrollableFrame updated")
        
    def get(self) -> dict:
        values = {
            "group": self.group,
            "physical_address": self.physical_address,
            "logical_address": self.logical_address,
            "value": self.value,
            "name": self.entry_name.get(),
            "description": self.entry_description.get(),
            "note": self.entry_note.get()
        }
        
        if self.group == "Coil" or self.group == "Holding register":
            values["value"] = self.entry_value.get()
        
        return values
class MyValuesScrollableFrame(tk.CTkScrollableFrame):
    def __init__(self, master, data, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.data = data
        self.lines = []
        
        for i in range(len(self.data["group"])):
            line = MyValuesLine(
                self,
                self.data["group"][i],
                self.data["physical_address"][i],
                self.data["logical_address"][i],
                self.data["value"][i],
                self.data["name"][i],
                self.data["description"][i],
                self.data["note"][i]
            )
            
            self.lines.append(line)
    
    def draw_frame(self, row, column) -> None:
        self.grid(row=row, column=column, sticky="w")
        
        for i in range(len(self.lines)):
            self.lines[i].draw_line(i)
        
        print("MyValuesScrollableFrame created")
        
    def update_values(self, values) -> None:
        for i in range(len(values)):
            self.lines[i].update(value=values[i])
            
        print("MyValuesScrollableFrame updated")
        
    def get_values(self) -> dict:
        values = []
        
        for i in range(len(self.lines)):
            values.append(self.lines[i].get())
        
        return values