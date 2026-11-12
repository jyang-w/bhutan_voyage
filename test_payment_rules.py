import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datetime import date
from payment_rules import *
from pricing import price_per_person
from catalog import get_destination

# Luhn: well-known test numbers pass, a one-digit typo fails
assert luhn_ok("4111111111111111") and luhn_ok("5555555555554444")
assert not luhn_ok("4111111111111112")
assert not luhn_ok("4111111111111121")          # swapped neighbours
assert not luhn_ok("") and not luhn_ok("41a1")
# card number
assert card_number_error("4111 1111 1111 1111") == ""
assert "16 digits" in card_number_error("4111 1111 1111 111")
assert "16 digits" in card_number_error("4111 1111 1111 11111")
assert "typos" in card_number_error("4111 1111 1111 1112")
assert "Enter" in card_number_error("")
# formatting
assert format_card_number("4111111111111111") == "4111 1111 1111 1111"
assert format_card_number("41111") == "4111 1"
assert format_card_number("4111-1111 1111 1111 9999") == "4111 1111 1111 1111"
assert format_expiry("1") == "1" and format_expiry("12") == "12"
assert format_expiry("123") == "12/3" and format_expiry("12/27") == "12/27" and format_expiry("122799") == "12/27"
# expiry (fixed 'today' = 2026-11-10)
t = date(2026, 11, 10)
assert expiry_error("11/26", t) == ""            # this month is still valid
assert expiry_error("10/26", t) == "This card has expired."
assert expiry_error("12/26", t) == "" and expiry_error("01/30", t) == ""
assert expiry_error("00/30", t) and expiry_error("13/30", t) and expiry_error("1/30", t)
assert expiry_error("12/60", t)                  # too far ahead
assert expiry_error("12/99", t)
# cvv
assert cvv_error("123") == "" and cvv_error("12") and cvv_error("1234") and cvv_error("12a") and cvv_error("")
# combined
assert card_errors("4111 1111 1111 1111", "12/28", "123", t) == {}
assert set(card_errors("1", "13/28", "1", t)) == {"number", "expiry", "cvv"}
# banks
assert [required_length(b) for b in BANKS] == [9, 9, 11, 14]
assert account_ok("Bank of Bhutan (BoB)", "123456789") and not account_ok("Bank of Bhutan (BoB)", "12345678")
assert account_ok("DK Bank", "12345678901") and not account_ok("DK Bank", "123456789")     # switching bank re-checks
assert account_ok("Druk PNB", "1"*14) and not account_ok("Druk PNB", "1"*15)
assert not account_ok("DK Bank", "1234567890²") and not account_ok("DK Bank", "")
assert only_ascii_digits("") and only_ascii_digits("007") and not only_ascii_digits("12a") and not only_ascii_digits("²")
assert "exactly 11" in account_error("DK Bank", "123")
# paypal
assert paypal_errors("a@b.com", "5TY05013RG002845M") == {}
assert set(paypal_errors("nope", "x")) == {"email", "txn"}
# pricing
p = get_destination("paro")
assert price_per_person(p, "Bhutanese") == ("Nu.", 3500.0)
cur, usd = price_per_person(p, "International"); assert cur == "USD" and usd == 41.0, usd
print("ALL RULE TESTS PASS")
