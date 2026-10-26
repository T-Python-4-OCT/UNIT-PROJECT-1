"""Encryption of the users file (Fernet, from the `cryptography` library)."""
import os

from cryptography.fernet import Fernet, InvalidToken

from agency.config import DATA_DIR, ENV_FILE
from agency.errors import ServiceError
from agency.utils.env_file import read_env_file

KEY_NAME = "SKYROUTE_DATA_KEY"
KEY_FILE = DATA_DIR / "secret.key"


# تجيب مفتاح التشفير من البيئة أو .env، وإلا من data/secret.key (وتنشئه أول مرة).
def _load_key() -> bytes:
    """The key from the environment or .env, else from data/secret.key (created on the first run)."""
    key = os.environ.get(KEY_NAME) or read_env_file(ENV_FILE).get(KEY_NAME)
    if key:
        return key.strip().encode()
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes().strip()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    return key


# تبني أداة التشفير من المفتاح، وتعطي خطأ واضح إذا المفتاح غير صالح.
def _cipher() -> Fernet:
    """A Fernet object for the current key, or a friendly error if the key is not valid."""
    try:
        return Fernet(_load_key())
    except ValueError:
        raise ServiceError(f"{KEY_NAME} is not a valid key. Remove it to use data/secret.key instead.")


# تشفّر نص ويرجع بايتات تنكتب في الملف بأمان.
def encrypt(text: str) -> bytes:
    """Encrypt text (the result is safe to write to a file)."""
    return _cipher().encrypt(text.encode("utf-8"))


# تفك التشفير، وتعطي خطأ واضح إذا المفتاح خطأ أو مفقود.
def decrypt(data: bytes) -> str:
    """Decrypt data made by `encrypt`, or raise a friendly error if the key is wrong or missing."""
    try:
        return _cipher().decrypt(data.strip()).decode("utf-8")
    except InvalidToken:
        raise ServiceError("The user data cannot be decrypted: the key is missing or wrong "
                           "(it is stored in data/secret.key).")
