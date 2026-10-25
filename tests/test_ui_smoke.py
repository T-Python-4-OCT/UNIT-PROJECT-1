import os
import sys
import tempfile
import unittest
from unittest import mock

_TMP = tempfile.mkdtemp()
os.environ.setdefault("SKYROUTE_DATA_DIR", _TMP)

os.environ["SKYROUTE_SMTP_HOST"] = ""

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

import contextlib
import shutil
from datetime import date, timedelta

import main
from agency import seed
from agency.config import (BOOKINGS_FILE, COUNTRIES_FILE, DEFAULT_DAYS,
                           MAX_DAYS, MIN_DAYS, OUTBOX_DIR, PROMOS_FILE, USERS_FILE)
from agency.errors import ServiceError
from agency.services import (auth, bookings, countries, notifications, planner, promos, reports,
                             users, weather)
from agency.ui import console as ui_console

ui_console.console._color_system = None   # plain text in the captured output, even in a real terminal
from agency.ui import customer_menu, manager_menu, views
from agency.ui.console import GoBack

PHONE = "0501234567"

FUTURE = (date.today() + timedelta(days=30)).isoformat()
FAKE_WEATHER = {"city": "X", "temperature": 31.0, "wind": 5.0, "condition": "Clear sky",
                "days": [{"date": "2026-10-21", "max": 33.0, "min": 25.0, "condition": "Clear sky"}] * 3}


def city_id(city):
    return next(c.id for c in countries.list_all() if c.city == city)


def fresh_data():
    for path in (USERS_FILE, COUNTRIES_FILE, BOOKINGS_FILE, PROMOS_FILE):
        if path.exists():
            path.unlink()
    shutil.rmtree(OUTBOX_DIR, ignore_errors=True)
    seed.run()


def outbox_texts():
    files = sorted(OUTBOX_DIR.glob("*.txt")) if OUTBOX_DIR.exists() else []
    return [file.read_text(encoding="utf-8") for file in files]


def run_screen(module, action, **patches):
    ui_console.console.width = 240
    patcher = mock.patch.multiple(module, **patches) if patches else contextlib.nullcontext()
    try:
        with patcher, module.console.capture() as cap:
            action()
    finally:
        ui_console.console.width = None
    return " ".join(cap.get().split())


NEW_COUNTRY = {
    "Country": "Kenya", "Most famous city": "Nairobi", "Best season": "Jun-Oct",
    "Highlights (comma separated)": "Safari, Giraffe Centre",
}


def answer_by_label(values):
    def fake(label, *args, **kwargs):
        default = kwargs.get("default")
        if default is None and args and not isinstance(args[0], (tuple, list)):
            default = args[0]
        for key, value in values.items():
            if label.startswith(key):
                return value
        if default is not None:
            return default
        raise AssertionError(f"Unexpected prompt: {label}")
    return fake


class TestManagerMenu(unittest.TestCase):
    def setUp(self):
        fresh_data()

    def test_add_then_edit_then_delete_destination(self):
        ints = {"Round-trip flight": 2000, "Hotel per night": 300, "Food per day": 100,
                "Transport per day": 40, "Activities per day": 150}
        with mock.patch.object(manager_menu, "ask_text", side_effect=answer_by_label(NEW_COUNTRY)), \
             mock.patch.object(manager_menu, "ask_int", side_effect=answer_by_label(ints)), \
             mock.patch.object(manager_menu, "ask_choice", side_effect=answer_by_label({"Type": "adventure"})):
            manager_menu.add_destination()
        new = [c for c in countries.list_all() if c.city == "Nairobi"][0]
        self.assertEqual(new.highlights, ["Safari", "Giraffe Centre"])


        with mock.patch.object(manager_menu, "ask_int", side_effect=answer_by_label({"Hotel per night": 350})), \
             mock.patch.object(manager_menu, "ask_text", side_effect=answer_by_label({})), \
             mock.patch.object(manager_menu, "ask_choice", side_effect=answer_by_label({})):
            countries.update(new.id, manager_menu._ask_fields(new))
        self.assertEqual(countries.get(new.id).hotel, 350)
        self.assertEqual(countries.get(new.id).city, "Nairobi")

    def test_dashboard_runs_on_empty_data(self):
        manager_menu.dashboard()

    def test_suspend_and_resume_a_trip(self):
        bali = city_id("Bali")
        with mock.patch.object(manager_menu, "ask_int", return_value=bali), \
             mock.patch.object(manager_menu, "confirm", return_value=True), \
             manager_menu.console.capture() as cap:
            manager_menu.toggle_suspension()
        self.assertTrue(countries.get(bali).suspended)
        self.assertIn("suspended", cap.get())

        with mock.patch.object(manager_menu, "ask_int", return_value=bali), \
             mock.patch.object(manager_menu, "confirm", return_value=True):
            manager_menu.toggle_suspension()
        self.assertFalse(countries.get(bali).suspended)

    def test_declining_the_confirmation_changes_nothing(self):
        bali = city_id("Bali")
        with mock.patch.object(manager_menu, "ask_int", return_value=bali), \
             mock.patch.object(manager_menu, "confirm", return_value=False):
            manager_menu.toggle_suspension()
        self.assertFalse(countries.get(bali).suspended)


class TestCustomerMenu(unittest.TestCase):
    def setUp(self):
        fresh_data()
        self.user = auth.register("tester", "secret1", "Test User", "t@mail.com", PHONE)

    def test_back_cancels_without_saving(self):
        with mock.patch.object(customer_menu, "ask_int", side_effect=GoBack):
            with self.assertRaises(GoBack):
                customer_menu.book_trip(self.user)
        self.assertEqual(bookings.list_for_user(self.user.id), [])

    def test_every_trip_type_has_its_own_emoji(self):
        out = self.run_menu(lambda user: customer_menu.browse())
        for category, icon in (("city", "\U0001F306"), ("beach", "\U0001F334"),
                               ("culture", "\U0001F3FA"), ("adventure", "\U0001F9ED")):
            self.assertIn(f"{icon} {category}", out)
        with views.console.capture() as cap:
            views.show_country_detail(countries.get(city_id("Dubai")))
        self.assertIn("\U0001F306 city", " ".join(cap.get().split()))

    def test_destination_screens_show_the_country_flag(self):
        out = self.run_menu(lambda user: customer_menu.browse())
        self.assertIn("\U0001F1F9\U0001F1F7 Turkey", out)
        with views.console.capture() as cap:
            views.show_country_detail(countries.get(city_id("Dubai")))
        self.assertIn("\U0001F1E6\U0001F1EA Dubai, UAE", " ".join(cap.get().split()))

    def test_lists_and_details_show_the_group_and_year_end_offers(self):
        out = " ".join(self.run_menu(lambda user: customer_menu.browse()).split())
        self.assertIn("if you are 2 travelers you get 10% off", out)
        self.assertIn("in December there is an extra year-end discount code (10% off): YEAREND10", out)
        with views.console.capture() as cap:
            customer_menu._show_destination_report(countries.get(city_id("Dubai")))
        self.assertIn("in December", " ".join(cap.get().split()))

    def test_empty_lists_do_not_crash(self):
        customer_menu.my_bookings(self.user)
        customer_menu.pay(self.user)
        customer_menu.cancel(self.user)
        customer_menu.receipt(self.user)
        customer_menu.browse()

    def test_details_survives_no_internet(self):
        with mock.patch.object(customer_menu, "ask_int", return_value=10), \
             mock.patch("urllib.request.urlopen", side_effect=OSError("offline")):
            customer_menu.details()

    def run_menu(self, action, **patches):
        return run_screen(customer_menu, lambda: action(self.user), **patches)

    def booked(self, city="Dubai", pay=False):
        booking = bookings.create(self.user.id, city_id(city), FUTURE, 4, 1, "standard")
        if pay:
            bookings.pay(booking.id, self.user.id, "apple_pay")
        return booking


    def test_recommend_shows_city_type_weather_and_7_day_plan(self):
        with mock.patch.object(weather, "get_forecast", return_value=FAKE_WEATHER):
            out = self.run_menu(customer_menu.recommend, ask_choice=mock.Mock(return_value="beach"),
                                ask_int=mock.Mock(return_value=DEFAULT_DAYS))
        for text in ("Bali", "Male", "beach", "Clear sky", "7-day plan", "Day 7"):
            self.assertIn(text, out)
        self.assertNotIn("Paris", out)

    def test_recommend_plan_follows_the_days_the_customer_chose(self):
        with mock.patch.object(weather, "get_forecast", return_value=FAKE_WEATHER):
            out = self.run_menu(customer_menu.recommend, ask_choice=mock.Mock(return_value="beach"),
                                ask_int=mock.Mock(return_value=3))
        self.assertIn("3-day plan", out)
        self.assertIn("Day 3", out)
        self.assertNotIn("Day 4", out)

    def test_recommend_without_weather_still_shows_trips(self):
        with mock.patch.object(weather, "get_forecast", side_effect=ServiceError("offline")):
            out = self.run_menu(customer_menu.recommend, ask_choice=mock.Mock(return_value="culture"),
                                ask_int=mock.Mock(return_value=DEFAULT_DAYS))
        self.assertIn("not available right now", out)
        self.assertIn("Day 7", out)


    def test_days_question_suggests_7_and_allows_2_to_30(self):
        asked = mock.Mock(return_value=10)
        out = self.run_menu(lambda user: customer_menu._ask_days(), ask_int=asked)
        self.assertEqual((asked.call_args.kwargs["default"], asked.call_args.kwargs["minimum"],
                          asked.call_args.kwargs["maximum"]), (7, 2, 30))
        self.assertIn("7 days is a good trip", out)
        self.assertIn("choose what suits you", out)
        self.assertNotIn("type any number", out)
        self.assertEqual((DEFAULT_DAYS, MIN_DAYS, MAX_DAYS), (7, 2, 30))

    def test_the_customer_can_type_any_length_but_not_outside_the_limits(self):
        with mock.patch("agency.ui.console.Prompt.ask", side_effect=["1", "31", "abc", "12"]) as prompt, \
                ui_console.console.capture() as cap:
            days = ui_console.ask_int("Number of days", minimum=MIN_DAYS, maximum=MAX_DAYS, default=DEFAULT_DAYS)
        self.assertEqual(days, 12)
        self.assertEqual(prompt.call_args.kwargs["default"], "7")
        text = " ".join(cap.get().split())
        for message in ("at least 2", "at most 30", "whole number"):
            self.assertIn(message, text)

    def test_city_details_use_the_default_length_in_their_example(self):
        with views.console.capture() as cap:
            views.show_country_detail(countries.get(city_id("Dubai")))
        self.assertIn("Example: 7 days", cap.get())

    def test_city_details_use_the_travelers_and_style_the_user_chose(self):
        dubai = countries.get(city_id("Dubai"))
        with views.console.capture() as cap:
            views.show_country_detail(dubai, 5, 2, "luxury")
        text = " ".join(cap.get().split())
        total = planner.estimate(dubai, 5, 2, "luxury")["Total"]
        self.assertIn("Your trip: 5 days, 2 travelers, luxury style", text)
        self.assertIn(views.money(total), text)
        self.assertIn(f"{views.money(round(total / 2))} per person", text)
        self.assertNotIn("Example:", text)


    def test_card_payment_asks_name_number_cvv_and_lets_user_retry(self):
        booking = self.booked()
        answers = iter(["Sara1", "Sara Ali", "4242 4242 4242 4242", "12", "123"])
        out = self.run_menu(customer_menu.pay, ask_int=mock.Mock(return_value=booking.id),
                            ask_choice=mock.Mock(return_value="card"),
                            ask_text=mock.Mock(side_effect=lambda *a, **k: next(answers)))
        self.assertIn("Use letters only", out)
        self.assertIn("CVV must be 3 or 4 digits", out)
        self.assertIn("Payment received", out)
        self.assertTrue(bookings.get(booking.id).paid)

    def test_card_number_accepts_8_to_16_digits_and_refuses_the_rest(self):
        booking = self.booked()
        answers = iter(["Sara Ali", "1234567", "12345678901234567", "12345678", "123"])
        out = self.run_menu(customer_menu.pay, ask_int=mock.Mock(return_value=booking.id),
                            ask_choice=mock.Mock(return_value="card"),
                            ask_text=mock.Mock(side_effect=lambda *a, **k: next(answers)))
        self.assertEqual(out.count("Card number must be 8 to 16 digits"), 2)
        self.assertIn("Payment received", out)
        self.assertTrue(bookings.get(booking.id).paid)

    def test_payment_menu_has_no_bank_transfer(self):
        booking = self.booked()
        choices = mock.Mock(return_value="apple_pay")
        self.run_menu(customer_menu.pay, ask_int=mock.Mock(return_value=booking.id), ask_choice=choices)
        self.assertEqual(tuple(choices.call_args.args[1]), ("card", "apple_pay"))


    def test_cancel_paid_booking_shows_refund_time(self):
        booking = self.booked(pay=True)
        out = self.run_menu(customer_menu.cancel, ask_int=mock.Mock(return_value=booking.id),
                            confirm=mock.Mock(return_value=True))
        self.assertIn("24 hours to 4 business days", out)

    def test_cancel_unpaid_booking_has_no_refund_message(self):
        booking = self.booked()
        out = self.run_menu(customer_menu.cancel, ask_int=mock.Mock(return_value=booking.id),
                            confirm=mock.Mock(return_value=True))
        self.assertNotIn("refunded", out)


    def test_search_by_country_fixes_a_spelling_mistake(self):
        out = self.run_menu(lambda user: customer_menu.search(), ask_choice=mock.Mock(return_value="country"),
                            ask_text=mock.Mock(return_value="turky"), ask_int=mock.Mock(return_value=0))
        self.assertIn("closest spelling", out)
        self.assertIn("Istanbul", out)

    def test_search_by_type(self):
        out = self.run_menu(lambda user: customer_menu.search(),
                            ask_choice=mock.Mock(side_effect=["type", "adventure"]),
                            ask_int=mock.Mock(return_value=0))
        self.assertIn("Zurich", out)
        self.assertNotIn("Paris", out)
        self.assertNotIn("Live weather", out)

    def test_search_then_pick_a_result_shows_city_details_and_weather(self):
        with mock.patch.object(weather, "get_forecast", return_value=FAKE_WEATHER):
            out = self.run_menu(lambda user: customer_menu.search(),
                                ask_choice=mock.Mock(side_effect=["type", "beach"]),
                                ask_int=mock.Mock(return_value=city_id("Bali")))
        for text in ("Destination #", "Highlights", "Uluwatu Temple", "Daily costs per person",
                     "Live weather", "Clear sky", "Forecast"):
            self.assertIn(text, out)

    def test_search_only_accepts_an_id_from_the_results(self):
        with mock.patch.object(weather, "get_forecast", return_value=FAKE_WEATHER):
            out = self.run_menu(lambda user: customer_menu.search(),
                                ask_choice=mock.Mock(side_effect=["type", "beach"]),
                                ask_int=mock.Mock(side_effect=[city_id("Paris"), 0]))
        self.assertIn("one of the IDs shown", out)
        self.assertNotIn("Live weather", out)

    def test_search_details_survive_no_internet(self):
        with mock.patch.object(weather, "get_forecast", side_effect=ServiceError("Live weather is unavailable")):
            out = self.run_menu(lambda user: customer_menu.search(),
                                ask_choice=mock.Mock(side_effect=["type", "beach"]),
                                ask_int=mock.Mock(return_value=city_id("Bali")))
        self.assertIn("Highlights", out)
        self.assertIn("Live weather is unavailable", out)


    def test_budget_plan_table_shows_city_details(self):
        out = self.run_menu(customer_menu.plan_trip, ask_int=mock.Mock(side_effect=[20000, 5, 1, 0]),
                            ask_choice=mock.Mock(side_effect=["standard", "beach"]))
        for text in ("City details", "Bali", "Best season: Apr-Oct", "Highlights: Uluwatu Temple"):
            self.assertIn(text, out)

    def test_budget_plan_pick_shows_city_details_weather_and_the_full_plan(self):
        with mock.patch.object(weather, "get_forecast", return_value=FAKE_WEATHER):
            out = self.run_menu(customer_menu.plan_trip,
                                ask_int=mock.Mock(side_effect=[20000, DEFAULT_DAYS, 1, 1]),
                                ask_choice=mock.Mock(side_effect=["standard", "beach"]),
                                confirm=mock.Mock(return_value=False))
        for text in ("Destination #", "Highlights", "Daily costs per person", "Live weather", "Clear sky",
                     "Day 7", "Cost breakdown", "Remaining budget"):
            self.assertIn(text, out)


    def test_welcome_panel(self):
        with views.console.capture() as cap:
            views.show_welcome(self.user, reports.welcome_notes(self.user))
        out = cap.get()
        self.assertIn("Test User", out)
        self.assertIn("No bookings yet", out)
        self.assertIn(f"Customer ID: #{self.user.id}", out)


    def test_booking_a_trip_emails_the_customer(self):
        out = self.run_menu(customer_menu.book_trip, ask_int=mock.Mock(side_effect=[city_id("Dubai"), 7, 2]),
                            ask_choice=mock.Mock(return_value="standard"),
                            confirm=mock.Mock(side_effect=[True, False]),
                            ask_text=answer_by_label({"Travel date": FUTURE}))
        self.assertIn("Booking #1 created", out)
        self.assertIn("t@mail.com", out)
        mails = outbox_texts()
        self.assertEqual(len(mails), 1)
        self.assertIn("To: t@mail.com", mails[0])
        self.assertIn("booking #1 received", mails[0])
        self.assertIn("Dubai", mails[0])

    def test_paying_emails_the_receipt(self):
        booking = self.booked()
        out = self.run_menu(customer_menu.pay, ask_int=mock.Mock(return_value=booking.id),
                            ask_choice=mock.Mock(return_value="apple_pay"))
        self.assertIn("Payment received", out)
        reference = bookings.get(booking.id).reference
        self.assertIn(reference, outbox_texts()[-1])
        self.assertIn("payment confirmed", outbox_texts()[-1])

    def test_cancelling_a_paid_booking_emails_the_refund_notice(self):
        booking = self.booked(pay=True)
        self.run_menu(customer_menu.cancel, ask_int=mock.Mock(return_value=booking.id),
                      confirm=mock.Mock(return_value=True))
        self.assertIn("24 hours to 4 business days", outbox_texts()[-1])

    def test_a_failed_email_never_blocks_the_booking(self):
        failed = notifications_failed()
        with mock.patch.object(customer_menu.notifications, "notify_booking", return_value=failed):
            out = self.run_menu(customer_menu.book_trip, ask_int=mock.Mock(side_effect=[city_id("Dubai"), 7, 1]),
                                ask_choice=mock.Mock(return_value="standard"),
                                confirm=mock.Mock(side_effect=[True, False]),
                                ask_text=answer_by_label({"Travel date": FUTURE}))
        self.assertIn("could not be sent", out)
        self.assertEqual(len(bookings.list_for_user(self.user.id)), 1)


def notifications_failed():
    from agency.services.notifications import MailResult
    return MailResult("failed", "t@mail.com", "Could not reach the mail server: timed out")


class TestManagerCustomers(unittest.TestCase):

    def setUp(self):
        fresh_data()
        self.sara = auth.register("sara", "secret1", "Sara Ali", "sara@mail.com", PHONE)
        self.omar = auth.register("omar", "secret1", "Omar Saleh", "omar@mail.com", "+966555000111")
        self.paid = bookings.create(self.sara.id, city_id("Dubai"), FUTURE, 3, 1, "standard")
        bookings.pay(self.paid.id, self.sara.id, "apple_pay")
        self.pending = bookings.create(self.omar.id, city_id("Rome"), FUTURE, 3, 2, "standard")
        self.admin = auth.login("admin", "admin123")

    def screen(self, action, **patches):
        return run_screen(manager_menu, action, **patches)

    def test_booking_list_shows_who_booked(self):
        out = self.screen(manager_menu.list_bookings)
        for text in ("Sara Ali", "@sara", "sara@mail.com", PHONE, "Omar Saleh", "@omar", "omar@mail.com",
                     "+966555000111", "Dubai", "Rome"):
            self.assertIn(text, out)

    def test_customer_list_has_contact_details_and_numbers(self):
        out = self.screen(manager_menu.list_customers)
        for text in ("Customers", "Sara Ali", "sara@mail.com", PHONE, "Omar Saleh"):
            self.assertIn(text, out)
        self.assertNotIn("Agency Manager", out)

    def test_status_screen_lists_customers_and_emails_them_when_cancelled(self):
        out = self.screen(manager_menu.update_status, ask_int=mock.Mock(return_value=self.pending.id),
                          ask_choice=mock.Mock(return_value="cancelled"))
        self.assertIn("Omar Saleh", out)
        self.assertIn("is now cancelled", out)
        mail = outbox_texts()[-1]
        self.assertIn("To: omar@mail.com", mail)
        self.assertIn("cancelled", mail)

    def test_deleting_a_customer_cancels_refunds_and_tells_them(self):
        out = self.screen(manager_menu.delete_customer, ask_int=mock.Mock(return_value=self.sara.id),
                          confirm=mock.Mock(return_value=True))
        for text in ("Sara Ali (@sara) has 1 active booking(s)", "deleted", "1 booking(s) cancelled",
                     "refund total"):
            self.assertIn(text, out)
        with self.assertRaises(ServiceError):
            users.get(self.sara.id)
        self.assertEqual(bookings.get(self.paid.id).status, "cancelled")
        mails = [mail for mail in outbox_texts() if "To: sara@mail.com" in mail]
        self.assertEqual(len(mails), 2)
        self.assertTrue(any("24 hours to 4 business days" in mail for mail in mails))
        self.assertTrue(any("account was deleted" in mail for mail in mails))

    def test_the_deleted_customers_booking_stays_in_the_list_as_history(self):
        self.screen(manager_menu.delete_customer, ask_int=mock.Mock(return_value=self.sara.id),
                    confirm=mock.Mock(return_value=True))
        out = self.screen(manager_menu.list_bookings)
        self.assertIn(f"Deleted customer #{self.sara.id}", out)
        self.assertIn("Omar Saleh", out)

    def test_declining_the_confirmation_deletes_nothing(self):
        out = self.screen(manager_menu.delete_customer, ask_int=mock.Mock(return_value=self.sara.id),
                          confirm=mock.Mock(return_value=False))
        self.assertIn("Nothing was deleted", out)
        self.assertEqual(users.get(self.sara.id).username, "sara")
        self.assertEqual(bookings.get(self.paid.id).status, "confirmed")

    def test_a_manager_cannot_be_deleted(self):
        with self.assertRaises(ServiceError):
            self.screen(manager_menu.delete_customer, ask_int=mock.Mock(return_value=self.admin.id),
                        confirm=mock.Mock(return_value=True))
        self.assertEqual(auth.login("admin", "admin123").id, self.admin.id)

    def test_empty_customer_list_is_friendly(self):
        fresh_data()
        for action in (manager_menu.list_customers, manager_menu.delete_customer):
            self.assertIn("no customers yet", self.screen(action))

    def test_the_menu_loop_reaches_the_new_screens(self):
        out = self.screen(lambda: manager_menu.run(self.admin), pause=mock.Mock(),
                          ask_choice=mock.Mock(side_effect=["2", "4", "0"]))
        for text in ("Delete a customer", "Discount codes", "List customers", "All bookings", "Customers", "Sara Ali"):
            self.assertIn(text, out)


class TestDiscounts(unittest.TestCase):
    def setUp(self):
        fresh_data()
        self.user = auth.register("tester", "secret1", "Test User", "t@mail.com", PHONE)

    def book(self, code_answers, travelers=2, pay_now=False, card=("Sara Ali", "12345678", "123")):
        codes = iter(code_answers)
        cards = iter(card)

        def text(label, *args, **kwargs):
            if label.startswith("Travel date"):
                return FUTURE
            if label.startswith("Do you have a discount code"):
                return next(codes)
            return next(cards)
        return run_screen(customer_menu, lambda: customer_menu.book_trip(self.user),
                          ask_int=mock.Mock(side_effect=[city_id("Dubai"), 7, travelers]),
                          ask_choice=mock.Mock(side_effect=["standard", "card"]),
                          confirm=mock.Mock(side_effect=[True, pay_now]), ask_text=text)

    def test_the_travelers_question_announces_the_offer_for_two(self):
        out = self.book(["no"])
        self.assertIn("if you are 2 travelers you get 10% off", out)

    def test_two_travelers_pay_10_percent_less_in_the_quote_and_the_booking(self):
        out = self.book(["no"], travelers=2)
        booking = bookings.list_for_user(self.user.id)[0]
        self.assertIn("Group discount (10%)", out)
        self.assertIn("Group discount (10%)", booking.breakdown)
        solo = self.book(["no"], travelers=1)
        self.assertNotIn("Group discount", solo)

    def test_a_valid_code_is_accepted_and_lowers_the_price(self):
        out = self.book(["eid20"], travelers=1)
        booking = bookings.list_for_user(self.user.id)[0]
        self.assertIn("Code EID20 accepted: 20% off", out)
        self.assertEqual(booking.promo_code, "EID20")
        self.assertIn("Code EID20 (20%)", booking.breakdown)

    def test_a_wrong_code_asks_again_and_no_skips_it(self):
        out = self.book(["WRONG1", "no"], travelers=1)
        self.assertIn("does not exist", out)
        self.assertEqual(bookings.list_for_user(self.user.id)[0].promo_code, "")

    def test_a_switched_off_code_is_refused(self):
        promos.set_active("EID20", False)
        out = self.book(["EID20", "no"], travelers=1)
        self.assertIn("is not active right now", out)

    def test_after_the_booking_the_customer_goes_straight_to_payment(self):
        out = self.book(["no"], travelers=1, pay_now=True)
        booking = bookings.list_for_user(self.user.id)[0]
        self.assertIn("Amount due", out)
        self.assertIn("Payment received", out)
        self.assertTrue(booking.paid)
        self.assertEqual(booking.status, "confirmed")

    def test_declining_payment_leaves_the_booking_pending(self):
        out = self.book(["no"], travelers=1, pay_now=False)
        self.assertIn("Pay for a booking", out)
        self.assertEqual(bookings.list_for_user(self.user.id)[0].status, "pending")

    def test_the_receipt_shows_the_discount_lines(self):
        self.book(["EID20"], travelers=2, pay_now=True)
        booking = bookings.list_for_user(self.user.id)[0]
        with views.console.capture() as cap:
            views.show_receipt(booking, "Test User")
        text = " ".join(cap.get().split())
        self.assertIn("Group discount (10%)", text)
        self.assertIn("Code EID20 (20%)", text)


class TestManagerDiscountCodes(unittest.TestCase):
    def setUp(self):
        fresh_data()

    def run_codes(self, choices, **answers):
        return run_screen(manager_menu, manager_menu.discount_codes,
                          ask_choice=mock.Mock(side_effect=choices),
                          ask_text=answer_by_label(answers), ask_int=answer_by_label(answers),
                          confirm=mock.Mock(return_value=True))

    def test_the_list_shows_the_starter_codes(self):
        out = self.run_codes(["l"])
        for text in ("EID20", "YEAREND10", "20%", "active"):
            self.assertIn(text, out)

    def test_the_manager_adds_a_code_with_the_default_20_percent(self):
        out = self.run_codes(["a", "l"], **{"New code": "ADHA20", "Occasion": "Eid Al-Adha"})
        self.assertIn("Code ADHA20 created: 20% off", out)
        self.assertEqual(promos.get_active("ADHA20").percent, 20)

    def test_switch_off_and_on_again(self):
        out = self.run_codes(["t", "l"], **{"Code to switch": "EID20"})
        self.assertIn("is now off", out)
        with self.assertRaises(ServiceError):
            promos.get_active("EID20")
        self.run_codes(["t", "l"], **{"Code to switch": "EID20"})
        self.assertTrue(promos.get_active("EID20").active)

    def test_delete_a_code(self):
        self.run_codes(["d", "l"], **{"Code to delete": "YEAREND10"})
        self.assertEqual([p.code for p in promos.list_all()], ["EID20"])

    def test_mistakes_are_shown_in_red_and_the_screen_keeps_going(self):
        out = self.run_codes(["a", "t", "l"], **{"New code": "EID20", "Occasion": "Duplicate",
                                                 "Code to switch": "NOPE99"})
        self.assertIn("already exists", out)
        self.assertIn("does not exist", out)


class TestTestEmailCommand(unittest.TestCase):
    def setUp(self):
        fresh_data()

    def test_it_sends_one_message_to_the_given_address(self):
        with views.console.capture() as cap:
            main.test_email("me@mail.com")
        self.assertIn("me@mail.com", " ".join(cap.get().split()))
        mails = outbox_texts()
        self.assertEqual(len(mails), 1)
        self.assertIn("test email", mails[0])

    def test_a_bad_address_sends_nothing(self):
        with main.console.capture() as cap:
            main.test_email("not-an-email")
        self.assertIn("does not look like an email", cap.get())
        self.assertEqual(outbox_texts(), [])


class TestRegistrationScreen(unittest.TestCase):
    def setUp(self):
        fresh_data()

    ANSWERS = {"Choose a username": "noor", "Full name": "Noor Ali", "Email": "noor@mail.com",
               "Mobile number": "055 123 4567"}

    def register(self, **answers):
        values = {**self.ANSWERS, **answers}
        with mock.patch.object(main, "ask_text", side_effect=answer_by_label(values)), \
                mock.patch.object(main, "ask_password", return_value="secret1"), \
                main.console.capture() as cap:
            user = main.do_register()
        return user, " ".join(cap.get().split())

    def test_asks_for_the_phone_shows_the_customer_id_and_sends_a_welcome_email(self):
        user, out = self.register()
        self.assertEqual((user.phone, user.email), ("0551234567", "noor@mail.com"))
        self.assertIn(f"Your customer ID is #{user.id}", out)
        self.assertIn("noor@mail.com", out)
        mail = outbox_texts()[0]
        self.assertIn("To: noor@mail.com", mail)
        self.assertIn(f"Customer ID : #{user.id}", mail)

    def test_a_bad_phone_number_is_refused(self):
        with self.assertRaises(ServiceError):
            self.register(**{"Mobile number": "12"})
        self.assertEqual(outbox_texts(), [])


if __name__ == "__main__":
    unittest.main()
