import tkinter as tk
from tkinter import font
import os
import re
from PIL import Image, ImageTk, ImageDraw

BG_COLOR = "#FFFFFF"
MAROON = "#7B241C"
LIGHT_GRAY = "#F4F4F4"
TEXT_DARK = "#2C3E50"
TEXT_LIGHT = "#7F8C8D"
FOOTER_TEXT_SOFT = "#E6B0AA"
FOOTER_ADMIN = "#F5DEB3"
CARD_GREY = "#D9D9D9"
CARD_LAV = "#ECECF3"
HIGHLIGHT_RED = "#E63946"

IMG_EXTS = (".jpg", ".jpeg", ".png", ".jfif", ".webp", ".bmp", ".gif")

# Notice: The class is now named AboutUsPage and it inherits from tk.Frame
class AboutUsPage(tk.Frame):
    def __init__(self, parent, on_home=None, on_destination=None, on_booking=None, on_admin=None, **kwargs):
        super().__init__(parent, bg=BG_COLOR, **kwargs)
        
        self.on_home = on_home
        self.on_destination = on_destination
        self.on_booking = on_booking
        self.on_admin = on_admin

        self.font_nav = font.Font(family="Georgia", size=12)
        self.font_button = font.Font(family="Georgia", size=11, weight="bold")
        self.font_footer_brand = font.Font(family="Georgia", size=15, weight="bold")
        self.font_footer_sub = font.Font(family="Georgia", size=10, slant="italic")
        self.font_footer_tag = font.Font(family="Helvetica", size=10)
        self.font_footer_admin = font.Font(family="Helvetica", size=10, weight="bold")

        self.f_small = font.Font(family="Georgia", size=11)
        self.f_body = font.Font(family="Georgia", size=12)
        self.f_hero = font.Font(family="Georgia", size=32)
        self.f_h1 = font.Font(family="Georgia", size=26)
        self.f_h2 = font.Font(family="Georgia", size=20)
        self.f_card_t = font.Font(family="Georgia", size=13, weight="bold")
        self.f_icon = font.Font(family="Segoe UI Emoji", size=20)

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.images_dir = os.path.join(self.base_dir, "images")

        self.setup_scrollable_area()
        self.setup_ui()
        self.bind("<Configure>", self.on_window_resize)

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

        self.content_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if self.winfo_exists() and self.canvas.winfo_exists():
            if event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")

    def _normalize_name(self, name):
        s = name.lower().strip()
        root, ext = os.path.splitext(s)
        while ext in IMG_EXTS:
            root, ext = os.path.splitext(root)
        return re.sub(r"[\s_\-]+", "", root)

    def _find_image_path(self, requested_name):
        exact = os.path.join(self.images_dir, requested_name)
        if os.path.exists(exact):
            return exact
        if not os.path.isdir(self.images_dir):
            return None
        target_norm = self._normalize_name(requested_name)
        for f in os.listdir(self.images_dir):
            if not f.lower().endswith(IMG_EXTS):
                continue
            if self._normalize_name(f) == target_norm:
                return os.path.join(self.images_dir, f)
        return None

    def load_image(self, path, fallback_color="#BDC3C7", text=""):
        full_path = self._find_image_path(path)
        if full_path is None:
            return Image.new("RGB", (900, 530), fallback_color)
        try:
            img = Image.open(full_path)
            img.load()
            return img
        except Exception:
            return Image.new("RGB", (900, 530), fallback_color)

    def resize_image(self, img_obj, width, height):
        width, height = max(1, width), max(1, height)
        return ImageTk.PhotoImage(img_obj.resize((width, height), Image.Resampling.LANCZOS))

    def on_window_resize(self, event):
        if event.widget == self:
            self.update_images()

    def update_images(self):
        w = self.content_frame.winfo_width()
        if w <= 1 or not hasattr(self, "about_img_original") or not self.about_img_lbl.winfo_exists():
            return

        img_w = max(1, min(700, w - 80))
        orig_w, orig_h = self.about_img_original.size
        img_h = int(img_w * orig_h / orig_w)
        radius = max(8, int(img_w * 70 / 2209 * 2))

        resized = self.about_img_original.convert("RGB").resize((img_w, img_h), Image.Resampling.LANCZOS)
        mask = Image.new("L", (img_w, img_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, img_w, img_h), radius=radius, fill=255)
        rounded = Image.new("RGB", (img_w, img_h), "white")
        rounded.paste(resized, (0, 0), mask)
        self.about_img_tk = ImageTk.PhotoImage(rounded)
        self.about_img_lbl.config(image=self.about_img_tk)
        self.about_img_lbl.image = self.about_img_tk

    def info_card(self, parent, row, col, icon, title, body, bg):
        card = tk.Frame(parent, bg=bg, padx=15, pady=12)
        card.grid(row=row, column=col, sticky="nsew", padx=15, pady=12)
        tk.Label(card, text=icon, font=self.f_icon, bg=bg, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(card, text=title, font=self.f_card_t, bg=bg, fg=TEXT_DARK).pack(anchor="w")
        lbl = tk.Label(card, text=body, font=self.f_small, bg=bg, fg=TEXT_DARK, justify="left", anchor="w", wraplength=240)
        lbl.pack(anchor="w", fill="x")
        card.bind("<Configure>", lambda e, l=lbl: l.config(wraplength=max(100, e.width - 30)))

    def text_block(self, parent, title, body, title_font=None):
        tk.Label(parent, text=title, font=title_font or self.f_h2, bg=BG_COLOR, fg=TEXT_DARK).pack(pady=(18, 4))
        tk.Label(parent, text=body, font=self.f_body, bg=BG_COLOR, fg=TEXT_DARK, justify="center", wraplength=700).pack()

    def setup_ui(self):
        header_frame = tk.Frame(self.content_frame, bg="white", height=90)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        header_frame.columnconfigure(0, weight=0)
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(2, weight=0)

        logo_img = self.load_image("logo.jpg", MAROON, "Logo")
        self.logo_tk = self.resize_image(logo_img, 60, 60)
        logo_label = tk.Label(header_frame, image=self.logo_tk, bg="white", cursor="hand2")
        logo_label.image = self.logo_tk
        logo_label.grid(row=0, column=0, sticky="w", padx=30, pady=15)
        logo_label.bind("<Button-1>", lambda _e: self.on_home() if callable(self.on_home) else None)

        nav_frame = tk.Frame(header_frame, bg="white")
        nav_frame.grid(row=0, column=1, sticky="ew")
        nav_inner = tk.Frame(nav_frame, bg="white")
        nav_inner.pack(expand=True)

        nav_items = [("Home", self.on_home), ("Destination", self.on_destination), ("Booking", self.on_booking), ("About us", None)]
        for item, cb in nav_items:
            lbl = tk.Label(nav_inner, text=item, font=self.font_nav, fg=MAROON, bg="white", cursor="hand2" if cb else "arrow")
            lbl.pack(side="left", padx=25)
            if cb: lbl.bind("<Button-1>", lambda _e, c=cb: c())

        cta_btn = tk.Button(header_frame, text="Plan Your Trip", command=self.on_destination if callable(self.on_destination) else None,
                            bg=MAROON, fg="white", font=self.font_button, relief="flat", padx=22, pady=10, cursor="hand2",
                            activebackground="#5C1A14", activeforeground="white")
        cta_btn.grid(row=0, column=2, sticky="e", padx=30, pady=15)

        tk.Label(self.content_frame, text="About Bhutan Voyage", font=self.f_small, bg=BG_COLOR, fg=TEXT_DARK).pack(pady=(35, 5))

        hero = tk.Text(self.content_frame, width=28, height=3, bg=BG_COLOR, bd=0, highlightthickness=0, font=self.f_hero, wrap="word", cursor="arrow", fg=TEXT_DARK)
        hero.tag_configure("center", justify="center")
        hero.tag_configure("red", foreground=HIGHLIGHT_RED)
        hero.insert("end", "Your trusted gateway to the\n", "center")
        hero.insert("end", "kingdom", ("center", "red"))
        hero.insert("end", " of the Thunder Dragon.", "center")
        hero.configure(state="disabled")
        hero.pack()

        tk.Label(self.content_frame, text=("We believe every journey to Bhutan should be as magical as the destination itself. Bhutan Voyage was born from a deep love for Bhutan's culture, nature and the happiness it brings."),
                 font=self.f_body, bg=BG_COLOR, fg=TEXT_DARK, justify="center", wraplength=650).pack(pady=20)

        self.about_img_original = self.load_image("about us.jpg", "#8FAE7A", "about us.jpg")
        self.about_img_lbl = tk.Label(self.content_frame, bg=BG_COLOR)
        self.about_img_lbl.pack(pady=20)

        tk.Label(self.content_frame, text="A small idea with a very big view", font=self.f_h1, bg=BG_COLOR, fg=TEXT_DARK).pack(pady=(40, 15))
        self.text_block(self.content_frame, "The beginning", "Bhutan Voyage started as a small collection of stories from travelers who fell in love with Bhutan. What began as sharing personal adventures grew into a mission to help others discover the magic of the Dragon Kingdom.")
        self.text_block(self.content_frame, "Our mission", "To make Bhutan travel accessible, authentic and unforgettable for everyone.")
        self.text_block(self.content_frame, "Our vision", "To be the world's most trusted platform for experiencing the kingdom of Bhutan.")

        tk.Label(self.content_frame, text="Our values.", font=self.f_h1, bg=BG_COLOR, fg=TEXT_DARK).pack(pady=(45, 15))
        values = tk.Frame(self.content_frame, bg=BG_COLOR)
        values.pack(fill="x", padx=100)
        values.columnconfigure(0, weight=1, uniform="v")
        values.columnconfigure(1, weight=1, uniform="v")
        vals = [("🛡", "Authenticity", "We showcase Bhutan as it truly is, preserving its culture, stories and traditions."),
                ("☺", "Happiness", "We believe travel should bring joy and positive transformation to every traveler."),
                ("🌱", "Sustainability", "We promote responsible tourism that protects Bhutan's pristine environment."),
                ("🌐", "Community", "We build a community of travelers who share a genuine love for Bhutan.")]
        for i, (ic, t, b) in enumerate(vals):
            self.info_card(values, i // 2, i % 2, ic, t, b, CARD_GREY)

        tk.Label(self.content_frame, text="We'd love to hear from you", font=self.f_h1, bg=BG_COLOR, fg=TEXT_DARK).pack(pady=(50, 15))
        contact = tk.Frame(self.content_frame, bg=BG_COLOR)
        contact.pack(fill="x", padx=100, pady=(0, 50))
        contact.columnconfigure(0, weight=1, uniform="c")
        contact.columnconfigure(1, weight=1, uniform="c")
        info = [("📍", "Location", "Thimphu, Bhutan"), ("📞", "Phone", "+975 2123 456"), ("✉", "Email", "Hello@BhutanVoyage.com"), ("🕘", "Working hours", "Mon-Fri. 9AM-6PM")]
        for i, (ic, t, b) in enumerate(info):
            self.info_card(contact, i // 2, i % 2, ic, t, b, CARD_LAV)

        bottom_bar = tk.Frame(self.content_frame, bg=MAROON, height=80)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)
        bottom_bar.columnconfigure(0, weight=0)
        bottom_bar.columnconfigure(1, weight=1)
        bottom_bar.columnconfigure(2, weight=0)
        brand_frame = tk.Frame(bottom_bar, bg=MAROON)
        brand_frame.grid(row=0, column=0, sticky="w", padx=40, pady=12)
        tk.Label(brand_frame, text="BhutanVoyage", font=self.font_footer_brand, bg=MAROON, fg="white").pack(anchor="w")
        tk.Label(brand_frame, text="Plan Himalayan Dreams, Always.", font=self.font_footer_sub, bg=MAROON, fg="#E8C5BE").pack(anchor="w")
        tk.Label(bottom_bar, text="Made for curious people", font=self.font_footer_tag, bg=MAROON, fg=FOOTER_TEXT_SOFT).grid(row=0, column=1)
        admin_lbl = tk.Label(bottom_bar, text="Admin Login", font=self.font_footer_admin, bg=MAROON, fg=FOOTER_ADMIN, cursor="hand2")
        admin_lbl.grid(row=0, column=2, sticky="e", padx=40)
        admin_lbl.bind("<Button-1>", lambda _e: self.on_admin() if callable(self.on_admin) else None)

        self.after(100, self.update_images)