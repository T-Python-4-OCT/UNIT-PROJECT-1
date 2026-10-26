class KickoffError(Exception):
    """Base class for every expected error in the program."""


class InvalidSeatError(KickoffError):
    pass


class SeatTakenError(KickoffError):
    pass


class SeatHeldError(KickoffError):
    pass


class CartLimitError(KickoffError):
    pass


class EmptyCartError(KickoffError):
    pass


class MatchClosedError(KickoffError):
    pass


class PaymentError(KickoffError):
    pass


class NotFoundError(KickoffError):
    pass