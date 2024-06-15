import customtkinter as tk

app = tk.CTk()

app.title("Hello World")
app.geometry("400x400")

app.frame1 = tk.CTkFrame(app, fg_color="red")
app.frame1.grid(row=0, column=0)

app.label1 = tk.CTkLabel(app.frame1, text="Hello World")
app.label1.grid(row=0, column=0)
app.label2 = tk.CTkLabel(app.frame1, text="Hello World")
app.label2.grid(row=1, column=0)

app.frame2 = tk.CTkFrame(app, fg_color="blue")
app.frame2.grid(row=0, column=1)

app.label3 = tk.CTkLabel(app.frame2, text="Hello World")
app.label3.grid(row=0, column=0)
app.label4 = tk.CTkLabel(app.frame2, text="Hello World")
app.label4.grid(row=1, column=0)

app.mainloop()