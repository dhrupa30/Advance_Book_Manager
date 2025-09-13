import tkinter as tk
from tkinter import messagebox
import sqlite3
import os

DB_PATH = os.path.join("database", "books.db")

class LoginWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Admin Login")
        self.configure(bg="#1e1e2f")

        # --- Center the window ---
        width, height = 400, 300
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)

        self.create_ui()

    def create_ui(self):
        tk.Label(
            self, text="Admin Login", bg="#1e1e2f", fg="white",
            font=("Helvetica", 18, "bold")
        ).pack(pady=20)

        tk.Label(self, text="Username", bg="#1e1e2f", fg="white").pack()
        self.username_entry = tk.Entry(self, bg="#40405a", fg="white")
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password", bg="#1e1e2f", fg="white").pack()
        self.password_entry = tk.Entry(self, show="*", bg="#40405a", fg="white")
        self.password_entry.pack(pady=5)

        tk.Button(
            self, text="Login", bg="#3498db", fg="white",
            command=self.check_login
        ).pack(pady=20)

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Error", "All fields are required")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, password)
        )
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == "admin":
            self.destroy()
            self.master.deiconify()
            # lazy import to avoid circular import
            from ui.main_window import MainWindow
            MainWindow(self.master)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")
