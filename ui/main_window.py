import tkinter as tk

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Advanced Book Manager - Admin")
        self.root.geometry("1100x650")
        self.root.configure(bg="#ecf0f1")

        # Sidebar
        self.sidebar = tk.Frame(self.root, width=200, bg="#2c3e50")
        self.sidebar.pack(side="left", fill="y")

        self.logo = tk.Label(
            self.sidebar, text="Book Manager", bg="#2c3e50",
            fg="white", font=("Helvetica", 16, "bold")
        )
        self.logo.pack(pady=20)

        # Sidebar buttons
        btn_config = {"bg":"#34495e", "fg":"white", "bd":0, "height":2, "font":("Helvetica", 12)}
        tk.Button(self.sidebar, text="Dashboard", command=self.show_dashboard, **btn_config).pack(fill="x", pady=5, padx=10)
        tk.Button(self.sidebar, text="Books", command=self.show_books, **btn_config).pack(fill="x", pady=5, padx=10)
        tk.Button(self.sidebar, text="Authors", command=self.show_authors, **btn_config).pack(fill="x", pady=5, padx=10)
        tk.Button(self.sidebar, text="Categories", command=self.show_categories, **btn_config).pack(fill="x", pady=5, padx=10)
        tk.Button(self.sidebar, text="Logout", command=self.logout, bg="#e74c3c", fg="white", bd=0, height=2).pack(side="bottom", fill="x", pady=10, padx=10)

        # Container
        self.container = tk.Frame(self.root, bg="#ecf0f1")
        self.container.pack(side="right", fill="both", expand=True)

        # Pages dictionary
        self.pages = {}

        # Show default page
        self.show_dashboard()

    def show_dashboard(self):
        if "Dashboard" not in self.pages:
            from ui.dashboard_page import DashboardPage
            self.pages["Dashboard"] = DashboardPage(self.container)
            self.pages["Dashboard"].place(relx=0, rely=0, relwidth=1, relheight=1)
        else:
            # Refresh counts and pie chart every time
            self.pages["Dashboard"].load_counts()
            self.pages["Dashboard"].load_pie_chart()
        self.pages["Dashboard"].tkraise()

    def show_books(self):
        if "Books" not in self.pages:
            from ui.books_page import BooksPage
            self.pages["Books"] = BooksPage(self.container)
            self.pages["Books"].place(relx=0, rely=0, relwidth=1, relheight=1)
        self.pages["Books"].tkraise()

    def show_authors(self):
        if "Authors" not in self.pages:
            from ui.authors_page import AuthorsPage
            self.pages["Authors"] = AuthorsPage(self.container)
            self.pages["Authors"].place(relx=0, rely=0, relwidth=1, relheight=1)
        self.pages["Authors"].tkraise()

    def show_categories(self):
        if "Categories" not in self.pages:
            from ui.categories_page import CategoriesPage
            self.pages["Categories"] = CategoriesPage(self.container)
            self.pages["Categories"].place(relx=0, rely=0, relwidth=1, relheight=1)
        self.pages["Categories"].tkraise()

    def logout(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
