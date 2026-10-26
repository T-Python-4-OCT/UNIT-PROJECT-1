import json
import os
import tempfile
import unittest

from metro_data import (
    estimate_metro_route_duration,
    find_metro_route,
)

STATIONS = [
    {"name": "KAFD", "name_ar": "المركز المالي", "metro_line": "Blue line",
     "metro_line_code": "Line1", "station_sequence": 3},
    {"name": "Al Murooj", "name_ar": "المروج", "metro_line": "Blue line",
     "metro_line_code": "Line1", "station_sequence": 4},
    {"name": "National Museum", "name_ar": "المتحف الوطني",
     "metro_line": "Blue line", "metro_line_code": "Line1",
     "station_sequence": 16},
    {"name": "Al Hilla", "name_ar": "الحلة", "metro_line": "Green line",
     "metro_line_code": "Line3", "station_sequence": 51},
]


class FindMetroRouteTests(unittest.TestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(handle, "w", encoding="utf-8") as file:
            json.dump(STATIONS, file, ensure_ascii=False)

    def tearDown(self):
        os.remove(self.path)

    def route(self, origin, destination):
        return find_metro_route(origin, destination, self.path)

    def test_same_line_route(self):
        route = self.route("KAFD", "National Museum")
        self.assertEqual(route["number_of_stations"], 13)
        self.assertEqual(route["metro_line_code"], "Line1")

    def test_search_is_case_insensitive(self):
        self.assertIsNotNone(self.route("kafd", "AL MUROOJ"))

    def test_spelling_alias(self):
        self.assertIsNotNone(self.route("Al Muruj", "KAFD"))

    def test_different_lines_have_no_route(self):
        self.assertIsNone(self.route("Al Hilla", "KAFD"))

    def test_same_station_has_no_route(self):
        self.assertIsNone(self.route("KAFD", "KAFD"))

    def test_unknown_station(self):
        self.assertIsNone(self.route("Al Narjis", "KAFD"))

    def test_empty_query(self):
        self.assertIsNone(self.route("", "KAFD"))

    def test_missing_file(self):
        self.assertIsNone(find_metro_route("KAFD", "Al Murooj", "nope.json"))


class DurationEstimateTests(unittest.TestCase):
    def test_line1_thirteen_stations(self):
        route = {"metro_line_code": "Line1", "number_of_stations": 13}
        self.assertEqual(estimate_metro_route_duration(route), 28)

    def test_unknown_line(self):
        route = {"metro_line_code": "Line9", "number_of_stations": 3}
        self.assertIsNone(estimate_metro_route_duration(route))

    def test_negative_waiting_time(self):
        route = {"metro_line_code": "Line1", "number_of_stations": 3}
        self.assertIsNone(estimate_metro_route_duration(route, -1))


if __name__ == "__main__":
    unittest.main()
