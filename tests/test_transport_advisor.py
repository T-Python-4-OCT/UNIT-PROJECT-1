import contextlib
import io
import unittest
from unittest import mock

import transport_advisor
from transport_advisor import (
    calculate_car_fuel_cost,
    compare_transport_options,
    find_transport_options,
    get_recommendation,
    normalize_location,
)

ROUTES = [
    {"origin": "Al Muruj", "destination": "KAFD",
     "distance_km": 7, "base_duration_minutes": 15},
]


class FuelCostTests(unittest.TestCase):
    def test_cost_for_17_km(self):
        self.assertEqual(calculate_car_fuel_cost(17), 2.22)

    def test_invalid_distance(self):
        self.assertIsNone(calculate_car_fuel_cost(None))
        self.assertIsNone(calculate_car_fuel_cost(0))
        self.assertIsNone(calculate_car_fuel_cost(-5))


class RecommendationTests(unittest.TestCase):
    def test_fastest(self):
        self.assertEqual(get_recommendation("fastest", 34, 2.2, 28, 4)[0],
                         "Metro")
        self.assertEqual(get_recommendation("fastest", 20, 2.2, 28, 4)[0],
                         "Car")

    def test_cheapest(self):
        self.assertEqual(get_recommendation("cheapest", 34, 2.2, 28, 4)[0],
                         "Car")
        self.assertEqual(get_recommendation("cheapest", 34, 5.0, 28, 4)[0],
                         "Metro")

    def test_cheapest_without_car_cost(self):
        self.assertIsNone(get_recommendation("cheapest", 34, None, 28, 4)[0])

    def test_balanced(self):
        self.assertEqual(get_recommendation("balanced", 34, 2.2, 28, 4)[0],
                         "Car")

    def test_cancelled_priority_is_balanced(self):
        self.assertEqual(
            get_recommendation(None, 34, 2.2, 28, 4),
            get_recommendation("balanced", 34, 2.2, 28, 4),
        )


class RouteLookupTests(unittest.TestCase):
    def test_normalize_location(self):
        self.assertEqual(normalize_location("  Al Murooj "), "almuruj")

    def test_spelling_variants_match(self):
        with mock.patch.object(transport_advisor, "load_routes",
                               return_value=ROUTES):
            self.assertIsNotNone(find_transport_options("al murooj", "kafd"))

    def test_unknown_route(self):
        with mock.patch.object(transport_advisor, "load_routes",
                               return_value=ROUTES):
            self.assertIsNone(find_transport_options("KAFD", "Al Muruj"))


class CompareTests(unittest.TestCase):
    def setUp(self):
        quiet = contextlib.redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)

    def test_unknown_route_returns_none(self):
        with mock.patch.object(transport_advisor, "load_routes",
                               return_value=ROUTES):
            self.assertIsNone(
                compare_transport_options("A", "B", "08:00", interactive=False)
            )

    def test_result_without_metro_route(self):
        with mock.patch.object(transport_advisor, "load_routes",
                               return_value=ROUTES), \
                mock.patch.object(transport_advisor, "find_metro_route",
                                  return_value=None):
            result = compare_transport_options(
                "Al Muruj", "KAFD", "08:00", interactive=False
            )
        self.assertEqual(result["car_duration"], 26)
        self.assertIsNone(result["metro_duration"])
        self.assertIsNone(result["metro_cost"])

    def test_result_with_metro_route(self):
        metro = {"metro_line": "Blue line", "metro_line_code": "Line1",
                 "number_of_stations": 13}
        with mock.patch.object(transport_advisor, "load_routes",
                               return_value=ROUTES), \
                mock.patch.object(transport_advisor, "find_metro_route",
                                  return_value=metro):
            result = compare_transport_options(
                "Al Muruj", "KAFD", "08:00", interactive=False
            )
        self.assertEqual(result["metro_duration"], 28)
        self.assertEqual(result["metro_line"], "Blue line")


if __name__ == "__main__":
    unittest.main()
