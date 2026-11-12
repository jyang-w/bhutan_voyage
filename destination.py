import tkinter as tk
from tkinter import font
from PIL import ImageTk
from pathlib import Path

# =====================================================
# COLOURS
# =====================================================
WHITE = "#FFFFFF"
DARK = "#2C3E50"
GREY = "#7F8C8D"
MAROON = "#7B241C"
DARK_MAROON = "#5C1A14"
CARD_BORDER = "#E0E0E0"
SEARCH_BG = "#F2DCDB"
BG_GREY = "#F2F2F2"
PIN_GOLD = "#E0A22C"

BASE_DIR = Path(__file__).parent
IMAGE_DIR = BASE_DIR / "images"


# =====================================================
# DESTINATIONS DATA
# =====================================================
from catalog import (DESTINATIONS, district_counts, filter_destinations, dzongkhag_of,
                     rating_short)
import place_images
from database import get_favourites, add_favourite, remove_favourite
from tkinter import messagebox
import sqlite3


def draw_pin(parent, size=20, bg=WHITE, color=PIN_GOLD):
    c = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0, bd=0)
    cx = size / 2
    r = size * 0.34
    c.create_oval(cx - r, size * 0.06, cx + r, size * 0.06 + 2 * r, fill=color, outline=color)
    c.create_polygon(cx - r * 0.75, size * 0.06 + 1.5 * r, cx + r * 0.75, size * 0.06 + 1.5 * r, cx, size * 0.98, fill=color, outline=color)
    inner = r * 0.42
    c.create_oval(cx - inner, size * 0.06 + r - inner, cx + inner, size * 0.06 + r + inner, fill=bg, outline=bg)
    return c

def draw_heart(canvas, filled=False, size=24):
    canvas.delete("all")
    s = size
    pad = s * 0.15
    fill_color = "#E74C3C" if filled else WHITE
    outline_color = "#E74C3C" if filled else GREY
    canvas.create_oval(pad, pad, s * 0.5, s * 0.55, fill=fill_color, outline=outline_color, width=2)
    canvas.create_oval(s * 0.5, pad, s - pad, s * 0.55, fill=fill_color, outline=outline_color, width=2)
    canvas.create_polygon(pad, s * 0.42, s - pad, s * 0.42, s / 2, s - pad, fill=fill_color, outline=outline_color, width=2)


# =====================================================
# DESTINATION PAGE CLASS
# =====================================================
class DestinationPage(tk.Frame):

    PLACEHOLDER = "Search places or districts..."
    COLUMNS = 4

    def __init__(self, parent, on_home=None, on_booking=None, on_about=None,
                 on_open_detail=None, on_admin=None, user=None, on_signin_required=None,
                 district=None, on_district_change=None, **kwargs):
        super().__init__(parent, bg=WHITE, **kwargs)
        
        self.root = self.winfo_toplevel()
        self.on_home = on_home
        self.on_booking = on_booking
        self.on_about = on_about
        self.on_open_detail = on_open_detail   # called with the destination dict
        self.on_admin = on_admin
        # Hearts are saved per signed-in traveller. A visitor who is not signed in (or an admin)
        # is handed to on_signin_required(dest_key) instead, the same way booking does it.
        self.user = user or {}
        self.on_signin_required = on_signin_required
        # Which district is showing (None = "All districts"). on_district_change(name_or_None) lets the
        # app remember it, so "Back to destinations" returns to the same district.
        self.district = district
        self.on_district_change = on_district_change
        self.user_id = self.user.get("id") if self.user.get("role") != "admin" else None

        self.photos = {}
        self.favorites = set()
        if self.user_id:
            try:
                self.favorites = set(get_favourites(self.user_id))   # hearts come back filled
            except sqlite3.Error as e:
                print(f"[favourites] could not load: {e}")
        self.card_widgets = []          # [(card frame, destination dict)] - every place, built once
        self._shown = []                # the places currently on screen, in order
        self.district_var = tk.StringVar(value=district or "")
        self.font_nav_menu = font.Font(family="Georgia", size=11)

        self.title_font    = font.Font(family="Georgia", size=24, weight="bold")
        self.subtitle_font = font.Font(family="Helvetica", size=12)
        self.card_font     = font.Font(family="Helvetica", size=12, weight="bold") 
        self.small_font    = font.Font(family="Helvetica", size=9) 
        
        self.font_nav = font.Font(family="Georgia", size=12)
        self.font_button = font.Font(family="Georgia", size=11, weight="bold")

        self.container = tk.Frame(self, bg=WHITE)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_explore_page()

    def create_explore_page(self):
        # 1. HEADER
        header_frame = tk.Frame(self.container, bg="white", height=90)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        header_frame.columnconfigure(0, weight=0)
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(2, weight=0)

        tk.Label(header_frame, text="BhutanVoyage", bg="white", fg=MAROON, font=("Georgia", 16, "bold"), cursor="hand2").grid(row=0, column=0, sticky="w", padx=30, pady=15)
        
        nav_frame = tk.Frame(header_frame, bg="white")
        nav_frame.grid(row=0, column=1, sticky="ew")
        nav_inner = tk.Frame(nav_frame, bg="white")
        nav_inner.pack(expand=True)

        nav_items = [("Home", self.on_home), ("Destination", None), ("Booking", self.on_booking), ("About us", self.on_about)]
        for item, cb in nav_items:
            color = MAROON if item == "Destination" else DARK
            if item == "Destination":
                # "Destination" opens a list: All districts, then the 20 dzongkhags
                lbl = tk.Label(nav_inner, text="Destination  \u25BE", font=self.font_nav, fg=color, bg="white", cursor="hand2")
                lbl.pack(side="left", padx=25)
                lbl.bind("<Button-1>", self._open_district_menu)
                self.destination_nav = lbl
                continue
            lbl = tk.Label(nav_inner, text=item, font=self.font_nav, fg=color, bg="white", cursor="hand2" if cb else "arrow")
            lbl.pack(side="left", padx=25)
            if cb: lbl.bind("<Button-1>", lambda _e, c=cb: c())

        tk.Button(header_frame, text="Plan Your Trip", command=lambda: self.search_entry.focus_set(),
                  bg=MAROON, fg="white", font=self.font_button, relief="flat", padx=22, pady=10, cursor="hand2",
                  activebackground="#5C1A14", activeforeground="white").grid(row=0, column=2, sticky="e", padx=30, pady=15)

        # 2. TITLE & SEARCH
        tk.Label(self.container, text="Explore Bhutan", font=self.title_font, bg=WHITE, fg=DARK).pack(pady=(6, 2))
        tk.Label(self.container, text="Discover and book amazing tours", font=self.subtitle_font, bg=WHITE, fg=GREY).pack(pady=(0, 8))

        wrap = tk.Frame(self.container, bg=SEARCH_BG, height=40)
        wrap.pack(fill="x", padx=120, pady=(0, 8))
        wrap.pack_propagate(False)

        self.search_entry = tk.Entry(wrap, font=("Helvetica", 12), relief="flat", bg=SEARCH_BG, fg=DARK)
        self.search_entry.pack(fill="both", expand=True, padx=12, pady=6)
        self.search_entry.insert(0, self.PLACEHOLDER)
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_placeholder)
        self.search_entry.bind("<KeyRelease>", self.filter_cards)
        self.search_entry.bind("<Return>", self.filter_cards)

        # "Paro - 6 places"  [Show all districts]
        status = tk.Frame(self.container, bg=WHITE)
        status.pack(fill="x", padx=120, pady=(0, 4))
        self.status_label = tk.Label(status, text="", font=("Helvetica", 10, "bold"), bg=WHITE, fg=DARK, anchor="w")
        self.status_label.pack(side="left")
        self.show_all_btn = tk.Label(status, text="Show all districts", font=("Helvetica", 10, "underline"),
                                     bg=WHITE, fg=MAROON, cursor="hand2")
        self.show_all_btn.bind("<Button-1>", lambda _e: self.set_district(None))
        # (packed only while a district is selected - see _update_status)

        # 3. FOOTER
        bottom_bar = tk.Frame(self.container, bg=MAROON, height=80)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)
        bottom_bar.columnconfigure(0, weight=0)
        bottom_bar.columnconfigure(1, weight=1)
        bottom_bar.columnconfigure(2, weight=0)

        brand_frame = tk.Frame(bottom_bar, bg=MAROON)
        brand_frame.grid(row=0, column=0, sticky="w", padx=40, pady=12)
        tk.Label(brand_frame, text="BhutanVoyage", font=("Georgia", 15, "bold"), bg=MAROON, fg="white").pack(anchor="w")
        tk.Label(brand_frame, text="Plan Himalayan Dreams, Always.", font=("Georgia", 10, "italic"), bg=MAROON, fg="#E8C5BE").pack(anchor="w")
        tk.Label(bottom_bar, text="Made for curious people", font=("Helvetica", 10), bg=MAROON, fg="#E6B0AA").grid(row=0, column=1)
        admin_lbl = tk.Label(bottom_bar, text="Admin Login", font=("Helvetica", 10, "bold"), bg=MAROON, fg="#F5DEB3", cursor="hand2")
        admin_lbl.grid(row=0, column=2, sticky="e", padx=40)
        admin_lbl.bind("<Button-1>", lambda _e: self.on_admin() if callable(self.on_admin) else None)

        # 4. SCROLLABLE GRID
        scroll_wrap = tk.Frame(self.container, bg=WHITE)
        scroll_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        self.canvas = tk.Canvas(scroll_wrap, bg=WHITE, highlightthickness=0)
        sb = tk.Scrollbar(scroll_wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grid_frame = tk.Frame(self.canvas, bg=WHITE)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")

        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        for col in range(4):
            self.grid_frame.grid_columnconfigure(col, weight=1, uniform="card")

        self.cards_by_key = {}
        for d in DESTINATIONS:                       # every place gets a card, built once
            card = self.create_card(d)
            self.cards_by_key[d["key"]] = card
            self.card_widgets.append((card, d))

        self.empty_label = tk.Label(self.grid_frame, text="No places match your search.",
                                    font=("Helvetica", 12), bg=WHITE, fg=GREY)

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self._last_card_width = 180

        self._bind_wheel()
        self._relayout()                             # show the current district (or all)

    # ---------------- district + search ----------------
    def _query(self):
        raw = self.search_entry.get().strip()
        return "" if raw == self.PLACEHOLDER else raw

    def set_district(self, name):
        """Show one district (name) or everything (None). The search box keeps working inside it."""
        self.district = name or None
        self.district_var.set(name or "")
        if callable(self.on_district_change):
            self.on_district_change(self.district)
        self._relayout()

    def _open_district_menu(self, event):
        """The Destination menu: All districts, then the 20 dzongkhags (A-Z) with their place counts."""
        menu = tk.Menu(self, tearoff=0, font=self.font_nav_menu)
        menu.add_radiobutton(label=f"All districts  ({len(DESTINATIONS)})", variable=self.district_var,
                             value="", command=lambda: self.set_district(None))
        menu.add_separator()
        for name, count in district_counts():
            menu.add_radiobutton(label=f"{name}  ({count})", variable=self.district_var, value=name,
                                 command=lambda n=name: self.set_district(n))
        w = event.widget
        try:
            menu.tk_popup(w.winfo_rootx(), w.winfo_rooty() + w.winfo_height())
        finally:
            menu.grab_release()

    def _update_status(self, count):
        where = self.district or "All districts"
        text = f"{where}  \u00b7  {count} {'place' if count == 1 else 'places'}"
        q = self._query()
        if q:
            text += f"  matching \u201c{q}\u201d"
        self.status_label.config(text=text)
        if self.district:
            self.show_all_btn.pack(side="left", padx=(14, 0))
        else:
            self.show_all_btn.pack_forget()

    def _relayout(self):
        """Put exactly the matching cards in the grid, packed from the top-left (no gaps)."""
        self._shown = filter_destinations(self.district, self._query())
        for card, _ in self.card_widgets:
            card.grid_forget()
        self.empty_label.grid_forget()
        for i, d in enumerate(self._shown):
            self.cards_by_key[d["key"]].grid(row=i // self.COLUMNS, column=i % self.COLUMNS,
                                             padx=10, pady=10, sticky="nsew")
        if not self._shown:
            self.empty_label.grid(row=0, column=0, columnspan=self.COLUMNS, pady=40)
        self._render_shown_images()
        self._update_status(len(self._shown))
        self.grid_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)

    def _render_shown_images(self):
        """Pictures are only drawn for cards on screen, and redrawn only if the card width changed."""
        w = self._last_card_width
        for d in self._shown:
            card = self.cards_by_key[d["key"]]
            if card.image_width != w:
                self.set_card_image(card.image_label, d, w)
                card.image_width = w

    def _on_canvas_resize(self, event):
        if hasattr(self, "_resize_job") and self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(100, self._resize_cards, event.width)

    def _resize_cards(self, canvas_width):
        new_card_w = max(150, (canvas_width - 120) // self.COLUMNS)
        if abs(new_card_w - self._last_card_width) > 10:
            self._last_card_width = new_card_w
            self._render_shown_images()
            self.grid_frame.update_idletasks()
            gw = self.grid_frame.winfo_reqwidth()
            self.canvas.coords(self.canvas_window, max((canvas_width - gw) // 2, 0), 0)

    def _clear_placeholder(self, event=None):
        if self.search_entry.get() == self.PLACEHOLDER:
            self.search_entry.delete(0, "end")

    def _restore_placeholder(self, event=None):
        if self.search_entry.get().strip() == "":
            self.search_entry.insert(0, self.PLACEHOLDER)

    def _bind_wheel(self):
        def _on_wheel(event):
            if self.winfo_exists() and self.canvas.winfo_exists():
                if event.num == 5 or event.delta < 0: self.canvas.yview_scroll(1, "units")
                elif event.num == 4 or event.delta > 0: self.canvas.yview_scroll(-1, "units")

        def bind_all_descendants(w):
            w.bind("<MouseWheel>", _on_wheel, add="+")
            w.bind("<Button-4>", _on_wheel, add="+")
            w.bind("<Button-5>", _on_wheel, add="+")
            for child in w.winfo_children():
                bind_all_descendants(child)

        self.canvas.bind("<MouseWheel>", _on_wheel, add="+")
        self.canvas.bind("<Button-4>", _on_wheel, add="+")
        self.canvas.bind("<Button-5>", _on_wheel, add="+")

        self.root.update_idletasks()
        bind_all_descendants(self.grid_frame)

        self.container.bind("<MouseWheel>", _on_wheel, add="+")
        self.container.bind("<Button-4>", _on_wheel, add="+")
        self.container.bind("<Button-5>", _on_wheel, add="+")

    def toggle_favorite(self, key, heart_canvas):
        if not self.user_id:                       # not signed in -> ask them to sign in
            if callable(self.on_signin_required):
                self.on_signin_required(key)
            return
        try:
            if key in self.favorites:
                remove_favourite(self.user_id, key)
                self.favorites.discard(key)
                draw_heart(heart_canvas, filled=False, size=24)
            else:
                add_favourite(self.user_id, key)
                self.favorites.add(key)
                draw_heart(heart_canvas, filled=True, size=24)
        except sqlite3.Error as e:
            messagebox.showerror("Favourites", f"Could not save your favourite: {e}")

    def create_card(self, data):
        card = tk.Frame(self.grid_frame, bg=WHITE, highlightbackground=CARD_BORDER, highlightthickness=1, cursor="hand2")
        card.image_width = 0                      # width its picture was last drawn at

        img_container = tk.Frame(card, bg=WHITE)
        img_container.pack(fill="x")

        img_lbl = tk.Label(img_container, bg="#BDC3C7", cursor="hand2")
        img_lbl.pack(fill="x", expand=True)
        card.image_label = img_lbl

        heart_canvas = tk.Canvas(img_container, width=24, height=24, bg=WHITE, highlightthickness=0, bd=0, cursor="hand2")
        heart_canvas.place(x=6, y=6)
        draw_heart(heart_canvas, filled=data["key"] in self.favorites, size=24)

        def on_enter(e):
            if data["key"] not in self.favorites: draw_heart(heart_canvas, filled=True, size=24)
        def on_leave(e):
            if data["key"] not in self.favorites: draw_heart(heart_canvas, filled=False, size=24)
        def on_click(e):
            self.toggle_favorite(data["key"], heart_canvas)
            return "break"

        heart_canvas.bind("<Enter>", on_enter)
        heart_canvas.bind("<Leave>", on_leave)
        heart_canvas.bind("<Button-1>", on_click)

        info = tk.Frame(card, bg=WHITE)
        info.pack(fill="both", expand=True, padx=10, pady=6)

        title_row = tk.Frame(info, bg=WHITE)
        title_row.pack(fill="x", pady=(4, 0))

        tk.Label(title_row, text=data["title"], font=self.card_font, bg=WHITE, fg=DARK, anchor="w",
                 justify="left", wraplength=140).pack(side="left", fill="x", expand=True)

        tk.Label(info, text=f"{dzongkhag_of(data)}  \u00b7  {data['subtitle']}", font=self.small_font, bg=WHITE,
                 fg=GREY, anchor="w", justify="left", wraplength=190).pack(fill="x")

        rating_row = tk.Frame(info, bg=WHITE)
        rating_row.pack(fill="x", pady=(5, 0))

        rating = rating_short(data)
        if rating:
            tk.Label(rating_row, text=f"\u2605 {rating}", font=("Helvetica", 8, "bold"), bg=WHITE, fg="#F1C40F").pack(side="left")
        else:
            tk.Label(rating_row, text="New", font=("Helvetica", 8, "bold"), bg=WHITE, fg=GREY).pack(side="left")
        tk.Label(rating_row, text=data["stay"], font=("Helvetica", 8), bg=WHITE, fg=GREY).pack(side="right")

        for w in (card, img_lbl, img_container, info, title_row):
            w.bind("<Button-1>", lambda e, d=data: self.open_detail(d))

        return card

    def set_card_image(self, label, data, target_width):
        """The place's photo, or the neutral "Photo coming soon" card when it has none yet."""
        target_height = int(target_width * 0.6)
        try:
            photo = ImageTk.PhotoImage(place_images.load(data, target_width, target_height))
            self.photos[f"card_{data['key']}"] = photo        # keyed by place (not file name: placeholders have none)
            label.image = photo
            label.configure(image=photo, text="", width=target_width, height=target_height)
        except Exception as e:
            print(f"[image error] {data['key']}: {e}")
            label.configure(text=f"Missing:\n{data['title']}", fg=MAROON, bg="#E8E8E8", height=5)

    def open_detail(self, data):
        if callable(self.on_open_detail):
            self.on_open_detail(data)

    def filter_cards(self, event=None):
        """Typing narrows the places (inside the chosen district). Enter on a single match opens it."""
        if event is not None and getattr(event, "keysym", "") == "Return":
            matches = filter_destinations(self.district, self._query())
            if len(matches) == 1:
                self.search_entry.delete(0, "end")
                self._relayout()
                self.root.after(50, lambda dd=matches[0]: self.open_detail(dd))
                return
        self._relayout()
