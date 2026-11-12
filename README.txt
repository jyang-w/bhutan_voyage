BhutanVoyage - how it works now
===============================
Run:   python main.py        (needs: pip install pillow)

Who can see what
  Open to everyone     Home, Destinations (and each destination's page), About us
  Traveller sign-in    Anything that starts a booking: the "Book Now" button, the "Booking"
                       menu link, the booking form and both payment pages.
                       If someone is not signed in they see the sign-in page with
                       "Sign in to book Tiger's Nest". After they sign in (or create an
                       account) they land on the booking form with that place already chosen.
  Admin                Separate sign-in ("Admin Login" in the footer). Cannot make bookings,
                       and the admin account is refused on the traveller sign-in form.

Customer flow
  Destinations -> a destination -> Book Now -> [sign in if needed] -> Booking form
  -> Payment page (Bhutanese or international, chosen on the form) -> Submit payment
  -> booking saved as PENDING -> traveller dashboard.
  The booking form shows the price per person and a live total. "Back" from the payment page
  returns to the form with everything still filled in.

Favourites and Bucket List (saved in the database, per traveller)
  Tables: favourites and bucket_list (user, destination key). Created automatically on start.
  Heart on Destinations   Signed in: saves / removes a favourite and shows filled when you come
                          back. Not signed in: asks them to sign in ("Sign in to save Tiger's
                          Nest to your favourites"); after signing in the heart is saved and they
                          land back on Destinations. Admin accounts cannot save favourites.
  Dashboard               Favourites and Bucket List both read from the database. Each entry opens
                          that destination's page; "x" removes it. "+ Add" is a drop-down of the
                          real destinations, so names always match the catalog.
  Tests                   python -m unittest test_saved_places -v

Payment pages (nothing is charged - the app only checks the format, the admin confirms by hand)
  Bhutanese      Pick a bank; the account number must be digits only and exactly:
                 BoB 9, BNB 9, DK Bank 11, Druk PNB 14. Live counter ("10 / 11"). Submit stays
                 disabled until the length is right (re-checked if the bank is changed) and a
                 transaction / journal number is entered. Only the last 4 digits of the account
                 number are saved, plus the transaction number.
  International  Debit card: 16 digits that pass the card checksum (Luhn), expiry MM/YY not in
                 the past, 3-digit CVV. Only the last 4 digits are saved; the full number and
                 CVV are discarded. PayPal: PayPal email + PayPal transaction ID.

Destinations by district (77 places, all 20 dzongkhags)
  Top menu "Destination" is a drop-down: "All districts" (the default mixed view), then the 20
  districts A-Z with how many places each has. Picking one filters the cards; the search box
  works inside the chosen district, and "Show all districts" clears it. "Back to destinations"
  from a place returns to the same district.
  Booking form      Pick the District first, then the Place (the place list only shows that district).
  Where the places live
                    The original 12 (with their photos) are in catalog.py. The 65 added places are in
                    places_data.py, one row each: key, title, district, tagline, stay, price, text,
                    three highlights. Edit or add rows there.
  Photos            Places without a photo show a neutral "Photo coming soon" card. To add one, save the
                    file in images/ named after the place's key, e.g. images/rinpung-dzong.jpg
                    (.jpg .jpeg .png .webp all work). No code change needed; it shows on next start.
                    places_to_confirm.csv lists every key and the file name to use.
  PLACEHOLDER PRICES  The prices of the 65 added places are placeholders. Confirm each one (the csv has a
                    column for it) and edit it in places_data.py before taking real bookings.
  Tests             python -m unittest test_catalog -v

Prices
  Destination prices live in ONE place: catalog.py (person_price, in Nu.) for the original 12 places and
  places_data.py for the added ones.
  International travellers see the same price converted to USD - set the rate (NU_PER_USD) or
  fixed dollar prices (USD_PRICE_OVERRIDE) in pricing.py.

Admin flow
  Footer "Admin Login" -> email: admin + password.
  The admin dashboard lists every booking. Check the payment in your bank app / PayPal, then
  press "Confirm payment" (or "Reject" with a reason).

FIRST THING TO DO: sign in as admin (default password: admin123) and press
"Change password". You can also set BHUTAN_ADMIN_PASSWORD before the very
first run on a new database.

Real QR code: save your merchant QR as images/payment_qr.png and the
Bhutanese payment page will show it instead of the example QR.

Notes
  * Card payments are NOT processed. Real card or PayPal charging needs a payment gateway
    (Stripe, PayPal Checkout) - a separate project.
  * Keep bhutan_voyage.db together with the app: it holds users + bookings. The app adds the
    new "notes" column to your existing database automatically on first start.
  * payment_options.py (the old "choose international or Bhutanese" page) is no longer used;
    you can delete it.
