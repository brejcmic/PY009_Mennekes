import tkinter as tk
import serial.tools.list_ports

def update_option_menu(option_menu, variable, new_choices):
    # Clear the old choices
    option_menu['menu'].delete(0, 'end')

    # Set the new choices
    for choice in new_choices:
        option_menu['menu'].add_command(label=choice, command=tk._setit(variable, choice))

    # Set the default choice
    variable.set(new_choices[0] if new_choices else '')

# Find avalible devices connected to the computer
def avalible_ports() -> list:
    print("\nFind avalible ports\n.")
    # Get all connected devices
    ports = serial.tools.list_ports.comports()
    # List of devices
    ports_usb = []

    
    for port in ports:
        if port.device.startswith("/dev/cu.usbserial"):
            print("└─ Found usb-port:", port.device)
            ports_usb.append(port.device.split(" ")[0])
        else:
            print("└─ Unknown port:", port.device)

    if not ports_usb:
        print("└─ !!! No usb-port found !!!")
        ports_usb.append("No usb-port found")

    return ports_usb

def load_data(type: str, address: int, value: int, note: str, row: int, column: int, root: tk.Tk):
    print("\nLoad data\n.")
    print("└─ Type:", type)
    print("└─ Address:", address)
    print("└─ Value:", value)
    print("└─ Note:", note)

    label_type = tk.Label(root, text="Type: " + type)
    label_address = tk.Label(root, text="Address: " + str(address))

    if type == "coil" or type == "discrete":
        label_value = tk.Label(root, text="Value: ")
        entry_value = tk.Entry(root, width=20)
        entry_value.insert(0, str(value))
        entry_value.grid(row=row + 0, column=column + 3)
    else:
        label_value = tk.Label(root, text="Value: " + str(value))

    entry_note = tk.Entry(root, width=20)
    entry_note.insert(0, note)

    label_type.grid(row=row + 0, column= column + 0)
    label_address.grid(row= row + 0, column= column + 1)
    label_value.grid(row= row + 0, column= column + 2)
    entry_note.grid(row= row + 0, column= column + 4)

    

