import tkinter as tk
import tkinter.filedialog as filedialog
import device
import func

# variables
ports_usb = func.avalible_ports()
dev = device.Device()

# Root
root = tk.Tk()
root.title("Pymodbus GUI")

# Statue
label_status = tk.Label(root, text="Status:", width=10)
label_status.grid(row=0, column=0)

indicator_status = tk.Label(root, text="Disconnected", width=20, bg="red")
indicator_status.grid(row=0, column=1)

# Method
label_method = tk.Label(root, text="Method:", width=10)
label_method.grid(row=1, column=0)

method_var = tk.StringVar(root)
method_var.set("rtu")  # default value

method_choices = ["rtu", "ascii", "binary"]
option_method = tk.OptionMenu(root, method_var, *method_choices)
option_method.config(width=16)  # Set the width of the option menu
option_method.grid(row=1, column=1)

# Port
label_ports = tk.Label(root, text="Port:", width=10)
label_ports.grid(row=2, column=0)

ports_var = tk.StringVar(root)
ports_var.set(ports_usb[0])  # default value

ports_choices = ports_usb
option_ports = tk.OptionMenu(root, ports_var, *ports_choices)
option_ports.config(width=16)  # Set the width of the option menu
option_ports.grid(row=2, column=1)

# Baudrate
label_baudrate = tk.Label(root, text="Baudrate:", width=10)
label_baudrate.grid(row=3, column=0)

entry_baudrate = tk.Entry(root, width=20)
entry_baudrate.insert(0, "115100")
entry_baudrate.grid(row=3, column=1)

# Bytesize
label_bytesize = tk.Label(root, text="Bytesize:", width=10)
label_bytesize.grid(row=4, column=0)

entry_bytesize = tk.Entry(root, width=20)
entry_bytesize.insert(0, "8")
entry_bytesize.grid(row=4, column=1)

# Parity
# Parity
label_parity = tk.Label(root, text="Parity:", width=10)
label_parity.grid(row=5, column=0)

parity_var = tk.StringVar(root)
parity_var.set("N")  # default value

parity_choices = ["N", "E", "O", "M", "S"]
option_parity = tk.OptionMenu(root, parity_var, *parity_choices)
option_parity.config(width=16)  # Set the width of the option menu
option_parity.grid(row=5, column=1)

# Stopbits
label_stopbits = tk.Label(root, text="Stopbits:", width=10)
label_stopbits.grid(row=6, column=0)

entry_stopbits = tk.Entry(root, width=20)
entry_stopbits.insert(0, "1")
entry_stopbits.grid(row=6, column=1)

# Connect
def connect():
    print("\nConnect device\n.")
    print("└─ Connect")
    print("└─ Method:", method_var.get())
    print("└─ Port:", ports_var.get())
    print("└─ Baudrate:", entry_baudrate.get())
    print("└─ Bytesize:", entry_bytesize.get())
    print("└─ Parity:", parity_var.get())
    print("└─ Stopbits:", entry_stopbits.get())

    dev.connect(
        method=method_var.get(),
        port=ports_var.get(),
        baudrate=int(entry_baudrate.get()),
        bytesize=int(entry_bytesize.get()),
        parity=parity_var.get(),
        stopbits=int(entry_stopbits.get())
    )


button_connect = tk.Button(root, text="Connect", command=connect, width=15)
button_connect.grid(row=7, column=0, columnspan=2)

def disconnect():
    print("\nDisconnect")
    dev.disconnect()

button_discornect = tk.Button(root, text="Disconnect", command=disconnect, width=15)
button_discornect.grid(row=8, column=0, columnspan=2)

func.load_data("coil", 0, 10, "Test", 0, 3, root)

# Update
def update():
    ports_usb = func.avalible_ports()
    func.update_option_menu(option_ports, ports_var, ports_usb)


button_update = tk.Button(root, text="Update", command=update, width=15)
button_update.grid(row=9, column=0, columnspan=2)

def load_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        print("File path:", file_path)

button_load_csv = tk.Button(root, text="Load CSV", command=load_csv, width=15)
button_load_csv.grid(row=10, column=0, columnspan=2)

root.mainloop()
