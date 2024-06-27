import content.ports as ports
from content.values import Values

class MyDevice:
    def __init__(self) -> None:
        self.ports = ports.find()
        self.values = Values()
        
    def update(self) -> None:
        self.ports.find()
        self.values.load_csv("resource/data.csv")
