# ui/user_dashboard_page.py
import tkinter as tk
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

DB_PATH = os.path.join("database", "books.db")

class UserDashboardPage(tk.Frame):
    def __init__(self, parent, user_id):
        super().__init__(parent, bg="#ecf0f1")
        self.user_id = user_id
        self.pack(fill="both", expand=True)
        self.chart_canvas = None
        self.create_ui()
        self.refresh()

    def create_ui(self):
        tk.Label(self, text="My Dashboard", font=("Arial", 24, "bold"), bg="#ecf0f1").pack(pady=20)
        tk.Label(self, text="Welcome to your personal library", font=("Arial", 12), bg="#ecf0f1").pack(pady=5)

        # Count panel
        self.count_frame = tk.Frame(self, bg="#ecf0f1")
        self.count_frame.pack(pady=20, fill="x")

        self.books_count_label = tk.Label(
            self.count_frame, text="My Books: 0", font=("Arial", 14, "bold"),
            bg="#3498db", fg="white", width=20, height=3
        )
        self.books_count_label.pack(side="left", padx=10, pady=5)

        # Pie chart frame
        self.chart_frame = tk.Frame(self, bg="#ecf0f1")
        self.chart_frame.pack(pady=20, fill="both", expand=True)

    def load_counts(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user_book_status WHERE user_id=?", (self.user_id,))
        books_count = cursor.fetchone()[0] or 0
        conn.close()
        self.books_count_label.config(text=f"My Books: {books_count}")

    def load_pie_chart(self):
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM user_book_status
            WHERE user_id=?
            GROUP BY status
        """, (self.user_id,))
        data = cursor.fetchall()
        conn.close()

        if not data:
            # show empty message
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            tk.Label(self.chart_frame, text="No tracked books yet. Add books from 'My Books'.", bg="#ecf0f1").pack(pady=20)
            return

        labels = [row[0] for row in data]
        sizes = [row[1] for row in data]

        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
        ax.axis("equal")

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def refresh(self):
        self.load_counts()
        self.load_pie_chart()
