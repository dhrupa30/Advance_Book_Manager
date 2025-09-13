# view_window.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
import os

DB_PATH = os.path.join("database", "books.db")

class BookDetailWindow(tk.Toplevel):
    def __init__(self, parent, book_id):
        super().__init__(parent)
        self.title("Book Details")
        self.geometry("450x600")
        self.transient(parent)
        self.grab_set()

        self.book_id = book_id
        self.cover_image_label = None

        self.create_ui()
        self.load_book_details()

    def create_ui(self):
        self.title_label = tk.Label(self, text="", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        self.author_label = tk.Label(self, text="", font=("Arial", 12))
        self.author_label.pack(pady=5)

        self.status_label = tk.Label(self, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.categories_label = tk.Label(self, text="", font=("Arial", 12))
        self.categories_label.pack(pady=5)

        tk.Label(self, text="Cover Image:", font=("Arial", 12, "bold")).pack(pady=5)

        self.cover_image_label = tk.Label(self)
        self.cover_image_label.pack(pady=5)

    def load_book_details(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT b.title, a.name, b.status, b.cover_image, GROUP_CONCAT(c.name, ', ')
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            LEFT JOIN book_categories bc ON b.id = bc.book_id
            LEFT JOIN categories c ON bc.category_id = c.id
            WHERE b.id=?
            GROUP BY b.id
        """, (self.book_id,))
        book = cur.fetchone()
        conn.close()

        if not book:
            tk.messagebox.showerror("Error", "Book not found")
            self.destroy()
            return

        title, author, status, cover_path, categories = book

        self.title_label.config(text=title or "N/A")
        self.author_label.config(text=f"Author: {author or 'N/A'}")
        self.status_label.config(text=f"Status: {status or 'N/A'}")
        self.categories_label.config(text=f"Categories: {categories or 'N/A'}")

        # Display cover image
        if cover_path and os.path.exists(cover_path):
            try:
                img = Image.open(cover_path)
                img.thumbnail((250, 350))
                self.cover_img = ImageTk.PhotoImage(img)
                self.cover_image_label.config(image=self.cover_img)
            except Exception as e:
                self.cover_image_label.config(text="Image cannot be opened")
        else:
            self.cover_image_label.config(text="No cover image available")
