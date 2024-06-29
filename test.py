import customtkinter as ctk
from time import sleep

# Create the main application window
app = ctk.CTk()

# Set the window title
app.title("CTk OptionMenu Example")

# Set the window size
app.geometry("400x300")

# Define a list of options for the OptionMenu
options = ["Option 1", "Option 2", "Option 3"]

# Variable to store the selected option
selected_option = ctk.StringVar(app)
selected_option.set(options[0])  # Set default value

# Function to print the selected option
def print_selected_option():
    print("Selected Option:", selected_option.get())

# Create the OptionMenu
option_menu = ctk.CTkOptionMenu(app, variable=selected_option, values=options)
option_menu.pack(pady=20)

# Create a button to print the selected option
print_button = ctk.CTkButton(app, text="Print Selected Option", command=print_selected_option)
print_button.pack(pady=10)

# Run the application
app.mainloop()
