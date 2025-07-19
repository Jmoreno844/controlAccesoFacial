import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

class AdminPanelWindow:
    def __init__(self, parent, api_client):
        self.api_client = api_client
        self.window = tk.Toplevel(parent)
        self.window.title("Admin Panel")
        self.window.geometry("800x600")

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True)

        # Users tab
        self.users_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.users_frame, text="Users")
        self.setup_users_tab()

        # Logs tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        self.setup_logs_tab()

    def setup_users_tab(self):
        columns = ("id", "name", "rfid_card_id", "role")
        self.tree = ttk.Treeview(self.users_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

        btn_frame = ttk.Frame(self.users_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_users).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edit RFID", command=self.edit_rfid).pack(side="left", padx=5)

        self.load_users()

    def load_users(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        users = self.api_client.get_users()
        if users is None:
            messagebox.showerror("Error", "Failed to load users.")
            return
        for user in users:
            self.tree.insert("", "end", values=(
                user.get("id"), user.get("name"), user.get("rfid_card_id", ""), user.get("role")
            ))

    def edit_rfid(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No user selected.")
            return
        item = selected[0]
        user_id, name, current_rfid, role = self.tree.item(item, "values")
        new_rfid = simpledialog.askstring("Edit RFID", f"Enter new RFID for {name}:", initialvalue=current_rfid)
        if new_rfid is None:
            return
        result = self.api_client.update_user(int(user_id), new_rfid)
        if result:
            messagebox.showinfo("Success", f"RFID updated for {name}.")
            self.load_users()
        else:
            messagebox.showerror("Error", f"Failed to update RFID for {name}.")

    def setup_logs_tab(self):
        columns = ("id", "user_id", "event_type", "details", "timestamp")
        self.logs_tree = ttk.Treeview(self.logs_frame, columns=columns, show="headings")
        for col in columns:
            self.logs_tree.heading(col, text=col.capitalize())
            self.logs_tree.column(col, width=150)
        self.logs_tree.pack(fill="both", expand=True)

        btn_frame = ttk.Frame(self.logs_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_logs).pack(side="left", padx=5)

        self.load_logs()

    def load_logs(self):
        for row in self.logs_tree.get_children():
            self.logs_tree.delete(row)
        logs = self.api_client.get_logs()
        if logs is None:
            messagebox.showerror("Error", "Failed to load logs.")
            return
        for log in logs:
            self.logs_tree.insert("", "end", values=(
                log.get("id"), log.get("user_id"), log.get("event_type"), log.get("details", ""), log.get("timestamp")
            )) 