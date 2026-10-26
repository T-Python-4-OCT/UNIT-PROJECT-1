from pathlib import Path
import re
import shutil

path = Path("commands/command_handler.py")
source = path.read_text(encoding="utf-8")

old_intent = '''        intent = SimpleNamespace(
            action=action,
            surah=result.get("surah"),
            ayah=result.get("ayah"),
            query=result.get("query", ""),
        )'''

new_intent = '''        intent = SimpleNamespace(
            action=action,
            surah=result.get("surah"),
            ayah=result.get("ayah"),
            query=result.get("query", ""),
            play_audio=result.get("play_audio", False),
            repeats=result.get("repeats", 1),
        )'''

if source.count(old_intent) != 1:
    raise SystemExit(
        "توقف التعديل: لم أجد كتلة intent المتوقعة مرة واحدة. "
        "لم يتم حفظ أي تغيير."
    )

source = source.replace(old_intent, new_intent, 1)

pattern = (
    r'(?m)^(?P<indent>[ \t]*)'
    r'# تشغيل التلاوة إذا طلب المستخدم سماع الآية\..*?'
    r'(?=^[ \t]*elif intent\.action == "tafsir":)'
)

replacement = '''        play_audio = getattr(intent, "play_audio", None)

        # الحفاظ على سلوك الأوامر المباشرة القديمة.
        if play_audio is None:
            play_audio = command_requests_audio(command)

        if play_audio:
            player.play_ayah(
                current_surah,
                current_ayah,
                repeats=getattr(intent, "repeats", 1),
            )

'''

updated, count = re.subn(
    pattern,
    replacement,
    source,
    count=1,
    flags=re.DOTALL,
)

if count != 1:
    raise SystemExit(
        "تم إلغاء التعديل: لم أجد كتلة تشغيل الصوت المتوقعة. "
        "لم يتم حفظ أي تغيير."
    )

backup = path.with_name("command_handler.py.before_ai_audio_fields.bak")

if not backup.exists():
    shutil.copy2(path, backup)

path.write_text(updated, encoding="utf-8")

print("تم تحديث command_handler.py.")
print(f"النسخة الاحتياطية: {backup}")
