from abc import ABC, abstractmethod

from .errors import PaymentError


class PaymentMethod(ABC):
    label: str = ""

    @abstractmethod
    def pay(self, amount: float) -> str:
        """Simulate the payment and return a reference text."""


class CardPayment(PaymentMethod):
    label = "Mada / Credit card"

    def __init__(self, number: str) -> None:
        digits = number.replace(" ", "")
        if not (digits.isdigit() and len(digits) == 16):
            raise PaymentError("Card number must be 16 digits.")
        self.__last4 = digits[-4:]            # private: we never keep the full number

    def pay(self, amount: float) -> str:
        return f"CARD-****{self.__last4}"


class ApplePay(PaymentMethod):
    label = "Apple Pay"

    def pay(self, amount: float) -> str:
        return "APPLEPAY-OK"


class StcPay(PaymentMethod):
    label = "STC Pay"

    def __init__(self, phone: str) -> None:
        if not (phone.isdigit() and len(phone) == 10 and phone.startswith("05")):
            raise PaymentError("STC Pay phone must look like 05XXXXXXXX.")
        self.__phone = phone

    def pay(self, amount: float) -> str:
        return f"STCPAY-***{self.__phone[-3:]}"