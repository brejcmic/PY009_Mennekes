import customtkinter as ctk

# Create the main application window
app = ctk.CTk()

# Set the window title
app.title("CTk invoke() Example")

# Set the window size
app.geometry("300x200")

# Function to be called when the button is clicked
def on_button_click():
    print("Button clicked!")

# Create a button and bind it to the on_button_click function
button = ctk.CTkButton(app, text="Click Me", command=on_button_click)
button.pack(pady=20)

# Create another button to invoke the first button's command
invoke_button = ctk.CTkButton(app, text="Invoke Click", command=button.invoke)
invoke_button.pack(pady=20)

# Run the application
app.mainloop()
