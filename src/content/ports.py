import serial.tools.list_ports as lp

def update_ports(option_menu) -> None:
    inputs = lp.comports()
    usb = []
    
    for input in inputs:
        if input.device.startswith("/dev/cu.usbserial"):
            usb.append(input.device.replace("/dev/cu.usbserial-", ""))
            
    option_menu.configure(values=usb)
    
    print("Ports updated")