"""
database.py - SQLite storage for BhutanVoyage

Tables
------
users     : travellers and the admin (passwords are stored hashed, never in plain text)
bookings  : every booking request + payment submitted by a traveller.
            New bookings start as "Pending"; the admin checks the payment and
            marks them "Confirmed" (or "Rejected").
favourites  : places a traveller hearted (one row per user + destination key)
bucket_list : places a traveller wants to visit one day (same shape as favourites)
"""
import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime

# Always use the database that sits next to this file, no matter which folder
# the app is started from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "bhutan_voyage.db")

BOOKING_STATUSES = ("Pending", "Confirmed", "Rejected", "Cancelled")

# Table names are fixed here (never taken from user input) because they go into SQL text.
SAVED_TABLES = ("favourites", "bucket_list")

_HASH_NAME = "pbkdf2_sha256"
_HASH_ITERATIONS = 200_000
_REF_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O/1/I confusion


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ======================================================================
# PASSWORDS
# ======================================================================
def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _HASH_ITERATIONS)
    return f"{_HASH_NAME}${_HASH_ITERATIONS}${salt.hex()}${digest.hex()}"


def _is_hashed(stored):
    return bool(stored) and stored.startswith(_HASH_NAME + "$")


def verify_password(password, stored):
    if not stored:
        return False
    if _is_hashed(stored):
        try:
            _, iters, salt_hex, hash_hex = stored.split("$")
            digest = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iters)
            )
            return hmac.compare_digest(digest.hex(), hash_hex)
        except (ValueError, TypeError):
            return False
    # Old plain-text row (init_db() converts these, this is just a safety net)
    return hmac.compare_digest(stored.encode("utf-8"), password.encode("utf-8"))


# ======================================================================
# SET-UP / MIGRATION  (safe to run every time the app starts)
# ======================================================================
def init_db():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        """)
        # Columns added later - add them to databases created by the old version
        cols = {r["name"] for r in cur.execute("PRAGMA table_info(users)")}
        if "phone" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN phone TEXT DEFAULT ''")
        if "created_at" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
        cur.execute("UPDATE users SET created_at = ? WHERE created_at IS NULL", (_now(),))

        cur.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(id),
                traveller_name TEXT NOT NULL,
                traveller_email TEXT NOT NULL,
                dzongkhag TEXT,
                place TEXT NOT NULL,
                package TEXT,
                travel_date TEXT NOT NULL,
                travellers INTEGER NOT NULL,
                currency TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT,
                payment_reference TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                admin_note TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        bcols = {r["name"] for r in cur.execute("PRAGMA table_info(bookings)")}
        if "notes" not in bcols:                       # traveller's "anything we should know?"
            cur.execute("ALTER TABLE bookings ADD COLUMN notes TEXT")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status)")

        # Saved places: the Favourites hearts and the dashboard's Bucket List.
        # dest_key is the key from catalog.py (e.g. "paro"). One row per user + place.
        for table in SAVED_TABLES:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    dest_key TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE (user_id, dest_key)
                )
            """)
            cur.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_user ON {table}(user_id)")

        # Convert any plain-text passwords from the old version to hashes
        for row in cur.execute("SELECT id, password FROM users").fetchall():
            if not _is_hashed(row["password"]):
                cur.execute("UPDATE users SET password = ? WHERE id = ?",
                            (hash_password(row["password"]), row["id"]))

        # Make sure the admin account exists
        if not cur.execute("SELECT 1 FROM users WHERE email = 'admin'").fetchone():
            first_password = os.environ.get("BHUTAN_ADMIN_PASSWORD") or "admin123"
            cur.execute(
                "INSERT INTO users (name, email, password, role, created_at) "
                "VALUES ('Admin', 'admin', ?, 'admin', ?)",
                (hash_password(first_password), _now()),
            )
        conn.commit()
    finally:
        conn.close()


# ======================================================================
# USERS
# ======================================================================
def register_user(name, email, password):
    """Create a traveller account. Returns (ok, message)."""
    name, email = name.strip(), email.strip().lower()
    conn = get_db_connection()
    try:
        if conn.execute("SELECT 1 FROM users WHERE LOWER(email) = ?", (email,)).fetchone():
            return False, "An account with this email already exists."
        conn.execute(
            "INSERT INTO users (name, email, password, role, created_at) VALUES (?, ?, ?, 'user', ?)",
            (name, email, hash_password(password), _now()),
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()


def authenticate(email, password):
    """Return {"id","name","email","role"} if the login is correct, else None."""
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT id, name, email, password, role FROM users WHERE LOWER(email) = ?",
            (email.strip().lower(),),
        ).fetchone()
        if not row or not verify_password(password, row["password"]):
            return None
        if not _is_hashed(row["password"]):  # upgrade old plain-text row on the spot
            conn.execute("UPDATE users SET password = ? WHERE id = ?",
                         (hash_password(password), row["id"]))
            conn.commit()
        return {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}
    finally:
        conn.close()


def check_login(email, password):
    """Kept for compatibility: returns (success, name, role)."""
    user = authenticate(email, password)
    return (True, user["name"], user["role"]) if user else (False, None, None)


def check_email_exists(email):
    conn = get_db_connection()
    try:
        return conn.execute("SELECT 1 FROM users WHERE LOWER(email) = ?",
                            (email.strip().lower(),)).fetchone() is not None
    finally:
        conn.close()


def get_user(user_id):
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT id, name, email, role, phone, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_profile(user_id, name, phone):
    """Returns (ok, message). Email is deliberately not editable (it is the login)."""
    name, phone = name.strip(), phone.strip()
    if not name:
        return False, "Name cannot be empty."
    conn = get_db_connection()
    try:
        conn.execute("UPDATE users SET name = ?, phone = ? WHERE id = ?", (name, phone, user_id))
        conn.commit()
        return True, "Profile updated."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()


def change_password(user_id, old_password, new_password, min_length=8):
    """Returns (ok, message)."""
    if len(new_password) < min_length:
        return False, f"The new password must be at least {min_length} characters."
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT password FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row or not verify_password(old_password, row["password"]):
            return False, "The current password is not correct."
        conn.execute("UPDATE users SET password = ? WHERE id = ?",
                     (hash_password(new_password), user_id))
        conn.commit()
        return True, "Password changed."
    finally:
        conn.close()


# ======================================================================
# BOOKINGS
# ======================================================================
def _new_reference(conn):
    for _ in range(25):
        ref = "BV-" + datetime.now().strftime("%y%m%d") + "-" + \
              "".join(secrets.choice(_REF_ALPHABET) for _ in range(4))
        if not conn.execute("SELECT 1 FROM bookings WHERE reference = ?", (ref,)).fetchone():
            return ref
    raise RuntimeError("Could not generate a unique booking reference.")


def create_booking(user_id, traveller_name, traveller_email, dzongkhag, place, package,
                   travel_date, travellers, currency, amount, payment_method, payment_reference,
                   notes=None):
    """Save a new booking as 'Pending'. Returns (True, reference) or (False, error)."""
    if int(travellers) < 1:
        return False, "At least one traveller is required."
    if float(amount) <= 0:
        return False, "The booking amount must be greater than zero."
    conn = get_db_connection()
    try:
        ref = _new_reference(conn)
        conn.execute(
            """INSERT INTO bookings
               (reference, user_id, traveller_name, traveller_email, dzongkhag, place, package,
                travel_date, travellers, currency, amount, payment_method, payment_reference,
                status, created_at, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?, ?)""",
            (ref, user_id, traveller_name, traveller_email, dzongkhag, place, package,
             travel_date, int(travellers), currency, float(amount), payment_method,
             payment_reference, _now(), (notes or "").strip() or None),
        )
        conn.commit()
        return True, ref
    except (sqlite3.Error, RuntimeError) as e:
        return False, f"Could not save the booking: {e}"
    finally:
        conn.close()


def get_user_bookings(user_id):
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM bookings WHERE user_id = ? ORDER BY id DESC", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_bookings(status=None, limit=300):
    conn = get_db_connection()
    try:
        if status and status != "All":
            rows = conn.execute(
                "SELECT * FROM bookings WHERE status = ? ORDER BY id DESC LIMIT ?", (status, limit)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM bookings ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_booking_stats():
    """{'total', 'Pending', 'Confirmed', 'Rejected', 'Cancelled', 'revenue': {currency: amount}}
    Revenue only counts Confirmed bookings."""
    conn = get_db_connection()
    try:
        stats = {"total": 0, **{s: 0 for s in BOOKING_STATUSES}, "revenue": {}}
        for r in conn.execute("SELECT status, COUNT(*) AS n FROM bookings GROUP BY status"):
            if r["status"] in stats:
                stats[r["status"]] = r["n"]
            stats["total"] += r["n"]
        for r in conn.execute(
            "SELECT currency, SUM(amount) AS s FROM bookings WHERE status = 'Confirmed' GROUP BY currency"
        ):
            stats["revenue"][r["currency"]] = r["s"] or 0
        return stats
    finally:
        conn.close()


def set_booking_status(booking_id, status, note=None):
    """Admin action. Returns True if a booking was updated."""
    if status not in BOOKING_STATUSES:
        raise ValueError(f"Unknown status: {status}")
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "UPDATE bookings SET status = ?, admin_note = ?, updated_at = ? WHERE id = ?",
            (status, (note or "").strip() or None, _now(), booking_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ======================================================================
# SAVED PLACES  (favourites + bucket list)
# ======================================================================
def _check_table(table):
    if table not in SAVED_TABLES:
        raise ValueError(f"Unknown list: {table}")
    return table


def get_saved(table, user_id):
    """Destination keys saved by this user, oldest first, e.g. ['paro', 'bumthang']."""
    _check_table(table)
    conn = get_db_connection()
    try:
        rows = conn.execute(
            f"SELECT dest_key FROM {table} WHERE user_id = ? ORDER BY id", (user_id,)
        ).fetchall()
        return [r["dest_key"] for r in rows]
    finally:
        conn.close()


def add_saved(table, user_id, dest_key):
    """Save a place. Returns True if it was added, False if it was already there."""
    _check_table(table)
    conn = get_db_connection()
    try:
        cur = conn.execute(
            f"INSERT OR IGNORE INTO {table} (user_id, dest_key, created_at) VALUES (?, ?, ?)",
            (user_id, dest_key, _now()),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def remove_saved(table, user_id, dest_key):
    """Remove a place. Returns True if something was removed."""
    _check_table(table)
    conn = get_db_connection()
    try:
        cur = conn.execute(
            f"DELETE FROM {table} WHERE user_id = ? AND dest_key = ?", (user_id, dest_key)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_favourites(user_id):
    return get_saved("favourites", user_id)


def add_favourite(user_id, dest_key):
    return add_saved("favourites", user_id, dest_key)


def remove_favourite(user_id, dest_key):
    return remove_saved("favourites", user_id, dest_key)


def get_bucket_list(user_id):
    return get_saved("bucket_list", user_id)


def add_bucket_item(user_id, dest_key):
    return add_saved("bucket_list", user_id, dest_key)


def remove_bucket_item(user_id, dest_key):
    return remove_saved("bucket_list", user_id, dest_key)
