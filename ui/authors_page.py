# ui/authors_page.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

DB_PATH = os.path.join("database", "books.db")

class AuthorsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f8f9fa")
        self.selected_author_id = None
        print("[DEBUG] AuthorsPage loaded")
        self.create_ui()
        self.load_authors()

    def create_ui(self):
        # Title
        tk.Label(self, text="Authors Management", bg="#f8f9fa",
                 font=("Arial", 18, "bold")).grid(row=0, column=0, pady=15, sticky="n")

        # Authors Treeview
        self.tree = ttk.Treeview(self, columns=("ID", "Name"), show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=250, anchor="w")
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Button Frame
        btn_frame = tk.Frame(self, bg="#f8f9fa")
        btn_frame.grid(row=2, column=0, pady=10)

        tk.Button(btn_frame, text="Add Author", bg="#2ecc71", fg="white",
                  command=self.add_author).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit Author", bg="#f1c40f", fg="white",
                  command=self.edit_author).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Author", bg="#e74c3c", fg="white",
                  command=self.delete_author).pack(side="left", padx=5)

        # Allow resizing
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_author_id = self.tree.item(selected[0])["values"][0]

    def load_authors(self):
        # Clear old data
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Load from DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM authors ORDER BY id ASC")
        for a in cursor.fetchall():
            self.tree.insert("", "end", values=a)
        conn.close()

    def add_author(self):
        self.author_form()

    def edit_author(self):
        if not self.selected_author_id:
            messagebox.showwarning("Warning", "Select an author first")
            return
        self.author_form(self.selected_author_id)

    def author_form(self, author_id=None):
        win = tk.Toplevel(self)
        win.title("Author Form")
        win.geometry("350x200")
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Name").pack(pady=5)
        name_entry = tk.Entry(win, width=40)
        name_entry.pack(pady=5)

        if author_id:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM authors WHERE id=?", (author_id,))
            r = cursor.fetchone()
            conn.close()
            if r:
                name_entry.insert(0, r[0])

        def save_author():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if author_id:
                cursor.execute("UPDATE authors SET name=? WHERE id=?", (name, author_id))
            else:
                cursor.execute("INSERT INTO authors(name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            win.destroy()
            self.load_authors()

        tk.Button(win, text="Save", bg="#2ecc71", fg="white",
                  command=save_author).pack(pady=15)

    def delete_author(self):
        if not self.selected_author_id:
            messagebox.showwarning("Warning", "Select an author first")
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this author?"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM authors WHERE id=?", (self.selected_author_id,))
            conn.commit()
            conn.close()
            self.selected_author_id = None
            self.load_authors()
