import tkinter as tk
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

DB_PATH = "database/books.db"

class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")
        self.pack(fill="both", expand=True)
        self.create_ui()
        self.load_counts()
        self.load_pie_chart()

    def create_ui(self):
        tk.Label(self, text="Dashboard", font=("Arial", 24, "bold"), bg="#ecf0f1").pack(pady=20)
        tk.Label(self, text="Welcome to Advanced Book Collection Manager", bg="#ecf0f1", font=("Arial", 12)).pack(pady=5)

        # Counts Frame
        self.count_frame = tk.Frame(self, bg="#ecf0f1")
        self.count_frame.pack(pady=20, fill="x")

        self.authors_count_label = tk.Label(self.count_frame, text="Authors: 0", font=("Arial", 14, "bold"), bg="#27ae60", fg="white", width=20, height=3)
        self.authors_count_label.pack(side="left", padx=10, pady=5)

        self.books_count_label = tk.Label(self.count_frame, text="Books: 0", font=("Arial", 14, "bold"), bg="#3498db", fg="white", width=20, height=3)
        self.books_count_label.pack(side="left", padx=10, pady=5)

        self.categories_count_label = tk.Label(self.count_frame, text="Categories: 0", font=("Arial", 14, "bold"), bg="#e67e22", fg="white", width=20, height=3)
        self.categories_count_label.pack(side="left", padx=10, pady=5)

        # Pie Chart Frame
        self.chart_frame = tk.Frame(self, bg="#ecf0f1")
        self.chart_frame.pack(pady=20, fill="both", expand=True)

    def load_counts(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM authors")
        authors_count = cursor.fetchone()[0]
        self.authors_count_label.config(text=f"Authors: {authors_count}")

        cursor.execute("SELECT COUNT(*) FROM books")
        books_count = cursor.fetchone()[0]
        self.books_count_label.config(text=f"Books: {books_count}")

        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        self.categories_count_label.config(text=f"Categories: {categories_count}")

        conn.close()

    def load_pie_chart(self):
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT status, COUNT(*) FROM books GROUP BY status")
        data = cursor.fetchall()
        conn.close()

        if data:
            labels = [row[0] for row in data]
            sizes = [row[1] for row in data]

            fig, ax = plt.subplots(figsize=(4,4))
            ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, colors=["#27ae60","#3498db","#e74c3c"])
            ax.axis("equal")

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
