import pandas as pd

class DeviceValues:
    def __init__(self) -> None:
        self.data = []
        self.data_group = []
        self.data_physical_address = []
        self.data_logical_address = []
        self.data_value = []
        self.data_name = []
        self.data_description = []
        self.data_note = []

    def read_csv(self, file_path) -> None:
        self.data = pd.read_csv(file_path, sep=';')
        print(len(self.data))

        self.data_group = self.data["Group"]
        self.data_physical_address = self.data["Physical address"]
        self.data_logical_address = self.data["Logical address"]
        self.data_value = self.data["Value"]
        self.data_name = self.data["Name"]
        self.data_description = self.data["Description"]
        self.data_note = self.data["Note"]

if __name__ == "__main__":
    dev = DeviceValues()
    dev.read_csv("resource/data.csv")