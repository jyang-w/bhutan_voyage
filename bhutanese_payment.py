import tkinter as tk
from tkinter import ttk, messagebox

from payment_common import (MAROON, DARK, WHITE, BORDER, TEXT_MUTED, ERROR_RED, OK_GREEN,
                            FONT_TITLE, FONT_HEADING, FONT_SUB, FONT_BODY, FONT_BODY_BOLD,
                            load_img, build_footer, build_scroll_body, bind_wheel, build_summary)
from booking_utils import submit_booking
from payment_rules import BANKS, DEFAULT_BANK, required_length, only_ascii_digits, account_ok, account_error

PAGE_BG = "#F4F7F6"
DARK_GREEN = "#0B5D3B"
LIGHT_GREEN = "#E8F4EE"
DISABLED_BG = "#9CA3AF"


class BhutanesePaymentPage(tk.Frame):
    """Payment for Bhutanese travellers (Nu.).

    The booking details are read-only here (set on the booking form). The traveller picks a
    bank, types their account number (digits only, exact length for that bank) and the
    transaction / journal number from their banking app. Nothing is charged by this app -
    the admin matches the transaction number against the bank statement.
    """

    def __init__(self, parent, app, booking_data=None, on_back=None):
        super().__init__(parent, bg=PAGE_BG)
        self.app = app
        self.booking = booking_data or {}
        self.on_back = on_back

        self.bank_var = tk.StringVar(value=DEFAULT_BANK)
        self.acct_var = tk.StringVar()
        self.txn_var = tk.StringVar()
        self.counter_var = tk.StringVar()

        build_footer(self, self.app)

        top_bar = tk.Frame(self, bg=PAGE_BG, pady=15, padx=20)
        top_bar.pack(side="top", fill="x")
        tk.Button(top_bar, text="<-- Back to booking form",
                  command=self.on_back if callable(self.on_back) else None,
                  bg=PAGE_BG, fg=DARK_GREEN, font=("Helvetica", 12, "bold"),
                  relief="flat", cursor="hand2", activebackground=PAGE_BG).pack(anchor="w")

        self.canvas, content = build_scroll_body(self, PAGE_BG)
        wrap = tk.Frame(content, bg=PAGE_BG)
        wrap.pack(fill="x", padx=50, pady=(10, 30))

        banner = tk.Frame(wrap, bg=DARK_GREEN, padx=25, pady=22)
        banner.pack(fill="x", pady=(0, 20))
        tk.Label(banner, text="Bhutanese Traveller", font=FONT_TITLE, bg=DARK_GREEN, fg=WHITE).pack(anchor="w")
        tk.Label(banner, text="Pay in Ngultrum (Nu.) through your bank.", font=FONT_SUB,
                 bg=DARK_GREEN, fg="#A7F3D0").pack(anchor="w", pady=(5, 0))

        build_summary(wrap, self.booking, DARK_GREEN).pack(fill="x", pady=(0, 20))

        cols = tk.Frame(wrap, bg=PAGE_BG)
        cols.pack(fill="x")
        cols.columnconfigure(0, weight=1, uniform="c")
        cols.columnconfigure(1, weight=1, uniform="c")
        self._build_bank_box(cols)
        self._build_pay_box(cols)

        self.bank_var.trace_add("write", self._refresh)
        self.acct_var.trace_add("write", self._refresh)
        self.txn_var.trace_add("write", self._refresh)
        self._refresh()
        bind_wheel(self, self.canvas)

    # ---------------- layout ----------------
    def _build_bank_box(self, parent):
        box = tk.LabelFrame(parent, text=" 1  Your bank ", bg=WHITE, fg=DARK_GREEN,
                            font=FONT_HEADING, padx=20, pady=18)
        box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(box, text="Bank", font=FONT_BODY_BOLD, bg=WHITE).pack(anchor="w")
        ttk.Combobox(box, textvariable=self.bank_var, values=list(BANKS), state="readonly",
                     font=FONT_SUB).pack(fill="x", pady=(4, 14), ipady=4)

        tk.Label(box, text="Your account number", font=FONT_BODY_BOLD, bg=WHITE).pack(anchor="w")
        vcmd = (self.register(self._allow_typing), "%P")
        self.acct_entry = tk.Entry(box, textvariable=self.acct_var, font=FONT_SUB, relief="solid", bd=1,
                                   validate="key", validatecommand=vcmd)
        self.acct_entry.pack(fill="x", pady=(4, 2), ipady=5)
        self.counter_lbl = tk.Label(box, textvariable=self.counter_var, font=FONT_BODY_BOLD,
                                    bg=WHITE, fg=TEXT_MUTED)
        self.counter_lbl.pack(anchor="e")
        self.hint_lbl = tk.Label(box, text="", font=("Helvetica", 9), bg=WHITE, fg=TEXT_MUTED,
                                 justify="left", wraplength=320)
        self.hint_lbl.pack(anchor="w", pady=(2, 0))

    def _build_pay_box(self, parent):
        box = tk.LabelFrame(parent, text=" 2  Scan & pay ", bg=WHITE, fg=DARK_GREEN,
                            font=FONT_HEADING, padx=20, pady=18)
        box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Put your real merchant QR image at images/payment_qr.png and it is shown here.
        qr_photo = load_img("payment_qr.jpg", (150, 150))
        if qr_photo:
            tk.Label(box, text="Scan to pay BhutanVoyage", font=FONT_BODY, bg=WHITE, fg=TEXT_MUTED).pack()
            lbl = tk.Label(box, image=qr_photo, bg=WHITE)
            lbl.image = qr_photo
            lbl.pack(pady=10)
        else:
            tk.Label(box, text="(Example: Bhutan QR)", font=FONT_BODY, bg=WHITE, fg=TEXT_MUTED).pack()
            qr = tk.Canvas(box, width=150, height=150, bg=WHITE, highlightthickness=0)
            qr.pack(pady=10)
            for i in range(0, 150, 10):
                for j in range(0, 150, 10):
                    if (i + j) % 20 == 0:
                        qr.create_rectangle(i, j, i + 10, j + 10, fill="#000", outline="")
            qr.create_rectangle(10, 10, 50, 50, fill=WHITE, outline="#000", width=4)
            qr.create_rectangle(100, 10, 140, 50, fill=WHITE, outline="#000", width=4)
            qr.create_rectangle(10, 100, 50, 140, fill=WHITE, outline="#000", width=4)
        tk.Label(box, text="Open your banking app and scan the QR code.", bg=WHITE,
                 font=FONT_BODY, justify="center").pack()

        tk.Label(box, text="Transaction / Journal No.", font=FONT_BODY_BOLD, bg=WHITE).pack(anchor="w", pady=(14, 0))
        tk.Entry(box, textvariable=self.txn_var, font=FONT_SUB, relief="solid", bd=1).pack(fill="x", pady=(4, 0), ipady=5)
        tk.Label(box, text="Shown in your banking app after you pay. We match it to the bank statement.",
                 font=("Helvetica", 9), bg=WHITE, fg=TEXT_MUTED, justify="left", wraplength=320
                 ).pack(anchor="w", pady=(3, 0))

        self.submit_btn = tk.Button(box, text="Submit payment", bg=DISABLED_BG, fg=WHITE,
                                    font=("Helvetica", 12, "bold"), pady=10, relief="flat",
                                    cursor="hand2", state="disabled", command=self._confirm,
                                    activebackground=DARK_GREEN, activeforeground=WHITE)
        self.submit_btn.pack(fill="x", pady=(16, 0))
        tk.Label(box, text="We do not take money on this page. Our team confirms your payment by hand.",
                 font=("Helvetica", 9), bg=WHITE, fg=TEXT_MUTED, wraplength=320, justify="left"
                 ).pack(anchor="w", pady=(8, 0))

    # ---------------- behaviour ----------------
    def _allow_typing(self, proposed):
        """Digits only. Typing past the bank's length is blocked; deleting is always allowed."""
        if not only_ascii_digits(proposed):
            return False
        n = required_length(self.bank_var.get())
        return len(proposed) <= n or len(proposed) < len(self.acct_var.get())

    def _refresh(self, *_):
        """Re-check the account number against the CURRENT bank, and enable/disable Submit."""
        bank = self.bank_var.get()
        n = required_length(bank)
        digits = self.acct_var.get()
        ok = account_ok(bank, digits)

        self.counter_var.set(f"{len(digits)} / {n}")
        if ok:
            self.counter_lbl.config(fg=OK_GREEN)
            self.hint_lbl.config(text="", fg=TEXT_MUTED)
        elif len(digits) > n:
            self.counter_lbl.config(fg=ERROR_RED)
            self.hint_lbl.config(text=account_error(bank, digits), fg=ERROR_RED)
        else:
            self.counter_lbl.config(fg=TEXT_MUTED)
            self.hint_lbl.config(text=f"{bank} account numbers have {n} digits.", fg=TEXT_MUTED)

        ready = ok and len(self.txn_var.get().strip()) >= 4
        self.submit_btn.config(state="normal" if ready else "disabled",
                               bg=DARK_GREEN if ready else DISABLED_BG)

    def _confirm(self):
        # Check again here - never rely only on the button being enabled.
        bank, digits = self.bank_var.get(), self.acct_var.get()
        if not account_ok(bank, digits):
            messagebox.showwarning("Check account number", account_error(bank, digits))
            return
        txn = self.txn_var.get().strip()
        if len(txn) < 4:
            messagebox.showwarning("Transaction number needed",
                                   "Please pay first, then enter the transaction / journal number "
                                   "from your banking app so we can verify your payment.")
            return
        # Only the last 4 digits of the account number are kept.
        submit_booking(self.app, self.booking,
                       payment_method=f"Bhutan QR / bank ({bank})",
                       payment_reference=f"Txn {txn} | A/C ending {digits[-4:]}")
