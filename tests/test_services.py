import email
import email.policy
import json
import os
import shutil
import smtplib
import socket
import socketserver
import tempfile
import threading
import unittest
import urllib.error
from datetime import date, timedelta
from pathlib import Path
from unittest import mock


_TMP = tempfile.mkdtemp()
os.environ["SKYROUTE_DATA_DIR"] = _TMP

os.environ["SKYROUTE_SMTP_HOST"] = ""

from agency import seed
from agency.config import (BOOKINGS_FILE, COUNTRIES_FILE, DEFAULT_DAYS,
                           OUTBOX_DIR, PROMOS_FILE, REFUND_NOTICE, USERS_FILE)
from agency.countries_data import COUNTRIES
from agency.errors import ServiceError
from agency.flags import UNKNOWN_FLAG, flag
from agency.services import (auth, bookings, countries, notifications,
                             planner, promos, recommendations, reports, users, weather)
from agency.utils import validators
from agency.utils.env_file import read_env_file
from agency.utils.security import hash_password, verify_password

FUTURE = (date.today() + timedelta(days=30)).isoformat()
GOOD_CARD = "4242 4242 4242 4242"
CARD = {"card_number": GOOD_CARD, "card_holder": "Sara Ali", "cvv": "123"}


PHONE = "0501234567"


def reset():
    for f in (USERS_FILE, COUNTRIES_FILE, BOOKINGS_FILE, PROMOS_FILE):
        if f.exists():
            f.unlink()
    shutil.rmtree(OUTBOX_DIR, ignore_errors=True)
    seed.run()


def make_customer(name="sara"):
    return auth.register(name, "secret1", "Sara Ali", f"{name}@mail.com", PHONE)


def city_id(city):
    return next(c.id for c in countries.list_all() if c.city == city)


class Base(unittest.TestCase):
    def setUp(self):
        reset()

    @classmethod
    def tearDownClass(cls):
        pass


class TestSecurity(unittest.TestCase):
    def test_hash_and_verify(self):
        h = hash_password("abc123")
        self.assertTrue(verify_password("abc123", h))
        self.assertFalse(verify_password("wrong", h))
        self.assertNotEqual(h, hash_password("abc123"))
        self.assertFalse(verify_password("abc123", "garbage"))


class TestValidators(unittest.TestCase):
    def test_card_number_is_8_to_16_digits(self):
        for good in ("12345678", "1234567890123456", "4242 4242 4242 4242", "1234-5678-9012"):
            self.assertTrue(validators.is_valid_card_number(good), good)
        for bad in ("1234567", "12345678901234567", "abcd1234", "", "1234 56 7x"):
            self.assertFalse(validators.is_valid_card_number(bad), bad)

    def test_promo_code_shape(self):
        for good in ("EID20", "abc", "YEAREND2026"):
            self.assertTrue(validators.is_valid_promo_code(good), good)
        for bad in ("ab", "EID 20", "EID-20", "عيد20", "A" * 16, ""):
            self.assertFalse(validators.is_valid_promo_code(bad), bad)

    def test_card_holder_and_cvv(self):
        for good in ("Sara Ali", "Mary-Jane O'Neil", "محمد علي"):
            self.assertTrue(validators.is_valid_card_holder(good), good)
        for bad in ("", "  ", "Al", "R2D2", "Sara_Ali", "!!!"):
            self.assertFalse(validators.is_valid_card_holder(bad), bad)
        self.assertTrue(validators.is_valid_cvv("123") and validators.is_valid_cvv("1234"))
        for bad in ("", "12", "12345", "abc", "12 3"):
            self.assertFalse(validators.is_valid_cvv(bad), bad)

    def test_phone_numbers(self):
        good = {"0501234567": "0501234567", "+966 50 123 4567": "+966501234567",
                "00966-50-123-4567": "+966501234567", "(050) 123.4567": "0501234567"}
        for typed, clean in good.items():
            self.assertEqual(validators.normalize_phone(typed), clean, typed)
        for typed in ("", "123", "abc12345", "+", "05012345x7", "1234567890123456", "050 123"):
            self.assertEqual(validators.normalize_phone(typed), "", typed)

    def test_full_name(self):
        self.assertTrue(validators.is_valid_full_name("Sara Al-Harbi"))
        self.assertTrue(validators.is_valid_full_name("محمد علي"))
        self.assertFalse(validators.is_valid_full_name("A"))
        self.assertFalse(validators.is_valid_full_name("A" * 61))
        self.assertFalse(validators.is_valid_full_name("Ali\nBcc: x@y.z"))

    def test_dates(self):
        self.assertEqual(validators.parse_future_date(FUTURE), FUTURE)
        with self.assertRaises(ServiceError):
            validators.parse_future_date("2020-01-01")
        with self.assertRaises(ServiceError):
            validators.parse_future_date("not a date")


class TestSeedAndAuth(Base):
    def test_seed(self):
        self.assertEqual(len(countries.list_all()), len(COUNTRIES))
        admin = auth.login("admin", "admin123")
        self.assertEqual(admin.role, "manager")

    def test_register_and_login(self):
        u = make_customer()
        self.assertEqual(u.role, "customer")
        self.assertEqual(auth.login("SARA", "secret1").id, u.id)

    def test_register_keeps_a_clean_phone_number(self):
        user = auth.register("omar", "secret1", "Omar Saleh", "omar@mail.com", "+966 50-123 4567")
        self.assertEqual(user.phone, "+966501234567")
        self.assertEqual(auth.login("omar", "secret1").phone, "+966501234567")

    def test_register_errors(self):
        make_customer()
        bad = [("sara", "secret1", "Ali", "x@mail.com", PHONE),
               ("new1", "secret1", "Ali", "sara@mail.com", PHONE),
               ("ab", "secret1", "Ali", "x@mail.com", PHONE),
               ("new2", "123", "Ali", "x@mail.com", PHONE),
               ("new3", "secret1", " ", "x@mail.com", PHONE),
               ("new4", "secret1", "Ali", "not-an-email", PHONE),
               ("new5", "secret1", "Ali", "x@mail.com", "123"),
               ("new6", "secret1", "Ali", "x@mail.com", "abc12345"),
               ("new7", "secret1", "Ali", "x@mail.com", ""),
               ("new8", "secret1", "Ali\nBcc: a@b.c", "x@mail.com", PHONE)]
        for args in bad:
            with self.assertRaises(ServiceError, msg=str(args)):
                auth.register(*args)

    def test_old_accounts_without_a_phone_still_load(self):
        records = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        records[0].pop("phone", None)
        USERS_FILE.write_text(json.dumps(records), encoding="utf-8")
        self.assertEqual(auth.login("admin", "admin123").phone, "")

    def test_login_fail(self):
        with self.assertRaises(ServiceError):
            auth.login("admin", "nope")
        with self.assertRaises(ServiceError):
            auth.login("ghost", "nope")


class TestCountries(Base):
    def test_search(self):
        self.assertEqual([c.city for c in countries.search("paris")], ["Paris"])
        self.assertTrue(all(c.category == "beach" for c in countries.search(category="beach")))
        self.assertEqual(countries.search("zzz"), [])

    def test_crud(self):
        data = dict(country="Kenya", city="Nairobi", category="adventure", flight=2000,
                    hotel=300, food=100, transport=40, activities=150,
                    best_season="Jun-Oct", highlights="Safari, Giraffe Centre")
        c = countries.add(data)
        self.assertEqual(c.highlights, ["Safari", "Giraffe Centre"])
        self.assertEqual(countries.update(c.id, {"hotel": 350}).hotel, 350)
        with self.assertRaises(ServiceError):
            countries.add(data)
        countries.delete(c.id)
        with self.assertRaises(ServiceError):
            countries.get(c.id)
        with self.assertRaises(ServiceError):
            countries.delete(c.id)

    def test_validation(self):
        base = dict(country="A", city="B", category="city", flight=1, hotel=1,
                    food=1, transport=1, activities=1, best_season="x", highlights="h")
        for key, value in [("category", "space"), ("flight", "abc"),
                           ("hotel", -5), ("highlights", " , "), ("city", " ")]:
            with self.assertRaises(ServiceError, msg=key):
                countries.add({**base, key: value})


class TestPlanner(Base):
    def test_estimate_math(self):
        istanbul = countries.get(city_id("Istanbul"))
        cost = planner.estimate(istanbul, 3, 2, "standard")

        self.assertEqual(cost, {"Flights": 2400, "Hotel": 1200, "Food": 720, "Transport": 240,
                                "Activities": 600, "Group discount (10%)": -516, "Total": 4644})

    def test_only_two_travelers_get_the_group_discount(self):
        c = countries.get(city_id("Istanbul"))
        for people in (1, 3, 4):
            self.assertNotIn("Group discount (10%)", planner.estimate(c, 3, people, "standard"))
        pair = planner.estimate(c, 3, 2, "standard")
        single = planner.estimate(c, 3, 1, "standard")
        self.assertEqual(pair["Total"], round(single["Total"] * 2 * 0.9))

    def test_promo_is_a_percent_of_the_base_costs(self):
        c = countries.get(city_id("Istanbul"))
        single = planner.estimate(c, 3, 1, "standard")
        cost = planner.apply_promo(single, "EID20", 20)
        self.assertEqual(cost["Code EID20 (20%)"], -516)
        self.assertEqual(cost["Total"], 2580 - 516)
        pair = planner.apply_promo(planner.estimate(c, 3, 2, "standard"), "EID20", 20)
        self.assertEqual(pair["Total"], 5160 - 516 - 1032)

    def test_style_changes_price(self):
        c = countries.get(city_id("Paris"))
        eco = planner.estimate(c, 5, 1, "economy")["Total"]
        std = planner.estimate(c, 5, 1, "standard")["Total"]
        lux = planner.estimate(c, 5, 1, "luxury")["Total"]
        self.assertLess(eco, std)
        self.assertLess(std, lux)

    def test_matches_respect_budget(self):
        matches, cheapest = planner.find_matches(8000, 5, 1, "standard")
        self.assertTrue(matches)
        self.assertTrue(all(cost["Total"] <= 8000 for _, cost in matches))
        totals = [cost["Total"] for _, cost in matches]
        self.assertEqual(totals, sorted(totals, reverse=True))

    def test_not_enough_budget(self):
        matches, cheapest = planner.find_matches(500, 5, 1, "standard")
        self.assertEqual(matches, [])
        self.assertGreater(cheapest[1]["Total"], 500)

    def test_category_filter(self):
        matches, _ = planner.find_matches(50000, 5, 1, "standard", category="beach")
        self.assertTrue(matches)
        self.assertTrue(all(c.category == "beach" for c, _ in matches))

    def test_invalid_inputs(self):
        c = countries.get(1)
        for args in [(c, 1, 1, "standard"), (c, 5, 0, "standard"), (c, 5, 1, "royal")]:
            with self.assertRaises(ServiceError):
                planner.estimate(*args)
        with self.assertRaises(ServiceError):
            planner.find_matches(0, 5, 1, "standard")

    def test_itinerary(self):
        c = countries.get(1)
        plan = planner.build_itinerary(c, 6)
        self.assertEqual(len(plan), 6)
        self.assertTrue(plan[0].startswith("Arrive"))
        self.assertEqual(len(planner.build_itinerary(c, 2)), 2)


class TestFlags(unittest.TestCase):
    def test_a_known_country_gets_its_flag(self):
        self.assertEqual(flag("Turkey"), "\U0001F1F9\U0001F1F7")
        self.assertEqual(flag(" uae "), "\U0001F1E6\U0001F1EA")
        self.assertEqual(flag("United Kingdom"), "\U0001F1EC\U0001F1E7")

    def test_an_unknown_country_gets_a_globe(self):
        self.assertEqual(flag("Atlantis"), UNKNOWN_FLAG)

    def test_every_built_in_destination_has_a_flag(self):
        for row in COUNTRIES:
            self.assertNotEqual(flag(row[0]), UNKNOWN_FLAG, row[0])


class TestPromos(Base):
    def test_starter_codes_have_their_own_percent(self):
        codes = {promo.code: promo for promo in promos.list_all()}
        self.assertEqual({"EID20", "YEAREND10"}, set(codes))
        self.assertEqual(codes["EID20"].percent, 20)
        self.assertEqual(codes["YEAREND10"].percent, 10)
        self.assertTrue(all(p.active for p in codes.values()))

    def test_codes_are_not_case_sensitive(self):
        self.assertEqual(promos.get_active(" eid20 ").code, "EID20")

    def test_add_switch_and_delete(self):
        created = promos.add("adha20", "Eid Al-Adha")
        self.assertEqual((created.code, created.percent), ("ADHA20", 20))
        promos.set_active("ADHA20", False)
        with self.assertRaises(ServiceError):
            promos.get_active("ADHA20")
        promos.set_active("ADHA20", True)
        self.assertEqual(promos.get_active("ADHA20").occasion, "Eid Al-Adha")
        promos.delete("ADHA20")
        with self.assertRaises(ServiceError):
            promos.get_active("ADHA20")

    def test_bad_codes_are_refused(self):
        for args in (("x", "Eid"), ("EID 1", "Eid"), ("NEW1", " "), ("NEW1", "Eid", 0),
                     ("NEW1", "Eid", 51), ("eid20", "Duplicate")):
            with self.assertRaises(ServiceError, msg=str(args)):
                promos.add(*args)

    def test_unknown_code(self):
        for call in (promos.get_active, promos.delete):
            with self.assertRaises(ServiceError):
                call("NOPE99")

    def test_booking_with_a_code_gets_the_discount_and_remembers_it(self):
        user = make_customer()
        plain = bookings.create(user.id, city_id("Dubai"), FUTURE, 4, 1, "standard")
        coded = bookings.create(user.id, city_id("Dubai"), FUTURE, 4, 1, "standard", " eid20 ")
        self.assertEqual(coded.promo_code, "EID20")
        base = sum(plain.breakdown[item] for item in planner.BASE_ITEMS)
        self.assertEqual(coded.total_price, plain.total_price - round(base * 0.2))
        self.assertEqual(coded.total_price, coded.breakdown["Total"])
        self.assertEqual(bookings.get(coded.id).promo_code, "EID20")
        self.assertEqual(plain.promo_code, "")

    def test_a_switched_off_or_unknown_code_creates_no_booking(self):
        user = make_customer()
        promos.set_active("EID20", False)
        for code in ("EID20", "NOPE99"):
            with self.assertRaises(ServiceError):
                bookings.create(user.id, city_id("Dubai"), FUTURE, 4, 1, "standard", code)
        self.assertEqual(bookings.list_for_user(user.id), [])

    def test_old_bookings_without_a_code_field_still_load(self):
        user = make_customer()
        booking = bookings.create(user.id, city_id("Dubai"), FUTURE, 4, 1, "standard")
        records = json.loads(BOOKINGS_FILE.read_text(encoding="utf-8"))
        del records[0]["promo_code"]
        BOOKINGS_FILE.write_text(json.dumps(records), encoding="utf-8")
        self.assertEqual(bookings.get(booking.id).promo_code, "")

    def test_the_receipt_email_names_the_code(self):
        user = make_customer()
        booking = bookings.create(user.id, city_id("Dubai"), FUTURE, 4, 2, "standard", "EID20")
        _, body = notifications.build_booking_message("created", booking, user)
        self.assertIn("code EID20", body)
        paid = bookings.pay(booking.id, user.id, "card", **CARD)
        _, receipt = notifications.build_booking_message("paid", paid, user)
        self.assertIn("Code EID20 (20%)", receipt)
        self.assertIn("Group discount (10%)", receipt)


class TestBookings(Base):
    def setUp(self):
        super().setUp()
        self.user = make_customer()
        self.other = make_customer("omar")
        self.cid = city_id("Dubai")

    def book(self, user=None):
        return bookings.create((user or self.user).id, self.cid, FUTURE, 4, 2, "standard")

    def test_create(self):
        b = self.book()
        self.assertEqual(b.status, "pending")
        self.assertFalse(b.paid)
        self.assertEqual(b.total_price, b.breakdown["Total"])
        self.assertEqual(len(bookings.list_for_user(self.user.id)), 1)
        self.assertEqual(bookings.list_for_user(self.other.id), [])

    def test_create_errors(self):
        with self.assertRaises(ServiceError):
            bookings.create(self.user.id, 9999, FUTURE, 4, 2, "standard")
        with self.assertRaises(ServiceError):
            bookings.create(self.user.id, self.cid, "2020-01-01", 4, 2, "standard")

    def test_pay_flow(self):
        b = self.book()
        with self.assertRaises(ServiceError):
            bookings.pay(b.id, self.user.id, "card", **{**CARD, "card_number": "1234"})
        paid = bookings.pay(b.id, self.user.id, "card", **CARD)
        self.assertTrue(paid.paid)
        self.assertEqual(paid.status, "confirmed")
        self.assertTrue(paid.reference.startswith("SR-"))
        with self.assertRaises(ServiceError):
            bookings.pay(b.id, self.user.id, "card", **CARD)
        with self.assertRaises(ServiceError):
            bookings.pay(b.id, self.user.id, "bitcoin")

    def test_card_needs_name_and_cvv(self):
        b = self.book()
        for bad in ({"card_holder": ""}, {"card_holder": "R2D2"}, {"cvv": ""}, {"cvv": "12"}, {"cvv": "12a4"}):
            with self.assertRaises(ServiceError, msg=str(bad)):
                bookings.pay(b.id, self.user.id, "card", **{**CARD, **bad})
        self.assertFalse(bookings.get(b.id).paid)

    def test_bank_transfer_was_removed(self):
        b = self.book()
        self.assertNotIn("bank_transfer", bookings.PAYMENT_METHODS)
        with self.assertRaises(ServiceError):
            bookings.pay(b.id, self.user.id, "bank_transfer")

    def test_other_users_cannot_touch(self):
        b = self.book()
        for action in (lambda: bookings.pay(b.id, self.other.id, "apple_pay"),
                       lambda: bookings.cancel(b.id, self.other.id),
                       lambda: bookings.receipt(b.id, self.other.id)):
            with self.assertRaises(ServiceError):
                action()

    def test_receipt_needs_payment(self):
        b = self.book()
        with self.assertRaises(ServiceError):
            bookings.receipt(b.id, self.user.id)
        bookings.pay(b.id, self.user.id, "apple_pay")
        self.assertEqual(bookings.receipt(b.id, self.user.id).id, b.id)

    def test_cancel_refund(self):
        b = self.book()
        _, refund = bookings.cancel(b.id, self.user.id)
        self.assertEqual(refund, 0)
        b2 = self.book()
        bookings.pay(b2.id, self.user.id, "apple_pay")
        cancelled, refund = bookings.cancel(b2.id, self.user.id)
        self.assertEqual(refund, b2.total_price)
        self.assertEqual(cancelled.status, "cancelled")
        self.assertFalse(cancelled.paid)
        with self.assertRaises(ServiceError):
            bookings.cancel(b2.id, self.user.id)
        with self.assertRaises(ServiceError):
            bookings.pay(b2.id, self.user.id, "apple_pay")

    def test_manager_status_rules(self):
        b = self.book()
        with self.assertRaises(ServiceError):
            bookings.set_status(b.id, "confirmed")
        with self.assertRaises(ServiceError):
            bookings.set_status(b.id, "flying")
        bookings.pay(b.id, self.user.id, "apple_pay")
        self.assertEqual(bookings.set_status(b.id, "completed")[0].status, "completed")
        _, refund = bookings.set_status(b.id, "cancelled")
        self.assertEqual(refund, b.total_price)
        with self.assertRaises(ServiceError):
            bookings.set_status(b.id, "pending")
        with self.assertRaises(ServiceError):
            bookings.set_status(999, "pending")


class TestReportsAndRecommendations(Base):
    def test_reports(self):
        u = make_customer()
        r0 = reports.summary()
        self.assertEqual((r0["total_bookings"], r0["revenue"], r0["average_booking"]), (0, 0, 0))
        b1 = bookings.create(u.id, city_id("Dubai"), FUTURE, 3, 1, "standard")
        b2 = bookings.create(u.id, city_id("Paris"), FUTURE, 3, 1, "standard")
        bookings.pay(b1.id, u.id, "apple_pay")
        bookings.cancel(b2.id, u.id)
        r = reports.summary()
        self.assertEqual(r["total_bookings"], 2)
        self.assertEqual(r["revenue"], b1.total_price)
        self.assertEqual(r["customers"], 1)
        self.assertEqual(r["by_status"]["confirmed"], 1)
        self.assertEqual(r["by_status"]["cancelled"], 1)
        self.assertEqual(len(r["top_destinations"]), 1)

    def test_recommend_without_history(self):
        u = make_customer()
        recs = recommendations.recommend(u.id)
        self.assertEqual(len(recs), 3)
        costs = [planner.estimate(c, DEFAULT_DAYS, 1, "standard")["Total"] for c, _ in recs]
        self.assertEqual(costs, sorted(costs))

    def test_recommend_from_history(self):
        u = make_customer()
        bookings.create(u.id, city_id("Bali"), FUTURE, 5, 1, "standard")
        recs = recommendations.recommend(u.id)
        names = [c.city for c, _ in recs]
        self.assertNotIn("Bali", names)
        self.assertEqual(recs[0][0].city, "Male")
        self.assertIn("beach", recs[0][1])

    def test_cancelled_booking_does_not_count(self):
        u = make_customer()
        b = bookings.create(u.id, city_id("Bali"), FUTURE, 5, 1, "standard")
        bookings.cancel(b.id, u.id)
        names = [c.city for c, _ in recommendations.recommend(u.id, limit=30)]
        self.assertIn("Bali", names)


class TestWeather(Base):

    GEOCODING = {"results": [
        {"name": "Male", "country": "India", "latitude": 1.0, "longitude": 1.0},
        {"name": "Male", "country": "Maldives", "latitude": 4.17, "longitude": 73.51},
    ]}
    FORECAST = {
        "current": {"temperature_2m": 31.5, "weather_code": 2, "wind_speed_10m": 12.0},
        "daily": {"time": ["2026-10-21", "2026-10-22"],
                  "temperature_2m_max": [32.0, 33.1], "temperature_2m_min": [26.0, 27.2],
                  "weather_code": [0, 61]},
    }

    def fake_api(self, url, params):
        self.calls.append((url, params))
        return self.GEOCODING if url == weather.GEOCODING_URL else self.FORECAST

    def setUp(self):
        super().setUp()
        self.calls = []
        self.male = countries.get(city_id("Male"))

    def test_forecast_is_parsed(self):
        with mock.patch.object(weather, "_get_json", side_effect=self.fake_api):
            report = weather.get_forecast(self.male)
        self.assertEqual(report["city"], "Male")
        self.assertEqual(report["temperature"], 31.5)
        self.assertEqual(report["condition"], "Partly cloudy")
        self.assertEqual(report["days"][1],
                         {"date": "2026-10-22", "max": 33.1, "min": 27.2, "condition": "Light rain"})

    def test_picks_result_from_the_right_country(self):
        with mock.patch.object(weather, "_get_json", side_effect=self.fake_api):
            weather.get_forecast(self.male)
        forecast_params = self.calls[1][1]
        self.assertEqual(forecast_params["latitude"], 4.17)

    def test_unknown_city(self):
        with mock.patch.object(weather, "_get_json", return_value={}):
            with self.assertRaises(ServiceError):
                weather.get_forecast(self.male)

    def test_unexpected_data(self):
        def broken(url, params):
            return self.GEOCODING if url == weather.GEOCODING_URL else {"oops": 1}
        with mock.patch.object(weather, "_get_json", side_effect=broken):
            with self.assertRaises(ServiceError):
                weather.get_forecast(self.male)

    def test_offline_gives_friendly_error(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("down")):
            with self.assertRaises(ServiceError) as ctx:
                weather.get_forecast(self.male)
        self.assertIn("unavailable", str(ctx.exception))

    def test_describe(self):
        self.assertEqual(weather.describe(0), "Clear sky")
        self.assertEqual(weather.describe(12345), "Unknown")


class TestSearchBy(Base):
    def test_exact_and_case_insensitive(self):
        results, corrected = countries.search_by("country", "TURKEY")
        self.assertEqual([c.city for c in results], ["Istanbul"])
        self.assertFalse(corrected)

    def test_misspelled_country_and_city_are_corrected(self):
        results, corrected = countries.search_by("country", "turky")
        self.assertEqual([c.city for c in results], ["Istanbul"])
        self.assertTrue(corrected)
        results, corrected = countries.search_by("city", "pariss")
        self.assertEqual([c.city for c in results], ["Paris"])
        self.assertTrue(corrected)

    def test_nonsense_finds_nothing(self):
        self.assertEqual(countries.search_by("country", "qqqqqqq"), ([], False))

    def test_by_type(self):
        for kind in countries.CATEGORIES:
            results, _ = countries.search_by("category", kind)
            self.assertTrue(results)
            self.assertTrue(all(c.category == kind for c in results))


class TestSuspendedTrips(Base):
    def setUp(self):
        super().setUp()
        self.user = make_customer()
        self.bali = city_id("Bali")

    def test_old_data_without_the_field_still_loads(self):
        self.assertFalse(countries.get(self.bali).suspended)

    def test_suspend_and_resume(self):
        self.assertTrue(countries.set_suspended(self.bali, True).suspended)
        self.assertTrue(countries.get(self.bali).suspended)
        self.assertFalse(countries.set_suspended(self.bali, False).suspended)
        with self.assertRaises(ServiceError):
            countries.set_suspended(9999, True)

    def test_editing_keeps_the_suspension(self):
        countries.set_suspended(self.bali, True)
        self.assertTrue(countries.update(self.bali, {"hotel": 260}).suspended)

    def test_suspended_trip_cannot_be_booked_until_resumed(self):
        countries.set_suspended(self.bali, True)
        with self.assertRaises(ServiceError):
            bookings.create(self.user.id, self.bali, FUTURE, 4, 1, "standard")
        countries.set_suspended(self.bali, False)
        self.assertEqual(bookings.create(self.user.id, self.bali, FUTURE, 4, 1, "standard").status, "pending")

    def test_suspended_trip_is_hidden_from_plans_and_recommendations(self):
        countries.set_suspended(self.bali, True)
        matches, _ = planner.find_matches(50000, 5, 1, "standard", category="beach")
        self.assertEqual([c.city for c, _ in matches], ["Male"])
        picks = recommendations.recommend(self.user.id, limit=30, category="beach")
        self.assertEqual([c.city for c, _ in picks], ["Male"])


class TestRecommendationsByType(Base):
    def test_only_the_chosen_type(self):
        u = make_customer()
        for kind in countries.CATEGORIES:
            picks = recommendations.recommend(u.id, category=kind)
            self.assertTrue(picks)
            self.assertTrue(all(c.category == kind for c, _ in picks), kind)

    def test_type_filter_works_with_history(self):
        u = make_customer()
        bookings.create(u.id, city_id("Bali"), FUTURE, 5, 1, "standard")
        picks = recommendations.recommend(u.id, category="culture")
        self.assertTrue(picks)
        self.assertTrue(all(c.category == "culture" for c, _ in picks))

    def test_nothing_left_to_recommend(self):
        u = make_customer()
        for city in ("Bali", "Male"):
            bookings.create(u.id, city_id(city), FUTURE, 5, 1, "standard")
        self.assertEqual(recommendations.recommend(u.id, category="beach"), [])


class TestWelcomeNotes(Base):
    def test_new_customer(self):
        u = make_customer()
        self.assertIn("No bookings yet", reports.welcome_notes(u)[0])

    def test_customer_with_unpaid_and_upcoming(self):
        u = make_customer()
        b = bookings.create(u.id, city_id("Dubai"), FUTURE, 3, 1, "standard")
        self.assertEqual(reports.welcome_notes(u), ["You have 1 unpaid booking(s)."])
        bookings.pay(b.id, u.id, "apple_pay")
        self.assertEqual(reports.welcome_notes(u), [f"Your next trip starts on {FUTURE}."])

    def test_manager_notes(self):
        admin = auth.login("admin", "admin123")
        self.assertEqual(len(reports.welcome_notes(admin)), 1)
        countries.set_suspended(city_id("Bali"), True)
        self.assertIn("1 trip(s) are suspended", reports.welcome_notes(admin)[1])

class TestCustomerAccounts(Base):

    def setUp(self):
        super().setUp()
        self.sara = make_customer("sara")
        self.omar = make_customer("omar")

        self.paid = bookings.create(self.sara.id, city_id("Dubai"), FUTURE, 3, 1, "standard")
        bookings.pay(self.paid.id, self.sara.id, "apple_pay")
        self.pending = bookings.create(self.sara.id, city_id("Paris"), FUTURE, 3, 1, "standard")
        self.done = bookings.create(self.sara.id, city_id("Cairo"), FUTURE, 3, 1, "standard")
        bookings.pay(self.done.id, self.sara.id, "apple_pay")
        bookings.set_status(self.done.id, "completed")
        self.omar_booking = bookings.create(self.omar.id, city_id("Rome"), FUTURE, 3, 1, "standard")

    def test_overview_lists_customers_only(self):
        rows = {row.user.username: row for row in users.customer_overview()}
        self.assertEqual(set(rows), {"sara", "omar"})
        self.assertEqual((rows["sara"].bookings, rows["sara"].active), (3, 2))
        self.assertEqual(rows["sara"].paid_total, self.paid.total_price + self.done.total_price)
        self.assertEqual((rows["omar"].bookings, rows["omar"].paid_total), (1, 0))

    def test_directory_maps_ids_to_users(self):
        directory = users.directory()
        self.assertEqual(directory[self.sara.id].email, "sara@mail.com")
        self.assertEqual(directory[self.sara.id].phone, PHONE)

    def test_managers_and_unknown_ids_cannot_be_deleted(self):
        admin = auth.login("admin", "admin123")
        for user_id in (admin.id, 9999):
            with self.assertRaises(ServiceError):
                users.delete_customer(user_id)
        self.assertEqual(auth.login("admin", "admin123").id, admin.id)

    def test_plan_changes_nothing(self):
        plan = users.plan_deletion(self.sara.id)
        self.assertEqual(len(plan.cancelled), 2)
        self.assertEqual(plan.refund_total, self.paid.total_price)
        self.assertEqual(plan.kept_history, 1)
        self.assertEqual(users.get(self.sara.id).username, "sara")
        self.assertEqual(bookings.get(self.paid.id).status, "confirmed")

    def test_delete_cancels_active_bookings_and_keeps_history(self):
        report = users.delete_customer(self.sara.id)
        self.assertEqual(report.refund_total, self.paid.total_price)
        self.assertEqual(report.kept_history, 1)
        with self.assertRaises(ServiceError):
            users.get(self.sara.id)
        with self.assertRaises(ServiceError):
            auth.login("sara", "secret1")
        self.assertEqual(bookings.get(self.paid.id).status, "cancelled")
        self.assertFalse(bookings.get(self.paid.id).paid)
        self.assertEqual(bookings.get(self.pending.id).status, "cancelled")
        self.assertEqual(bookings.get(self.done.id).status, "completed")
        self.assertEqual(bookings.get(self.omar_booking.id).status, "pending")

    def test_revenue_ignores_refunded_money(self):
        users.delete_customer(self.sara.id)
        self.assertEqual(reports.summary()["revenue"], self.done.total_price)

    def test_ids_of_deleted_customers_are_never_reused(self):
        users.delete_customer(self.omar.id)
        newcomer = auth.register("noor", "secret1", "Noor Ali", "noor@mail.com", PHONE)
        self.assertGreater(newcomer.id, self.omar.id)
        self.assertEqual(bookings.list_for_user(newcomer.id), [])


class FakeSMTPServer:

    def __init__(self):
        self.messages = []
        recorder = self

        class Handler(socketserver.StreamRequestHandler):
            def handle(self):
                self.wfile.write(b"220 fake.local ESMTP\r\n")
                in_data, lines = False, []
                while True:
                    line = self.rfile.readline()
                    if not line:
                        return
                    if in_data:
                        if line in (b".\r\n", b".\n"):
                            in_data = False
                            recorder.messages.append(
                                email.message_from_bytes(b"".join(lines), policy=email.policy.default))
                            lines = []
                            self.wfile.write(b"250 queued\r\n")
                        else:
                            lines.append(line[1:] if line.startswith(b"..") else line)
                        continue
                    command = line.decode("ascii", "replace").strip().upper()
                    if command.startswith(("EHLO", "HELO")):
                        self.wfile.write(b"250 fake.local\r\n")
                    elif command.startswith(("MAIL FROM", "RCPT TO", "RSET", "NOOP")):
                        self.wfile.write(b"250 OK\r\n")
                    elif command == "DATA":
                        in_data = True
                        self.wfile.write(b"354 go ahead\r\n")
                    elif command == "QUIT":
                        self.wfile.write(b"221 bye\r\n")
                        return
                    else:
                        self.wfile.write(b"502 not implemented\r\n")

        self.server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.port = self.server.server_address[1]

    def __enter__(self):
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *exc_info):
        self.server.shutdown()
        self.server.server_close()


def smtp_env(**overrides):
    values = {"SKYROUTE_SMTP_HOST": "127.0.0.1", "SKYROUTE_SMTP_PORT": "25", "SKYROUTE_SMTP_SECURITY": "none",
              "SKYROUTE_MAIL_FROM": "agency@skyroute.test", "SKYROUTE_SMTP_USER": "",
              "SKYROUTE_SMTP_PASSWORD": ""}
    values.update(overrides)
    return mock.patch.dict(os.environ, values)


class TestEmailSettings(Base):
    def test_not_configured_by_default(self):
        self.assertIsNone(notifications.load_settings())

    def test_gmail_style_settings(self):
        with smtp_env(SKYROUTE_SMTP_HOST="smtp.gmail.com", SKYROUTE_SMTP_PORT="465", SKYROUTE_SMTP_SECURITY="",
                      SKYROUTE_SMTP_USER="me@gmail.com", SKYROUTE_SMTP_PASSWORD="abcd efgh", SKYROUTE_MAIL_FROM=""):
            settings = notifications.load_settings()
        self.assertEqual((settings.host, settings.port, settings.security), ("smtp.gmail.com", 465, "ssl"))
        self.assertEqual(settings.sender, "me@gmail.com")
        self.assertEqual(settings.password, "abcd efgh")

    def test_port_587_uses_starttls(self):
        with smtp_env(SKYROUTE_SMTP_PORT="587", SKYROUTE_SMTP_SECURITY=""):
            self.assertEqual(notifications.load_settings().security, "starttls")

    def test_bad_settings_are_reported(self):
        for overrides in ({"SKYROUTE_SMTP_PORT": "abc"}, {"SKYROUTE_SMTP_SECURITY": "magic"},
                          {"SKYROUTE_MAIL_FROM": "", "SKYROUTE_SMTP_USER": ""}):
            with smtp_env(**overrides), self.assertRaises(ServiceError, msg=str(overrides)):
                notifications.load_settings()

    def test_env_file_is_read_and_environment_wins(self):
        env_file = Path(_TMP) / "test.env"
        env_file.write_text("\ufeff# comment\nSKYROUTE_SMTP_HOST = 'smtp.example.com'\n\n"
                            "SKYROUTE_MAIL_FROM=\"a@b.co\"\nnot a setting\n", encoding="utf-8")
        self.assertEqual(read_env_file(env_file),
                         {"SKYROUTE_SMTP_HOST": "smtp.example.com", "SKYROUTE_MAIL_FROM": "a@b.co"})
        self.assertEqual(read_env_file(Path(_TMP) / "missing.env"), {})
        with mock.patch.object(notifications, "ENV_FILE", env_file):
            with mock.patch.dict(os.environ, {"SKYROUTE_SMTP_HOST": ""}):
                self.assertIsNone(notifications.load_settings())
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("SKYROUTE_SMTP_HOST", None)
                self.assertEqual(notifications.load_settings().host, "smtp.example.com")


class TestEmailSending(Base):
    def outbox_files(self):
        return sorted(OUTBOX_DIR.glob("*.txt")) if OUTBOX_DIR.exists() else []

    def test_without_smtp_a_copy_is_saved(self):
        result = notifications.send_email("sara@mail.com", "Hello  there\n", "Body text")
        self.assertEqual((result.status, result.recipient), ("saved", "sara@mail.com"))
        saved = (OUTBOX_DIR / result.outbox_file).read_text(encoding="utf-8")
        self.assertIn("To: sara@mail.com", saved)
        self.assertIn("Subject: Hello there", saved)
        self.assertIn("Body text", saved)

    def test_real_smtp_conversation(self):
        with FakeSMTPServer() as server:
            with smtp_env(SKYROUTE_SMTP_PORT=str(server.port)):
                result = notifications.send_email("sara@mail.com", "Hi\nBcc: evil@x.y", "Line one\nLine two")
        self.assertEqual(result.status, "sent")
        self.assertEqual(self.outbox_files(), [])
        message = server.messages[0]
        self.assertEqual((message["To"], message["From"]), ("sara@mail.com", "agency@skyroute.test"))
        self.assertEqual(message["Subject"], "Hi Bcc: evil@x.y")
        self.assertIsNone(message["Bcc"])
        self.assertIn("Line two", message.get_content())

    def test_a_computer_name_with_arabic_letters_does_not_break_sending(self):

        with FakeSMTPServer() as server, mock.patch("socket.getfqdn", return_value="جهاز-محمد.local"):
            with smtp_env(SKYROUTE_SMTP_PORT=str(server.port)):
                result = notifications.send_email("sara@mail.com", "Hi", "Body")
        self.assertEqual(result.status, "sent")
        self.assertEqual(len(server.messages), 1)

    def test_an_encoding_error_is_reported_not_raised(self):
        with smtp_env(SKYROUTE_SMTP_PORT="465", SKYROUTE_SMTP_SECURITY="ssl", SKYROUTE_SMTP_USER="me@gmail.com",
                      SKYROUTE_SMTP_PASSWORD="p"), mock.patch("smtplib.SMTP_SSL", side_effect=UnicodeEncodeError(
                          "ascii", "م", 0, 1, "ordinal not in range")):
            result = notifications.send_email("sara@mail.com", "Subject", "Body")
        self.assertEqual(result.status, "failed")
        self.assertIn("character", result.detail)
        self.assertEqual(len(self.outbox_files()), 1)

    def test_ssl_login_and_send(self):
        with smtp_env(SKYROUTE_SMTP_PORT="465", SKYROUTE_SMTP_SECURITY="ssl", SKYROUTE_SMTP_USER="me@gmail.com",
                      SKYROUTE_SMTP_PASSWORD="app-pass"), mock.patch("smtplib.SMTP_SSL") as smtp_ssl:
            result = notifications.send_email("sara@mail.com", "Subject", "Body")
        self.assertEqual(result.status, "sent")
        client = smtp_ssl.return_value
        client.login.assert_called_once_with("me@gmail.com", "app-pass")
        client.send_message.assert_called_once()

    def test_starttls_runs_before_login(self):
        with smtp_env(SKYROUTE_SMTP_PORT="587", SKYROUTE_SMTP_SECURITY="starttls", SKYROUTE_SMTP_USER="u",
                      SKYROUTE_SMTP_PASSWORD="p"), mock.patch("smtplib.SMTP") as smtp:
            notifications.send_email("sara@mail.com", "Subject", "Body")
        names = [call[0] for call in smtp.return_value.method_calls]
        self.assertEqual([n for n in names if n in ("starttls", "login", "send_message")],
                         ["starttls", "login", "send_message"])

    def test_wrong_password_is_explained_and_a_copy_is_saved(self):
        with smtp_env(SKYROUTE_SMTP_PORT="465", SKYROUTE_SMTP_SECURITY="ssl", SKYROUTE_SMTP_USER="me@gmail.com",
                      SKYROUTE_SMTP_PASSWORD="super-secret"), mock.patch("smtplib.SMTP_SSL") as smtp_ssl:
            smtp_ssl.return_value.login.side_effect = smtplib.SMTPAuthenticationError(535, b"rejected")
            result = notifications.send_email("sara@mail.com", "Subject", "Body")
        self.assertEqual(result.status, "failed")
        self.assertIn("App Password", result.detail)
        self.assertNotIn("super-secret", result.detail)
        self.assertEqual(len(self.outbox_files()), 1)

    def test_unreachable_server_never_raises(self):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            closed_port = probe.getsockname()[1]
        with smtp_env(SKYROUTE_SMTP_PORT=str(closed_port)):
            result = notifications.send_email("sara@mail.com", "Subject", "Body")
        self.assertEqual(result.status, "failed")
        self.assertIn("mail server", result.detail)
        self.assertEqual(len(self.outbox_files()), 1)

    def test_an_address_the_email_library_refuses_does_not_crash(self):
        with FakeSMTPServer() as server, smtp_env(SKYROUTE_SMTP_PORT=str(server.port)):
            result = notifications.send_email("a@b.co\nBcc: evil@x.y", "Subject", "Body")
        self.assertEqual(result.status, "failed")
        self.assertEqual(server.messages, [])

    def test_bad_settings_do_not_crash_either(self):
        with smtp_env(SKYROUTE_SMTP_PORT="abc"):
            result = notifications.send_email("sara@mail.com", "Subject", "Body")
        self.assertEqual(result.status, "failed")
        self.assertIn("SKYROUTE_SMTP_PORT", result.detail)


class TestEmailContent(Base):
    def setUp(self):
        super().setUp()
        self.user = make_customer()
        self.booking = bookings.create(self.user.id, city_id("Dubai"), FUTURE, 4, 2, "standard")

    def paid_booking(self):
        return bookings.pay(self.booking.id, self.user.id, "card", **CARD)

    def test_welcome_has_the_customer_id(self):
        subject, body = notifications.build_welcome(self.user)
        self.assertIn("Welcome", subject)
        self.assertIn(f"#{self.user.id}", body)
        self.assertIn("sara", body)

    def test_booking_received(self):
        subject, body = notifications.build_booking_message("created", self.booking, self.user)
        self.assertIn(f"#{self.booking.id}", subject)
        for text in ("Dubai", FUTURE, "pending payment", "Pay for a booking"):
            self.assertIn(text, body)

    def test_payment_email_is_a_receipt_and_never_has_card_details(self):
        paid = self.paid_booking()
        subject, body = notifications.build_booking_message("paid", paid, self.user)
        self.assertIn(paid.reference, subject)
        for text in ("Flights", "Hotel", "Total", "card"):
            self.assertIn(text, body)
        for secret in ("4242 4242", "4242424242424242", "cvv"):
            self.assertNotIn(secret, body.lower())

    def test_cancellation_with_and_without_a_refund(self):
        paid = self.paid_booking()
        _, body = notifications.build_booking_message("cancelled", paid, self.user, refund=paid.total_price)
        self.assertIn(REFUND_NOTICE, body)
        self.assertIn(f"{paid.total_price:,}", body)
        _, body = notifications.build_booking_message("cancelled", self.booking, self.user, refund=0)
        self.assertIn("nothing to refund", body)
        self.assertNotIn("refunded within", body)

    def test_completed_and_account_deleted(self):
        _, body = notifications.build_booking_message("completed", self.booking, self.user)
        self.assertIn("completed", body)
        subject, body = notifications.build_account_deleted(self.user, 2, 1500)
        self.assertIn("deleted", subject)
        self.assertIn("2 active booking(s)", body)
        self.assertIn(REFUND_NOTICE, body)

    def test_unknown_event(self):
        with self.assertRaises(ValueError):
            notifications.build_booking_message("exploded", self.booking, self.user)

    def test_notify_booking_sends_to_the_customers_email(self):
        with FakeSMTPServer() as server, smtp_env(SKYROUTE_SMTP_PORT=str(server.port)):
            result = notifications.notify_booking("created", self.booking)
            welcome = notifications.notify_welcome(self.user)
        self.assertEqual((result.status, welcome.status), ("sent", "sent"))
        self.assertEqual([m["To"] for m in server.messages], ["sara@mail.com", "sara@mail.com"])
        self.assertIn("booking", server.messages[0]["Subject"])

    def test_unknown_customer_gives_a_failed_result_not_a_crash(self):
        users.delete_customer(self.user.id)
        result = notifications.notify_booking("cancelled", self.booking)
        self.assertEqual(result.status, "failed")

        self.assertEqual(notifications.notify_booking("cancelled", self.booking, user=self.user).status, "saved")
        self.assertEqual(notifications.notify_account_deleted(self.user, 1, 0).status, "saved")


def tearDownModule():
    shutil.rmtree(_TMP, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
