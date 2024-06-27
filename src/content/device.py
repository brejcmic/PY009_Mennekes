import content.ports as ports
from content.values import Values

class MyDevice:
    def __init__(self) -> None:
        self.values = Values()
        
    def update(self) -> None:
        self.values.load_csv("resource/data.csv")
