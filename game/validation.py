import re


ARABIC_NAME = re.compile(r"[ء-ي]+(?: [ء-ي]+)*")
ENGLISH_NAME = re.compile(r"[A-Za-z]+(?: [A-Za-z]+)*")


def validate_explorer_name(name):
    name = " ".join(name.strip().split())

    if not name:
        return False, "لا يمكن ترك اسم المستكشف فارغًا."

    letters_count = len(name.replace(" ", ""))

    if letters_count < 2:
        return False, "يجب أن يحتوي الاسم على حرفين على الأقل."

    if letters_count > 30:
        return False, "يجب ألا يتجاوز الاسم 30 حرفًا."

    if ARABIC_NAME.fullmatch(name):
        return True, name

    if ENGLISH_NAME.fullmatch(name):
        return True, name

    return (
        False,
        "استخدم حروفًا عربية فقط أو إنجليزية فقط، دون أرقام أو رموز.",
    )