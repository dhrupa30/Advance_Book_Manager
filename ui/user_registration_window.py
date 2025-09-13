import tkinter as tk
from tkinter import messagebox
import sqlite3
import os

DB_PATH = os.path.join("database", "books.db")

class UserRegisterWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("User Registration")
        self.geometry("400x400")
        self.configure(bg="#1e1e2f")
        self.create_ui()

    def create_ui(self):
        tk.Label(self, text="User Registration", bg="#1e1e2f", fg="white", font=("Helvetica", 18, "bold")).pack(pady=20)

        tk.Label(self, text="Username", bg="#1e1e2f", fg="white").pack()
        self.username_entry = tk.Entry(self, bg="#40405a", fg="white")
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password", bg="#1e1e2f", fg="white").pack()
        self.password_entry = tk.Entry(self, show="*", bg="#40405a", fg="white")
        self.password_entry.pack(pady=5)

        tk.Label(self, text="Confirm Password", bg="#1e1e2f", fg="white").pack()
        self.confirm_entry = tk.Entry(self, show="*", bg="#40405a", fg="white")
        self.confirm_entry.pack(pady=5)

        tk.Button(self, text="Register", bg="#27ae60", fg="white", width=15, command=self.register_user).pack(pady=20)
        tk.Button(self, text="Cancel", bg="#e74c3c", fg="white", width=15, command=self.cancel).pack()

    def register_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if not username or not password or not confirm:
            messagebox.showwarning("Error", "All fields are required")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            conn.close()
            return

        cursor.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)", (username, password, "user"))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Registration successful! Please login.")
        # Return to login with username pre-filled
        self.master.deiconify()  # show login window
        self.master.username_entry.delete(0, tk.END)
        self.master.username_entry.insert(0, username)
        self.destroy()

    def cancel(self):
        self.master.deiconify()  # show login window
        self.destroy()
