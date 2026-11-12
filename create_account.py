import tkinter as tk
from tkinter import font, messagebox
import re
from database import register_user, authenticate  # <-- Import the SQLite functions

# ==========================================
# COLOURS
# ==========================================
WHITE = "#FFFFFF"
MAROON = "#7B241C"
DARK_MAROON = "#5C1A14"
TEXT_DARK = "#2C3E50"
TEXT_LIGHT = "#7F8C8D"
MAIN_BG = "#EEEAE0"
ERROR_RED = "#C0392B"

class CreateAccountPage(tk.Frame):
    def __init__(self, parent, on_success=None, on_back=None, **kwargs):
        super().__init__(parent, bg=MAIN_BG, **kwargs)
        self.on_success = on_success
        self.on_back = on_back

        # FONT MOVED INSIDE SO IT DOESN'T CRASH
        font_title = font.Font(family="Georgia", size=22, weight="bold")

        # 1. SCROLLABLE MAIN AREA
        main_area = tk.Frame(self, bg=MAIN_BG)
        main_area.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_area, bg=MAIN_BG, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(main_area, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = tk.Frame(canvas, bg=MAIN_BG)
        window_id = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))

        def on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(-int(event.delta / 120), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # 2. REGISTRATION FORM CARD
        form_card = tk.Frame(
            self.scrollable_frame, bg=WHITE, width=540, height=650,
            highlightbackground="#E5E0D8", highlightthickness=1
        )
        form_card.pack(pady=30)
        form_card.pack_propagate(False)

        # Close button
        tk.Button(
            form_card, text="✖ CLOSE", font=("Helvetica", 8, "bold"),
            bg=WHITE, fg=TEXT_LIGHT, relief="flat", cursor="hand2",
            command=self.on_back
        ).place(relx=0.95, y=18, anchor="ne")

        # Heading
        tk.Label(form_card, text="TRAVELLER ACCOUNT", font=("Helvetica", 9, "bold"), fg=MAROON, bg=WHITE).pack(pady=(42, 7))
        tk.Label(form_card, text="Create Account", font=font_title, fg="#111111", bg=WHITE).pack()
        tk.Label(form_card, text="Join BhutanVoyage and start planning your dream Bhutan adventure!", font=("Helvetica", 9), fg="#222222", bg=WHITE, wraplength=450).pack(pady=(12, 18))

        # 3. INPUT FIELDS
        fields_frame = tk.Frame(form_card, bg=WHITE)
        fields_frame.pack(fill="x", padx=65)

        def create_field(label_text, show=None):
            tk.Label(fields_frame, text=label_text, font=("Helvetica", 9, "bold"), fg="#555555", bg=WHITE).pack(anchor="w", pady=(2, 2))
            entry = tk.Entry(fields_frame, font=("Helvetica", 11), relief="solid", bd=1, show=show)
            entry.pack(fill="x", ipady=3, pady=(0, 5))
            error_label = tk.Label(fields_frame, text="", font=("Helvetica", 8), fg=ERROR_RED, bg=WHITE)
            error_label.pack(anchor="w")
            return entry, error_label

        self.name_entry, self.name_error = create_field("Full Name")
        self.email_entry, self.email_error = create_field("Email Address")
        self.password_entry, self.password_error = create_field("Password", show="*")
        self.confirm_entry, self.confirm_error = create_field("Confirm Password", show="*")

        # 4. TERMS
        self.agree_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            form_card, text="I agree to the Terms of Service and Privacy Policy",
            variable=self.agree_var, font=("Helvetica", 9), fg=TEXT_DARK,
            bg=WHITE, activebackground=WHITE, selectcolor=WHITE, cursor="hand2"
        ).pack(pady=(3, 5))
        
        self.terms_error = tk.Label(form_card, text="", font=("Helvetica", 8), fg=ERROR_RED, bg=WHITE)
        self.terms_error.pack()

        # 5. BUTTONS
        tk.Button(
            form_card, text="Create Account     ✓", font=("Helvetica", 10, "bold"),
            bg=MAROON, fg=WHITE, activebackground=DARK_MAROON, activeforeground=WHITE,
            relief="flat", cursor="hand2", command=self.create_account
        ).pack(fill="x", padx=65, ipady=5, pady=(5, 0))

        login_frame = tk.Frame(form_card, bg=WHITE)
        login_frame.pack(pady=8)
        tk.Label(login_frame, text="Already have an account?", font=("Helvetica", 9), fg=TEXT_LIGHT, bg=WHITE).pack(side="left", padx=3)
        tk.Button(
            login_frame, text="Login here", font=("Helvetica", 9, "bold"),
            fg=MAROON, bg=WHITE, relief="flat", cursor="hand2", command=self.on_back
        ).pack(side="left")

        tk.Button(
            form_card, text="← CLOSE REGISTRATION", font=("Helvetica", 8),
            fg=TEXT_LIGHT, bg=WHITE, relief="flat", cursor="hand2", command=self.on_back
        ).place(relx=0.5, y=620, anchor="center")

    # --- THESE FUNCTIONS MUST BE INDENTED UNDER THE CLASS ---

    def create_account(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_entry.get()

        # Clear errors
        self.name_error.config(text="")
        self.email_error.config(text="")
        self.password_error.config(text="")
        self.confirm_error.config(text="")
        self.terms_error.config(text="")

        valid = True

        if not name:
            self.name_error.config(text="Please enter your full name.")
            valid = False

        if not email:
            self.email_error.config(text="Please enter your email address.")
            valid = False
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            self.email_error.config(text="Please enter a valid email address.")
            valid = False

        if not password:
            self.password_error.config(text="Please enter a password.")
            valid = False
        elif len(password) < 6:
            self.password_error.config(text="Password must contain at least 6 characters.")
            valid = False

        if not confirm_password:
            self.confirm_error.config(text="Please confirm your password.")
            valid = False
        elif password and password != confirm_password:
            self.confirm_error.config(text="Passwords do not match.")
            valid = False

        if not self.agree_var.get():
            self.terms_error.config(text="Please agree to the Terms and Privacy Policy.")
            valid = False

        if not valid:
            return

        # --- SAVE TO SQLITE DATABASE ---
        success, message = register_user(name, email, password)
        
        if success:
            messagebox.showinfo("Success", message)
            if callable(self.on_success):
                # Sign them in right away so a booking they started is not interrupted
                self.on_success(authenticate(email, password))
        else:
            messagebox.showerror("Error", message)
        
            