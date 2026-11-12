"""payment_rules.py - pure checks for the two payment pages (no screens in here, so they are easy to test).

Nothing here charges anyone. The app only checks that what was typed is well-formed;
the admin confirms the real payment by hand.
"""
import re
from datetime import date

# Bhutanese banks and the exact length of an account number at each one.
BANKS = {
    "Bank of Bhutan (BoB)": 9,
    "Bhutan National Bank (BNB)": 9,
    "DK Bank": 11,
    "Druk PNB": 14,
}
DEFAULT_BANK = "Bank of Bhutan (BoB)"

EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def required_length(bank):
    return BANKS.get(bank, 0)


def only_ascii_digits(text):
    """True for '' or a string of 0-9 only (str.isdigit() also accepts things like '²')."""
    return re.fullmatch(r"[0-9]*", text) is not None


def account_ok(bank, digits):
    return only_ascii_digits(digits) and len(digits) == required_length(bank) > 0


def account_error(bank, digits):
    n = required_length(bank)
    if not digits:
        return f"Enter your {n}-digit account number."
    if not only_ascii_digits(digits):
        return "Account number can only contain digits."
    if len(digits) != n:
        return f"{bank} account numbers have exactly {n} digits."
    return ""


# ---------------- international ----------------
def luhn_ok(number):
    """Standard card checksum. Catches nearly all single-digit typos and swapped neighbours."""
    if not number.isascii() or not number.isdigit():
        return False
    total = 0
    for i, ch in enumerate(reversed(number)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def digits_of(text):
    return re.sub(r"\D", "", text)


def format_card_number(raw):
    """'4111111111111111' -> '4111 1111 1111 1111'  (16 digits max)"""
    d = digits_of(raw)[:16]
    return " ".join(d[i:i + 4] for i in range(0, len(d), 4))


def format_expiry(raw):
    """'1227' -> '12/27'. Up to two digits stay as typed so Backspace works naturally."""
    d = digits_of(raw)[:4]
    return d if len(d) <= 2 else d[:2] + "/" + d[2:]


def card_number_error(text):
    d = text.replace(" ", "")
    if not d:
        return "Enter your card number."
    if not (d.isascii() and d.isdigit()) or len(d) != 16:
        return "Card number must be exactly 16 digits."
    if not luhn_ok(d):
        return "This card number doesn't look right. Please check for typos."
    return ""


def expiry_error(text, today=None):
    today = today or date.today()
    m = re.fullmatch(r"(\d{2})/(\d{2})", text.strip())
    if not m:
        return "Use the format MM/YY."
    month, year = int(m.group(1)), 2000 + int(m.group(2))
    if not 1 <= month <= 12:
        return "Month must be 01 to 12."
    if (year, month) < (today.year, today.month):
        return "This card has expired."
    if year > today.year + 20:
        return "Please check the expiry year."
    return ""


def cvv_error(text):
    if not (text.isascii() and text.isdigit()) or len(text) != 3:
        return "CVV must be 3 digits."
    return ""


def card_errors(number, expiry, cvv, today=None):
    """{'number': msg, 'expiry': msg, 'cvv': msg} - only the fields that have a problem."""
    errs = {
        "number": card_number_error(number),
        "expiry": expiry_error(expiry, today),
        "cvv": cvv_error(cvv),
    }
    return {k: v for k, v in errs.items() if v}


def paypal_errors(email, txn_id):
    errs = {}
    if not EMAIL_RE.fullmatch(email.strip()):
        errs["email"] = "Enter the email address of your PayPal account."
    if not re.fullmatch(r"[A-Za-z0-9]{8,25}", txn_id.strip()):
        errs["txn"] = "PayPal transaction IDs are letters and numbers only (usually 17 characters)."
    return errs
