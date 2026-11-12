"""booking_utils.py - helpers shared by the payment pages and the dashboards."""
import re
from datetime import date
from tkinter import messagebox

from database import create_booking

EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def parse_price(price_text):
    """'Nu. 5,000' -> ('Nu.', 5000.0);  '$2,500' -> ('USD', 2500.0)"""
    m = re.search(r"\d[\d,]*(?:\.\d+)?", price_text)
    amount = float(m.group().replace(",", "")) if m else 0.0
    currency = "USD" if "$" in price_text else "Nu."
    return currency, amount


def parse_travellers(text):
    """'2 people' / '3 travellers' / '10+ travellers' -> int"""
    m = re.search(r"\d+", str(text))
    return int(m.group()) if m else 1


def travellers_label(n):
    return "1 person" if n == 1 else f"{n} people"


TRAVELLER_CHOICES = [travellers_label(n) for n in range(1, 11)]


def format_money(currency, amount):
    amount = float(amount)
    text = f"{amount:,.0f}" if amount == int(amount) else f"{amount:,.2f}"
    return f"${text} USD" if currency == "USD" else f"Nu. {text}"


def validate_traveller_details(name, email, date_text, travellers_text):
    """Returns (ok, error_message, cleaned_dict)."""
    name, email, date_text = name.strip(), email.strip(), date_text.strip()
    if not name:
        return False, "Please enter the traveller's full name.", None
    if not EMAIL_RE.fullmatch(email):
        return False, "Please enter a valid email address.", None
    try:
        travel_date = date.fromisoformat(date_text)
    except ValueError:
        return False, "Enter the travel date as YYYY-MM-DD, for example 2026-12-25.", None
    if travel_date < date.today():
        return False, "The travel date cannot be in the past.", None
    n = parse_travellers(travellers_text)
    if n < 1:
        return False, "Please choose the number of travellers.", None
    return True, "", {"name": name, "email": email, "date": travel_date.isoformat(), "travellers": n}


def submit_booking(app, b, payment_method, payment_reference):
    """Save the booking as Pending, tell the traveller, and open their dashboard.

    b = the dict built by the booking form: name, email, date (YYYY-MM-DD), travellers (int),
        dzongkhag, place, package, currency ('Nu.' or 'USD'), per_person, notes
    """
    user = getattr(app, "current_user", None)
    if not user or not user.get("id"):
        messagebox.showwarning("Sign in required", "Please sign in to complete your booking.")
        app.show_signin()
        return False
    if user.get("role") == "admin":
        messagebox.showinfo("Admin account", "Admin accounts cannot make bookings.")
        return False

    total = float(b["per_person"]) * int(b["travellers"])
    ok, result = create_booking(
        user_id=user["id"],
        traveller_name=b["name"],
        traveller_email=b["email"],
        dzongkhag=b["dzongkhag"],
        place=b["place"],
        package=b["package"],
        travel_date=b["date"],
        travellers=b["travellers"],
        currency=b["currency"],
        amount=total,
        payment_method=payment_method,
        payment_reference=payment_reference,
        notes=b.get("notes"),
    )
    if not ok:
        messagebox.showerror("Booking failed", result)
        return False

    messagebox.showinfo(
        "Payment submitted",
        f"Thank you! Your booking has been received.\n\n"
        f"Reference:  {result}\n"
        f"Trip:  {b['place']}\n"
        f"Travel date:  {b['date']}\n"
        f"Travellers:  {b['travellers']}\n"
        f"Total:  {format_money(b['currency'], total)}\n\n"
        f"Status: PENDING.\nOur team will check your payment and confirm your booking. "
        f"You can follow its status on your dashboard.",
    )
    app.show_user_dashboard()
    return True
