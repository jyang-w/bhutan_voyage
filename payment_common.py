"""payment_common.py - pieces shared by the Bhutanese and international payment pages."""
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk

from booking_utils import format_money

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"

MAROON = "#A71930"
DARK = "#252525"
WHITE = "#FFFFFF"
BORDER = "#D1D5DB"
TEXT_MUTED = "#6B7280"
ERROR_RED = "#DC2626"
OK_GREEN = "#0B5D3B"

FONT_TITLE = ("Georgia", 22, "bold")
FONT_HEADING = ("Georgia", 15, "bold")
FONT_SUB = ("Helvetica", 11)
FONT_BODY = ("Helvetica", 10)
FONT_BODY_BOLD = ("Helvetica", 10, "bold")


def load_img(filename, size):
    try:
        with Image.open(IMAGE_DIR / filename) as img:
            return ImageTk.PhotoImage(img.convert("RGB").resize(size, Image.Resampling.LANCZOS))
    except Exception:
        return None


def build_footer(page, app):
    footer = tk.Frame(page, bg=MAROON, padx=24, pady=14)
    footer.pack(side="bottom", fill="x", padx=24, pady=(0, 20))
    footer.columnconfigure(0, weight=1)
    footer.columnconfigure(1, weight=1)
    footer.columnconfigure(2, weight=0)
    tk.Label(footer, text="BhutanVoyage", bg=MAROON, fg=WHITE,
             font=("Georgia", 15, "bold")).grid(row=0, column=0, sticky="w")
    tk.Label(footer, text="Plan Himalayan Dreams, Always.", bg=MAROON,
             fg="#E8C5BE", font=("Georgia", 9, "italic")).grid(row=1, column=0, sticky="w")
    tk.Label(footer, text="Made for curious people", bg=MAROON,
             fg="#E6B0AA", font=("Arial", 9)).grid(row=0, column=1, rowspan=2, sticky="e", padx=16)
    admin = tk.Label(footer, text="Admin Login", bg=MAROON, fg="#F5DEB3",
                     font=("Arial", 9, "bold"), cursor="hand2")
    admin.grid(row=0, column=2, rowspan=2, sticky="e")
    admin.bind("<Button-1>", lambda _e: app.show_admin_signin())


def build_scroll_body(page, bg):
    """Scrollable middle area. Returns (canvas, content_frame).
    The wheel is bound to the widgets themselves (not bind_all) so nothing is left behind
    when the page is closed."""
    canvas = tk.Canvas(page, bg=bg, highlightthickness=0)
    sb = tk.Scrollbar(page, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    content = tk.Frame(canvas, bg=bg)
    win = canvas.create_window((0, 0), window=content, anchor="nw")
    content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width))
    return canvas, content


def bind_wheel(widget, canvas):
    """Make the mouse wheel scroll `canvas` from anywhere inside `widget`."""
    def wheel(e):
        if getattr(e, "num", None) == 4:
            canvas.yview_scroll(-1, "units")
        elif getattr(e, "num", None) == 5:
            canvas.yview_scroll(1, "units")
        elif getattr(e, "delta", 0):
            canvas.yview_scroll(-1 if e.delta > 0 else 1, "units")

    def visit(w):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            w.bind(seq, wheel, add="+")
        for child in w.winfo_children():
            visit(child)
    visit(widget)


def build_summary(parent, b, accent):
    """Read-only booking summary - the traveller already chose all of this on the booking form."""
    box = tk.Frame(parent, bg=WHITE, padx=25, pady=20, highlightbackground=BORDER, highlightthickness=1)
    tk.Label(box, text="Your booking", font=FONT_HEADING, bg=WHITE, fg=accent).pack(anchor="w", pady=(0, 12))

    total = float(b["per_person"]) * int(b["travellers"])
    n = int(b["travellers"])
    rows = [
        ("Destination", b["place"]),
        ("Travel date", b["date"]),
        ("Traveller", f"{b['name']}  ({b['email']})"),
        ("Price per person", format_money(b["currency"], b["per_person"])),
        ("Travellers", f"{n} {'person' if n == 1 else 'people'}"),
    ]
    for label, value in rows:
        r = tk.Frame(box, bg=WHITE)
        r.pack(fill="x", pady=3)
        tk.Label(r, text=label, bg=WHITE, fg=TEXT_MUTED, font=FONT_SUB).pack(side="left")
        tk.Label(r, text=value, bg=WHITE, fg=DARK, font=FONT_BODY_BOLD).pack(side="right")
    tk.Frame(box, bg=BORDER, height=1).pack(fill="x", pady=8)
    r = tk.Frame(box, bg=WHITE)
    r.pack(fill="x")
    tk.Label(r, text="Total to pay", bg=WHITE, fg=DARK, font=FONT_HEADING).pack(side="left")
    tk.Label(r, text=format_money(b["currency"], total), bg=WHITE, fg=accent,
             font=FONT_HEADING).pack(side="right")
    return box
