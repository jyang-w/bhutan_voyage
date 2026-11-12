
import tkinter as tk
from tkinter import font, messagebox
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont
from database import init_db, add_favourite

# ==========================================
# SAFE IMPORTS
# ==========================================
from catalog import get_destination
from bhutanese_payment import BhutanesePaymentPage
from international_payment import InternationalPaymentPage
from user_dashboard import UserDashboard

try:
    from paro_page import DetailPage
except ImportError:
    class DetailPage(tk.Frame):
        def __init__(self, parent, **kwargs):
            super().__init__(parent, bg="white")
            tk.Label(self, text="Detail Page", font=("Helvetica", 24, "bold")).pack(pady=50)

try:
    from destination import DestinationPage
except ImportError:
    class DestinationPage(tk.Frame):
        def __init__(self, parent, **kwargs):
            super().__init__(parent, bg="white")
            tk.Label(self, text="Destination Page", font=("Helvetica", 24, "bold")).pack(pady=50)

try:
    from Booking import BookingPage
except ImportError:
    class BookingPage(tk.Frame):
        def __init__(self, parent, **kwargs):
            super().__init__(parent, bg="white")
            tk.Label(self, text="Booking Page", font=("Helvetica", 24, "bold")).pack(pady=50)

try:
    from aboutus import AboutUsPage
except ImportError:
    class AboutUsPage(tk.Frame):
        def __init__(self, parent, **kwargs):
            super().__init__(parent, bg="white")
            tk.Label(self, text="About Us Page", font=("Helvetica", 24, "bold")).pack(pady=50)

try:
    from signin import SignInPage
except ImportError:
    class SignInPage(tk.Frame):
        def __init__(self, parent, **kwargs):
            super().__init__(parent, bg="white")
            tk.Label(self, text="Sign In Page", font=("Helvetica", 24, "bold")).pack(pady=50)

try:
    from create_account import CreateAccountPage
except ImportError:
    class CreateAccountPage(tk.Frame):
        def __init__(self, parent, **kwargs):
            super().__init__(parent, bg="white")
            tk.Label(self, text="Create Account Page", font=("Helvetica", 24, "bold")).pack(pady=50)

try:
    from admin_dashboard import AdminDashboard
except ImportError:
    class AdminDashboard(tk.Frame):
        def __init__(self, parent, **kwargs):
            super().__init__(parent, bg="white")
            tk.Label(self, text="Admin Dashboard", font=("Helvetica", 24, "bold")).pack(pady=50)


BG_COLOR        = "#FFFFFF"
MAROON          = "#7B241C"
LIGHT_GRAY      = "#F4F4F4"
TEXT_DARK       = "#2C3E50"
TEXT_LIGHT      = "#7F8C8D"
FOOTER_TEXT_SOFT = "#E6B0AA"
FOOTER_ADMIN    = "#F5DEB3"

BREAKPOINT_NARROW = 700
BREAKPOINT_MEDIUM = 1000

# Get the absolute path to the folder containing main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# YOUR HOME PAGE CLASS
# ==========================================
class BhutanApp(tk.Frame):
    def __init__(self, parent, on_plan_trip=None, on_go_destination=None, on_go_booking=None, on_go_about=None, on_admin=None, on_open_detail=None, **kwargs):
        super().__init__(parent, bg=BG_COLOR, **kwargs)

        self.on_plan_trip      = on_plan_trip
        self.on_go_destination = on_go_destination
        self.on_go_booking     = on_go_booking
        self.on_go_about       = on_go_about
        self.on_admin          = on_admin
        self.on_open_detail    = on_open_detail

        self.font_logo          = font.Font(family="Helvetica", size=18, weight="bold")
        self.font_nav           = font.Font(family="Georgia", size=12)
        self.font_section_title = font.Font(family="Helvetica", size=14, weight="bold")
        self.font_card_title    = font.Font(family="Helvetica", size=12, weight="bold")
        self.font_button        = font.Font(family="Georgia", size=11, weight="bold")
        self.font_footer_brand  = font.Font(family="Georgia", size=15, weight="bold")
        self.font_footer_sub    = font.Font(family="Georgia", size=10, slant="italic")
        self.font_footer_tag    = font.Font(family="Helvetica", size=10)
        self.font_footer_admin  = font.Font(family="Helvetica", size=10, weight="bold")

        self.image_references = {}
        self._last_layout = "wide"
        self._last_width = 0
        self._rendering = False
        self._resize_job = None

        self.setup_scrollable_area()
        self.setup_ui()

        self.bind("<Configure>", self.on_window_resize)
        
        # Wait 500ms for the window to fully draw before loading images
        self.after(500, self.update_images)

    def setup_scrollable_area(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.main_frame, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.content_frame = tk.Frame(self.canvas, bg=BG_COLOR)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

    def _on_mousewheel(self, event):
        if self.winfo_exists() and self.canvas.winfo_exists():
            if event.num == 5 or event.delta < 0: self.canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0: self.canvas.yview_scroll(-1, "units")

    def _bind_wheel(self, _e=None):
        if self.winfo_exists():
            self.bind_all("<MouseWheel>", self._on_mousewheel)
            self.bind_all("<Button-4>",   self._on_mousewheel)
            self.bind_all("<Button-5>",   self._on_mousewheel)

    def _unbind_wheel(self, _e=None):
        try:
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
        except Exception: pass

    def load_image(self, path, fallback_color="#BDC3C7", text=""):
        # FIX 1: Use absolute BASE_DIR to find the image
        full_path = os.path.join(BASE_DIR, "images", path)
        
        if os.path.exists(full_path):
            try: 
                # FIX 2: Force .convert("RGB") so Tkinter can always read it
                return Image.open(full_path).convert("RGB")
            except Exception as e: 
                print(f"❌ Error opening {path}: {e}")
        else:
            print(f"❌ FILE NOT FOUND: {full_path}")
            
        img = Image.new('RGB', (400, 300), fallback_color)
        d = ImageDraw.Draw(img)
        if text:
            d.text((10, 10), f"Missing:\n{text}", fill=(255, 255, 255))
        return img

    @staticmethod
    def _load_font(candidates, size):
        for path in candidates:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        raise OSError("no font found")

    def resize_image(self, img_obj, width, height):
        return ImageTk.PhotoImage(img_obj.resize((max(1, width), max(1, height)), Image.Resampling.LANCZOS))

    def on_window_resize(self, event=None):
        if event is not None and event.widget is not self: return
        w = self.winfo_width()
        if w <= 1: return
        
        layout = ("narrow" if w < BREAKPOINT_NARROW else "medium" if w < BREAKPOINT_MEDIUM else "wide")
        if layout != self._last_layout:
            self._last_layout = layout
            self.apply_layout(layout)
            
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(100, self.update_images)

    def apply_layout(self, layout):
        if hasattr(self, "nav_labels"):
            for lbl, item in self.nav_labels:
                lbl.pack_forget()
                if layout == "narrow" and item != "Home": continue
                lbl.pack(side="left", padx={"narrow": 6, "medium": 12, "wide": 25}[layout])
        if hasattr(self, "cta_btn"):
            if layout == "narrow": self.cta_btn.config(text="Plan", padx=10, pady=6)
            else: self.cta_btn.config(text="Plan Your Trip", padx=22, pady=10)
        if hasattr(self, "cards_frame"):
            for i in range(4): self.cards_frame.columnconfigure(i, weight=0)
            cols = {"wide": 4, "medium": 2, "narrow": 1}[layout]
            for i in range(cols): self.cards_frame.columnconfigure(i, weight=1)
            self._grid_cards(cols)
        if hasattr(self, "hero_btn1"):
            if layout == "narrow":
                self.hero_btn1.place(x=20, y=195); self.hero_btn2.place(x=140, y=195)
            else:
                self.hero_btn1.place(x=60, y=290); self.hero_btn2.place(x=170, y=290)

    def _grid_cards(self, cols):
        for idx, (card, _) in enumerate(getattr(self, "card_widgets", [])):
            row, col = divmod(idx, cols)
            card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

    def update_images(self):
        if getattr(self, "_rendering", False): return
        if not self.winfo_exists(): return
        self._rendering = True
        try:
            w = self.content_frame.winfo_width()
            if w <= 1: return

            if (hasattr(self, 'hero_img_original') and getattr(self, 'hero_bg_label', None) and self.hero_bg_label.winfo_exists()):
                h = 350 if w >= BREAKPOINT_NARROW else 240
                resized = self.hero_img_original.resize((w, h), Image.Resampling.LANCZOS)
                draw = ImageDraw.Draw(resized)
                title_size, sub_size = (40, 13) if w >= BREAKPOINT_NARROW else (24, 9)
                try:
                    # FIX 3: Use full Windows font paths so it doesn't crash
                    title_font = self._load_font(["C:/Windows/Fonts/georgia.ttf", "/Library/Fonts/Georgia.ttf",
                                                  "/System/Library/Fonts/Supplemental/Georgia.ttf",
                                                  "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"], title_size)
                    sub_font   = self._load_font(["C:/Windows/Fonts/arial.ttf", "/Library/Fonts/Arial.ttf",
                                                  "/System/Library/Fonts/Supplemental/Arial.ttf",
                                                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"], sub_size)
                except Exception:
                    title_font = ImageFont.load_default(); sub_font = ImageFont.load_default()
                def txt(text, pos, f, color="white"):
                    x, y = pos
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            if dx or dy: draw.text((x + dx, y + dy), text, font=f, fill=(0, 0, 0))
                    draw.text((x, y), text, font=f, fill=color)
                pad = 30 if w >= BREAKPOINT_NARROW else 20
                txt("Discover the", (pad, 60 if w >= BREAKPOINT_NARROW else 40), title_font)
                txt("magic of Bhutan", (pad, 110 if w >= BREAKPOINT_NARROW else 75), title_font)
                txt("Explore Breathtaking Landscapes, ancient", (pad, 180 if w >= BREAKPOINT_NARROW else 130), sub_font)
                txt("monasteries, and vibrant culture in", (pad, 200 if w >= BREAKPOINT_NARROW else 145), sub_font)
                txt("the kingdom of BHUTAN.", (pad, 220 if w >= BREAKPOINT_NARROW else 160), sub_font)
                self.hero_img_tk = ImageTk.PhotoImage(resized)
                self.hero_bg_label.config(image=self.hero_img_tk); self.hero_bg_label.image = self.hero_img_tk

            if hasattr(self, 'dest_imgs_original'):
                cols = {"narrow": 1, "medium": 2, "wide": 4}[self._last_layout]
                card_w = max(150, (w - 100 - (cols - 1) * 20) // cols)
                card_h = int(card_w * 0.6)
                for city, img_obj, label in self.dest_imgs_original:
                    if label is not None and label.winfo_exists():
                        tk_img = self.resize_image(img_obj, card_w, card_h)
                        label.config(image=tk_img); label.image = tk_img

            if (hasattr(self, 'foot_img_original') and getattr(self, 'foot_img_lbl', None) and self.foot_img_lbl.winfo_exists()):
                img_w = int(w * 0.4) if w >= BREAKPOINT_NARROW else int(w * 0.8)
                if img_w > 1:
                    self.foot_img_tk = self.resize_image(self.foot_img_original, img_w, int(img_w * 0.6))
                    self.foot_img_lbl.config(image=self.foot_img_tk); self.foot_img_lbl.image = self.foot_img_tk
        finally:
            self._rendering = False

    def _go_to_booking(self):
        if callable(self.on_go_booking): self.on_go_booking()
        elif callable(self.on_plan_trip): self.on_plan_trip()
    def _go_to_plan(self):
        # "Plan Your Trip" starts on the Destinations page (no sign-in needed to browse)
        if callable(self.on_plan_trip): self.on_plan_trip()
    def _go_to_admin(self):
        if callable(self.on_admin): self.on_admin()
    def _go_to_destination(self):
        if callable(self.on_go_destination): self.on_go_destination()
    def _go_to_about(self):
        if callable(self.on_go_about): self.on_go_about()
    def _go_to_home(self):
        self.canvas.yview_moveto(0)

    def setup_ui(self):
        header_frame = tk.Frame(self.content_frame, bg="white", height=90)
        header_frame.pack(fill="x", side="top"); header_frame.pack_propagate(False)
        header_frame.columnconfigure(0, weight=0); header_frame.columnconfigure(1, weight=1); header_frame.columnconfigure(2, weight=0)

        logo_img = self.load_image("logo.jpg", MAROON, "Logo")
        self.logo_tk = self.resize_image(logo_img, 60, 60)
        logo_label = tk.Label(header_frame, image=self.logo_tk, bg="white", cursor="hand2")
        logo_label.image = self.logo_tk; logo_label.grid(row=0, column=0, sticky="w", padx=30, pady=15)
        logo_label.bind("<Button-1>", lambda _e: self._go_to_home())

        nav_frame = tk.Frame(header_frame, bg="white"); nav_frame.grid(row=0, column=1, sticky="ew")
        nav_inner = tk.Frame(nav_frame, bg="white"); nav_inner.pack(expand=True)

        nav_items = [("Home", self._go_to_home), ("Destination", self._go_to_destination), ("Booking", self._go_to_booking), ("About us", self._go_to_about)]
        self.nav_labels = []
        for item, cb in nav_items:
            lbl = tk.Label(nav_inner, text=item, font=self.font_nav, fg=MAROON, bg="white", cursor="hand2")
            lbl.pack(side="left", padx=25); lbl.bind("<Button-1>", lambda _e, c=cb: c())
            self.nav_labels.append((lbl, item))

        self.cta_btn = tk.Button(header_frame, text="Plan Your Trip", command=self._go_to_plan, bg=MAROON, fg="white", font=self.font_button, relief="flat", padx=22, pady=10, cursor="hand2", activebackground="#5C1A14", activeforeground="white")
        self.cta_btn.grid(row=0, column=2, sticky="e", padx=30, pady=15)

        self.hero_frame = tk.Frame(self.content_frame, height=350, bg="#34495E", width=1)
        self.hero_frame.pack(fill="x"); self.hero_frame.pack_propagate(False)
        self.hero_img_original = self.load_image("hero.jpg", "#2C3E50", "Hero Image")
        self.hero_bg_label = tk.Label(self.hero_frame); self.hero_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.hero_btn1 = tk.Button(self.hero_frame, text="Explore Bhutan", command=self._go_to_destination, bg=MAROON, fg="white", relief="flat", font=("Helvetica", 9), padx=10, pady=5, cursor="hand2")
        self.hero_btn1.place(x=60, y=290)
        self.hero_btn2 = tk.Button(self.hero_frame, text="Plan Your Trip", command=self._go_to_plan, bg="white", fg=MAROON, relief="flat", font=("Helvetica", 9), padx=10, pady=5, cursor="hand2")
        self.hero_btn2.place(x=170, y=290)

        dest_container = tk.Frame(self.content_frame, bg=LIGHT_GRAY)
        dest_container.pack(fill="both", expand=True)
        dest_header = tk.Frame(dest_container, bg=LIGHT_GRAY)
        dest_header.pack(fill="x", padx=40, pady=(20, 10))
        tk.Label(dest_header, text="Popular Destinations", font=self.font_section_title, bg=LIGHT_GRAY, fg=TEXT_DARK).pack(side="left")
        view_all = tk.Label(dest_header, text="View all destination →", font=("Helvetica", 10), bg=LIGHT_GRAY, fg=MAROON, cursor="hand2")
        view_all.pack(side="right"); view_all.bind("<Button-1>", lambda _e: self._go_to_destination())

        self.cards_frame = tk.Frame(dest_container, bg=LIGHT_GRAY); self.cards_frame.pack(fill="x", padx=30, pady=10)
        # Homepage cards use the real catalog entries, so each card shows its own
        # description and opens its own detail page.
        home_cards = [("paro", "paro.jpg", "#27AE60"), ("punakha", "punakha.jpg", "#D35400"),
                      ("thimphu", "thimphu.jpg", "#2980B9"), ("samtse-town", "samtse.jpg", "#8E44AD")]
        self.dest_imgs_original = []; self.card_widgets = []
        for idx, (key, img_name, color) in enumerate(home_cards):
            d = get_destination(key)
            img_obj = self.load_image(img_name, color, d["title"])
            self.dest_imgs_original.append((d["title"], img_obj, None))
            card = self.create_card(self.cards_frame, idx, d, img_obj)
            self.card_widgets.append((card, d["title"]))

        footprint_frame = tk.Frame(self.content_frame, bg="white", height=320)
        footprint_frame.pack(fill="x", pady=20); footprint_frame.pack_propagate(False)
        self.img_holder = tk.Frame(footprint_frame, bg="white", width=450, height=260)
        self.img_holder.pack(side="left", padx=(60, 20), pady=30); self.img_holder.pack_propagate(False)
        self.foot_img_original = self.load_image("footer.jpg", "#95A5A6", "Landscape")
        self.foot_img_tk = self.resize_image(self.foot_img_original, 450, 260)
        self.foot_img_lbl = tk.Label(self.img_holder, image=self.foot_img_tk, bg="white")
        self.foot_img_lbl.image = self.foot_img_tk; self.foot_img_lbl.pack(fill="both", expand=True)

        text_frame = tk.Frame(footprint_frame, bg="white"); text_frame.pack(side="left", padx=40, pady=50)
        tk.Label(text_frame, text="TRAVEL, THOUGHTFULLY", font=("Helvetica", 9, "bold"), fg=MAROON, bg="white").pack(anchor="w")
        tk.Label(text_frame, text="The best journeys\nleave a lighter footprint.", font=("Georgia", 24), fg=TEXT_DARK, bg="white", justify="left").pack(anchor="w", pady=10)
        tk.Label(text_frame, text=("We partner with local hosts, guides, and makers so every\nstay gives back to the places that make Bhutan\nunforgettable."), font=("Helvetica", 10), fg=TEXT_LIGHT, bg="white", justify="left").pack(anchor="w")

        bottom_bar = tk.Frame(self.content_frame, bg=MAROON, height=80)
        bottom_bar.pack(fill="x", side="bottom"); bottom_bar.pack_propagate(False)
        bottom_bar.columnconfigure(0, weight=0); bottom_bar.columnconfigure(1, weight=1); bottom_bar.columnconfigure(2, weight=0)
        brand_frame = tk.Frame(bottom_bar, bg=MAROON); brand_frame.grid(row=0, column=0, sticky="w", padx=40, pady=12)
        tk.Label(brand_frame, text="BhutanVoyage", font=self.font_footer_brand, bg=MAROON, fg="white").pack(anchor="w")
        tk.Label(brand_frame, text="Plan Himalayan Dreams, Always.", font=self.font_footer_sub, bg=MAROON, fg="#E8C5BE").pack(anchor="w")
        tk.Label(bottom_bar, text="Made for curious people", font=self.font_footer_tag, bg=MAROON, fg=FOOTER_TEXT_SOFT).grid(row=0, column=1)
        
        admin_lbl = tk.Label(bottom_bar, text="Admin Login", font=self.font_footer_admin, bg=MAROON, fg=FOOTER_ADMIN, cursor="hand2")
        admin_lbl.grid(row=0, column=2, sticky="e", padx=40)
        admin_lbl.bind("<Button-1>", lambda _e: self._go_to_admin())
        
        self.bind("<Enter>", self._bind_wheel); self.bind("<Leave>", self._unbind_wheel)

    def create_card(self, parent, idx, d, img_obj):
        card = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#E0E0E0", cursor="hand2")
        card.grid(row=0, column=idx, sticky="nsew", padx=10, pady=10)
        img_lbl = tk.Label(card, bg="#BDC3C7"); img_lbl.pack(fill="x")
        self.dest_imgs_original[idx] = (d["title"], img_obj, img_lbl)
        content = tk.Frame(card, bg="white", padx=10, pady=5); content.pack(fill="both", expand=True)
        title_row = tk.Frame(content, bg="white"); title_row.pack(fill="x", pady=(5, 0))
        tk.Label(title_row, text=d["title"], font=self.font_card_title, bg="white", fg=TEXT_DARK).pack(side="left")
        tk.Label(content, text=d["subtitle"], font=("Helvetica", 9), bg="white", fg=TEXT_LIGHT).pack(anchor="w")
        desc = d.get("description", "")
        short = desc if len(desc) <= 90 else desc[:87].rstrip() + "…"
        tk.Label(content, text=short, font=("Helvetica", 8), bg="white", fg=TEXT_LIGHT,
                 wraplength=190, justify="left").pack(anchor="w", pady=(4, 0))
        rating_row = tk.Frame(content, bg="white"); rating_row.pack(fill="x", pady=5)
        r = (d.get("rating") or "").split(" ")[0]
        if r:
            tk.Label(rating_row, text=f"★ {r}", font=("Helvetica", 8, "bold"), bg="white", fg="#F1C40F").pack(side="left")
        tk.Label(rating_row, text=d.get("stay", ""), font=("Helvetica", 8), bg="white", fg=TEXT_LIGHT).pack(side="right")
        for w in (card, img_lbl, content, title_row, rating_row):
            w.bind("<Button-1>", lambda _e, dd=d: self._open_detail(dd))
        return card

    def _open_detail(self, d):
        if callable(self.on_open_detail): self.on_open_detail(d)
        else: self._go_to_destination()


# ==========================================
# WINDOW CONTROLLER
# ==========================================
class App(tk.Tk):
    """Who can see what
        Open to everyone : Home, Destinations (+ each detail page), About us
        Needs a traveller sign-in : anything that starts a booking - the Book Now button, the
                                    Booking menu link, the booking form and both payment pages
        Admin : signs in separately (Admin Login) and cannot make bookings
    """

    def __init__(self):
        super().__init__()
        self.title("BhutanVoyage")
        self.geometry("1100x850")
        self.minsize(360, 500)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.current_page = None
        self.current_user = None     # {'id','name','email','role'} once signed in
        # Set while a visitor is being sent to sign in so we can bring them straight back:
        # {"dest_key": "paro"} (place already chosen) or {"dest_key": None} (came from the menu)
        self.pending_booking = None
        # Same idea for a heart tapped while signed out: the destination key to save once they
        # have signed in (None = nothing waiting).
        self.pending_favourite = None
        # District last chosen on the Destinations page (None = all districts), so a detail page's
        # "Back to destinations" returns to the same list.
        self.destination_district = None

        self.show_home()
        print("--- APP STARTED ---")

    def _swap(self, page_class, **kwargs):
        if page_class is None: return
        if self.current_page is not None:
            self.current_page.destroy()
        try:
            self.current_page = page_class(self.container, **kwargs)
            self.current_page.pack(fill="both", expand=True)
            print(f"Loaded page: {page_class.__name__}")
        except Exception as e:
            import traceback; traceback.print_exc()
            error_frame = tk.Frame(self.container, bg="white"); error_frame.pack(fill="both", expand=True)
            self.current_page = error_frame   # so the next page swap removes it
            tk.Label(error_frame, text="Error Loading Page:", font=("Helvetica", 20, "bold"), fg="red", bg="white").pack(pady=20)
            tk.Label(error_frame, text=str(e), font=("Helvetica", 12), bg="white").pack()

    # ==========================================
    # OPEN PAGES (no sign-in)
    # ==========================================
    def show_home(self):
        self._swap(BhutanApp,
                   on_plan_trip=self.show_all_destinations,      # "Plan Your Trip" -> Destinations
                   on_go_destination=self.show_all_destinations,
                   on_open_detail=self.show_detail,
                   on_go_booking=self.show_booking,         # menu link: asks for sign-in
                   on_go_about=self.show_about,
                   on_admin=self.show_admin_signin)

    def show_destination(self):
        self._swap(DestinationPage,
                   on_home=self.show_home,
                   on_booking=self.show_booking,
                   on_about=self.show_about,
                   on_open_detail=self.show_detail,
                   on_admin=self.show_admin_signin,
                   user=self.current_user,                  # hearts are saved per traveller
                   on_signin_required=self.sign_in_to_favourite,
                   district=self.destination_district,
                   on_district_change=self._remember_district)

    def show_all_destinations(self):
        """Menu / Home entry points start from the mixed "All districts" view."""
        self.destination_district = None
        self.show_destination()

    def _remember_district(self, name):
        self.destination_district = name

    def sign_in_to_favourite(self, dest_key):
        """A heart was tapped by someone who cannot save it: ask them to sign in (admins are told why not)."""
        user = self.current_user
        if user and user.get("role") == "admin":
            messagebox.showinfo("Admin account",
                                "Admin accounts cannot save favourites. Please sign out and use a traveller account.")
            return
        self.pending_booking = None
        self.pending_favourite = dest_key
        self.show_signin()

    def show_detail(self, data):
        self._swap(DetailPage,
                   data=data,
                   on_back=self.show_destination,
                   on_book=self.show_booking,               # Book Now -> form with this place chosen
                   on_home=self.show_home,
                   on_admin=self.show_admin_signin)

    def show_about(self):
        self._swap(AboutUsPage,
                   on_home=self.show_home,
                   on_destination=self.show_all_destinations,
                   on_booking=self.show_booking,
                   on_admin=self.show_admin_signin)

    # ==========================================
    # BOOKING (sign-in needed)
    # ==========================================
    def _require_traveller(self, dest_key=None):
        """True if a traveller is signed in. Otherwise sends the visitor to sign in (remembering
        the place they picked) or explains why an admin cannot book, and returns False."""
        user = self.current_user
        if user and user.get("role") == "admin":
            messagebox.showinfo("Admin account",
                                "Admin accounts cannot make bookings. Please sign out and use a traveller account.")
            return False
        if not user or not user.get("id"):
            self.pending_favourite = None
            self.pending_booking = {"dest_key": dest_key}
            self.show_signin()
            return False
        return True

    def show_booking(self, dest_key=None, prefill=None):
        """The one booking form. dest_key pre-selects a place; prefill restores what the
        traveller already typed when they come back from the payment page."""
        if not self._require_traveller(dest_key or (prefill or {}).get("dest_key")):
            return
        self._swap(BookingPage,
                   on_home=self.show_home,
                   on_destination=self.show_destination,
                   on_about=self.show_about,
                   on_payment=self.show_payment,
                   on_admin=self.show_admin_signin,
                   user=self.current_user,
                   preselect=dest_key,
                   prefill=prefill)

    def show_payment(self, booking):
        """Booking form -> the right payment page, depending on Bhutanese / international."""
        if not self._require_traveller(booking.get("dest_key")):
            return
        if booking.get("residency") == "International":
            self.show_international_payment(booking)
        else:
            self.show_bhutanese_payment(booking)

    def show_international_payment(self, booking):
        self._swap(InternationalPaymentPage,
                   app=self,
                   booking_data=booking,
                   on_back=lambda: self.show_booking(prefill=booking))

    def show_bhutanese_payment(self, booking):
        self._swap(BhutanesePaymentPage,
                   app=self,
                   booking_data=booking,
                   on_back=lambda: self.show_booking(prefill=booking))

    # ==========================================
    # AUTH ROUTING
    # ==========================================
    def _signin_notice(self):
        """e.g. "Sign in to book Tiger's Nest" - shown while a booking is waiting."""
        if self.pending_favourite is not None:
            dest = get_destination(self.pending_favourite)
            return f"Sign in to save {dest['title']} to your favourites" if dest else "Sign in to save your favourite"
        if self.pending_booking is None:
            return None
        dest = get_destination(self.pending_booking.get("dest_key"))
        return f"Sign in to book {dest['title']}" if dest else "Sign in to book your trip"

    def show_signin(self):
        self._swap(SignInPage,
                   on_success=self.handle_login_success,
                   on_create_account=self.show_create_account,
                   on_home=self.cancel_signin,
                   notice=self._signin_notice())

    def show_admin_signin(self):
        """Separate admin sign-in (opened from 'Admin Login' in any footer)."""
        self.pending_booking = None
        self.pending_favourite = None
        self._swap(SignInPage,
                   on_success=self.handle_login_success,
                   on_create_account=self.show_create_account,
                   on_home=self.cancel_signin,
                   admin_mode=True)

    def cancel_signin(self):
        """'Back to Home' on the sign-in page: forget the booking / favourite that was waiting."""
        self.pending_booking = None
        self.pending_favourite = None
        self.show_home()

    def show_create_account(self):
        self._swap(CreateAccountPage,
                   on_success=self.handle_login_success,    # new accounts are signed in straight away
                   on_back=self.show_signin)                # pending booking is kept

    def handle_login_success(self, user):
        """user = {'id','name','email','role'} from database.authenticate()"""
        if not user:
            self.show_signin()
            return
        self.current_user = user
        if user["role"] == "admin":
            self.pending_booking = None
            self.pending_favourite = None
            self.show_admin_dashboard()
        elif self.pending_favourite is not None:
            key, self.pending_favourite = self.pending_favourite, None
            try:
                add_favourite(user["id"], key)           # the heart they tapped before signing in
            except Exception as e:
                print(f"[favourites] could not save {key}: {e}")
            self.show_destination()                      # back where they were, heart now filled
        elif self.pending_booking is not None:
            pending, self.pending_booking = self.pending_booking, None
            self.show_booking(pending.get("dest_key"))   # back to the form, place already chosen
        else:
            self.show_user_dashboard()

    def logout(self):
        self.current_user = None
        self.pending_booking = None
        self.pending_favourite = None
        self.show_home()

    def show_user_dashboard(self):
        if not self.current_user:
            self.show_signin()
            return
        self._swap(UserDashboard,
                   user=self.current_user,
                   on_home=self.show_home,
                   on_booking=self.show_booking,
                   on_open_detail=self.show_detail,         # a saved place opens its page
                   on_logout=self.logout)

    def show_admin_dashboard(self):
        # Only a signed-in admin may open this page
        if not self.current_user or self.current_user.get("role") != "admin":
            self.show_admin_signin()
            return
        self._swap(AdminDashboard, admin=self.current_user, on_logout=self.logout)


if __name__ == "__main__":
    # Create / upgrade the database (users + bookings tables, hashed passwords, admin account)
    init_db()

    app = App()
    app.mainloop()
