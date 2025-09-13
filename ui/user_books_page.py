# ui/user_books_page.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sqlite3
import os

DB_PATH = os.path.join("database", "books.db")

class UserBooksPage(tk.Frame):
    def __init__(self, parent, user_id):
        super().__init__(parent, bg="#ecf0f1")
        self.user_id = user_id
        self.pack(fill="both", expand=True)
        self.create_ui()
        self.load_books()

    def create_ui(self):
        top_frame = tk.Frame(self, bg="#ecf0f1")
        top_frame.pack(fill="x", pady=(10,0))

        tk.Label(self, text="My Books", font=("Arial", 24, "bold"), bg="#ecf0f1").pack(pady=10)

        btn_frame = tk.Frame(top_frame, bg="#ecf0f1")
        btn_frame.pack(side="right", padx=20)
        tk.Button(btn_frame, text="Add Book", command=self.open_add_book_dialog, bg="#2ecc71", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Status", command=self.open_update_status_dialog, bg="#3498db", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_books).pack(side="left", padx=5)

        # Treeview for book list
        self.tree = ttk.Treeview(self, columns=("Title", "Authors", "Status", "Categories"), show="headings", height=15)
        for col in ("Title", "Authors", "Status", "Categories"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

    def load_books(self):
        # clear
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.title,
                   COALESCE(GROUP_CONCAT(DISTINCT a.name), '') AS authors,
                   ubs.status,
                   COALESCE(GROUP_CONCAT(DISTINCT c.name), '') AS categories
            FROM user_book_status ubs
            JOIN books b ON ubs.book_id = b.id
            LEFT JOIN book_authors ba ON b.id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.id
            LEFT JOIN book_categories bc ON b.id = bc.book_id
            LEFT JOIN categories c ON bc.category_id = c.id
            WHERE ubs.user_id = ?
            GROUP BY b.id, ubs.status
            ORDER BY b.title
        """, (self.user_id,))
        rows = cursor.fetchall()
        conn.close()

        for r in rows:
            book_id, title, authors, status, categories = r
            self.tree.insert("", "end", iid=str(book_id), values=(title, authors, status, categories))

    def open_add_book_dialog(self):
        # Show a simple dialog with list of all books not yet added by this user
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title FROM books
            WHERE id NOT IN (SELECT book_id FROM user_book_status WHERE user_id=?)
            ORDER BY title
        """, (self.user_id,))
        available = cursor.fetchall()
        conn.close()

        if not available:
            messagebox.showinfo("Add Book", "No more books available to add.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Add Book")
        dialog.geometry("400x400")
        tk.Label(dialog, text="Select a book to add", font=("Arial", 12)).pack(pady=8)

        lb = tk.Listbox(dialog, width=60, height=15)
        lb.pack(padx=10, pady=10, fill="both", expand=True)
        for b in available:
            lb.insert("end", f"{b[0]}: {b[1]}")

        status_var = tk.StringVar(value="unread")
        tk.Label(dialog, text="Initial status:").pack(pady=(5,0))
        status_menu = ttk.Combobox(dialog, values=['unread','reading','completed','on_hold','dropped'], textvariable=status_var, state="readonly")
        status_menu.pack(pady=5)

        def add_selected():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Add Book", "Please select a book.")
                return
            line = lb.get(sel[0])
            book_id = int(line.split(":")[0])
            status = status_var.get()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_book_status (user_id, book_id, status, started_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (self.user_id, book_id, status))
            conn.commit()
            conn.close()
            dialog.destroy()
            self.load_books()
            messagebox.showinfo("Added", "Book added to your library.")
        tk.Button(dialog, text="Add", command=add_selected, bg="#2ecc71", fg="white").pack(pady=8)

    def open_update_status_dialog(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Update Status", "Select a book in the list first.")
            return
        book_id = int(sel[0])
        current_status = self.tree.item(sel[0])['values'][2]

        dialog = tk.Toplevel(self)
        dialog.title("Update Status")
        dialog.geometry("300x200")
        tk.Label(dialog, text="Update status", font=("Arial", 12)).pack(pady=8)

        status_var = tk.StringVar(value=current_status)
        status_menu = ttk.Combobox(dialog, values=['unread','reading','completed','on_hold','dropped'], textvariable=status_var, state="readonly")
        status_menu.pack(pady=10)

        def save_status():
            new_status = status_var.get()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_book_status
                SET status=?, updated_at=CURRENT_TIMESTAMP,
                    finished_at = CASE WHEN ?='completed' THEN datetime('now') ELSE finished_at END,
                    started_at = CASE WHEN ?='reading' AND started_at IS NULL THEN datetime('now') ELSE started_at END
                WHERE user_id=? AND book_id=?
            """, (new_status, new_status, new_status, self.user_id, book_id))
            conn.commit()
            conn.close()
            dialog.destroy()
            self.load_books()
            messagebox.showinfo("Updated", "Status updated.")
        tk.Button(dialog, text="Save", command=save_status, bg="#3498db", fg="white").pack(pady=10)
