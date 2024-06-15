import serial.tools.list_ports as lp

class Ports:
    def __init__(self) -> None:
        self.inputs = []
        self.usb = []

    def find(self) -> None:
        self.inputs = lp.comports()
        
        for input in self.inputs:
            if input.device.startswith("/dev/cu.usbserial"):
                self.usb.append(input.device.split(" ")[0])
            
        if not self.usb:
            self.usb.append("No USB port found")