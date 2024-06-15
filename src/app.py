import customtkinter as tk

from layout.uiconnection import MyConnectionFrame

class App(tk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Diagnostic Tool")
        self.geometry("800x600")
        
        self.connection_frame = MyConnectionFrame(self)
        self.connection_frame.draw_frame(row=0)