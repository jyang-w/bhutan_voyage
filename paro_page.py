# paro_page.py  -  Destination detail page (an in-app page, not a separate window)
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw, ImageFont

import place_images
from catalog import dzongkhag_of

# =====================================================
# COLOURS (matching the Home page)
# =====================================================
WHITE = "#FFFFFF"
DARK = "#2C3E50"
GREY = "#7F8C8D"
MAROON = "#7B241C"
DARK_MAROON = "#5C1A14"
BORDER = "#DED9D0"
CREAM = "#F7F2E7"
PIN_GOLD = "#E0A22C"
STAR_GOLD = "#E5A100"

FOOTER_TEXT_SOFT = "#E6B0AA"
FOOTER_ADMIN = "#F5DEB3"
FOOTER_SUB = "#E8C5BE"

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"


def _wheel_delta(event):
    """Normalise the mouse-wheel delta across platforms."""
    if getattr(event, "num", None) == 4:
        return -1
    if getattr(event, "num", None) == 5:
        return 1
    if getattr(event, "delta", 0):
        return -int(event.delta / 120) if abs(event.delta) >= 120 else -event.delta
    return 0


def _make_rounded_pill(w, h, r, fill_rgba, outline_rgba):
    pill = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle((0, 0, w - 1, h - 1), radius=r,
                                           fill=fill_rgba, outline=outline_rgba, width=1)
    return pill


def _make_gold_pin(size):
    pin = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(pin)
    cx = size / 2
    r = size * 0.34
    top = size * 0.06
    d.ellipse((cx - r, top, cx + r, top + 2 * r), fill=PIN_GOLD, outline=PIN_GOLD)
    d.polygon([(cx - r * 0.75, top + 1.5 * r), (cx + r * 0.75, top + 1.5 * r), (cx, size * 0.98)], fill=PIN_GOLD)
    inner = r * 0.42
    cy = top + r
    d.ellipse((cx - inner, cy - inner, cx + inner, cy + inner), fill=(255, 255, 255, 255))
    return pin


def _try_load_font(px):
    for name in ("DejaVuSans-Bold.ttf", "Arial.ttf", "Helvetica.ttc", "arial.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except Exception:
            continue
    return ImageFont.load_default()


# =====================================================
# DETAIL PAGE
# =====================================================
class DetailPage(tk.Frame):
    """One destination. "Book Now" opens the booking form with this place already chosen."""

    def __init__(self, parent, data, on_back=None, on_book=None, on_home=None, on_admin=None, **kwargs):
        super().__init__(parent, bg=WHITE, **kwargs)
        self.data = data
        self.on_back = on_back
        self.on_book = on_book
        self.on_home = on_home
        self.on_admin = on_admin
        self.photos = {}
        self._hero_ready = False

        self._build_header()
        self._build_body()

    # ---------------- header ----------------
    def _build_header(self):
        header = tk.Frame(self, bg=WHITE, height=90)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        header.columnconfigure(0, weight=0)
        header.columnconfigure(1, weight=1)
        header.columnconfigure(2, weight=0)

        logo = None
        try:
            with Image.open(IMAGE_DIR / "logo.jpg") as img:
                img = img.convert("RGBA")
                img.thumbnail((60, 60), Image.Resampling.LANCZOS)
                self.photos["logo"] = ImageTk.PhotoImage(img)
            logo = tk.Label(header, image=self.photos["logo"], bg=WHITE, cursor="hand2")
        except Exception:
            logo = tk.Label(header, text="BhutanVoyage", font=("Helvetica", 18, "bold"),
                            fg=MAROON, bg=WHITE, cursor="hand2")
        logo.grid(row=0, column=0, sticky="w", padx=30, pady=15)
        logo.bind("<Button-1>", lambda _e: self.on_home() if callable(self.on_home) else None)

        tk.Button(header, text="\u2190  Back to destinations",
                  command=self.on_back if callable(self.on_back) else None,
                  font=("Georgia", 11, "bold"), fg=MAROON, bg=WHITE, activebackground=WHITE,
                  relief="flat", cursor="hand2").grid(row=0, column=2, sticky="e", padx=30, pady=15)

    # ---------------- body ----------------
    def _build_body(self):
        data = self.data
        outer = tk.Frame(self, bg=WHITE)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg=WHITE, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(self.canvas, bg=WHITE)
        self.body_window = self.canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # ---- hero image ----
        self.image_label = tk.Label(body, bg=WHITE)
        self.image_label.pack(fill="x", padx=32, pady=(8, 8))
        try:                                   # the photo, or the "Photo coming soon" card if there is none yet
            self._render_hero(650)
            self._hero_ready = True
        except Exception as exc:
            self.image_label.configure(
                text=f"{data['title']} image could not be loaded.", fg=MAROON, font=("Arial", 12), height=5)
            print(f"[detail image error] {data['key']}: {exc}")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # ---- text ----
        tk.Label(body, text=f"{dzongkhag_of(data)} District, Bhutan", font=("Arial", 12), fg=GREY, bg=WHITE,
                 anchor="w").pack(fill="x", padx=32, pady=(0, 2))

        title_row = tk.Frame(body, bg=WHITE)
        title_row.pack(fill="x", padx=32, pady=(0, 6))
        tk.Label(title_row, text=data["title"], font=("Georgia", 30, "bold"), bg=WHITE, fg=DARK,
                 anchor="w", justify="left", wraplength=700).pack(side="left")
        if data.get("rating"):                 # new places have no reviews yet, so no stars
            rating_box = tk.Frame(title_row, bg=WHITE)
            rating_box.pack(side="right")
            tk.Label(rating_box, text="\u2605", font=("Arial", 20), fg=STAR_GOLD, bg=WHITE).pack(side="left", padx=(0, 8))
            tk.Label(rating_box, text=data["rating"], font=("Arial", 14), fg=DARK, bg=WHITE).pack(side="left")

        tk.Label(body, text=data["subtitle"], font=("Georgia", 14, "italic"), bg=WHITE, fg=DARK,
                 anchor="w").pack(fill="x", padx=32, pady=(4, 10))
        tk.Label(body, text=data["description"], font=("Georgia", 13), bg=WHITE, fg=GREY,
                 justify="left", anchor="w", wraplength=900).pack(fill="x", padx=32, pady=(0, 16))

        details = tk.Frame(body, bg=WHITE)
        details.pack(anchor="w", padx=32, pady=(0, 18))

        def detail_column(heading, value):
            col = tk.Frame(details, bg=WHITE)
            tk.Label(col, text=heading, font=("Arial", 12), bg=WHITE, fg=GREY).pack(anchor="w")
            tk.Label(col, text=value, font=("Arial", 15, "bold"), bg=WHITE, fg=DARK).pack(anchor="w")
            tk.Frame(col, bg=BORDER, height=1, width=140).pack(anchor="w", pady=(7, 0))
            return col

        detail_column("Ideal stay", data["stay"]).pack(side="left", padx=(0, 45))
        detail_column("per person", f"Nu. {data['person_price']}").pack(side="left")

        tk.Button(body, text="Book Now   \u279c", command=self._book,
                  font=("Arial", 14, "bold"), bg=MAROON, fg=WHITE,
                  activebackground=DARK_MAROON, activeforeground=WHITE,
                  relief="flat", cursor="hand2", padx=24, pady=11).pack(anchor="w", padx=32, pady=(0, 22))

        # ---- highlights ----
        section = tk.Frame(body, bg=CREAM)
        section.pack(fill="x", pady=(6, 0))
        tk.Label(section, text="WORTH MAKING TIME FOR", font=("Arial", 11, "bold"), bg=CREAM,
                 fg=MAROON).pack(anchor="w", padx=32, pady=(20, 6))
        tk.Label(section, text=f"Highlights of {data['title']}", font=("Georgia", 24), bg=CREAM,
                 fg=DARK).pack(anchor="w", padx=32, pady=(0, 16))
        cards = tk.Frame(section, bg=CREAM)
        cards.pack(fill="x", padx=24, pady=(0, 28))
        for heading, desc in data["highlights"]:
            card = tk.Frame(cards, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=8)
            tk.Label(card, text="\u2713", font=("Arial", 16, "bold"), fg=MAROON, bg=WHITE).pack(anchor="w", padx=14, pady=(12, 4))
            tk.Label(card, text=heading, font=("Arial", 13, "bold"), bg=WHITE, fg=DARK,
                     wraplength=230, justify="left").pack(anchor="w", padx=14)
            tk.Label(card, text=desc, font=("Arial", 11), bg=WHITE, fg=GREY,
                     wraplength=230, justify="left").pack(anchor="w", padx=14, pady=(6, 16))

        self._build_footer(body)

        # mouse wheel: bind to the widgets themselves (nothing is left behind when the page closes)
        self.update_idletasks()
        self._bind_wheel(self.canvas)
        self._bind_wheel(body)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _build_footer(self, parent):
        footer = tk.Frame(parent, bg=MAROON, height=80)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        footer.columnconfigure(0, weight=0)
        footer.columnconfigure(1, weight=1)
        footer.columnconfigure(2, weight=0)
        brand = tk.Frame(footer, bg=MAROON)
        brand.grid(row=0, column=0, sticky="w", padx=40, pady=12)
        tk.Label(brand, text="BhutanVoyage", font=("Georgia", 15, "bold"), bg=MAROON, fg=WHITE).pack(anchor="w")
        tk.Label(brand, text="Plan Himalayan Dreams, Always.", font=("Georgia", 10, "italic"),
                 bg=MAROON, fg=FOOTER_SUB).pack(anchor="w")
        tk.Label(footer, text="Made for curious people", font=("Helvetica", 10), bg=MAROON,
                 fg=FOOTER_TEXT_SOFT).grid(row=0, column=1)
        admin = tk.Label(footer, text="Admin Login", font=("Helvetica", 10, "bold"), bg=MAROON,
                         fg=FOOTER_ADMIN, cursor="hand2")
        admin.grid(row=0, column=2, sticky="e", padx=40)
        admin.bind("<Button-1>", lambda _e: self.on_admin() if callable(self.on_admin) else None)

    def _bind_wheel(self, widget):
        def on_wheel(e):
            self.canvas.yview_scroll(_wheel_delta(e), "units")
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            widget.bind(seq, on_wheel, add="+")
        for child in widget.winfo_children():
            self._bind_wheel(child)

    # ---------------- behaviour ----------------
    def _book(self):
        if callable(self.on_book):
            self.on_book(self.data["key"])

    def _on_canvas_resize(self, event):
        self.canvas.itemconfigure(self.body_window, width=event.width)
        if self._hero_ready:
            self._render_hero(max(360, min(event.width - 80, 720)))

    def _render_hero(self, width):
        width = max(360, min(width, 720))
        height = int(width * 0.44)
        fitted = place_images.load(self.data, width, height).convert("RGBA")
        mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=20, fill=255)
        rounded = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        rounded.paste(fitted, (0, 0), mask)

        text = self.data["location"]
        font_px = max(11, int(height * 0.062))
        fnt = _try_load_font(font_px)
        bbox = ImageDraw.Draw(Image.new("RGBA", (10, 10))).textbbox((0, 0), text, font=fnt)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = 10, 5
        pin_size = int(font_px * 1.10)
        gap = 6
        pill_w = pad_x + pin_size + gap + text_w + pad_x
        pill_h = max(pin_size + pad_y * 2, text_h + pad_y * 2 + 2)

        pill = _make_rounded_pill(pill_w, pill_h, pill_h // 2, (80, 80, 80, 200), (60, 60, 60, 220))
        pin = _make_gold_pin(pin_size)
        pill.paste(pin, (pad_x, (pill_h - pin_size) // 2), pin)
        label_layer = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
        ImageDraw.Draw(label_layer).text((pad_x + pin_size + gap, (pill_h - text_h) // 2 - bbox[1]),
                                         text, font=fnt, fill=(255, 255, 255, 255))
        pill = Image.alpha_composite(pill, label_layer)
        margin = 11
        rounded.alpha_composite(pill, (margin, height - pill_h - margin))

        photo = ImageTk.PhotoImage(rounded)
        self.photos["hero"] = photo
        self.image_label.configure(image=photo)
        self.image_label.image = photo


# =====================================================
# STANDALONE RUNNER (python paro_page.py)
# =====================================================
if __name__ == "__main__":
    from catalog import get_destination

    root = tk.Tk()
    root.title("BhutanVoyage")
    root.geometry("1100x850")
    DetailPage(root, get_destination("trongsa"),
               on_back=root.destroy,
               on_book=lambda key: print("Book Now ->", key)).pack(fill="both", expand=True)
    root.mainloop()
