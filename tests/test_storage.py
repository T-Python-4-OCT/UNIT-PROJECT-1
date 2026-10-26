import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

import storage


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "trips.json")
        patcher = mock.patch.object(storage, "TRIPS_FILE", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.folder.cleanup)
        quiet = contextlib.redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(storage.load_trips(), [])

    def test_save_creates_file_and_loads_back(self):
        storage.save_trip({"origin": "A", "destination": "B"})
        self.assertEqual(storage.load_trips()[0]["origin"], "A")

    def test_update_merges_values(self):
        storage.save_trip({"origin": "A", "departure_time": "08:00"})
        self.assertTrue(storage.update_trip(0, {"departure_time": "09:00"}))
        trip = storage.load_trips()[0]
        self.assertEqual(trip["origin"], "A")
        self.assertEqual(trip["departure_time"], "09:00")

    def test_update_invalid_index(self):
        self.assertFalse(storage.update_trip(3, {}))

    def test_delete_returns_trip(self):
        storage.save_trip({"origin": "A"})
        self.assertEqual(storage.delete_trip(0), {"origin": "A"})
        self.assertEqual(storage.load_trips(), [])

    def test_delete_invalid_index(self):
        self.assertIsNone(storage.delete_trip(0))
        self.assertIsNone(storage.delete_trip(-1))

    def test_invalid_json_gives_empty_list(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("{not json")
        self.assertEqual(storage.load_trips(), [])

    def test_non_list_json_gives_empty_list(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write('{"a": 1}')
        self.assertEqual(storage.load_trips(), [])


if __name__ == "__main__":
    unittest.main()
