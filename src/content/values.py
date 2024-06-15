import pandas as pd

class Values:
    def __init__(self) -> None:
        self.data = []
        self.group = []
        self.physical_address = []
        self.logical_address = []
        self.value = []
        self.name = []
        self.description = []
        self.note = []

    def load_csv(self, file_path) -> None:
        self.data = pd.read_csv(file_path, sep=';')
        print(len(self.data))

        self.group = self.data["Group"]
        self.physical_address = self.data["Physical address"]
        self.logical_address = self.data["Logical address"]
        self.value = self.data["Value"]
        self.name = self.data["Name"]
        self.description = self.data["Description"]
        self.note = self.data["Note"]

if __name__ == "__main__":
    dev = Values()
    dev.load_csv("resource/data.csv")