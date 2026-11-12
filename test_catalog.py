"""Tests for the district-wise catalog. Run:  python -m unittest test_catalog -v
(no window is opened - these check the data and the filtering the pages rely on)"""
import re
import unittest

import catalog
import place_images
from catalog import (DESTINATIONS, DZONGKHAG_LIST, get_destination, places_in, filter_destinations,
                     district_counts, destination_label, find_by_label, nu_per_person, dzongkhag_of,
                     rating_short, REGION_OF_DZONGKHAG)
from pricing import price_per_person

REQUIRED = ("key", "title", "place", "dzongkhag", "location", "stay", "person_price", "subtitle",
            "description", "highlights", "price", "rating", "image")
POPULAR = ("Paro", "Thimphu", "Punakha", "Bumthang", "Wangdue Phodrang")


class CatalogTest(unittest.TestCase):
    def test_twenty_districts_a_to_z(self):
        self.assertEqual(len(DZONGKHAG_LIST), 20)
        self.assertEqual(DZONGKHAG_LIST, sorted(DZONGKHAG_LIST))
        self.assertEqual(set(REGION_OF_DZONGKHAG), set(DZONGKHAG_LIST))

    def test_every_place_is_complete_and_in_a_real_district(self):
        for d in DESTINATIONS:
            for field in REQUIRED:
                self.assertIn(field, d, f"{d.get('key')} is missing {field}")
            self.assertIn(d["dzongkhag"], DZONGKHAG_LIST, d["key"])
            self.assertEqual(len(d["highlights"]), 3, d["key"])
            self.assertTrue(d["description"].strip() and d["title"].strip() and d["stay"].strip(), d["key"])
            self.assertGreater(nu_per_person(d), 0, d["key"])
            self.assertTrue(re.fullmatch(r"[a-z0-9-]+", d["key"]), d["key"])

    def test_keys_titles_and_labels_are_unique(self):
        self.assertEqual(len({d["key"] for d in DESTINATIONS}), len(DESTINATIONS))
        self.assertEqual(len({destination_label(d) for d in DESTINATIONS}), len(DESTINATIONS))
        for name in DZONGKHAG_LIST:                       # the booking form picks by title inside a district
            titles = [d["title"] for d in places_in(name)]
            self.assertEqual(len(titles), len(set(titles)), name)

    def test_size_of_the_catalog(self):
        self.assertGreaterEqual(len(DESTINATIONS), 75)
        counts = dict(district_counts())
        for name in DZONGKHAG_LIST:
            self.assertGreaterEqual(counts[name], 2, name)       # every district is represented
        for name in POPULAR:
            self.assertIn(counts[name], (5, 6), name)

    def test_original_places_unchanged(self):
        """Favourites, bucket lists and bookings use these keys and prices - they must keep working."""
        paro = get_destination("paro")
        self.assertEqual((paro["title"], paro["image"], nu_per_person(paro)), ("Tiger's Nest", "paro.jpeg", 3500.0))
        self.assertEqual(dzongkhag_of(get_destination("phobjikha")), "Wangdue Phodrang")
        for key in ("paro", "punakha", "trongsa", "phobjikha", "thimphu", "trashigang", "tsirang", "gasa",
                    "haa", "bumthang", "mongar", "wangdue"):
            self.assertIsNotNone(get_destination(key), key)
        self.assertEqual(price_per_person(paro, "Bhutanese"), ("Nu.", 3500.0))

    def test_new_places_price_placeholders_are_flagged(self):
        new = [d for d in DESTINATIONS if not d["price_confirmed"]]
        self.assertGreater(len(new), 50)
        self.assertTrue(all(d["image"] is None or d["key"] == "shivalaya-mandir" for d in new))


class FilterTest(unittest.TestCase):
    def test_all_and_by_district(self):
        self.assertEqual(len(filter_destinations()), len(DESTINATIONS))
        paro = filter_destinations("Paro")
        self.assertEqual(len(paro), 6)
        self.assertTrue(all(d["dzongkhag"] == "Paro" for d in paro))
        self.assertIn("paro", [d["key"] for d in paro])

    def test_search_inside_a_district(self):
        hits = filter_destinations("Paro", "dzong")
        self.assertEqual({d["key"] for d in hits}, {"rinpung-dzong", "drukgyal-dzong", "national-museum"})   # museum: tagline "Ta Dzong"
        self.assertEqual(filter_destinations("Paro", "zzz-nothing"), [])
        self.assertEqual(filter_destinations("Thimphu", "rinpung"), [])        # a Paro place, not in Thimphu

    def test_search_everywhere_matches_title_district_and_tagline(self):
        self.assertEqual(len(filter_destinations(None, "paro")), 6)             # by district name
        self.assertIn("gasa-tshachu", [d["key"] for d in filter_destinations(None, "hot spring")])
        self.assertEqual(len(filter_destinations(None, "  ")), len(DESTINATIONS))
        self.assertEqual([d["key"] for d in filter_destinations(None, "TIGER")], ["paro"])

    def test_unknown_district_shows_nothing_not_everything(self):
        self.assertEqual(places_in("Atlantis"), [])

    def test_labels_round_trip(self):
        for d in DESTINATIONS:
            self.assertIs(find_by_label(destination_label(d)), d)

    def test_rating_short(self):
        self.assertEqual(rating_short(get_destination("paro")), "4.8")
        self.assertIsNone(rating_short(get_destination("rinpung-dzong")))


class PhotoTest(unittest.TestCase):
    def test_existing_photos_resolve_and_new_places_get_a_placeholder(self):
        for key in ("paro", "gasa", "haa", "shivalaya-mandir"):
            self.assertTrue(place_images.has_photo(get_destination(key)), key)
        d = dict(get_destination("rinpung-dzong"), key="no-such-photo-xyz")
        self.assertFalse(place_images.has_photo(d))
        img = place_images.load(d, 240, 144)
        self.assertEqual(img.size, (240, 144))

    def test_every_place_renders_at_card_and_hero_size(self):
        for d in DESTINATIONS:
            self.assertEqual(place_images.load(d, 180, 108).size, (180, 108), d["key"])
            self.assertEqual(place_images.load(d, 650, 286).size, (650, 286), d["key"])

    def test_dropping_a_file_named_after_the_key_is_picked_up(self):
        import tempfile, shutil
        from pathlib import Path
        from PIL import Image
        tmp = Path(tempfile.mkdtemp())
        orig = place_images.IMAGE_DIR
        try:
            place_images.IMAGE_DIR = tmp
            d = get_destination("rinpung-dzong")
            self.assertIsNone(place_images.photo_path(d))
            Image.new("RGB", (50, 30), (200, 30, 30)).save(tmp / "rinpung-dzong.png")
            self.assertEqual(place_images.photo_path(d), tmp / "rinpung-dzong.png")
            self.assertEqual(place_images.load(d, 100, 60).getpixel((50, 30)), (200, 30, 30))
        finally:
            place_images.IMAGE_DIR = orig
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
