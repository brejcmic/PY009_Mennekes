import tkinter as tk
from gui import DeviceCommunacationGUI, DeviceValuesGUI, ParametersGUI
from device import DeviceValues

device_values = DeviceValues()
device_values.read_csv("resource/data.csv")

device_values_gui = []

# Run the GUI
root = tk.Tk()
root.title("Pymodbus GUI")

device_method = DeviceCommunacationGUI(root, "Method", ["RTU", "ASCII", "Binary"], True, False)
device_port = DeviceCommunacationGUI(root, "Port", ["Port1", "Port2"], True, True)
device_baudrate = DeviceCommunacationGUI(root, "Baudrate", ["115100", "9600"], True, False)
device_bytesize = DeviceCommunacationGUI(root, "Bytesize", ["8", "7"], True, False)
device_parity = DeviceCommunacationGUI(root, "Parity", ["None", "Even", "Odd"], True, False)
device_stopbits = DeviceCommunacationGUI(root, "Stopbits", ["1", "2"], True, False)

test0 = ParametersGUI(root, "Group", "Physical address", "Logical address", "Value", "Name", "Description", "Note")

device_method.grid(0, 0)
device_port.grid(1, 0)
device_baudrate.grid(2, 0)
device_bytesize.grid(3, 0)
device_parity.grid(4, 0)
device_stopbits.grid(5, 0)

test0.grid(0, 4)
for i in range(len(device_values.data)):
    device_values_gui.append(DeviceValuesGUI(root, device_values.data_group[i], device_values.data_physical_address[i], device_values.data_logical_address[i], device_values.data_value[i], device_values.data_name[i], device_values.data_description[i], device_values.data_note[i]))
    device_values_gui[i].grid(i + 1, 4)

root.mainloop()