"""pricing.py - price per person for a destination, in Nu. (Bhutanese) or USD (international).

The Ngultrum price lives in catalog.py (person_price). International travellers are shown the
same price converted to US dollars.

EDIT THESE TWO THINGS to match your business:
  * NU_PER_USD       - the exchange rate used for the conversion.
  * USD_PRICE_OVERRIDE - set a fixed dollar price for a destination instead of converting,
                         e.g.  {"paro": 120, "thimphu": 90}
"""
from catalog import nu_per_person

NU_PER_USD = 85.0
USD_PRICE_OVERRIDE = {}

BHUTANESE = "Bhutanese"
INTERNATIONAL = "International"


def price_per_person(dest, residency):
    """Return (currency, amount) where currency is 'Nu.' or 'USD'."""
    nu = nu_per_person(dest)
    if residency == INTERNATIONAL:
        usd = USD_PRICE_OVERRIDE.get(dest["key"])
        if usd is None:
            usd = max(1, round(nu / NU_PER_USD))
        return "USD", float(usd)
    return "Nu.", nu
