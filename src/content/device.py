from content.ports import Ports
from content.values import Values

class MyDevice:
    def __init__(self) -> None:
        self.ports = Ports()
        self.values = Values()
        
    def update(self) -> None:
        self.ports.find()
        self.values.load_csv("resource/data.csv")
        
if __name__ == "__main__":
    dev = MyDevice()
    dev.ports.find()
    print(dev.ports.usb)