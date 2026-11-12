

#python
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

import sqlite3

from database import (get_user, get_user_bookings, update_profile,
                      get_favourites, add_favourite, remove_favourite,
                      get_bucket_list, add_bucket_item, remove_bucket_item)
from booking_utils import format_money
from catalog import DESTINATIONS, get_destination, destination_label, dzongkhag_of

# ------------------------------------------------------------
# Travel Profile Dashboard
# ------------------------------------------------------------

BG = "#F7F3E9"          # warm cream background
PRIMARY = "#A71920"     # deep red
PRIMARY_DARK = "#86151B"
TEXT = "#242424"
MUTED = "#77736D"
LINE = "#E5DED2"
GREEN = "#2F8A62"
WHITE = "#FFFFFF"
GOLD = "#D8B56D"
ORANGE = "#D35400"
RED = "#C0392B"
STATUS_COLOURS = {"Pending": ORANGE, "Confirmed": GREEN, "Rejected": RED, "Cancelled": MUTED}
STATUS_MARKS = {"Pending": "◌", "Confirmed": "✓", "Rejected": "✕", "Cancelled": "–"}

class UserDashboard(tk.Frame):
    def __init__(self, parent, user=None, on_logout=None, on_home=None, on_booking=None,
                 on_open_detail=None, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self.user = user if user is not None else {}
        self.on_logout = on_logout
        self.on_home = on_home
        self.on_booking = on_booking
        self.on_open_detail = on_open_detail     # called with the destination dict

        record = get_user(self.user.get("id")) if self.user.get("id") else None
        record = record or {}
        member_since = ""
        try:
            member_since = datetime.strptime(record.get("created_at", ""), "%Y-%m-%d %H:%M:%S").strftime("%B %Y")
        except ValueError:
            pass
        self.profile = {
            "Name": record.get("name") or self.user.get("name", ""),
            "Email": record.get("email") or self.user.get("email", ""),
            "Phone": record.get("phone") or "",
            "Member since": member_since,
        }
        self.EDITABLE = ("Name", "Phone")   # email is the login, so it is not editable here
        self.bookings = get_user_bookings(self.user["id"]) if self.user.get("id") else []
        # Both lists are saved in the database (destination keys from catalog.py)
        uid = self.user.get("id")
        self.bucket_items = self._load(get_bucket_list, uid)
        self.favourites = self._load(get_favourites, uid)
        
        self.is_editing = False
        self.entries = {}

        self._setup_styles()
        self._build_page()

    def destroy(self):
        try:
            self.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass
        super().destroy()

    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Red.Horizontal.TProgressbar",
            troughcolor="#F0E8DE",
            background=PRIMARY,
            bordercolor="#F0E8DE",
            lightcolor=PRIMARY,
            darkcolor=PRIMARY,
        )

    def _build_page(self):
        # Scrollable page
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.page = tk.Frame(self.canvas, bg=BG, padx=28, pady=18)
        self.page_window = self.canvas.create_window((0, 0), window=self.page, anchor="nw")
        
        self.page.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.page_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._header()
        self._stats_card()
        self._personal_info_card()
        self._bookings_card()
        self._favourites_card()
        self._bucket_list_card()
        self._footer()

    def _card(self, parent, **kwargs):
        return tk.Frame(parent, bg=WHITE, highlightbackground=LINE, highlightthickness=1, bd=0, **kwargs)

    def _header(self):
        header = tk.Frame(self.page, bg=WHITE, padx=18, pady=12)
        header.pack(fill="x", pady=(0, 16))
        
        # Configure 3 columns: Brand (Left), Spacer (Center), Logout (Right)
        header.columnconfigure(0, weight=0)
        header.columnconfigure(1, weight=1)
        header.columnconfigure(2, weight=0)

        brand = tk.Frame(header, bg=WHITE)
        brand.grid(row=0, column=0, sticky="w")

        tk.Label(brand, text="♧", font=("Georgia", 27, "bold"), fg=PRIMARY, bg=WHITE).pack(side="left", padx=(0, 8))

        brand_text = tk.Frame(brand, bg=WHITE)
        brand_text.pack(side="left")
        tk.Label(brand_text, text="BhutanVoyage", font=("Georgia", 15, "bold"), fg=PRIMARY, bg=WHITE).pack(anchor="w")
        tk.Label(brand_text, text="DISCOVER BHUTAN. EXPERIENCE MORE.", font=("Arial", 7, "bold"), fg=MUTED, bg=WHITE).pack(anchor="w", pady=(2, 0))

        # BIG LOGOUT BUTTON on the far right (Column 2)
        tk.Button(
            header, 
            text="Logout", 
            command=self.on_logout, 
            font=("Helvetica", 14, "bold"),  # Increased font size
            fg=WHITE, 
            bg=PRIMARY, 
            activebackground=PRIMARY_DARK,
            activeforeground=WHITE,
            relief="flat", 
            cursor="hand2",
            padx=20,
            pady=5
        ).grid(row=0, column=2, sticky="e")

        # Welcome Text Below Header
        first = (self.profile["Name"] or "traveller").split()[0]
        self.welcome_lbl = tk.Label(self.page, text=f"Welcome back, {first}!", font=("Arial", 18, "bold"), fg=TEXT, bg=BG)
        self.welcome_lbl.pack(anchor="w")
        tk.Label(self.page, text="Keep exploring. Your next Bhutan story is waiting.", font=("Arial", 10), fg=MUTED, bg=BG).pack(anchor="w", pady=(3, 16))

    def _stats_card(self):
        card = self._card(self.page, padx=16, pady=14)
        card.pack(fill="x", pady=(0, 16))

        top = tk.Frame(card, bg=WHITE)
        top.pack(fill="x", pady=(0, 12))
        tk.Label(top, text="◉  YOUR TRAVEL OVERVIEW", font=("Arial", 9, "bold"), fg=PRIMARY, bg=WHITE).pack(side="left")
        tk.Label(top, text="✦", font=("Arial", 12, "bold"), fg=GOLD, bg=WHITE).pack(side="right")

        count = lambda s: sum(1 for b in self.bookings if b["status"] == s)
        spent = {}
        for b in self.bookings:
            if b["status"] == "Confirmed":
                spent[b["currency"]] = spent.get(b["currency"], 0) + b["amount"]
        spent_text = "  ".join(format_money(c, a) for c, a in spent.items()) or "Nu. 0"
        stats = [(str(len(self.bookings)), "Bookings"), (str(count("Confirmed")), "Confirmed"),
                 (str(count("Pending")), "Awaiting confirmation"), (spent_text, "Total paid (confirmed)")]
        grid = tk.Frame(card, bg=WHITE)
        grid.pack(fill="x")
        for i, (number, label) in enumerate(stats):
            cell = tk.Frame(grid, bg=WHITE, padx=8)
            cell.grid(row=0, column=i, sticky="nsew")
            grid.columnconfigure(i, weight=1)
            if i:
                tk.Frame(cell, bg=LINE, width=1).pack(side="left", fill="y", padx=(0, 10))
            tk.Label(cell, text=number, font=("Arial", 15 if len(number) < 9 else 10, "bold"), fg=TEXT, bg=WHITE, wraplength=120, justify="left").pack(anchor="w")
            tk.Label(cell, text=label, font=("Arial", 8), fg=MUTED, bg=WHITE).pack(anchor="w", pady=(3, 0))

    def _section_title(self, parent, text, icon=""):
        row = tk.Frame(parent, bg=WHITE)
        row.pack(fill="x", pady=(0, 12))
        tk.Label(row, text=f"{icon}  {text}".strip(), font=("Arial", 11, "bold"), fg=TEXT, bg=WHITE).pack(side="left")
        return row

    def _personal_info_card(self):
        self.info_card = self._card(self.page, padx=18, pady=16)
        self.info_card.pack(fill="x", pady=(0, 16))
        self._section_title(self.info_card, "PERSONAL INFO", "♟")

        self.fields_frame = tk.Frame(self.info_card, bg=WHITE)
        self.fields_frame.pack(fill="x")
        
        self.profile_labels = {}
        self.entries = {}

        field_order = ["Name", "Email", "Phone", "Member since"]
        for idx, key in enumerate(field_order):
            row, col = divmod(idx, 2)
            item = tk.Frame(self.fields_frame, bg=WHITE)
            item.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else 16, 8), pady=5)
            self.fields_frame.columnconfigure(col, weight=1)
            
            tk.Label(item, text=key, font=("Arial", 8), fg=MUTED, bg=WHITE).pack(anchor="w")
            
            # Label for viewing (default)
            value = tk.Label(item, text=self.profile[key], font=("Arial", 9), fg=TEXT, bg=WHITE, anchor="w")
            value.pack(fill="x", anchor="w", pady=(3, 4))
            
            # Entry for editing (hidden by default)
            entry = tk.Entry(item, font=("Arial", 9), relief="solid", bd=1, bg="#F8F4EF")
            entry.insert(0, self.profile[key])
            
            tk.Frame(item, bg=LINE, height=1).pack(fill="x")
            
            self.profile_labels[key] = value
            self.entries[key] = entry

        # Edit / Save Button
        self.edit_btn = tk.Button(
            self.info_card, text="Edit Profile", command=self.toggle_edit_profile, 
            font=("Arial", 9, "bold"), fg=WHITE, bg=PRIMARY, activebackground=PRIMARY_DARK, 
            activeforeground=WHITE, bd=0, cursor="hand2", pady=8
        )
        self.edit_btn.pack(fill="x", pady=(12, 5))

    def toggle_edit_profile(self):
        if not self.is_editing:
            self.is_editing = True
            self.edit_btn.config(text="Save Profile", bg=GREEN, activebackground="#226D4C")
            for key in self.EDITABLE:
                self.profile_labels[key].pack_forget()
                self.entries[key].pack(fill="x", anchor="w", pady=(3, 4))
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, self.profile[key])
        else:
            name = self.entries["Name"].get().strip()
            phone = self.entries["Phone"].get().strip()
            if self.user.get("id"):
                ok, msg = update_profile(self.user["id"], name, phone)
                if not ok:
                    messagebox.showerror("Profile", msg)
                    return
                self.user["name"] = name
            self.is_editing = False
            self.edit_btn.config(text="Edit Profile", bg=PRIMARY, activebackground=PRIMARY_DARK)
            self.profile["Name"], self.profile["Phone"] = name, phone
            self.welcome_lbl.config(text=f"Welcome back, {(name.split() or ['traveller'])[0]}!")
            for key in self.EDITABLE:
                self.profile_labels[key].config(text=self.profile[key])
                self.entries[key].pack_forget()
                self.profile_labels[key].pack(fill="x", anchor="w", pady=(3, 4))

    def _bookings_card(self):
        card = self._card(self.page, padx=18, pady=16)
        card.pack(fill="x", pady=(0, 16))
        self._section_title(card, "Bookings", "▣")

        if not self.bookings:
            tk.Label(card, text="You have no bookings yet.", font=("Arial", 9), fg=MUTED, bg=WHITE).pack(anchor="w", pady=(0, 8))
            if callable(self.on_booking):
                tk.Button(card, text="Plan a trip", command=self.on_booking, font=("Arial", 9, "bold"),
                          fg=WHITE, bg=PRIMARY, activebackground=PRIMARY_DARK, activeforeground=WHITE,
                          bd=0, cursor="hand2", padx=14, pady=6).pack(anchor="w")
            return

        for idx, b in enumerate(self.bookings):
            row = tk.Frame(card, bg=WHITE)
            row.pack(fill="x", pady=(2, 8))
            left = tk.Frame(row, bg=WHITE)
            left.pack(side="left", fill="x", expand=True)
            tk.Label(left, text=b["place"], font=("Arial", 9, "bold"), fg=TEXT, bg=WHITE).pack(anchor="w")
            n = b["travellers"]
            tk.Label(left, text=f"{b['travel_date']}  •  {n} traveller{'s' if n != 1 else ''}  •  {b['reference']}",
                     font=("Arial", 8), fg=MUTED, bg=WHITE).pack(anchor="w", pady=(3, 0))
            if b["admin_note"]:
                tk.Label(left, text=f"Note from our team: {b['admin_note']}", font=("Arial", 8, "italic"),
                         fg=MUTED, bg=WHITE, wraplength=380, justify="left").pack(anchor="w", pady=(3, 0))

            right = tk.Frame(row, bg=WHITE)
            right.pack(side="right", anchor="e")
            colour = STATUS_COLOURS.get(b["status"], MUTED)
            tk.Label(right, text=f"{STATUS_MARKS.get(b['status'], '')} {b['status']}", font=("Arial", 8, "bold"),
                     fg=colour, bg=WHITE).pack(anchor="e")
            tk.Label(right, text=format_money(b["currency"], b["amount"]), font=("Arial", 8, "bold"),
                     fg=TEXT, bg=WHITE).pack(anchor="e", pady=(3, 0))

            if idx < len(self.bookings) - 1:
                tk.Frame(card, bg=LINE, height=1).pack(fill="x", pady=(0, 8))

    # ------------------------------------------------------------------
    # Favourites + Bucket list (saved in the database, per signed-in user)
    # ------------------------------------------------------------------
    @staticmethod
    def _load(getter, user_id):
        if not user_id:
            return []
        try:
            return getter(user_id)
        except sqlite3.Error as e:
            print(f"[saved places] could not load: {e}")
            return []

    def _saved_row(self, parent, key, icon, on_remove):
        """One saved place: its name opens the destination page, × removes it."""
        d = get_destination(key)
        row = tk.Frame(parent, bg=WHITE)
        row.pack(fill="x", pady=6)
        if icon:
            tk.Label(row, text=icon, font=("Arial", 10), fg=PRIMARY, bg=WHITE).pack(side="left", padx=(0, 8))
        if d and callable(self.on_open_detail):
            name = tk.Label(row, text=destination_label(d), font=("Arial", 9, "underline"), fg=PRIMARY,
                            bg=WHITE, cursor="hand2")
            name.bind("<Button-1>", lambda _e, dest=d: self.on_open_detail(dest))
        else:
            name = tk.Label(row, text=destination_label(d) if d else key, font=("Arial", 9), fg=TEXT, bg=WHITE)
        name.pack(side="left", anchor="w")
        tk.Frame(row, bg=LINE, height=1).pack(side="left", fill="x", expand=True, padx=(12, 0))
        tk.Button(row, text="×", command=lambda: on_remove(key), font=("Arial", 10), fg=MUTED, bg=WHITE,
                  activebackground=WHITE, bd=0, cursor="hand2").pack(side="right", padx=(6, 0))

    def _pick_destination(self, title, prompt, exclude):
        """Small dialog with a drop-down of the real destinations (minus the ones in `exclude`).
        Returns the chosen destination key, or None if cancelled."""
        # grouped by district (A-Z) so the longer list stays easy to scan
        options = sorted((d for d in DESTINATIONS if d["key"] not in exclude),
                         key=lambda d: (dzongkhag_of(d), d["title"]))
        if not options:
            messagebox.showinfo(title, "You have already added every destination.")
            return None
        labels = [destination_label(d) for d in options]
        result = {"key": None}

        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=WHITE, padx=24, pady=20)
        win.resizable(False, False)
        win.transient(self.winfo_toplevel())

        tk.Label(win, text=prompt, font=("Arial", 10), fg=TEXT, bg=WHITE).pack(anchor="w", pady=(0, 10))
        combo = ttk.Combobox(win, values=labels, state="readonly", width=48, font=("Arial", 10))
        combo.current(0)
        combo.pack(fill="x")

        def choose(_e=None):
            result["key"] = options[combo.current()]["key"]
            win.destroy()

        buttons = tk.Frame(win, bg=WHITE)
        buttons.pack(fill="x", pady=(16, 0))
        tk.Button(buttons, text="Add", command=choose, font=("Arial", 9, "bold"), fg=WHITE, bg=PRIMARY,
                  activebackground=PRIMARY_DARK, activeforeground=WHITE, bd=0, cursor="hand2",
                  padx=18, pady=6).pack(side="right")
        tk.Button(buttons, text="Cancel", command=win.destroy, font=("Arial", 9), fg=MUTED, bg=WHITE,
                  activebackground=WHITE, bd=0, cursor="hand2", padx=12, pady=6).pack(side="right", padx=(0, 8))
        win.bind("<Return>", choose)
        win.bind("<Escape>", lambda _e: win.destroy())

        win.update_idletasks()
        try:      # centre over the window
            top = self.winfo_toplevel()
            x = top.winfo_rootx() + (top.winfo_width() - win.winfo_width()) // 2
            y = top.winfo_rooty() + (top.winfo_height() - win.winfo_height()) // 3
            win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        except tk.TclError:
            pass
        win.grab_set()
        combo.focus_set()
        self.wait_window(win)
        return result["key"]

    def _save_error(self, e):
        messagebox.showerror("Could not save", f"Your change could not be saved: {e}")

    # ---------------- Favourites ----------------
    def _favourites_card(self):
        card = self._card(self.page, padx=18, pady=16)
        card.pack(fill="x", pady=(0, 16))
        self._section_title(card, "Favourites", "♥")

        self.fav_frame = tk.Frame(card, bg=WHITE)
        self.fav_frame.pack(fill="x")
        self._refresh_favourites()

        tk.Button(card, text="+ Add Favourite", command=self.add_favourite, font=("Arial", 9, "bold"), fg=PRIMARY, bg=WHITE, activebackground="#F8F4EF", bd=0, cursor="hand2", pady=8).pack(anchor="w", pady=(4, 0))

    def _refresh_favourites(self):
        for child in self.fav_frame.winfo_children(): child.destroy()
        if not self.favourites:
            tk.Label(self.fav_frame, text="No favourites yet. Tap the heart on a destination, or add one here!", font=("Arial", 9, "italic"), fg=MUTED, bg=WHITE).pack(anchor="w", pady=6)
            return
        for key in self.favourites:
            self._saved_row(self.fav_frame, key, "♥", self.remove_favourite)

    def add_favourite(self):
        uid = self.user.get("id")
        if not uid:
            return
        key = self._pick_destination("Add Favourite", "Choose a place you love:", self.favourites)
        if not key:
            return
        try:
            add_favourite(uid, key)
        except sqlite3.Error as e:
            self._save_error(e)
            return
        self.favourites = self._load(get_favourites, uid)
        self._refresh_favourites()

    def remove_favourite(self, key):
        d = get_destination(key)
        if messagebox.askyesno("Remove Favourite", f"Remove '{destination_label(d) if d else key}' from your favourites?"):
            try:
                remove_favourite(self.user["id"], key)
            except sqlite3.Error as e:
                self._save_error(e)
                return
            self.favourites = self._load(get_favourites, self.user.get("id"))
            self._refresh_favourites()

    # ---------------- Bucket list ----------------
    def _bucket_list_card(self):
        card = self._card(self.page, padx=18, pady=16)
        card.pack(fill="x", pady=(0, 16))
        self._section_title(card, "Bucket List", "♡")
        self.bucket_frame = tk.Frame(card, bg=WHITE)
        self.bucket_frame.pack(fill="x")
        self._refresh_bucket_list()

        tk.Button(card, text="+ Add Item", command=self.add_bucket_item, font=("Arial", 9, "bold"), fg=PRIMARY, bg=WHITE, activebackground="#F8F4EF", bd=0, cursor="hand2", pady=8).pack(anchor="w", pady=(4, 0))

    def _refresh_bucket_list(self):
        for child in self.bucket_frame.winfo_children(): child.destroy()
        if not self.bucket_items:
            tk.Label(self.bucket_frame, text="Your bucket list is empty. Add a place you dream of visiting!", font=("Arial", 9, "italic"), fg=MUTED, bg=WHITE).pack(anchor="w", pady=6)
            return
        for key in self.bucket_items:
            self._saved_row(self.bucket_frame, key, "", self.remove_bucket_item)

    def add_bucket_item(self):
        uid = self.user.get("id")
        if not uid:
            return
        key = self._pick_destination("Add to Bucket List", "Choose a place you want to visit:", self.bucket_items)
        if not key:
            return
        try:
            add_bucket_item(uid, key)
        except sqlite3.Error as e:
            self._save_error(e)
            return
        self.bucket_items = self._load(get_bucket_list, uid)
        self._refresh_bucket_list()

    def remove_bucket_item(self, key):
        d = get_destination(key)
        if messagebox.askyesno("Remove Item", f"Remove '{destination_label(d) if d else key}' from your bucket list?"):
            try:
                remove_bucket_item(self.user["id"], key)
            except sqlite3.Error as e:
                self._save_error(e)
                return
            self.bucket_items = self._load(get_bucket_list, self.user.get("id"))
            self._refresh_bucket_list()

    def _footer(self):
        footer = tk.Frame(self.page, bg=PRIMARY, height=80, padx=18, pady=10)
        footer.pack(fill="x", pady=(0, 8))
        footer.pack_propagate(False)

        tk.Label(footer, text="BhutanVoyage", font=("Georgia", 13, "bold"), bg=PRIMARY, fg=WHITE).pack(anchor="w")
        tk.Label(footer, text="Plan Himalayan Dreams, Always.", font=("Georgia", 8, "italic"), bg=PRIMARY, fg="#E8C5BE").pack(anchor="w", pady=(2, 0))
