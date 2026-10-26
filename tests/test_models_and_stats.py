import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

import traffic_stats
from models import Trip


class TripTests(unittest.TestCase):
    def test_to_dict(self):
        trip = Trip("A", "B", "08:00", 20, "Morning Peak", 34)
        self.assertEqual(
            trip.to_dict(),
            {"origin": "A", "destination": "B", "departure_time": "08:00",
             "base_minutes": 20, "traffic_period": "Morning Peak",
             "estimated_minutes": 34},
        )


class TrafficStatsTests(unittest.TestCase):
    def report(self, path):
        output = io.StringIO()
        with mock.patch.object(traffic_stats, "STATS_FILE", path), \
                contextlib.redirect_stdout(output):
            traffic_stats.display_traffic_report()
        return output.getvalue()

    def test_missing_file_does_not_crash(self):
        self.assertIn("unavailable", self.report("missing.json"))

    def test_invalid_file_does_not_crash(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "stats.json")
            with open(path, "w", encoding="utf-8") as file:
                file.write("{bad")
            self.assertIn("unavailable", self.report(path))

    def test_incomplete_file_does_not_crash(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "stats.json")
            with open(path, "w", encoding="utf-8") as file:
                file.write('{"city": "Riyadh"}')
            self.assertIn("incomplete", self.report(path))


if __name__ == "__main__":
    unittest.main()
