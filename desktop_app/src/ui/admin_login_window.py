import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog

class AdminLoginWindow:
    def __init__(self, parent, api_client):
        self.api_client = api_client
        self.window = tk.Toplevel(parent)
        self.window.title("Admin Login")
        self.window.geometry("300x200")

        tk.Label(self.window, text="Username:").pack(pady=(20, 0))
        self.username_entry = tk.Entry(self.window)
        self.username_entry.pack()

        tk.Label(self.window, text="Password:").pack(pady=(10, 0))
        self.password_entry = tk.Entry(self.window, show="*")
        self.password_entry.pack()

        tk.Button(self.window, text="Login", command=self.login).pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        result = self.api_client.admin_login(username, password)
        if result and result.get("message") == "Admin login successful":
            messagebox.showinfo("Success", "Logged in as admin.")
            self.window.destroy()
            from ui.admin_panel_window import AdminPanelWindow
            AdminPanelWindow(self.window.master, self.api_client)
        else:
            messagebox.showerror("Error", "Invalid admin credentials.") 