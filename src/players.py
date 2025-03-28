import tkinter as tk
from tkinter import ttk

def on_select(event):
    selected_item = dropdown_var.get()
    print(f"Selected: {selected_item}")

# Create the main window
root = tk.Tk()
root.title("Dropdown Menu Example")

# Create a StringVar to hold the selected value
dropdown_var = tk.StringVar()

# Create a dropdown menu (combobox)
dropdown = ttk.Combobox(root, textvariable=dropdown_var)
dropdown['values'] = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"]
dropdown['state'] = 'readonly'  # Make it read-only
dropdown.pack(pady=20)

# Bind the selection event
dropdown.bind("<<ComboboxSelected>>", on_select)

# Run the application
root.mainloop()