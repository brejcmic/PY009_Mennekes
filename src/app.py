import customtkinter as tk

from layout.uiconnection import MyConnectionFrame
from layout.uivalues import MyValuesScrollableFrame
from layout.uicontrol import MyControlFrame

from content.device import MyDevice

device = MyDevice()
device.update()

app = tk.CTk()

app.title("Diagnostic Tool")
app.geometry("1310x270")

frame1 = tk.CTkFrame(app)
frame1.grid(row=0, column=0)

frame2 = tk.CTkFrame(app)
frame2.grid(row=1, column=0)

app.control_frame = MyControlFrame(frame1)
app.control_frame.draw_frame(row=1, column=0)

app.connection_frame = MyConnectionFrame(frame2)
app.connection_frame.draw_frame(row=0, column=0)

app.values_frame = MyValuesScrollableFrame(frame2, device.values, width=950, height=230)
app.values_frame.draw_frame(row=0, column=1)

app.mainloop()