"""Tests for the saved places (favourites + bucket list). Run:  python -m unittest test_saved_places -v"""
import os
import tempfile
import unittest

import database


class SavedPlacesTest(unittest.TestCase):
    def setUp(self):
        self._orig = database.DB_FILE
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        database.DB_FILE = self._tmp.name           # never touch the real database
        database.init_db()
        database.register_user("Tashi", "tashi@example.com", "password123")
        database.register_user("Pema", "pema@example.com", "password123")
        self.a = database.authenticate("tashi@example.com", "password123")["id"]
        self.b = database.authenticate("pema@example.com", "password123")["id"]

    def tearDown(self):
        database.DB_FILE = self._orig
        os.unlink(self._tmp.name)

    def test_tables_exist_and_init_is_repeatable(self):
        database.init_db()
        conn = database.get_db_connection()
        names = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        conn.close()
        self.assertTrue({"favourites", "bucket_list"} <= names)

    def test_add_remove_and_persist(self):
        self.assertEqual(database.get_favourites(self.a), [])
        self.assertTrue(database.add_favourite(self.a, "paro"))
        self.assertTrue(database.add_favourite(self.a, "bumthang"))
        self.assertEqual(database.get_favourites(self.a), ["paro", "bumthang"])
        self.assertTrue(database.remove_favourite(self.a, "paro"))
        self.assertEqual(database.get_favourites(self.a), ["bumthang"])
        self.assertFalse(database.remove_favourite(self.a, "paro"))     # already gone

    def test_no_duplicates(self):
        self.assertTrue(database.add_favourite(self.a, "paro"))
        self.assertFalse(database.add_favourite(self.a, "paro"))
        self.assertEqual(database.get_favourites(self.a), ["paro"])

    def test_users_are_separate(self):
        database.add_favourite(self.a, "paro")
        self.assertEqual(database.get_favourites(self.b), [])

    def test_lists_are_separate(self):
        database.add_favourite(self.a, "paro")
        database.add_bucket_item(self.a, "gasa")
        self.assertEqual(database.get_favourites(self.a), ["paro"])
        self.assertEqual(database.get_bucket_list(self.a), ["gasa"])
        database.remove_bucket_item(self.a, "gasa")
        self.assertEqual(database.get_favourites(self.a), ["paro"])

    def test_unknown_table_refused(self):
        with self.assertRaises(ValueError):
            database.get_saved("users; DROP TABLE users", self.a)


if __name__ == "__main__":
    unittest.main()
