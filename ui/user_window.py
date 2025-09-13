# ui/user_window.py
import tkinter as tk
from ui.user_dashboard_page import UserDashboardPage
from ui.user_books_page import UserBooksPage

class UserWindow:
    def __init__(self, username, user_id):
        self.username = username
        self.user_id = user_id

        self.root = tk.Tk()
        self.root.title(f"User Dashboard - {username}")
        self.root.geometry("1100x650")
        self.root.configure(bg="#ecf0f1")

        # Sidebar
        self.sidebar = tk.Frame(self.root, width=200, bg="#2c3e50")
        self.sidebar.pack(side="left", fill="y")

        tk.Label(
            self.sidebar, text="My Books",
            bg="#2c3e50", fg="white",
            font=("Helvetica", 16, "bold")
        ).pack(pady=20)

        btn_config = {
            "bg":"#34495e", "fg":"white", "bd":0,
            "height":2, "font":("Helvetica", 12)
        }

        # Container for pages
        self.container = tk.Frame(self.root, bg="#ecf0f1")
        self.container.pack(side="right", fill="both", expand=True)

        # Create pages FIRST
        self.dashboard_page = UserDashboardPage(self.container, self.user_id)
        self.dashboard_page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.books_page = UserBooksPage(self.container, self.user_id)
        self.books_page.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Now create buttons (so they can call the pages)
        tk.Button(self.sidebar, text="Dashboard", command=self.show_dashboard, **btn_config).pack(fill="x", pady=5, padx=10)
        tk.Button(self.sidebar, text="My Books", command=self.show_books, **btn_config).pack(fill="x", pady=5, padx=10)
        tk.Button(self.sidebar, text="Logout", command=self.logout,
                  bg="#e74c3c", fg="white", bd=0, height=2).pack(side="bottom", fill="x", pady=10, padx=10)

        # Default page
        self.show_dashboard()

        self.root.mainloop()

    def show_dashboard(self):
        self.dashboard_page.tkraise()
        self.dashboard_page.refresh()

    def show_books(self):
        self.books_page.tkraise()
        self.books_page.load_books()

    def logout(self):
        self.root.destroy()
