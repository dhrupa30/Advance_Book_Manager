import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

DB_PATH = os.path.join("database", "books.db")

class CategoriesPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f8f9fa")
        self.selected_category_id = None
        self.create_ui()
        self.load_categories()

    def create_ui(self):
        tk.Label(self, text="Categories Management", bg="#f8f9fa", font=("Arial", 18, "bold")).pack(pady=15)

        self.tree = ttk.Treeview(self, columns=("ID","Name"), show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.column("Name", width=200)
        self.tree.pack(pady=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        btn_frame = tk.Frame(self, bg="#f8f9fa")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Category", bg="#2ecc71", fg="white", command=self.add_category).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit Category", bg="#f1c40f", fg="white", command=self.edit_category).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Category", bg="#e74c3c", fg="white", command=self.delete_category).pack(side="left", padx=5)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_category_id = self.tree.item(selected[0])["values"][0]

    def load_categories(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories")
        for c in cursor.fetchall():
            self.tree.insert("", "end", values=c)
        conn.close()

    def add_category(self):
        self.category_form()

    def edit_category(self):
        if not self.selected_category_id:
            messagebox.showwarning("Warning", "Select a category")
            return
        self.category_form(self.selected_category_id)

    def category_form(self, category_id=None):
        win = tk.Toplevel(self)
        win.title("Category Form")
        win.geometry("350x150")
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Category Name").pack(pady=5)
        name_entry = tk.Entry(win, width=40)
        name_entry.pack(pady=5)

        if category_id:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories WHERE id=?", (category_id,))
            r = cursor.fetchone()
            conn.close()
            if r:
                name_entry.insert(0, r[0])

        def save_category():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name required")
                return
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if category_id:
                cursor.execute("UPDATE categories SET name=? WHERE id=?", (name, category_id))
            else:
                cursor.execute("INSERT INTO categories(name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            win.destroy()
            self.load_categories()

        tk.Button(win, text="Save", bg="#2ecc71", fg="white", command=save_category).pack(pady=15)

    def delete_category(self):
        if not self.selected_category_id:
            messagebox.showwarning("Warning", "Select a category")
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure?"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id=?", (self.selected_category_id,))
            conn.commit()
            conn.close()
            self.selected_category_id = None
            self.load_categories()
