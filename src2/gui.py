import tkinter as tk

class DeviceCommunacationGUI:
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
    def __init__(
        self, 
        root: tk.Tk,
        group: str,
        physical_address: int,
        logical_address: int,
        value: int,
        name: str,
        description: str,
        note: str
    ) -> None:
        
        self.root = root
        self.group = group
        self.physical_address = physical_address
        self.logical_address = logical_address
        self.value = value
        self.name = name
        self.description = description
        self.note = note

        self.label_group = tk.Label(self.root, text=self.group)
        self.label_physical_address = tk.Label(self.root, text=str(self.physical_address))
        self.label_logical_address = tk.Label(self.root, text=str(self.logical_address))

        if self.group == "Coil" or self.group == "Holding register":
            self.entry_value = tk.Entry(self.root, width=20)
            self.entry_value.insert(0, str(self.value))
        else:
            self.label_value = tk.Label(self.root, text=str(self.value))

        self.entry_name = tk.Entry(self.root, width=20)
        self.entry_name.insert(0, self.name)
        self.entry_description = tk.Entry(self.root, width=20)
        self.entry_description.insert(0, self.description)
        self.entry_note = tk.Entry(self.root, width=20)
        self.entry_note.insert(0, self.note)


    def grid(self, row: int, column: int) -> None:
        self.row = row
        self.column = column

        self.label_group.grid(row=row, column=column)
        self.label_physical_address.grid(row=row, column=column + 1)
        self.label_logical_address.grid(row=row, column=column + 2)
        
        if self.group == "Coil" or self.group == "Holding register":
            self.entry_value.grid(row=row, column=column + 3)
        else:
            self.label_value.grid(row=row, column=column + 3)

        self.entry_name.grid(row=row, column=column + 4)
        self.entry_description.grid(row=row, column=column + 5)
        self.entry_note.grid(row=row, column=column + 6)

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
