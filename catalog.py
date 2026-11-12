"""catalog.py - the ONE source of destinations and prices.

destination.py (cards), paro_page.py (detail page), Booking.py (form) and both payment
pages all read from here, so a price is only ever edited in this file.
"""
import re

_ORIGINAL_DESTINATIONS = [
    {"key": "paro", "title": "Tiger's Nest", "place": "Paro", "location": "Western Bhutan", "price": "Nu. 8,000", "stay": "4–6 days", "person_price": "3,500", "image": "paro.jpeg", "rating": "4.8 (128 reviews)", "subtitle": "Valley Retreat", "description": ("Begin your Bhutan story in a quiet valley of pine forests, painted farmhouses, and the legendary Tiger's Nest. Paro is the perfect first step into a slower, more meaningful kind of travel."), "highlights": [("Tiger's Nest monastery", "Experience the iconic monastery on the hillside."), ("Paro Valley walks", "Explore the beautiful countryside and valley."), ("Traditional farmhouses", "Discover traditional Bhutanese architecture.")]},
    {"key": "punakha", "title": "Punakha Dzong", "place": "Punakha", "location": "Western Bhutan", "price": "Nu. 10,000", "stay": "3–4 days", "person_price": "3,500", "image": "punakha.jpeg", "rating": "4.6 (90 reviews)", "subtitle": "Cultural Escape", "description": ("Explore Punakha and discover its historic dzong, beautiful river scenery and peaceful surroundings."), "highlights": [("Punakha Dzong", "Discover a historic Bhutanese dzong."), ("Suspension bridge", "Enjoy views of the surrounding river."), ("River valley", "Explore the peaceful landscape.")]},
    {"key": "trongsa", "title": "Trongsa Dzong", "place": "Trongsa", "location": "Central Bhutan", "price": "Nu. 7,000", "stay": "3–4 days", "person_price": "3,800", "image": "trongsa.jpeg", "rating": "4.6 (96 reviews)", "subtitle": "Mountain Heart", "description": ("Discover a dramatic mountain town shaped by its ancient dzong, winding roads, and sweeping views across Bhutan's central valleys."), "highlights": [("Trongsa Dzong", "Explore the historic dzong overlooking the valley."), ("Ta Dzong museum", "Discover the history and culture of Trongsa."), ("Mountain valley", "Enjoy views of the surrounding landscape.")]},
    {"key": "phobjikha", "title": "Phobjikha Valley", "place": "Wangdue", "location": "Western Bhutan", "price": "Nu. 11,000", "stay": "3–5 days", "person_price": "2,600", "image": "phobjikha.jpeg", "rating": "4.7 (112 reviews)", "subtitle": "Nature's Retreat", "description": ("A wide glacial valley surrounded by forested hills, Phobjikha is a refuge for black-necked cranes and anyone looking for a little more space to breathe."), "highlights": [("Black-necked cranes", "Experience the quieter side of Bhutan."), ("Gangtey monastery", "Discover the peaceful monastery and its surroundings."), ("Valley nature walks", "Enjoy the natural beauty of the valley.")]},
    {"key": "thimphu", "title": "Thimphu City", "place": "Thimphu", "location": "Western Bhutan", "price": "Nu. 12,000", "stay": "3–4 days", "person_price": "4,000", "image": "thimphu.png", "rating": "4.7 (320 reviews)", "subtitle": "Modern Bhutan", "description": ("Explore Thimphu, where Bhutanese traditions, local markets, landmarks and modern city life come together."), "highlights": [("Buddha Dordenma", "Visit the famous Buddha statue."), ("Tashichho Dzong", "Discover an important Bhutanese landmark."), ("Local markets", "Explore local crafts and products.")]},
    {"key": "trashigang", "title": "Trashigang Dzong", "place": "Trashigang", "location": "Eastern Bhutan", "price": "Nu. 5,500", "stay": "2–3 days", "person_price": "2,500", "image": "trashigang.jpeg", "rating": "4.3 (56 reviews)", "subtitle": "Eastern Gem", "description": ("Discover the eastern region of Bhutan, its historic dzong, local culture and dramatic mountain scenery."), "highlights": [("Trashigang Dzong", "Explore the historic dzong."), ("Eastern culture", "Discover local traditions."), ("Mountain scenery", "Enjoy the surrounding landscapes.")]},
    {"key": "tsirang", "title": "Tsirang", "place": "Tsirang", "location": "Central Bhutan", "price": "Nu. 6,500", "stay": "2–3 days", "person_price": "2,700", "image": "tsirang.jpg", "rating": "3.5 (45 reviews)", "subtitle": "Orange Orchards", "description": ("Tsirang is a warm southern district known for its orange orchards, terraced hills and relaxed pace of life."), "highlights": [("Orange orchards", "Visit the district's famous citrus groves."), ("Terraced hills", "Enjoy scenic hillside walks."), ("Local villages", "Discover rural Bhutanese life.")]},
    {"key": "gasa", "title": "Gasa", "place": "Gasa", "location": "Northern Bhutan", "price": "Nu. 7,500", "stay": "2–3 days", "person_price": "3,100", "image": "gasa.jpg", "rating": "4.3 (68 reviews)", "subtitle": "Hot Springs", "description": ("Gasa is a remote northern district known for its hot springs, alpine scenery and historic dzong."), "highlights": [("Gasa Tshachu", "Relax in natural hot springs."), ("Gasa Dzong", "Explore the historic fortress."), ("Alpine scenery", "Enjoy Himalayan views.")]},
    {"key": "haa", "title": "Haa Valley", "place": "Haa", "location": "Western Bhutan", "price": "Nu. 9,000", "stay": "2–3 days", "person_price": "3,000", "image": "haa-valley.webp", "rating": "4.6 (89 reviews)", "subtitle": "Hidden Valley", "description": ("A serene valley tucked away in the western hills, Haa remains one of Bhutan's most untouched corners."), "highlights": [("Haa Valley walks", "Explore the quiet countryside."), ("Local temples", "Discover small historic temples."), ("Mountain views", "Enjoy the surrounding peaks.")]},
    {"key": "bumthang", "title": "Bumthang Valley", "place": "Bumthang", "location": "Central Bhutan", "price": "Nu. 13,000", "stay": "4–5 days", "person_price": "3,700", "image": "bumthang.jpg", "rating": "4.8 (345 reviews)", "subtitle": "Spiritual Heart", "description": ("Bumthang is Bhutan's most sacred region, home to ancient temples, monasteries and legends."), "highlights": [("Kurjey Lhakhang", "Visit the sacred monastery."), ("Jakar Dzong", "Explore the historic fortress."), ("Sacred valleys", "Discover Bhutanese spirituality.")]},
    {"key": "mongar", "title": "Mongar Dzong", "place": "Mongar", "location": "Eastern Bhutan", "price": "Nu. 6,500", "stay": "2–3 days", "person_price": "2,800", "image": "mongar.jpg", "rating": "4.2 (67 reviews)", "subtitle": "Hidden Gem", "description": ("Mongar is a quiet eastern town with a modern dzong and stunning views over the surrounding valleys."), "highlights": [("Mongar Dzong", "Explore the modern fortress."), ("Local markets", "Discover eastern Bhutanese life."), ("Mountain roads", "Enjoy dramatic driving routes.")]},
    {"key": "wangdue", "title": "Wangdue Phodrang", "place": "Wangdue", "location": "Western Bhutan", "price": "Nu. 8,500", "stay": "2–3 days", "person_price": "3,200", "image": "wangdue-Phodrang-Dzong.jpg", "rating": "4.5 (92 reviews)", "subtitle": "River Confluence", "description": ("Wangdue Phodrang sits at the confluence of two rivers and is home to one of Bhutan's most important dzongs."), "highlights": [("Wangdue Dzong", "Visit the riverside fortress."), ("River confluence", "Enjoy beautiful river views."), ("Local villages", "Discover rural Bhutanese life.")]},
]


# =====================================================
# DISTRICTS (dzongkhags) - the 20 districts, A-Z.  This is the order of the Destination drop-down.
# To list them by region instead, sort DZONGKHAG_LIST with REGION_OF_DZONGKHAG (see below).
# =====================================================
DZONGKHAG_LIST = [
    "Bumthang", "Chhukha", "Dagana", "Gasa", "Haa", "Lhuentse", "Mongar", "Paro", "Pemagatshel",
    "Punakha", "Samdrup Jongkhar", "Samtse", "Sarpang", "Thimphu", "Trashigang", "Trashiyangtse",
    "Trongsa", "Tsirang", "Wangdue Phodrang", "Zhemgang",
]

# Region text shown on the detail page and booking form for the newly added places.
REGION_OF_DZONGKHAG = {
    "Paro": "Western Bhutan", "Thimphu": "Western Bhutan", "Punakha": "Western Bhutan",
    "Wangdue Phodrang": "Western Bhutan", "Haa": "Western Bhutan", "Chhukha": "Western Bhutan",
    "Bumthang": "Central Bhutan", "Trongsa": "Central Bhutan", "Zhemgang": "Central Bhutan",
    "Tsirang": "Central Bhutan",
    "Samtse": "Southern Bhutan", "Dagana": "Southern Bhutan", "Sarpang": "Southern Bhutan",
    "Gasa": "Northern Bhutan",
    "Mongar": "Eastern Bhutan", "Lhuentse": "Eastern Bhutan", "Trashigang": "Eastern Bhutan",
    "Trashiyangtse": "Eastern Bhutan", "Pemagatshel": "Eastern Bhutan",
    "Samdrup Jongkhar": "Eastern Bhutan",
}

# District of the twelve original places (they keep their own photos and wording).
_ORIGINAL_DZONGKHAG = {
    "paro": "Paro", "punakha": "Punakha", "trongsa": "Trongsa",
    "phobjikha": "Wangdue Phodrang", "thimphu": "Thimphu", "trashigang": "Trashigang",
    "tsirang": "Tsirang", "gasa": "Gasa", "haa": "Haa", "bumthang": "Bumthang",
    "mongar": "Mongar", "wangdue": "Wangdue Phodrang",
}


# A photo you already have for one of the new places (file name inside images/).
_PHOTO_FOR_NEW = {"shivalaya-mandir": "samtse.jpg"}


def _build_destinations():
    items = []
    for d in _ORIGINAL_DESTINATIONS:
        d = dict(d)
        d["dzongkhag"] = _ORIGINAL_DZONGKHAG[d["key"]]
        d.setdefault("price_confirmed", True)     # the original prices are yours already
        items.append(d)
    for key, title, dzong, subtitle, stay, nu, description, highlights in NEW_PLACES:
        items.append({
            "key": key, "title": title, "place": dzong, "dzongkhag": dzong,
            "location": REGION_OF_DZONGKHAG[dzong],
            "price": f"Nu. {nu}", "stay": stay, "person_price": nu,
            "image": _PHOTO_FOR_NEW.get(key),   # None = no photo yet: drop images/<key>.jpg in (place_images.py)
            "rating": None,                # no reviews yet
            "subtitle": subtitle, "description": description, "highlights": list(highlights),
            "price_confirmed": False,      # placeholder price - confirm it (places_to_confirm.csv)
        })
    return items


from places_data import NEW_PLACES  # noqa: E402  (kept next to where it is used)

DESTINATIONS = _build_destinations()
_BY_KEY = {d["key"]: d for d in DESTINATIONS}


def get_destination(key):
    """Return the destination dict for a key such as 'paro', or None."""
    return _BY_KEY.get(key)


def dzongkhag_of(d):
    return d.get("dzongkhag") or d["place"]


def places_in(dzongkhag):
    """All places in one district (all places if dzongkhag is empty / None), in catalog order."""
    if not dzongkhag:
        return list(DESTINATIONS)
    return [d for d in DESTINATIONS if d["dzongkhag"] == dzongkhag]


def district_counts():
    """[(district name, number of places)] in dropdown order (A-Z)."""
    return [(name, len(places_in(name))) for name in DZONGKHAG_LIST]


def filter_destinations(dzongkhag=None, query=""):
    """The places to show for the Destinations page: one district (or all), narrowed by the search text.

    The search looks at the place name, its district and its tagline, so "paro" or "hot springs" both work.
    """
    q = (query or "").strip().lower()
    out = []
    for d in places_in(dzongkhag):
        hay = f"{d['title']} {d['dzongkhag']} {d['subtitle']}".lower()
        if not q or q in hay:
            out.append(d)
    return out


def rating_short(d):
    """'4.8 (128 reviews)' -> '4.8'.  None when the place has no reviews yet."""
    r = d.get("rating")
    if not r:
        return None
    return str(r).split()[0]


def destination_label(d):
    """Text for dropdowns that list every place, e.g. "Tiger's Nest (Paro)"."""
    title, dz = d["title"], dzongkhag_of(d)
    return title if dz.lower() in title.lower() else f"{title} ({dz})"


def find_by_label(label):
    for d in DESTINATIONS:
        if destination_label(d) == label:
            return d
    return None


def nu_per_person(d):
    """'3,500' -> 3500.0   (person_price is in Ngultrum)"""
    m = re.search(r"\d[\d,]*(?:\.\d+)?", str(d["person_price"]))
    return float(m.group().replace(",", "")) if m else 0.0
