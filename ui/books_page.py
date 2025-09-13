# ui/books_page.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os
import shutil
from PIL import Image, ImageTk

DB_PATH = os.path.join("database", "books.db")
IMAGES_DIR = os.path.join(os.getcwd(), "images")
os.makedirs(IMAGES_DIR, exist_ok=True)


class BooksPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")
        self.image_cache = {}          # keep PhotoImage references keyed by iid
        self.search_var = tk.StringVar()
        self.search_entry = None       # keep reference to entry
        self._last_loaded_books = []   # keep last fetched list (tuples)
        self.create_ui()
        self.load_books()

    def create_ui(self):
        # Title row
        title = tk.Label(self, text="Books Management", bg="#ecf0f1", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))

        # Search row
        search_frame = tk.Frame(self, bg="#ecf0f1")
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))
        tk.Label(search_frame, text="Search:", bg="#ecf0f1").pack(side="left", padx=(0, 6))

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side="left", padx=(0, 6))
        self.search_entry.bind("<Return>", lambda e: self.search_books())

        tk.Button(search_frame, text="Go", command=self.search_books, bg="#2980b9", fg="white", width=8).pack(side="left")
        tk.Button(search_frame, text="Clear", command=self.clear_search, bg="#7f8c8d", fg="white", width=8).pack(side="left", padx=(6, 0))

        # Status label
        self.status_label = tk.Label(self, text="", bg="#ecf0f1", anchor="w")
        self.status_label.grid(row=1, column=1, sticky="w", padx=(6, 10))

        # Grid configuration
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tree container
        tree_frame = tk.Frame(self, bg="#ecf0f1")
        tree_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 6))

        style = ttk.Style(self)
        style.configure("Treeview", rowheight=84)

        self.tree = ttk.Treeview(tree_frame, columns=("Title", "Author", "Status", "Categories"), show=("tree", "headings"))
        self.tree.heading("#0", text="Cover")
        self.tree.column("#0", width=90, anchor="center", stretch=False)
        self.tree.heading("Title", text="Title")
        self.tree.column("Title", width=260, anchor="w")
        self.tree.heading("Author", text="Author")
        self.tree.column("Author", width=180, anchor="w")
        self.tree.heading("Status", text="Status")
        self.tree.column("Status", width=120, anchor="center")
        self.tree.heading("Categories", text="Categories")
        self.tree.column("Categories", width=260, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Buttons row
        btn_frame = tk.Frame(self, bg="#ecf0f1")
        btn_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(6, 12))
        tk.Button(btn_frame, text="Add Book", command=self.open_book_form, bg="#27ae60", fg="white", width=12).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Edit Book", command=self.edit_book, bg="#3498db", fg="white", width=12).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Delete Book", command=self.delete_book, bg="#e74c3c", fg="white", width=12).pack(side="left", padx=8)

    # DB fetch
    def _fetch_all_books(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                b.id,
                b.title,
                COALESCE(a_direct.name, GROUP_CONCAT(DISTINCT a_join.name)) AS author,
                b.status,
                COALESCE(GROUP_CONCAT(DISTINCT c.name), '') AS categories,
                b.cover_image
            FROM books b
            LEFT JOIN authors a_direct ON b.author_id = a_direct.id
            LEFT JOIN book_authors ba ON b.id = ba.book_id
            LEFT JOIN authors a_join ON ba.author_id = a_join.id
            LEFT JOIN book_categories bc ON b.id = bc.book_id
            LEFT JOIN categories c ON bc.category_id = c.id
            GROUP BY b.id
            ORDER BY b.id
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    def load_books(self):
        books = self._fetch_all_books()
        self._last_loaded_books = books
        self.populate_tree(books)
        self.status_label.config(text=f"Results: {len(books)}")
        print(f"[DEBUG] load_books: {len(books)} rows")

    def populate_tree(self, books):
        for r in self.tree.get_children():
            self.tree.delete(r)
        self.image_cache.clear()

        for book in books:
            raw_id, raw_title, raw_author, raw_status, raw_categories, cover_path = book
            iid = str(raw_id)
            title = str(raw_title or "")
            author = str(raw_author or "")
            status = str(raw_status or "")
            categories = str(raw_categories or "")

            img_tk = None
            if cover_path:
                try:
                    if os.path.exists(cover_path):
                        pil_img = Image.open(cover_path).resize((60, 84))
                        img_tk = ImageTk.PhotoImage(pil_img, master=self.tree)
                        self.image_cache[iid] = img_tk
                except Exception as e:
                    print(f"[books_page] Error loading image {cover_path}: {e}")

            insert_opts = {"text": "", "values": (title, author, status, categories)}
            if img_tk:
                insert_opts["image"] = img_tk
            self.tree.insert("", "end", iid=iid, **insert_opts)

    # ✅ Fixed search method
    def search_books(self):
        q = self.search_var.get().strip()
        if not q and self.search_entry:
            q = self.search_entry.get().strip()

        print(f"[DEBUG] search invoked. query='{q}'")
        if not q:
            self.load_books()
            return

        q = q.lower()
        all_books = self._fetch_all_books()
        filtered = []

        for book in all_books:
            book_id, title, author, status, categories, cover = book
            combined = " ".join([str(title or ""), str(author or ""), str(status or ""), str(categories or "")]).lower()
            if q in combined:
                filtered.append(book)

        self.populate_tree(filtered)
        if filtered:
            self.status_label.config(text=f"Results: {len(filtered)} (filtered)")
        else:
            self.status_label.config(text="Results: 0")
            messagebox.showinfo("No Results", f"No books found matching '{q}'.")

    def clear_search(self):
        self.search_var.set("")
        if self.search_entry:
            self.search_entry.delete(0, tk.END)
        self.load_books()

    # CRUD (edit/delete/add) methods stay same...
    def edit_book(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a book to edit")
            return
        self.open_book_form(book_id=selected)

    def delete_book(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a book to delete")
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure?"):
            return
        book_id = selected
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM book_categories WHERE book_id=?", (book_id,))
        cursor.execute("DELETE FROM book_authors WHERE book_id=?", (book_id,))
        cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        conn.close()
        self.load_books()

    # Add/edit form (kept same)
   
    def open_book_form(self, book_id=None):
    
          
            
        form = tk.Toplevel(self)
        form.title("Add / Edit Book")
        form.geometry("400x550")
        form.resizable(False, False)

        # Title
        tk.Label(form, text="Title:").pack(pady=5)
        title_entry = tk.Entry(form, width=40)
        title_entry.pack(pady=5)

        # Status
        tk.Label(form, text="Status:").pack(pady=5)
        status_cb = ttk.Combobox(
            form,
            values=["Available", "Reading", "Checked Out"],
            state="readonly",
            width=37
        )
        status_cb.pack(pady=5)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Author (single select dropdown)
        tk.Label(form, text="Select Author:").pack(pady=5)
        cur.execute("SELECT id, name FROM authors ORDER BY name")
        authors = cur.fetchall()
        author_cb = ttk.Combobox(form, values=[a[1] for a in authors], state="readonly", width=37)
        author_cb.pack(pady=5)

        # Categories (multi-select listbox)
        tk.Label(form, text="Select Categories:").pack(pady=5)
        cur.execute("SELECT id, name FROM categories ORDER BY name")
        categories = cur.fetchall()
        category_listbox = tk.Listbox(form, selectmode="multiple", width=40, height=6, exportselection=False)
        category_listbox.pack(pady=5)
        for idx, (_, name) in enumerate(categories):
            category_listbox.insert(idx, name)

        # Cover image
        tk.Label(form, text="Cover Image:").pack(pady=5)
        cover_label = tk.Label(form, text="No Image Selected", bg="#ddd", width=30, height=10)
        cover_label.pack(pady=5)
        cover_path_var = tk.StringVar()

        def upload_image():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
            )
            if file_path:
                img = Image.open(file_path).resize((100, 140))
                img_tk = ImageTk.PhotoImage(img, master=form)   # ✅ bind to form
                cover_label.config(image=img_tk, text="")
                cover_label.image = img_tk   # ✅ keep reference
                # copy to images folder
                new_path = os.path.join(IMAGES_DIR, os.path.basename(file_path))
                shutil.copy(file_path, new_path)
                cover_path_var.set(new_path)

        tk.Button(form, text="Upload Image", command=upload_image, bg="#3498db", fg="white").pack(pady=5)

        # If editing, load existing values
        if book_id:
            cur.execute("SELECT title, status, author_id, cover_image FROM books WHERE id=?", (book_id,))
            row = cur.fetchone()
            if row:
                title_entry.insert(0, row[0])
                status_cb.set(row[1])

                # Author
                for idx, (aid, name) in enumerate(authors):
                    if aid == row[2]:
                        author_cb.current(idx)

                # Cover
                if row[3] and os.path.exists(row[3]):
                    img = Image.open(row[3]).resize((100, 140))
                    img_tk = ImageTk.PhotoImage(img, master=form)
                    cover_label.config(image=img_tk, text="")
                    cover_label.image = img_tk
                    cover_path_var.set(row[3])

            # Load categories
            cur.execute("""
                SELECT c.id FROM categories c
                JOIN book_categories bc ON c.id = bc.category_id
                WHERE bc.book_id=?
            """, (book_id,))
            category_ids = {r[0] for r in cur.fetchall()}
            for idx, (cid, _) in enumerate(categories):
                if cid in category_ids:
                    category_listbox.selection_set(idx)

        conn.close()

        # Save handler
        def save_book():
            nonlocal book_id   # ✅ fix scope issue
            title = title_entry.get().strip()
            status = status_cb.get().strip()
            cover_path = cover_path_var.get()
            author_idx = author_cb.current()

            if not title or not status or author_idx == -1:
                messagebox.showwarning("Validation", "Title, Status and Author are required!")
                return

            author_id = authors[author_idx][0]

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            if book_id:  # update
                cur.execute(
                    "UPDATE books SET title=?, status=?, author_id=?, cover_image=? WHERE id=?",
                    (title, status, author_id, cover_path, book_id)
                )
                cur.execute("DELETE FROM book_categories WHERE book_id=?", (book_id,))
            else:  # insert new
                cur.execute(
                    "INSERT INTO books (title, status, author_id, cover_image) VALUES (?, ?, ?, ?)",
                    (title, status, author_id, cover_path)
                )
                book_id = cur.lastrowid

            # Save selected categories
            selected_categories = category_listbox.curselection()
            for idx in selected_categories:
                cid = categories[idx][0]
                cur.execute("INSERT INTO book_categories (book_id, category_id) VALUES (?, ?)", (book_id, cid))

            conn.commit()
            conn.close()

            self.load_books()
            form.destroy()

        # ✅ Save button at bottom
        tk.Button(
            form,
            text="Save",
            command=save_book,
            bg="#27ae60",
            fg="white",
            width=15
        ).pack(pady=15)
