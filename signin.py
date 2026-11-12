import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk
import os
from database import authenticate

# Colours
BG_COLOR = "#F0EDE3"
MAROON = "#8F1717"
WHITE = "#FFFFFF"
TEXT_COLOR = "#262626"
LIGHT_GREY = "#888888"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SignInPage(tk.Frame):
    def __init__(self, parent, on_success=None, on_create_account=None, on_home=None,
                 notice=None, admin_mode=False, **kwargs):
        """notice     - banner shown above the form, e.g. "Sign in to book Tiger's Nest"
        admin_mode - open as the separate admin sign-in (no 'Create Account', admins only)"""
        super().__init__(parent, bg=BG_COLOR, **kwargs)
        self.on_success = on_success
        self.on_create_account = on_create_account
        self.on_home = on_home
        self.notice = notice
        self.admin_mode = False

        # ================= HEADER =================
        header = tk.Frame(self, bg=WHITE, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        try:
            logo_image = Image.open(os.path.join(BASE_DIR, "images", "logo.jpg"))
            logo_image = logo_image.resize((75, 55), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            tk.Label(header, image=self.logo_photo, bg=WHITE).pack(side="left", padx=25)
        except Exception:
            tk.Label(header, text="BhutanVoyage", bg=WHITE, fg=MAROON, font=("Georgia", 16, "bold")).pack(side="left", padx=25)

        # Replaced the 4 nav buttons with just the Back arrow
        tk.Button(header, text="← Back to Home", command=self.on_home, 
                  bg=WHITE, fg=MAROON, relief="flat", font=("Helvetica", 11, "bold"), 
                  cursor="hand2").pack(side="left", padx=20)

        # ================= MAIN CONTENT =================
        content = tk.Frame(self, bg=BG_COLOR)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        try:
            mountain_image = Image.open(os.path.join(BASE_DIR, "images", "Mountain.jpg"))
            mountain_image = mountain_image.resize((350, 430), Image.Resampling.LANCZOS)
            self.mountain_photo = ImageTk.PhotoImage(mountain_image)
            tk.Label(content, image=self.mountain_photo, bg=BG_COLOR).grid(row=0, column=0, padx=15, pady=10, sticky="nsew")
        except Exception:
            tk.Label(content, text="[ Mountain Image ]", bg=BG_COLOR, fg=LIGHT_GREY).grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        form = tk.Frame(content, bg=WHITE, highlightbackground="#D6D1C7", highlightthickness=1)
        form.grid(row=0, column=1, padx=15, pady=25, sticky="nsew")

        form_inner = tk.Frame(form, bg=WHITE)
        form_inner.pack(fill="both", expand=True, padx=35, pady=30)

        self.notice_lbl = tk.Label(form_inner, text=notice or "", bg="#FBEDEA", fg=MAROON,
                                   font=("Arial", 11, "bold"), wraplength=300, justify="left",
                                   padx=12, pady=8)
        if notice:
            self.notice_lbl.pack(fill="x", pady=(0, 14))

        self.badge_lbl = tk.Label(form_inner, text="TRAVELLER ACCOUNT", bg=WHITE, fg=MAROON, font=("Arial", 9, "bold"))
        self.badge_lbl.pack(anchor="w", pady=(0, 12))
        tk.Label(form_inner, text="Welcome back.", bg=WHITE, fg=TEXT_COLOR, font=("Georgia", 21)).pack(anchor="w")
        tk.Label(form_inner, text="Sign in to keep your journeys, booking requests, and Bhutan notes in one place.", bg=WHITE, fg=LIGHT_GREY, font=("Arial", 10, "italic"), wraplength=300, justify="left").pack(anchor="w", pady=(12, 25))

        tk.Label(form_inner, text="Email address", bg=WHITE, fg=TEXT_COLOR, font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(0, 6))
        self.email_entry = tk.Entry(form_inner, font=("Arial", 11), relief="solid", bd=1)
        self.email_entry.pack(fill="x", padx=10, ipady=7, pady=(0, 18))

        tk.Label(form_inner, text="Password", bg=WHITE, fg=TEXT_COLOR, font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(0, 6))
        self.password_entry = tk.Entry(form_inner, font=("Arial", 11), show="*", relief="solid", bd=1)
        self.password_entry.pack(fill="x", padx=10, ipady=7, pady=(0, 5))

        self.show_password = tk.BooleanVar(value=False)
        tk.Checkbutton(form_inner, text="Show password", variable=self.show_password, command=self._toggle_password, bg=WHITE, fg=LIGHT_GREY, activebackground=WHITE).pack(anchor="e", padx=10, pady=(0, 15))

        # The button calls self._sign_in (which is correctly defined below)
        tk.Button(form_inner, text="Sign in    →", command=self._sign_in, bg=MAROON, fg=WHITE, activebackground="#701010", activeforeground=WHITE, font=("Arial", 11, "bold"), relief="flat", cursor="hand2").pack(fill="x", padx=10, ipady=8, pady=(0, 15))

        self.account_frame = tk.Frame(form_inner, bg=WHITE)
        self.account_frame.pack()
        tk.Label(self.account_frame, text="New to BhutanVoyage?", bg=WHITE, fg=LIGHT_GREY, font=("Arial", 9)).pack(side="left", padx=(0, 7))
        tk.Button(self.account_frame, text="Create Account", command=self.on_create_account, bg=WHITE, fg=MAROON, font=("Arial", 9, "bold"), relief="flat", cursor="hand2").pack(side="left")

        # ================= FOOTER =================
        footer = tk.Frame(self, bg=MAROON, height=75)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        footer_left = tk.Frame(footer, bg=MAROON)
        footer_left.pack(side="left", padx=25, pady=10)
        tk.Label(footer_left, text="BhutanVoyage", bg=MAROON, fg=WHITE, font=("Georgia", 15, "bold")).pack(anchor="w")
        tk.Label(footer_left, text="Plan Himalayan Dreams, Always.", bg=MAROON, fg="#E8C5BE", font=("Georgia", 9, "italic")).pack(anchor="w")

        tk.Label(footer, text="Made for curious people", bg=MAROON, fg="#E8C5BE", font=("Arial", 10)).pack(side="left", expand=True)

        self.admin_btn = tk.Button(footer, text="Admin Login", command=self._admin_login, bg=MAROON, fg="#F5DEB3", activebackground=MAROON, activeforeground=WHITE, relief="flat", font=("Arial", 10, "bold"), cursor="hand2")
        self.admin_btn.pack(side="right", padx=25)

        if admin_mode:
            self._set_mode(True)

    # --- THESE FUNCTIONS MUST BE INDENTED UNDER THE CLASS ---

    def _toggle_password(self):
        self.password_entry.config(show="" if self.show_password.get() else "*")

    def _sign_in(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showwarning("Missing Info", "Please enter your email and password.")
            return

        user = authenticate(email, password)
        if not user:
            messagebox.showerror("Login Failed", "Invalid email or password.")
            self.password_entry.delete(0, "end")
            return

        if self.admin_mode and user["role"] != "admin":
            messagebox.showerror("Login Failed", "This is not an admin account.")
            self.password_entry.delete(0, "end")
            return
        if not self.admin_mode and user["role"] == "admin":
            messagebox.showerror("Login Failed",
                                 "Admins sign in separately. Use 'Admin Login' at the bottom of the page.")
            self.password_entry.delete(0, "end")
            return

        messagebox.showinfo("Welcome", f"Welcome back, {user['name']}!")
        if callable(self.on_success):
            self.on_success(user)   # main.py sends admins to the Admin Dashboard

    def _admin_login(self):
        """Footer button: switch this form between traveller sign-in and admin sign-in."""
        self._set_mode(not self.admin_mode)

    def _set_mode(self, admin):
        self.admin_mode = admin
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        if admin:
            self.badge_lbl.config(text="ADMIN SIGN-IN")
            self.admin_btn.config(text="Traveller Login")
            self.account_frame.pack_forget()          # admins cannot create accounts here
            self.notice_lbl.pack_forget()
            self.email_entry.insert(0, "admin")
            self.password_entry.focus_set()
        else:
            self.badge_lbl.config(text="TRAVELLER ACCOUNT")
            self.admin_btn.config(text="Admin Login")
            self.account_frame.pack()
            if self.notice:
                self.notice_lbl.pack(fill="x", pady=(0, 14), before=self.badge_lbl)
            self.email_entry.focus_set()
