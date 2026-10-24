import getpass

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.theme import Theme

from agency.config import APP_NAME

THEME = Theme({
    "error": "bold red",
    "success": "bold green",
    "info": "cyan",
    "warn": "bold yellow",
    "title": "bold magenta",
})
console = Console(theme=THEME)


# تطبع رسالة نجاح بالأخضر.
def success(msg: str) -> None:
    console.print(f"✔ {escape(msg)}", style="success")


# تطبع رسالة خطأ بالأحمر.
def error(msg: str) -> None:
    console.print(f"✘ {escape(msg)}", style="error")


# تطبع معلومة بالسماوي.
def info(msg: str) -> None:
    console.print(escape(msg), style="info")


# تطبع تنبيه بالأصفر.
def warn(msg: str) -> None:
    console.print(f"! {escape(msg)}", style="warn")


# تطبع عنوان قسم بخط تحته.
def heading(text: str) -> None:
    console.print()
    console.rule(f"[title]{escape(text)}[/title]", style="magenta")


# تطبع شعار SkyRoute بحروف كبيرة (pyfiglet)، وإذا فشل تطبع الاسم عادي.
def show_banner() -> None:
    try:
        import pyfiglet
        art = pyfiglet.figlet_format(APP_NAME, font="slant")
        console.print(art, style="bold cyan", highlight=False)
    except Exception:
        console.print(f"=== {APP_NAME} ===", style="bold cyan")
    console.print(Panel("Your journey starts here ✈️", style="green", expand=False))


BACK_WORDS = ("b", "back")


# إشارة أن المستخدم كتب b للرجوع للقائمة.
class GoBack(Exception):
    pass


# إذا كتب المستخدم b أو back ترمي GoBack.
def _check_back(raw: str) -> None:
    if raw.strip().lower() in BACK_WORDS:
        raise GoBack


# تسأل سؤال نصي (مع قيمة افتراضية) وتكرره إذا الإجابة فاضية والحقل مطلوب.
def ask_text(label: str, default=None, required: bool = True) -> str:
    while True:
        kwargs = {} if default is None else {"default": str(default)}
        value = Prompt.ask(f"[bold]{escape(label)}[/bold]", console=console, **kwargs).strip()
        _check_back(value)
        if value or not required:
            return value
        error("This field is required.")


# تسأل عن كلمة السر بدون ما تظهر على الشاشة.
def ask_password(label: str = "Password") -> str:
    value = getpass.getpass(f"{label}: ")
    _check_back(value)
    return value


# تسأل عن رقم صحيح ضمن حد أدنى وأعلى، وتكرر السؤال إذا الإدخال غلط.
def ask_int(label: str, minimum=None, maximum=None, default=None) -> int:
    while True:
        kwargs = {} if default is None else {"default": str(default)}
        raw = Prompt.ask(f"[bold]{escape(label)}[/bold]", console=console, **kwargs).strip()
        _check_back(raw)
        try:
            value = int(raw)
        except ValueError:
            error("Please enter a whole number (or b to go back).")
            continue
        if value == 0 and minimum is not None and minimum >= 1:
            raise GoBack
        if minimum is not None and value < minimum:
            error(f"Value must be at least {minimum}.")
            continue
        if maximum is not None and value > maximum:
            error(f"Value must be at most {maximum}.")
            continue
        return value


# تسأل المستخدم يختار من قائمة خيارات محددة (ويقدر يكتب b للرجوع).
def ask_choice(label: str, choices, default=None, allow_back: bool = True) -> str:
    options = [*choices, "b"] if allow_back else list(choices)
    kwargs = {} if default is None else {"default": default}
    value = Prompt.ask(f"[bold]{escape(label)}[/bold]", console=console,
                       choices=options, **kwargs)
    if allow_back:
        _check_back(value)
    return value


# تسأل سؤال نعم/لا وترجع True أو False.
def confirm(label: str, default: bool = False) -> bool:
    return Confirm.ask(f"[bold]{escape(label)}[/bold]", console=console, default=default)


# توقف الشاشة لين يضغط المستخدم Enter.
def pause() -> None:
    console.input("\n[dim]Press Enter to continue...[/dim]")
