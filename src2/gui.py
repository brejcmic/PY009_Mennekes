import tkinter as tk

class DeviceCommunicationGUI:
    # Class for the device communication GUI
    def __init__(self, root: tk.Tk, description: str, parameters: list, custom: bool, refresh: bool) -> None:
        self.root = root
        self.description = description
        self.parameters = parameters
        self.custom = custom
        self.refresh = refresh

        # Description of the communication possibilities
        self.label_description = tk.Label(root, text=description, width=10)

        # Selection of the possible parameters
        self.default_parameter = tk.StringVar(root)
        if parameters:
            self.default_parameter.set(parameters[0])
        else:
            self.default_parameter.set("NaN")

        self.parameter_choices = parameters
        self.option_parameters = tk.OptionMenu(root, self.default_parameter, *self.parameter_choices)
        self.option_parameters.config(width=16)

        # Custom parameter - Entry
        if self.custom:
            self.entry_parameter = tk.Entry(root, width=20)
            self.entry_parameter.insert(0, "Custom")

        # Switch for custom parameter
        if self.custom:
            self.switch_var = tk.BooleanVar()
            self.switch_var.set(False)
            self.switch = tk.Checkbutton(root, text="Custom", variable=self.switch_var, command=lambda: self.switch_custom(self.switch_var))

        # Button for refresh [Toggle]
        if self.refresh:
            self.button_refresh = tk.Button(root, text="Refresh")

    def grid(self, row: int, column: int) -> None:
        self.row = row
        self.column = column
        # Grid the elements
        self.label_description.grid(row=row, column=column)
        self.option_parameters.grid(row=row, column=column + 1)
        if self.custom:
            self.switch.grid(row=row, column=column + 2)
        if self.refresh:
            self.button_refresh.grid(row=row, column=column + 3)

    def switch_custom(self, switch_var: tk.BooleanVar) -> None:
        print("Device parameter: [" + self.description + "] mod: -> ", end="")
        # Update the switch
        if switch_var.get():
            print("Custom")
            self.entry_parameter.grid(row=self.row + 0, column=self.column + 1)
            self.option_parameters.grid_remove()
        else:
            print("Options")
            self.entry_parameter.grid_remove()  # Hide the entry_parameter widget
            self.option_parameters.grid(row=self.row + 0, column=self.column + 1)

class DeviceValuesGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.frame= root

    def add(
        self, 
        group: list,
        physical_address: list,
        logical_address: list,
        value: list,
        name: list,
        description: list,
        note: list
    ) -> None:
        
        self.group = group
        self.physical_address = physical_address
        self.logical_address = logical_address
        self.value = value
        self.name = name
        self.description = description
        self.note = note

        self.label_group = []
        self.label_physical_address = []
        self.label_logical_address = []
        self.label_value = []
        self.entry_value = []
        self.entry_name = []
        self.entry_description = []
        self.entry_note = []
        
        for i in range(len(self.group)):
            self.label_group.append(tk.Label(self.frame, text=self.group[i]))
            self.label_physical_address.append(tk.Label(self.frame, text=str(self.physical_address[i])))
            self.label_logical_address.append(tk.Label(self.frame, text=str(self.logical_address[i])))

            if self.group[i] == "Coil" or self.group[i] == "Holding register":
                self.entry_value.append(tk.Entry(self.frame, width=20))
                self.label_value.append(tk.Label(self.frame, text="NaN"))
                self.entry_value[i].insert(0, str(self.value[i]))
            else:
                self.label_value.append(tk.Label(self.frame, text=str(self.value[i])))
                self.entry_value.append(tk.Entry(self.frame, width=20))

            self.entry_name.append(tk.Entry(self.frame, width=20))
            self.entry_name[i].insert(0, self.name[i])
            self.entry_description.append(tk.Entry(self.frame, width=40))
            self.entry_description[i].insert(0, self.description[i])
            self.entry_note.append(tk.Entry(self.frame, width=20))
            self.entry_note[i].insert(0, self.note[i])

    def grid(self, row: int, column: int) -> None:
        self.row = row
        self.column = column

        for i in range(len(self.group)):
            self.label_group[i].grid(row=row + i, column=column)
            self.label_physical_address[i].grid(row=row + i, column=column + 1)
            self.label_logical_address[i].grid(row=row + i, column=column + 2)

            if self.group[i] == "Coil" or self.group[i] == "Holding register":
                self.entry_value[i].grid(row=row + i, column=column + 3)
            else:
                self.label_value[i].grid(row=row + i, column=column + 3)

            self.entry_name[i].grid(row=row + i, column=column + 4)
            self.entry_description[i].grid(row=row + i, column=column + 5)
            self.entry_note[i].grid(row=row + i, column=column + 6)

class ParametersGUI:
    def __init__(self, root: tk.Tk, *argv: str) -> None:
        self.root = root
        self.argv = argv

        self.label_arg = []

        for arg in argv:
            self.label_arg.append(tk.Label(root, text=arg))

    def grid(self, row: int, column: int) -> None:
        self.row = row
        self.column = column

        for i in range(len(self.label_arg)):
            self.label_arg[i].grid(row=row, column=column + i)
