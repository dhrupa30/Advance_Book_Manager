# main.py
import tkinter as tk
from login_choice import choose_login  # Separate module to avoid circular imports

# Create root (main window, hidden at first)
root = tk.Tk()
root.withdraw()  # Hide root window

# Open login choice window
choose_login()

# Start Tkinter loop
root.mainloop()
