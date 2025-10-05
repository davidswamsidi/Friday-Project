#!/usr/bin/env python3
# Customer Information Management System
# Tkinter GUI + SQLite with simple validation

import sqlite3
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DB_PATH = "customers.db"

# -------------------------
# Database Setup
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birthday TEXT NOT NULL,             -- YYYY-MM-DD
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            preferred_contact TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

# -------------------------
# Validation Helpers
# -------------------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_name(name: str) -> bool:
    return len(name.strip()) > 0

def validate_birthday(bday: str) -> bool:
    try:
        datetime.strptime(bday.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip()))

def validate_phone(phone: str) -> bool:
    # allow digits, spaces, dashes, parentheses, plus
    digits = re.sub(r"\D", "", phone)
    return len(digits) >= 10

def validate_address(addr: str) -> bool:
    return len(addr.strip()) > 0

def validate_preferred_contact(choice: str) -> bool:
    return choice in ("Email", "Phone", "Mail")

def validate_all(fields: dict) -> tuple[bool, str]:
    # fields keys: name, birthday, email, phone, address, preferred_contact
    if not validate_name(fields["name"]):
        return False, "Please enter the customer's name."
    if not validate_birthday(fields["birthday"]):
        return False, "Birthday must be in YYYY-MM-DD format (e.g., 2001-09-15)."
    if not validate_email(fields["email"]):
        return False, "Please enter a valid email address."
    if not validate_phone(fields["phone"]):
        return False, "Please enter a valid phone number with at least 10 digits."
    if not validate_address(fields["address"]):
        return False, "Please enter the address."
    if not validate_preferred_contact(fields["preferred_contact"]):
        return False, "Please choose a preferred contact method."
    return True, ""

# -------------------------
# Persistence
# -------------------------
def insert_customer(fields: dict) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO customers (name, birthday, email, phone, address, preferred_contact)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            fields["name"].strip(),
            fields["birthday"].strip(),
            fields["email"].strip(),
            fields["phone"].strip(),
            fields["address"].strip(),
            fields["preferred_contact"],
        ),
    )
    conn.commit()
    conn.close()

# -------------------------
# GUI
# -------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Customer Information Management System")
        self.geometry("560x520")
        self.resizable(False, False)

        # Root container
        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(
            container,
            text="Enter Customer Information",
            font=("Segoe UI", 14, "bold")
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 12), sticky="w")

        # Name
        ttk.Label(container, text="Full Name *").grid(row=1, column=0, sticky="e", padx=(0, 10), pady=6)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(container, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=1, column=1, sticky="w", pady=6)

        # Birthday
        ttk.Label(container, text="Birthday (YYYY-MM-DD) *").grid(row=2, column=0, sticky="e", padx=(0, 10), pady=6)
        self.bday_var = tk.StringVar()
        self.bday_entry = ttk.Entry(container, textvariable=self.bday_var, width=20)
        self.bday_entry.grid(row=2, column=1, sticky="w", pady=6)

        # Email
        ttk.Label(container, text="Email *").grid(row=3, column=0, sticky="e", padx=(0, 10), pady=6)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(container, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=3, column=1, sticky="w", pady=6)

        # Phone
        ttk.Label(container, text="Phone *").grid(row=4, column=0, sticky="e", padx=(0, 10), pady=6)
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(container, textvariable=self.phone_var, width=28)
        self.phone_entry.grid(row=4, column=1, sticky="w", pady=6)

        # Address (multiline)
        ttk.Label(container, text="Address *").grid(row=5, column=0, sticky="ne", padx=(0, 10), pady=6)
        self.address_text = tk.Text(container, width=40, height=5, wrap="word")
        self.address_text.grid(row=5, column=1, sticky="w", pady=6)

        # Preferred Contact
        ttk.Label(container, text="Preferred Contact *").grid(row=6, column=0, sticky="e", padx=(0, 10), pady=6)
        self.pref_var = tk.StringVar()
        self.pref_combo = ttk.Combobox(
            container,
            textvariable=self.pref_var,
            values=["Email", "Phone", "Mail"],
            state="readonly",
            width=18
        )
        self.pref_combo.grid(row=6, column=1, sticky="w", pady=6)
        self.pref_combo.set("Email")

        # Buttons
        btns = ttk.Frame(container)
        btns.grid(row=7, column=0, columnspan=2, pady=16)

        submit_btn = ttk.Button(btns, text="Submit", command=self.on_submit)
        submit_btn.grid(row=0, column=0, padx=6)

        clear_btn = ttk.Button(btns, text="Clear Form", command=self.clear_form)
        clear_btn.grid(row=0, column=1, padx=6)

        # Status hint
        hint = ttk.Label(
            container,
            text="Fields marked * are required.",
            foreground="#666"
        )
        hint.grid(row=8, column=0, columnspan=2, sticky="w")

        # Grid tuning
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)

        # Focus first field
        self.name_entry.focus_set()

    def get_form_data(self) -> dict:
        return {
            "name": self.name_var.get(),
            "birthday": self.bday_var.get(),
            "email": self.email_var.get(),
            "phone": self.phone_var.get(),
            "address": self.address_text.get("1.0", "end").strip(),
            "preferred_contact": self.pref_var.get(),
        }

    def clear_form(self):
        self.name_var.set("")
        self.bday_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.address_text.delete("1.0", "end")
        self.pref_combo.set("Email")
        self.name_entry.focus_set()

    def on_submit(self):
        data = self.get_form_data()
        valid, msg = validate_all(data)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return

        try:
            insert_customer(data)
            messagebox.showinfo("Success", "Customer information saved.")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save data:\n{e}")

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()