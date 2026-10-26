from dataclasses import asdict, dataclass

from agency.config import (DEFAULT_PROMO_PERCENT, MAX_PROMO_PERCENT, PROMOS_FILE,
                           YEAR_END_PROMO_PERCENT)
from agency.errors import ServiceError
from agency.storage import json_db
from agency.utils import validators


# كود خصم لمناسبة: الكود والمناسبة والنسبة وهل هو شغال.
@dataclass
class Promo:
    code: str
    occasion: str
    percent: int
    active: bool = True


YEAR_END_CODE = "YEAREND10"

STARTER_CODES = [
    ("EID20", "Eid holiday", DEFAULT_PROMO_PERCENT),
    (YEAR_END_CODE, "End-of-year holiday", YEAR_END_PROMO_PERCENT),
]


# توحّد شكل الكود (حروف كبيرة بدون مسافات).
def normalize(code: str) -> str:
    return code.strip().upper()


# تقرأ أكواد الخصم من الملف.
def _load() -> list:
    return [Promo(**record) for record in json_db.load(PROMOS_FILE)]


# تحفظ أكواد الخصم في الملف.
def _save(promos: list) -> None:
    json_db.save(PROMOS_FILE, [asdict(promo) for promo in promos])


# تضيف أكواد البداية EID20 وYEAREND20 أول تشغيل.
def seed() -> None:
    if not PROMOS_FILE.exists():
        _save([Promo(code, occasion, percent) for code, occasion, percent in STARTER_CODES])


# ترجع كل أكواد الخصم.
def list_all() -> list:
    return sorted(_load(), key=lambda promo: promo.code)


# تدور على كود بالاسم أو ترمي ServiceError إذا ما وجد.
def _find(promos: list, code: str) -> Promo:
    wanted = normalize(code)
    for promo in promos:
        if promo.code == wanted:
            return promo
    raise ServiceError(f"Discount code '{wanted}' does not exist.")


# ترجع الكود إذا كان شغال، وإلا ترمي ServiceError.
def get_active(code: str) -> Promo:
    promo = _find(_load(), code)
    if not promo.active:
        raise ServiceError(f"Discount code '{promo.code}' is not active right now.")
    return promo


# المدير يضيف كود خصم جديد بعد التحقق من الكود والمناسبة والنسبة.
def add(code: str, occasion: str, percent: int = DEFAULT_PROMO_PERCENT) -> Promo:
    code = normalize(code)
    if not validators.is_valid_promo_code(code):
        raise ServiceError("Code must be 3-15 letters or numbers, for example EID20.")
    occasion = occasion.strip()
    if not occasion or not occasion.isprintable() or len(occasion) > 40:
        raise ServiceError("Occasion name must be 1-40 characters.")
    if not 1 <= percent <= MAX_PROMO_PERCENT:
        raise ServiceError(f"Discount must be between 1% and {MAX_PROMO_PERCENT}%.")
    promos = _load()
    if any(promo.code == code for promo in promos):
        raise ServiceError(f"Discount code '{code}' already exists.")
    promo = Promo(code, occasion, percent)
    promos.append(promo)
    _save(promos)
    return promo


# ترجع هل الكود شغال (True) أو موقوف (False).
def get_state(code: str) -> bool:
    return _find(_load(), code).active


# تشغّل الكود أو توقفه وترجعه.
def set_active(code: str, active: bool) -> Promo:
    promos = _load()
    promo = _find(promos, code)
    promo.active = active
    _save(promos)
    return promo


# تحذف كود خصم (الحجوزات القديمة تحتفظ بخصمها).
def delete(code: str) -> Promo:
    promos = _load()
    promo = _find(promos, code)
    promos.remove(promo)
    _save(promos)
    return promo
