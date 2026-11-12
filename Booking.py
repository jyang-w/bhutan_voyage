import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import date, datetime
import calendar
import os
from PIL import Image, ImageTk

from catalog import get_destination, dzongkhag_of, places_in, DZONGKHAG_LIST
from pricing import price_per_person, BHUTANESE, INTERNATIONAL
from booking_utils import (TRAVELLER_CHOICES, parse_travellers, travellers_label,
                           validate_traveller_details, format_money)

# --- Shared branding constants ---
MAROON = "#7B241C"
TEXT_DARK = "#2C3E50"
FOOTER_TEXT_SOFT = "#E6B0AA"
FOOTER_ADMIN = "#F5DEB3"

# Booking-page specific colors
DARK = "#252525"
MUTED = "#777777"
PAGE_BG = "#F7F5F0"
BORDER = "#D7D4CF"
WHITE = "#FFFFFF"
TOTAL_BG = "#FBF3EF"

CHOOSE_DISTRICT = "Choose a district..."
CHOOSE_PLACE = "Choose a place..."
CHOOSE_PLACE_FIRST = "Choose a district first"


class BookingPage(tk.Frame):
    """The ONE booking form.

    Reached from a destination's "Book Now" (place already chosen) or from the Booking menu.
    The price comes from catalog.py, so the traveller never re-picks a trip on the payment page.

    preselect : destination key (e.g. "paro") to have chosen already
    prefill   : the dict this page produced earlier - used when the traveller comes back from
                the payment page so nothing they typed is lost
    """

    def __init__(self, parent, on_home=None, on_destination=None, on_about=None, on_payment=None,
                 on_admin=None, user=None, preselect=None, prefill=None, **kwargs):
        super().__init__(parent, bg=PAGE_BG, **kwargs)
        self.user = user or {}
        self.on_home = on_home
        self.on_destination = on_destination
        self.on_about = on_about
        self.on_payment = on_payment
        self.on_admin = on_admin
        self.prefill = prefill or {}

        start = get_destination(self.prefill.get("dest_key") or preselect)
        # Two steps: the district first, then a place inside it (about 80 places would be too long for one list).
        # dest_var holds the chosen place's title (unique inside a district).
        self.district_var = tk.StringVar(value=dzongkhag_of(start) if start else CHOOSE_DISTRICT)
        self.dest_var = tk.StringVar(value=start["title"] if start else CHOOSE_PLACE_FIRST)
        self.travellers = tk.StringVar(
            value=travellers_label(int(self.prefill["travellers"])) if self.prefill.get("travellers")
            else travellers_label(2))
        self.residency = tk.StringVar(value=self.prefill.get("residency") or BHUTANESE)

        self.font_nav = font.Font(family="Georgia", size=12)
        self.font_button = font.Font(family="Georgia", size=11, weight="bold")
        self.font_footer_brand = font.Font(family="Georgia", size=15, weight="bold")
        self.font_footer_sub = font.Font(family="Georgia", size=10, slant="italic")
        self.font_footer_tag = font.Font(family="Helvetica", size=10)
        self.font_footer_admin = font.Font(family="Helvetica", size=10, weight="bold")

        self._build_page()
        self._prefill_fields()
        for var in (self.dest_var, self.travellers, self.residency):
            var.trace_add("write", self._refresh_total)
        self.district_var.trace_add("write", self._on_district_change)
        self._set_place_choices()
        self._refresh_total()

    # ------------------------------------------------------------------ scrolling
    def _on_mousewheel(self, event):
        if self.winfo_exists() and self.canvas.winfo_exists():
            if event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")

    def _bind_wheel(self, _event=None):
        if self.winfo_exists():
            self.bind_all("<MouseWheel>", self._on_mousewheel)
            self.bind_all("<Button-4>", self._on_mousewheel)
            self.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_wheel(self, _event=None):
        try:
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
        except Exception:
            pass

    def _on_canvas_resize(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)
        # keep the form a comfortable width and centred on wide windows
        side = max(24, (event.width - 780) // 2)
        self.card.pack_configure(padx=side)

    # ------------------------------------------------------------------ page
    def _build_page(self):
        self.canvas = tk.Canvas(self, bg=PAGE_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.page = tk.Frame(self.canvas, bg=PAGE_BG)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.page, anchor="n")
        self.page.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.bind("<Enter>", self._bind_wheel)
        self.bind("<Leave>", self._unbind_wheel)

        self._build_header()
        self._build_form()
        self._build_footer()

    def _build_header(self):
        header = tk.Frame(self.page, bg="white", height=90)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        header.columnconfigure(0, weight=0)
        header.columnconfigure(1, weight=1)
        header.columnconfigure(2, weight=0)

        try:
            logo_pil = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "logo.jpg"))
            logo_pil.thumbnail((140, 50))
            self.logo_tk = ImageTk.PhotoImage(logo_pil)
        except Exception:
            self.logo_tk = None
        if self.logo_tk is not None:
            logo = tk.Label(header, image=self.logo_tk, bg="white", cursor="hand2")
            logo.image = self.logo_tk
        else:
            logo = tk.Label(header, text="BhutanVoyage", bg="white", fg=MAROON,
                            font=("Georgia", 16, "bold"), cursor="hand2")
        logo.grid(row=0, column=0, sticky="w", padx=30, pady=15)
        logo.bind("<Button-1>", lambda _e: self.on_home() if callable(self.on_home) else None)

        nav_frame = tk.Frame(header, bg="white")
        nav_frame.grid(row=0, column=1, sticky="ew")
        nav_inner = tk.Frame(nav_frame, bg="white")
        nav_inner.pack(expand=True)
        for item, cb in (("Home", self.on_home), ("Destination", self.on_destination),
                         ("Booking", None), ("About us", self.on_about)):
            lbl = tk.Label(nav_inner, text=item, font=self.font_nav,
                           fg=MAROON if item == "Booking" else TEXT_DARK, bg="white",
                           cursor="hand2" if cb else "arrow")
            lbl.pack(side="left", padx=25)
            if cb:
                lbl.bind("<Button-1>", lambda _e, c=cb: c())

        tk.Button(header, text="Plan Your Trip", command=self.on_destination if callable(self.on_destination) else None,
                  bg=MAROON, fg="white", font=self.font_button, relief="flat", padx=22, pady=10, cursor="hand2",
                  activebackground="#5C1A14", activeforeground="white").grid(row=0, column=2, sticky="e", padx=30, pady=15)

    def _label(self, parent, text, pady=(10, 4)):
        tk.Label(parent, text=text, bg=WHITE, fg=DARK, font=("Arial", 9, "bold")).pack(anchor="w", pady=pady)

    def _build_form(self):
        self.card = tk.Frame(self.page, bg=WHITE, highlightbackground=BORDER, highlightthickness=1, padx=28, pady=22)
        self.card.pack(fill="x", padx=24, pady=20)
        card = self.card

        top = tk.Frame(card, bg=WHITE)
        top.pack(fill="x")
        tk.Button(top, text="<- Back to destinations", command=self.on_destination if callable(self.on_destination) else None,
                  bg=WHITE, fg=MAROON, relief="flat", cursor="hand2", font=("Arial", 9, "bold")).pack(side="left")
        tk.Label(top, text="BOOKING FORM", bg=WHITE, fg=DARK, font=("Arial", 10, "bold")).pack(side="right")

        tk.Label(card, text="YOUR NEXT STORY", bg=WHITE, fg=MAROON, font=("Arial", 9, "bold")).pack(anchor="w", pady=(16, 5))
        tk.Label(card, text="Plan your Bhutan escape", bg=WHITE, fg=DARK, font=("Georgia", 18, "bold")).pack(anchor="w")
        tk.Label(card, text="Choose your trip and tell us who is travelling. Payment comes next.",
                 bg=WHITE, fg=MUTED, font=("Arial", 9)).pack(anchor="w", pady=(3, 8))

        # ---- destination ----
        self._label(card, "District")
        self.district_box = ttk.Combobox(card, textvariable=self.district_var, state="readonly",
                                         values=list(DZONGKHAG_LIST))
        self.district_box.pack(fill="x", ipady=4)
        self._label(card, "Place")
        self.dest_box = ttk.Combobox(card, textvariable=self.dest_var, state="disabled", values=[])
        self.dest_box.pack(fill="x", ipady=4)
        self.dest_info = tk.Label(card, text="", bg=WHITE, fg=MUTED, font=("Arial", 9), anchor="w")
        self.dest_info.pack(fill="x", pady=(4, 0))

        # ---- traveller ----
        self._label(card, "Name")
        self.name_entry = ttk.Entry(card)
        self.name_entry.pack(fill="x", ipady=5)
        self._label(card, "Email address")
        self.email_entry = ttk.Entry(card)
        self.email_entry.pack(fill="x", ipady=5)

        row = tk.Frame(card, bg=WHITE)
        row.pack(fill="x")
        row.columnconfigure(0, weight=1, uniform="r")
        row.columnconfigure(1, weight=1, uniform="r")
        left = tk.Frame(row, bg=WHITE)
        left.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        right = tk.Frame(row, bg=WHITE)
        right.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        self._label(left, "Arrival date (YYYY-MM-DD)")
        date_row = tk.Frame(left, bg=WHITE)
        date_row.pack(fill="x")
        date_row.columnconfigure(0, weight=1)
        self.date_entry = ttk.Entry(date_row)
        self.date_entry.grid(row=0, column=0, sticky="ew", ipady=5)
        tk.Button(date_row, text="Cal", command=self._open_calendar, bg=WHITE, fg=MAROON, relief="solid",
                  bd=1, cursor="hand2", padx=9, pady=4).grid(row=0, column=1, padx=(5, 0))

        self._label(right, "Travellers")
        ttk.Combobox(right, textvariable=self.travellers, state="readonly",
                     values=TRAVELLER_CHOICES).pack(fill="x", ipady=4)

        # ---- Bhutanese or international ----
        self._label(card, "I am travelling as a...", pady=(16, 4))
        for value, text in ((BHUTANESE, "Bhutanese traveller  -  pay in Ngultrum (Nu.)"),
                            (INTERNATIONAL, "International traveller  -  pay in US dollars (USD)")):
            tk.Radiobutton(card, text=text, variable=self.residency, value=value, bg=WHITE, fg=DARK,
                           activebackground=WHITE, selectcolor=WHITE, font=("Arial", 10),
                           cursor="hand2").pack(anchor="w")

        # ---- live total ----
        self.total_box = tk.Frame(card, bg=TOTAL_BG, highlightbackground=BORDER, highlightthickness=1,
                                  padx=18, pady=14)
        self.total_box.pack(fill="x", pady=(16, 4))
        self.per_person_var = tk.StringVar()
        self.people_var = tk.StringVar()
        self.total_var = tk.StringVar()
        for label, var, big in (("Price per person", self.per_person_var, False),
                                ("Travellers", self.people_var, False),
                                ("Total", self.total_var, True)):
            r = tk.Frame(self.total_box, bg=TOTAL_BG)
            r.pack(fill="x", pady=2)
            tk.Label(r, text=label, bg=TOTAL_BG, fg=DARK if big else MUTED,
                     font=("Georgia", 13, "bold") if big else ("Arial", 10)).pack(side="left")
            tk.Label(r, textvariable=var, bg=TOTAL_BG, fg=MAROON if big else DARK,
                     font=("Georgia", 13, "bold") if big else ("Arial", 10, "bold")).pack(side="right")

        # ---- notes ----
        self._label(card, "Anything we should know? (optional)", pady=(12, 4))
        self.notes = tk.Text(card, height=4, wrap="word", relief="solid", bd=1, highlightthickness=1,
                             highlightbackground=BORDER, font=("Arial", 9), padx=8, pady=8)
        self.notes.pack(fill="x")

        tk.Button(card, text="Continue to payment ->", command=self._continue, bg=MAROON, fg=WHITE,
                  activebackground="#851329", activeforeground=WHITE, relief="flat", cursor="hand2",
                  padx=18, pady=10, font=("Arial", 9, "bold")).pack(anchor="e", pady=(16, 0))

    def _build_footer(self):
        bottom_bar = tk.Frame(self.page, bg=MAROON, height=80)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)
        bottom_bar.columnconfigure(0, weight=0)
        bottom_bar.columnconfigure(1, weight=1)
        bottom_bar.columnconfigure(2, weight=0)
        brand = tk.Frame(bottom_bar, bg=MAROON)
        brand.grid(row=0, column=0, sticky="w", padx=40, pady=12)
        tk.Label(brand, text="BhutanVoyage", font=self.font_footer_brand, bg=MAROON, fg="white").pack(anchor="w")
        tk.Label(brand, text="Plan Himalayan Dreams, Always.", font=self.font_footer_sub, bg=MAROON, fg="#E8C5BE").pack(anchor="w")
        tk.Label(bottom_bar, text="Made for curious people", font=self.font_footer_tag, bg=MAROON, fg=FOOTER_TEXT_SOFT).grid(row=0, column=1)
        admin = tk.Label(bottom_bar, text="Admin Login", font=self.font_footer_admin, bg=MAROON, fg=FOOTER_ADMIN, cursor="hand2")
        admin.grid(row=0, column=2, sticky="e", padx=40)
        admin.bind("<Button-1>", lambda _e: self.on_admin() if callable(self.on_admin) else None)

    # ------------------------------------------------------------------ behaviour
    def _prefill_fields(self):
        """Signed-in traveller's name/email, then anything they typed before going to payment."""
        p = self.prefill
        values = {
            self.name_entry: p.get("name") or self.user.get("name", ""),
            self.email_entry: p.get("email") or self.user.get("email", ""),
            self.date_entry: p.get("date") or date.today().isoformat(),
        }
        for entry, text in values.items():
            entry.delete(0, "end")
            entry.insert(0, text)
        if p.get("notes"):
            self.notes.insert("1.0", p["notes"])

    def _selected_destination(self):
        """The place chosen in the two drop-downs (None until both are chosen)."""
        title = self.dest_var.get()
        for d in places_in(self.district_var.get()):
            if d["title"] == title:
                return d
        return None

    def _set_place_choices(self):
        """Fill the Place list with the places of the chosen district (disabled until a district is chosen)."""
        places = places_in(self.district_var.get()) if self.district_var.get() in DZONGKHAG_LIST else []
        titles = [d["title"] for d in places]
        if not titles:
            self.dest_box.configure(values=[], state="disabled")
            self.dest_var.set(CHOOSE_PLACE_FIRST)
            return
        self.dest_box.configure(values=titles, state="readonly")
        if self.dest_var.get() not in titles:
            self.dest_var.set(CHOOSE_PLACE)

    def _on_district_change(self, *_):
        self._set_place_choices()
        self._refresh_total()

    def _refresh_total(self, *_):
        d = self._selected_destination()
        n = parse_travellers(self.travellers.get())
        self.people_var.set(f"{n} {'person' if n == 1 else 'people'}")
        if d is None:
            self.dest_info.config(text="Pick a district and a place to see the price.")
            self.per_person_var.set("-")
            self.total_var.set("-")
            return
        currency, per_person = price_per_person(d, self.residency.get())
        self.dest_info.config(text=f"{d['location']}   •   Ideal stay: {d['stay']}")
        self.per_person_var.set(format_money(currency, per_person))
        self.total_var.set(format_money(currency, per_person * n))

    def _continue(self):
        d = self._selected_destination()
        if d is None:
            messagebox.showwarning("Choose a destination", "Please choose a district and the place you would like to go.")
            return
        ok, err, details = validate_traveller_details(
            self.name_entry.get(), self.email_entry.get(), self.date_entry.get(), self.travellers.get())
        if not ok:
            messagebox.showwarning("Check your details", err)
            return

        currency, per_person = price_per_person(d, self.residency.get())
        booking = {
            "dest_key": d["key"],
            "name": details["name"],
            "email": details["email"],
            "date": details["date"],
            "travellers": details["travellers"],
            "residency": self.residency.get(),
            "dzongkhag": dzongkhag_of(d),
            "place": d["title"],
            "package": f"{d['title']} ({d['stay']})",
            "currency": currency,
            "per_person": per_person,
            "notes": self.notes.get("1.0", "end").strip(),
        }
        if callable(self.on_payment):
            self.on_payment(booking)
        else:
            print("--- ERROR: on_payment is not connected! ---")

    def _open_calendar(self):
        popup = tk.Toplevel(self)
        popup.title("Choose arrival date")
        popup.configure(bg=WHITE)
        popup.resizable(False, False)
        popup.transient(self.winfo_toplevel())
        popup.grab_set()

        try:
            chosen = datetime.strptime(self.date_entry.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            chosen = date.today()

        state = {"year": chosen.year, "month": chosen.month}
        heading = tk.Frame(popup, bg=WHITE, padx=10, pady=10)
        heading.pack(fill="x")
        month_label = tk.Label(heading, bg=WHITE, fg=DARK, font=("Arial", 11, "bold"))
        month_label.pack(side="top", pady=(0, 8))
        controls = tk.Frame(heading, bg=WHITE)
        controls.pack()
        grid_frame = tk.Frame(popup, bg=WHITE, padx=10, pady=5)
        grid_frame.pack()

        def change_month(offset):
            month = state["month"] + offset
            year = state["year"]
            if month < 1:
                month, year = 12, year - 1
            elif month > 12:
                month, year = 1, year + 1
            state["month"], state["year"] = month, year
            draw_calendar()

        def choose_date(selected):
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, selected.isoformat())
            popup.destroy()

        tk.Button(controls, text="<", command=lambda: change_month(-1), bg=WHITE, relief="flat", font=("Arial", 12, "bold")).pack(side="left", padx=8)
        tk.Button(controls, text="Today", command=lambda: choose_date(date.today()), bg=WHITE, fg=MAROON, relief="flat").pack(side="left", padx=8)
        tk.Button(controls, text=">", command=lambda: change_month(1), bg=WHITE, relief="flat", font=("Arial", 12, "bold")).pack(side="left", padx=8)

        def draw_calendar():
            for widget in grid_frame.winfo_children():
                widget.destroy()
            month_label.config(text=f"{calendar.month_name[state['month']]} {state['year']}")
            for col, day_name in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
                tk.Label(grid_frame, text=day_name, width=4, bg=WHITE, fg=MAROON, font=("Arial", 9, "bold")).grid(row=0, column=col, padx=1, pady=3)
            for row, week in enumerate(calendar.monthcalendar(state["year"], state["month"]), start=1):
                for col, day_num in enumerate(week):
                    if day_num == 0:
                        tk.Label(grid_frame, text="", width=4, bg=WHITE).grid(row=row, column=col, padx=1, pady=1)
                    else:
                        selected = date(state["year"], state["month"], day_num)
                        tk.Button(grid_frame, text=str(day_num), width=3, command=lambda d=selected: choose_date(d),
                                  bg=MAROON if selected == date.today() else WHITE,
                                  fg=WHITE if selected == date.today() else DARK,
                                  activebackground="#851329", activeforeground=WHITE, relief="flat",
                                  cursor="hand2").grid(row=row, column=col, padx=1, pady=1)

        draw_calendar()
