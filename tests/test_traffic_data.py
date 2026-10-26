import unittest

from traffic_data import (
    estimate_trip_duration,
    find_departure_time,
    get_traffic_info,
)


class TrafficInfoTests(unittest.TestCase):
    def test_periods_by_hour(self):
        cases = {
            "08:00": ("Morning Peak", 1.7),
            "12:30": ("Midday", 1.2),
            "17:00": ("Evening Peak", 1.6),
            "22:00": ("Off-Peak", 1.0),
            "03:15": ("Off-Peak", 1.0),
        }
        for time, expected in cases.items():
            with self.subTest(time=time):
                self.assertEqual(get_traffic_info(time), expected)

    def test_period_boundaries(self):
        self.assertEqual(get_traffic_info("07:00")[0], "Morning Peak")
        self.assertEqual(get_traffic_info("10:00")[0], "Midday")
        self.assertEqual(get_traffic_info("19:00")[0], "Off-Peak")

    def test_invalid_time_raises(self):
        with self.assertRaises(ValueError):
            get_traffic_info("25:99")


class DurationTests(unittest.TestCase):
    def test_estimate_uses_multiplier(self):
        self.assertEqual(estimate_trip_duration(20, "09:00"),
                         ("Morning Peak", 34))

    def test_off_peak_keeps_base_duration(self):
        self.assertEqual(estimate_trip_duration(20, "23:00"),
                         ("Off-Peak", 20))


class DepartureSuggestionTests(unittest.TestCase):
    def test_arrives_before_target(self):
        result = find_departure_time(20, "09:00")
        self.assertIsNotNone(result)
        self.assertLessEqual(result["arrival_minutes"], 9 * 60)

    def test_no_departure_possible(self):
        self.assertIsNone(find_departure_time(120, "00:10"))

    def test_invalid_arrival_time_raises(self):
        with self.assertRaises(ValueError):
            find_departure_time(20, "abc")


if __name__ == "__main__":
    unittest.main()
