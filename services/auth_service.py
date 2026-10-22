from models import Receptionist
from storage import json_store


def login(username, password):
    """Return the Receptionist if credentials are valid, otherwise None."""
    for d in json_store.load("receptionists"):
        r = Receptionist(**d)
        if r.username.lower() == username.strip().lower() and r.check_password(password):
            return r
    return None