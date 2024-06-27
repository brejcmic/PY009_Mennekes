import serial.tools.list_ports as lp

def find() -> list:
    inputs = lp.comports()
    usb = []
    
    for input in inputs:
        if input.device.startswith("/dev/cu.usbserial"):
            usb.append(input.device.split(" ")[0])
            
    if usb:
        return usb  
    else:
        return