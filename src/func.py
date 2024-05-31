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
    # Get all connected devices
    ports = serial.tools.list_ports.comports()
    # List of devices
    ports_usb = []

    
    for port in ports:
        if port.device.startswith("/dev/cu.usbserial"):
            print("Found device:", port.device)
            ports_usb.append(port.device.split(" ")[0])
        else:
            print("Unknown device:", port.device)

    return ports_usb