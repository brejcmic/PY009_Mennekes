import tkinter as tk
from gui import DeviceCommunicationGUI, DeviceValuesGUI, ParametersGUI
from device import DeviceValues

device_values = DeviceValues()
device_values.read_csv("resource/data.csv")

device_values_gui = []

# Run the GUI
root = tk.Tk()
root.title("Pymodbus GUI")

device_method = DeviceCommunicationGUI(root, "Method", ["RTU", "ASCII", "Binary"], True, False)
device_port = DeviceCommunicationGUI(root, "Port", ["Port1", "Port2"], True, True)
device_baudrate = DeviceCommunicationGUI(root, "Baudrate", ["115100", "9600"], True, False)
device_bytesize = DeviceCommunicationGUI(root, "Bytesize", ["8", "7"], True, False)
device_parity = DeviceCommunicationGUI(root, "Parity", ["None", "Even", "Odd"], True, False)
device_stopbits = DeviceCommunicationGUI(root, "Stopbits", ["1", "2"], True, False)

test0 = ParametersGUI(root, "Group", "Physical address", "Logical address", "Value", "Name", "Description", "Note")
device_values_gui = DeviceValuesGUI(root)

device_method.grid(0, 0)
device_port.grid(1, 0)
device_baudrate.grid(2, 0)
device_bytesize.grid(3, 0)
device_parity.grid(4, 0)
device_stopbits.grid(5, 0)

test0.grid(0, 4)
device_values_gui.add(device_values.data_group, device_values.data_physical_address, device_values.data_logical_address, device_values.data_value, device_values.data_name, device_values.data_description, device_values.data_note)
device_values_gui.grid(1, 4)

root.mainloop()