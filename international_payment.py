import tkinter as tk
from tkinter import messagebox

from payment_common import (MAROON, DARK, WHITE, BORDER, TEXT_MUTED, ERROR_RED,
                            FONT_TITLE, FONT_HEADING, FONT_SUB, FONT_BODY, FONT_BODY_BOLD,
                            build_footer, build_scroll_body, bind_wheel, build_summary)
from booking_utils import submit_booking
from payment_rules import (only_ascii_digits, format_card_number, format_expiry,
                           card_errors, paypal_errors)

PAGE_BG = "#F4F7F9"
BLUE = "#0759A6"
LIGHT_BLUE = "#EAF4FC"

CARD = "Debit card"
PAYPAL = "PayPal"


class InternationalPaymentPage(tk.Frame):
    """Payment for international travellers (USD).

    Booking details are read-only (chosen on the booking form). The traveller picks Debit card
    or PayPal. The app only CHECKS the format - it never charges anything. For cards only the
    last 4 digits are saved; the full number and the CVV are thrown away.
    """

    def __init__(self, parent, app, booking_data=None, on_back=None):
        super().__init__(parent, bg=PAGE_BG)
        self.app = app
        self.booking = booking_data or {}
        self.on_back = on_back

        self.method = tk.StringVar(value=CARD)
        self.card_var = tk.StringVar()
        self.expiry_var = tk.StringVar()
        self.cvv_var = tk.StringVar()
        self.pp_email_var = tk.StringVar()
        self.pp_txn_var = tk.StringVar()
        self._formatting = False

        build_footer(self, self.app)

        top_bar = tk.Frame(self, bg=PAGE_BG, pady=15, padx=20)
        top_bar.pack(side="top", fill="x")
        tk.Button(top_bar, text="<-- Back to booking form",
                  command=self.on_back if callable(self.on_back) else None,
                  bg=PAGE_BG, fg=BLUE, font=("Helvetica", 12, "bold"),
                  relief="flat", cursor="hand2", activebackground=PAGE_BG).pack(anchor="w")

        self.canvas, content = build_scroll_body(self, PAGE_BG)
        wrap = tk.Frame(content, bg=PAGE_BG)
        wrap.pack(fill="x", padx=50, pady=(10, 30))

        banner = tk.Frame(wrap, bg=BLUE, padx=25, pady=22)
        banner.pack(fill="x", pady=(0, 20))
        tk.Label(banner, text="International Traveller", font=FONT_TITLE, bg=BLUE, fg=WHITE).pack(anchor="w")
        tk.Label(banner, text="Pay in US dollars by debit card or PayPal.", font=FONT_SUB,
                 bg=BLUE, fg="#BFDBFE").pack(anchor="w", pady=(5, 0))

        build_summary(wrap, self.booking, BLUE).pack(fill="x", pady=(0, 20))

        cols = tk.Frame(wrap, bg=PAGE_BG)
        cols.pack(fill="x")
        cols.columnconfigure(0, weight=1, uniform="c")
        cols.columnconfigure(1, weight=1, uniform="c")
        self._build_method_box(cols)
        self._build_details_box(cols)

        self.card_var.trace_add("write", self._on_card_typed)
        self.expiry_var.trace_add("write", self._on_expiry_typed)
        self._show_method()
        bind_wheel(self, self.canvas)

    # ---------------- layout ----------------
    def _build_method_box(self, parent):
        box = tk.LabelFrame(parent, text=" 1  Payment method ", bg=WHITE, fg=BLUE,
                            font=FONT_HEADING, padx=20, pady=18)
        box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        for value, desc in ((CARD, "Visa / Mastercard debit card."),
                            (PAYPAL, "Pay from your PayPal account, then enter the transaction ID.")):
            row = tk.Frame(box, bg=WHITE, highlightbackground=BORDER, highlightthickness=1, padx=12, pady=10)
            row.pack(fill="x", pady=6)
            tk.Radiobutton(row, text=value, variable=self.method, value=value, command=self._show_method,
                           bg=WHITE, fg=DARK, font=FONT_BODY_BOLD, activebackground=WHITE,
                           cursor="hand2").pack(anchor="w")
            tk.Label(row, text=desc, bg=WHITE, fg=TEXT_MUTED, font=FONT_BODY,
                     wraplength=300, justify="left").pack(anchor="w", padx=26)

    def _build_details_box(self, parent):
        self.details_box = tk.LabelFrame(parent, text=" 2  Payment details ", bg=WHITE, fg=BLUE,
                                         font=FONT_HEADING, padx=20, pady=18)
        self.details_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # ---- card fields ----
        self.card_frame = tk.Frame(self.details_box, bg=WHITE)
        self.card_entry, self.card_err = self._field(self.card_frame, "Card number", self.card_var,
                                                     placeholder="1234 5678 9012 3456")
        row = tk.Frame(self.card_frame, bg=WHITE)
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)
        left = tk.Frame(row, bg=WHITE)
        left.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        right = tk.Frame(row, bg=WHITE)
        right.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.expiry_entry, self.expiry_err = self._field(left, "Expiry (MM/YY)", self.expiry_var,
                                                         placeholder="MM/YY")
        vcmd = (self.register(self._cvv_ok), "%P")
        self.cvv_entry, self.cvv_err = self._field(right, "CVV", self.cvv_var, show="*", vcmd=vcmd)

        # ---- PayPal fields ----
        self.pp_frame = tk.Frame(self.details_box, bg=WHITE)
        _e, self.pp_email_err = self._field(self.pp_frame, "PayPal email", self.pp_email_var)
        _t, self.pp_txn_err = self._field(self.pp_frame, "PayPal transaction ID", self.pp_txn_var)
        tk.Label(self.pp_frame, text="Pay the total to our PayPal account first, then paste the transaction ID "
                 "from your PayPal receipt. Our team checks it there.", font=("Helvetica", 9), bg=WHITE,
                 fg=TEXT_MUTED, wraplength=320, justify="left").pack(anchor="w")

        self.submit_btn = tk.Button(self.details_box, text="Submit payment", bg=BLUE, fg=WHITE,
                                    font=("Helvetica", 12, "bold"), pady=10, relief="flat", cursor="hand2",
                                    command=self._confirm, activebackground="#06478a", activeforeground=WHITE)
        tk.Label(self.details_box,
                 text="Your card is not charged on this page. Only the last 4 digits are saved - the full "
                      "number and CVV are discarded. Our team confirms your booking by hand.",
                 font=("Helvetica", 9), bg=WHITE, fg=TEXT_MUTED, wraplength=320, justify="left"
                 ).pack(side="bottom", anchor="w", pady=(10, 0))
        self.submit_btn.pack(side="bottom", fill="x", pady=(14, 0))

    def _field(self, parent, label, var, show=None, vcmd=None, placeholder=None):
        tk.Label(parent, text=label, font=FONT_BODY_BOLD, bg=WHITE).pack(anchor="w")
        kw = {"validate": "key", "validatecommand": vcmd} if vcmd else {}
        entry = tk.Entry(parent, textvariable=var, font=FONT_SUB, relief="solid", bd=1, show=show or "", **kw)
        entry.pack(fill="x", pady=(4, 2), ipady=5)
        err = tk.Label(parent, text="", fg=ERROR_RED, bg=WHITE, font=("Arial", 9), wraplength=300, justify="left")
        err.pack(anchor="w", pady=(0, 8))
        return entry, err

    # ---------------- behaviour ----------------
    def _show_method(self):
        self.card_frame.pack_forget()
        self.pp_frame.pack_forget()
        # pack above the Submit button / note (which are packed at the bottom)
        (self.card_frame if self.method.get() == CARD else self.pp_frame).pack(side="top", fill="x")

    def _cvv_ok(self, proposed):
        return only_ascii_digits(proposed) and len(proposed) <= 3

    def _reformat(self, var, formatter, entry):
        """Re-write the field in its tidy form (spaces in the card number, slash in the expiry)."""
        if self._formatting:
            return
        raw = var.get()
        tidy = formatter(raw)
        if tidy != raw:
            self._formatting = True
            try:
                var.set(tidy)
                entry.icursor("end")
            finally:
                self._formatting = False

    def _on_card_typed(self, *_):
        self._reformat(self.card_var, format_card_number, self.card_entry)
        self.card_err.config(text="")

    def _on_expiry_typed(self, *_):
        self._reformat(self.expiry_var, format_expiry, self.expiry_entry)
        self.expiry_err.config(text="")

    def _confirm(self):
        for lbl in (self.card_err, self.expiry_err, self.cvv_err, self.pp_email_err, self.pp_txn_err):
            lbl.config(text="")

        if self.method.get() == CARD:
            errs = card_errors(self.card_var.get(), self.expiry_var.get(), self.cvv_var.get())
            self.card_err.config(text=errs.get("number", ""))
            self.expiry_err.config(text=errs.get("expiry", ""))
            self.cvv_err.config(text=errs.get("cvv", ""))
            if errs:
                return
            last4 = self.card_var.get().replace(" ", "")[-4:]
            method, reference = CARD, f"Card ending {last4}"
        else:
            errs = paypal_errors(self.pp_email_var.get(), self.pp_txn_var.get())
            self.pp_email_err.config(text=errs.get("email", ""))
            self.pp_txn_err.config(text=errs.get("txn", ""))
            if errs:
                return
            method = PAYPAL
            reference = f"PayPal {self.pp_email_var.get().strip()} | Txn {self.pp_txn_var.get().strip()}"

        # Only `reference` (last 4 digits) is passed on; the full number and CVV stay on this page
        # and are discarded with it when the traveller moves on.
        submit_booking(self.app, self.booking, method, reference)
