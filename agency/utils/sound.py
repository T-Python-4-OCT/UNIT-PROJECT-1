"""Optional sounds: a spoken welcome at login, and an airport cabin chime on the receipt.

No extra library is needed: Windows speech and sound playback come from the system, and the
chime file lives in agency/sounds. Set the environment variable SKYROUTE_SOUND=off to switch
everything off. Where nothing can play, the program stays silent.
"""
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

WELCOME_TEXT = "Welcome to SkyRoute"
SOUNDS_DIR = Path(__file__).resolve().parent.parent / "sounds"
CHIME_SOUND = "chime.wav"
WINDOWS_PLATFORMS = ("win32", "cygwin", "msys")


# ترجع True إذا الصوت شغال (يوقف بالمتغير SKYROUTE_SOUND=off).
def enabled() -> bool:
    """Sounds are on unless SKYROUTE_SOUND is off/0/no/false."""
    return os.environ.get("SKYROUTE_SOUND", "on").strip().lower() not in ("off", "0", "no", "false")


# تشغّل ملف صوت .wav وتنتظر لين يخلص (وجرس الترمنل إذا ما فيه مشغّل).
def _play_file(path: Path) -> None:
    """Play one .wav file and wait until it ends (terminal bell if no player exists)."""
    try:
        import winsound
    except ImportError:
        winsound = None
    if winsound is not None:
        try:
            winsound.PlaySound(str(path), winsound.SND_FILENAME)
        except RuntimeError:        # no sound device
            pass
        return
    for player in ("afplay", "paplay", "aplay"):        # macOS, then Linux players
        if shutil.which(player):
            subprocess.run([player, str(path)], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, check=False)
            return
    print("\a", end="", flush=True)


# تشغّل ملفات الصوت واحد ورا الثاني، وتتجاهل الملف المفقود.
def _play_files(names) -> None:
    """Play the sound files one after another (a missing file is skipped)."""
    for name in names:
        path = SOUNDS_DIR / name
        if path.exists():
            _play_file(path)


# تشغّل الصوت في خيط جانبي عشان القائمة ما تنتظره.
def _in_background(task) -> None:
    """Run a sound without making the menu wait for it."""
    threading.Thread(target=task, daemon=True).start()


# تنطق النص بصوت النظام، وترجع False إذا ما فيه صوت متوفر.
def _speak(text: str) -> bool:
    """Say the text with the system voice. Returns False when no voice is available."""
    if sys.platform in WINDOWS_PLATFORMS:
        command = ("Add-Type -AssemblyName System.Speech; "
                   f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}')")
        arguments = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command]
    elif shutil.which("say"):                       # macOS
        arguments = ["say", text]
    elif shutil.which("espeak"):                    # Linux
        arguments = ["espeak", text]
    else:
        return False
    try:
        subprocess.Popen(arguments, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except OSError:
        return False
    return True


# جرس مقصورة الطائرة (يطلع مع الفاتورة).
def receipt_sound() -> None:
    """The airport cabin chime (used when the receipt is shown)."""
    if enabled():
        _in_background(lambda: _play_files((CHIME_SOUND,)))


# تنطق Welcome to SkyRoute بعد الدخول (أو جرس إذا ما فيه صوت).
def welcome() -> None:
    """Say 'Welcome to SkyRoute' after a login (the cabin chime if no voice is available)."""
    if enabled() and not _speak(WELCOME_TEXT):
        _in_background(lambda: _play_files((CHIME_SOUND,)))
