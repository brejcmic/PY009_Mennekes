import tkinter as tk

root = tk.Tk()

# Create a canvas

label = tk.Label(root, text="Label 0")
label.grid(row=0, column=0)

canvas = tk.Canvas(root)

# Create a scrollbar
scrollbar = tk.Scrollbar(root, command=canvas.yview)

# Configure the canvas to use the scrollbar

# Create a frame inside the canvas
frame = tk.Frame(canvas)
canvas.create_window((100, 100), window=frame, anchor='nw')  # Specify the desired coordinates here

canvas.grid(row=1, column=0, sticky='nsew')
scrollbar.grid(row=1, column=1, sticky='ns')
canvas.configure(yscrollcommand=scrollbar.set)
# Add some labels and entries to the frame
for i in range(100):
    label = tk.Label(frame, text=f"Label {i}")
    label.grid(row=i, column=0)
    entry = tk.Entry(frame)
    entry.grid(row=i, column=1)

# Update the scroll region of the canvas
frame.update()
canvas.configure(scrollregion=canvas.bbox('all'))

# Function to scroll the canvas with the mouse wheel
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Bind the mouse wheel to the function
canvas.bind_all("<MouseWheel>", on_mousewheel)

root.mainloop()
