# admin_dashboard.py - Admin dashboard: check payments, confirm or reject bookings
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path
from PIL import Image, ImageTk

from database import (get_all_bookings, get_booking_stats, set_booking_status,
                      change_password)
from booking_utils import format_money

# ---------------- COLOURS ----------------
WHITE = "#FFFFFF"
CREAM = "#F7F2E7"
DARK = "#2C3E50"
GREY = "#7F8C8D"
MAROON = "#7B241C"
DARK_MAROON = "#5C1A14"
SOFT_GOLD = "#F5DEB3"
SOFT_RED = "#E8C5BE"
BORDER = "#E5E0D8"
GREEN = "#27AE60"
GREEN_BG = "#E8F8EF"
ORANGE = "#D35400"
ORANGE_BG = "#FFF3E0"
RED = "#C0392B"
RED_BG = "#FDEDEC"
GREY_BG = "#ECEFF1"

STATUS_STYLE = {
    "Pending":   (ORANGE, ORANGE_BG, "◌"),
    "Confirmed": (GREEN, GREEN_BG, "✓"),
    "Rejected":  (RED, RED_BG, "✕"),
    "Cancelled": (GREY, GREY_BG, "–"),
}
FILTERS = ["All", "Pending", "Confirmed", "Rejected", "Cancelled"]

BASE_DIR = Path(__file__).parent
IMAGE_DIR = BASE_DIR / "images"


class AdminDashboard(tk.Frame):
    def __init__(self, parent, on_logout=None, admin=None, **kwargs):
        super().__init__(parent, bg=CREAM, **kwargs)
        self.on_logout = on_logout
        self.admin = admin or {}
        self.current_filter = "All"
        self.photos = {}

        self._build_scroll_area()
        self._build_header()
        self.dynamic = tk.Frame(self.content, bg=CREAM)   # stats + list, rebuilt on every change
        self.dynamic.pack(fill="x")
        self._build_footer()
        self._refresh()
        self._bind_wheel()

    # ---------------- scrolling ----------------
    def _build_scroll_area(self):
        self.canvas = tk.Canvas(self, bg=CREAM, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(self.canvas, bg=CREAM)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>",
                          lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width))

    def _bind_wheel(self):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.bind_all(seq, self._on_wheel)

    def _on_wheel(self, event):
        try:
            if getattr(event, "num", None) == 4:
                step = -2
            elif getattr(event, "num", None) == 5:
                step = 2
            else:
                step = -2 if event.delta > 0 else 2
            self.canvas.yview_scroll(step, "units")
        except tk.TclError:
            pass

    def destroy(self):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            try:
                self.unbind_all(seq)
            except tk.TclError:
                pass
        super().destroy()

    # ---------------- header ----------------
    def _build_header(self):
        header = tk.Frame(self.content, bg=CREAM)
        header.pack(fill="x", padx=40, pady=(25, 5))
        header.columnconfigure(1, weight=1)

        logo_holder = tk.Frame(header, bg=CREAM)
        logo_holder.grid(row=0, column=0, sticky="w")
        try:
            img = Image.open(IMAGE_DIR / "logo.jpg").convert("RGBA")
            img.thumbnail((48, 48), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.photos["logo"] = photo
            tk.Label(logo_holder, image=photo, bg=CREAM).pack()
        except Exception:
            tk.Label(logo_holder, text="BhutanVoyage", font=("Georgia", 12, "bold"),
                     fg=MAROON, bg=CREAM).pack()

        tk.Label(header, text="ADMIN DASHBOARD", font=("Georgia", 14, "bold"),
                 fg=MAROON, bg=CREAM).grid(row=0, column=1)

        buttons = tk.Frame(header, bg=CREAM)
        buttons.grid(row=0, column=2, sticky="e")
        tk.Button(buttons, text="Change password", command=self._change_password,
                  font=("Helvetica", 10), fg=MAROON, bg=CREAM, relief="flat",
                  cursor="hand2", activebackground=CREAM).pack(side="left", padx=(0, 10))
        tk.Button(buttons, text="→  Sign out",
                  command=self.on_logout if callable(self.on_logout) else None,
                  font=("Georgia", 11, "bold"), fg=WHITE, bg=MAROON, relief="flat",
                  cursor="hand2", activebackground=DARK_MAROON, activeforeground=WHITE,
                  padx=12, pady=3).pack(side="left")

        tk.Label(self.content, text="Check payments and confirm traveller bookings",
                 font=("Georgia", 12), fg=DARK, bg=CREAM).pack(pady=(4, 20))

    # ---------------- stats + filter + list (rebuilt) ----------------
    def _refresh(self):
        for child in self.dynamic.winfo_children():
            child.destroy()
        self.stats = get_booking_stats()
        self._build_stats()
        self._build_booking_list()

    def _build_stats(self):
        wrap = tk.Frame(self.dynamic, bg=CREAM)
        wrap.pack(fill="x", padx=40, pady=(0, 25))

        revenue = "   ".join(format_money(c, a) for c, a in self.stats["revenue"].items() if a) or "Nu. 0"
        cards = [
            (str(self.stats["total"]), "Total bookings"),
            (str(self.stats["Pending"]), "Awaiting confirmation"),
            (str(self.stats["Confirmed"]), "Confirmed"),
            (revenue, "Confirmed revenue"),
        ]
        for col in range(len(cards)):
            wrap.columnconfigure(col, weight=1, uniform="stats")
        for i, (number, label) in enumerate(cards):
            card = tk.Frame(wrap, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            inner = tk.Frame(card, bg=WHITE)
            inner.pack(fill="both", expand=True, padx=16, pady=16)
            size = 20 if len(number) < 8 else 12
            tk.Label(inner, text=number, font=("Georgia", size, "bold"), fg=DARK, bg=WHITE,
                     anchor="w", wraplength=150, justify="left").pack(anchor="w")
            tk.Label(inner, text=label, font=("Helvetica", 10, "bold"), fg=GREY, bg=WHITE,
                     anchor="w").pack(anchor="w", pady=(4, 0))

    def _build_booking_list(self):
        tk.Label(self.dynamic, text="BOOKING MANAGEMENT", font=("Helvetica", 11, "bold"),
                 fg=MAROON, bg=CREAM, anchor="w").pack(fill="x", padx=42, pady=(0, 8))

        bar = tk.Frame(self.dynamic, bg=CREAM)
        bar.pack(fill="x", padx=40, pady=(0, 10))
        for name in FILTERS:
            count = self.stats["total"] if name == "All" else self.stats[name]
            active = (name == self.current_filter)
            tk.Button(bar, text=f"{name} ({count})", command=lambda n=name: self._set_filter(n),
                      font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2",
                      fg=WHITE if active else MAROON, bg=MAROON if active else WHITE,
                      activebackground=DARK_MAROON, activeforeground=WHITE,
                      padx=10, pady=4).pack(side="left", padx=(0, 6))

        card = tk.Frame(self.dynamic, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=40, pady=(0, 25))
        tk.Label(card, text="Traveller Requests", font=("Georgia", 14, "bold"),
                 fg=DARK, bg=WHITE, anchor="w").pack(fill="x", padx=25, pady=(20, 6))

        bookings = get_all_bookings(self.current_filter)
        if not bookings:
            tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=25)
            msg = ("No bookings yet. They will appear here as soon as a traveller submits a payment."
                   if self.current_filter == "All" else f"No {self.current_filter.lower()} bookings.")
            tk.Label(card, text=msg, font=("Helvetica", 11), fg=GREY, bg=WHITE,
                     wraplength=600, justify="left").pack(anchor="w", padx=25, pady=20)
            return
        for i, b in enumerate(bookings):
            self._build_booking_row(card, b, is_last=(i == len(bookings) - 1))

    def _build_booking_row(self, parent, b, is_last=False):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=25)
        row = tk.Frame(parent, bg=WHITE)
        row.pack(fill="x", padx=25, pady=(10, 20 if is_last else 10))
        row.columnconfigure(0, weight=1)

        left = tk.Frame(row, bg=WHITE)
        left.grid(row=0, column=0, sticky="w")

        top = tk.Frame(left, bg=WHITE)
        top.pack(anchor="w")
        tk.Label(top, text=b["traveller_name"], font=("Georgia", 14, "bold"),
                 fg=DARK, bg=WHITE).pack(side="left")
        tk.Label(top, text=f"   {b['reference']}", font=("Helvetica", 9, "bold"),
                 fg=GREY, bg=WHITE).pack(side="left")
        tk.Label(left, text=b["traveller_email"], font=("Helvetica", 10), fg=GREY,
                 bg=WHITE).pack(anchor="w", pady=(2, 6))

        place = b["place"] + (f" ({b['dzongkhag']})" if b["dzongkhag"] else "")
        n = b["travellers"]
        tk.Label(left, text=f"{place}  •  {b['travel_date']}  •  {n} traveller{'s' if n != 1 else ''}",
                 font=("Georgia", 11, "bold"), fg=MAROON, bg=WHITE).pack(anchor="w", pady=(0, 3))
        tk.Label(left, text=f"Package: {b['package'] or '-'}", font=("Helvetica", 10),
                 fg=DARK, bg=WHITE).pack(anchor="w")
        if b.get("notes"):
            tk.Label(left, text=f"Traveller's notes: {b['notes']}", font=("Helvetica", 10),
                     fg=DARK, bg=WHITE, wraplength=520, justify="left").pack(anchor="w")
        tk.Label(left, text=f"Payment: {b['payment_method'] or '-'}   |   Ref: {b['payment_reference'] or '-'}",
                 font=("Helvetica", 10), fg=DARK, bg=WHITE).pack(anchor="w")
        tk.Label(left, text=format_money(b["currency"], b["amount"]), font=("Georgia", 12, "bold"),
                 fg=MAROON, bg=WHITE).pack(anchor="w", pady=(4, 6))

        self._build_status_pill(left, b["status"])
        if b["admin_note"]:
            tk.Label(left, text=f"Note: {b['admin_note']}", font=("Helvetica", 9, "italic"),
                     fg=GREY, bg=WHITE, wraplength=520, justify="left").pack(anchor="w", pady=(4, 0))
        tk.Label(left, text=f"Submitted {b['created_at']}", font=("Helvetica", 8),
                 fg=GREY, bg=WHITE).pack(anchor="w", pady=(4, 0))

        right = tk.Frame(row, bg=WHITE)
        right.grid(row=0, column=1, sticky="ne", padx=(15, 0))
        if b["status"] == "Pending":
            self._action_button(right, "✓  Confirm payment", GREEN, lambda: self._confirm_booking(b))
            self._action_button(right, "✕  Reject", RED, lambda: self._reject_booking(b))
        elif b["status"] == "Confirmed":
            self._action_button(right, "Cancel booking", GREY, lambda: self._cancel_booking(b))

    def _action_button(self, parent, text, colour, command):
        tk.Button(parent, text=text, command=command, bg=colour, fg=WHITE, activebackground=colour,
                  activeforeground=WHITE, relief="flat", cursor="hand2",
                  font=("Helvetica", 10, "bold"), padx=10, pady=5, width=18).pack(pady=3)

    def _build_status_pill(self, parent, status):
        fg, bg, mark = STATUS_STYLE.get(status, (GREY, GREY_BG, "•"))
        pill = tk.Frame(parent, bg=bg)
        pill.pack(anchor="w")
        inner = tk.Frame(pill, bg=bg)
        inner.pack(padx=10, pady=4)
        tk.Label(inner, text=mark, font=("Helvetica", 9, "bold"), fg=fg, bg=bg).pack(side="left", padx=(0, 4))
        tk.Label(inner, text=status, font=("Helvetica", 9, "bold"), fg=fg, bg=bg).pack(side="left")

    # ---------------- actions ----------------
    def _set_filter(self, name):
        self.current_filter = name
        self._refresh()

    def _confirm_booking(self, b):
        if messagebox.askyesno(
                "Confirm payment",
                f"Confirm booking {b['reference']}?\n\n"
                f"Amount: {format_money(b['currency'], b['amount'])}\n"
                f"Payment ref: {b['payment_reference'] or '-'}\n\n"
                "Only confirm after you have seen this payment arrive."):
            set_booking_status(b["id"], "Confirmed")
            self._refresh()

    def _reject_booking(self, b):
        reason = simpledialog.askstring(
            "Reject booking", "Reason (shown to the traveller, optional):", parent=self)
        if reason is None:      # dialog cancelled
            return
        set_booking_status(b["id"], "Rejected", reason)
        self._refresh()

    def _cancel_booking(self, b):
        reason = simpledialog.askstring(
            "Cancel booking", f"Cancel confirmed booking {b['reference']}?\n"
            "Reason (shown to the traveller, optional):", parent=self)
        if reason is None:
            return
        set_booking_status(b["id"], "Cancelled", reason)
        self._refresh()

    def _change_password(self):
        if not self.admin.get("id"):
            messagebox.showerror("Error", "Admin account not found. Please sign in again.")
            return
        old = simpledialog.askstring("Change password", "Current password:", show="*", parent=self)
        if old is None:
            return
        new = simpledialog.askstring("Change password", "New password (at least 8 characters):",
                                     show="*", parent=self)
        if new is None:
            return
        again = simpledialog.askstring("Change password", "Type the new password again:",
                                       show="*", parent=self)
        if again is None:
            return
        if new != again:
            messagebox.showerror("Change password", "The two new passwords do not match.")
            return
        ok, msg = change_password(self.admin["id"], old, new)
        (messagebox.showinfo if ok else messagebox.showerror)("Change password", msg)

    # ---------------- footer ----------------
    def _build_footer(self):
        footer = tk.Frame(self.content, bg=MAROON, height=80)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        tk.Label(footer, text="BhutanVoyage", font=("Georgia", 13, "bold"),
                 bg=MAROON, fg=WHITE).pack(anchor="w", padx=40, pady=(14, 0))
        tk.Label(footer, text="Plan Himalayan Dreams, Always.", font=("Georgia", 9, "italic"),
                 bg=MAROON, fg=SOFT_RED).pack(anchor="w", padx=40)
