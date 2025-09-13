import tkinter as tk

def choose_login():
    window = tk.Toplevel()
    window.title("Login Choice")
    window.configure(bg="#1e1e2f")

    # Desired size
    width, height = 400, 250   # you can adjust for "small" or "large"

    # Center on screen
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

    def open_admin():
        window.destroy()
        from ui.login_window import LoginWindow
        root = tk.Tk()
        root.withdraw()
        LoginWindow(root)
        root.mainloop()

    def open_user():
        window.destroy()
        from ui.user_login_window import UserLoginWindow
        root = tk.Tk()
        root.withdraw()
        UserLoginWindow(root)
        root.mainloop()

    tk.Label(window, text="Login as:", fg="white", bg="#1e1e2f", font=("Helvetica", 16)).pack(pady=20)
    tk.Button(window, text="Admin", width=15, command=open_admin).pack(pady=10)
    tk.Button(window, text="User", width=15, command=open_user).pack(pady=10)
