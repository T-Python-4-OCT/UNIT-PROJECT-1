import time

import questionary
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from game.localization import Localization
from game.validation import validate_explorer_name
from game.scoring import Scoring
from ui.audio import play_intro, play_forest, play_sound, stop_all_audio
from ui.effects import (
    console,
    show_forest_entry,
    show_magic_loading,
    show_secret_discovery,
    show_final_fate,
)


GREEN = "#2F5249"
GOLD = "#C5A46D"
SOFT_GREEN = "#A3B18A"
RED = "#C76D6D"

WORD_DELAY = 0.20
SCENE_DELAY = 0.80

loc = Localization("ar")

menu_style = questionary.Style([
    ("question", "fg:#C5A46D bold"),
    ("pointer", "fg:#C5A46D bold"),
    ("highlighted", "fg:#A3B18A bold"),
    ("selected", "fg:#2F5249"),
])


def ar(text):
    return loc.format_arabic(str(text))


def slow_text(text, color=SOFT_GREEN):
    words = str(text).split()

    if not words:
        return

    console.print()

    with Live(
        Text("", style=color),
        console=console,
        refresh_per_second=20,
        transient=False,
    ) as live:
        for index in range(1, len(words) + 1):
            current_text = " ".join(words[:index])

            live.update(
                Text(ar(current_text), style=color),
                refresh=True,
            )

            time.sleep(WORD_DELAY)

    console.print()
    time.sleep(SCENE_DELAY)


def pause(message="اضغط Enter للمتابعة..."):
    input(f"\n{ar(message)}")


def show_scene(title, description):
    console.print()

    console.print(
        Panel(
            Text(
                ar(title),
                style=GOLD,
                justify="center",
            ),
            title="🌲 ✦ ELDERGROVE ✦ 🌲",
            border_style=GREEN,
            expand=False,
        )
    )

    time.sleep(0.6)
    slow_text(description)


def choose(question, options):
    choices = [
        questionary.Choice(
            title=ar(label),
            value=value,
        )
        for label, value in options
    ]

    return questionary.select(
        ar(question),
        choices=choices,
        pointer="❯",
        style=menu_style,
        use_shortcuts=False,
    ).ask()


def get_explorer_name():
    while True:
        name = input(
            f"\n{ar('أدخل اسم المستكشف:')} "
        )

        valid, result = validate_explorer_name(name)

        if valid:
            return result

        console.print(
            Text(ar(result), style=RED)
        )


def show_points(points, category):
    if points <= 0:
        return

    console.print(
        Text(
            ar(f"✨ +{points} {category}"),
            style=GOLD,
        )
    )


def show_journal(evidence, solved_puzzles, discoveries):
    play_sound("journal")

    console.print(
        Panel(
            Text(
                "📜 EXPLORER JOURNAL",
                justify="center",
                style=GOLD,
            ),
            border_style=GREEN,
            expand=False,
        )
    )

    evidence_text = Text()

    if evidence:
        for index, item in enumerate(evidence, start=1):
            evidence_text.append(
                f"{index}. {ar(item)}\n",
                style=SOFT_GREEN,
            )
    else:
        evidence_text.append(
            ar("لم تكتشف أي أدلة بعد."),
            style=SOFT_GREEN,
        )

    console.print(
        Panel(
            evidence_text,
            title=ar("📜 الأدلة المكتشفة"),
            border_style=GREEN,
            padding=(1, 2),
            expand=False,
        )
    )

    puzzle_text = Text()

    if solved_puzzles:
        for puzzle in solved_puzzles:
            puzzle_text.append(
                f"🔮 {ar(puzzle)}\n",
                style=GOLD,
            )
    else:
        puzzle_text.append(
            ar("لم تحل أي ألغاز بعد."),
            style=SOFT_GREEN,
        )

    console.print(
        Panel(
            puzzle_text,
            title=ar("🔮 الألغاز المحلولة"),
            border_style=GOLD,
            padding=(1, 2),
            expand=False,
        )
    )

    discovery_text = Text()

    if discoveries:
        for discovery in discoveries:
            discovery_text.append(
                f"✨ {ar(discovery)}\n",
                style=GOLD,
            )
    else:
        discovery_text.append(
            ar("لم تفتح أي اكتشافات بعد."),
            style=SOFT_GREEN,
        )

    console.print(
        Panel(
            discovery_text,
            title=ar("✨ الاكتشافات"),
            border_style=GREEN,
            padding=(1, 2),
            expand=False,
        )
    )


def show_demo_score(
    score,
    start_time,
    puzzle_points,
    decision_points,
):
    play_sound("success")

    elapsed = int(time.monotonic() - start_time)
    minutes, seconds = divmod(elapsed, 60)

    content = Text(justify="center")

    content.append(
        f"⚖️ DECISIONS: {decision_points}/40\n",
        style=SOFT_GREEN,
    )

    content.append(
        f"🔮 PUZZLE: {puzzle_points}/100\n",
        style=GOLD,
    )

    content.append(
        "✨ SECRET: 50/50\n\n",
        style=SOFT_GREEN,
    )

    content.append(
        f"⭐ SCORE: {score}/190\n",
        style=GOLD,
    )

    content.append(
        f"⏳ TIME: {minutes:02d}:{seconds:02d}",
        style=SOFT_GREEN,
    )

    console.print(
        Panel(
            content,
            title="🏆 DEMO PROGRESS",
            border_style=GOLD,
            padding=(1, 2),
            expand=False,
        )
    )


def solve_demo_puzzle():
    play_sound("mystery")
    show_magic_loading("ar")

    show_scene(
        "اللغز الأول",
        "تتوهج الكلمات المنقوشة على اللوح الحجري أمامك.",
    )

    slow_text(
        "لدي مفاتيح كثيرة، لكنني لا أفتح أي قفل. فمن أنا؟",
        GOLD,
    )

    wrong_attempts = 0
    hint_used = False

    while True:
        options = [
            ("الباب", 1),
            ("لوحة المفاتيح", 2),
            ("الصندوق", 3),
            ("المفتاح الذهبي", 4),
        ]

        if not hint_used:
            options.append(
                ("💡 عرض تلميح (-10 نقاط)", "hint")
            )

        answer = choose(
            "اختر الإجابة الصحيحة:",
            options,
        )

        if answer is None:
            return None

        if answer == "hint":
            hint_used = True

            slow_text(
                "تلميح: أستخدم للكتابة.",
                GOLD,
            )

            continue

        if answer == 2:
            play_sound("success")

            points = Scoring.calculate_puzzle_reward(
                wrong_attempts=wrong_attempts,
                hint_used=hint_used,
            )

            slow_text(
                "إجابة صحيحة! تتوهج الرموز السحرية، "
                "وينفتح الممر أمامك.",
                GOLD,
            )

            console.print(
                Text(
                    f"🔮 PUZZLE SCORE: {points}/100",
                    style=GOLD,
                )
            )

            return points

        wrong_attempts += 1

        slow_text(
            "إجابة خاطئة! حاول مجددًا. "
            "خسرت 20 نقطة من مكافأة اللغز.",
            RED,
        )


def show_demo_ending(name, memory, score, decision):
    show_final_fate("ar")

    show_scene(
        "ذاكرة الغابة",
        f"تتذكر الغابة أنك {memory}. "
        "وتبدأ الأشجار بالهمس من جديد...",
    )

    if score >= 140 and decision != "push":
        ending_title = "النهاية: طريق النجاة"
        ending_description = (
            "تنفتح البوابة الأخيرة أمامك، "
            "وتسمح لك الغابة بالخروج. "
            "لكنها لن تنسى أثر رحلتك."
        )
        ending_message = "THE WAY BEYOND"

    else:
        ending_title = "النهاية: أسرار لا تُنسى"
        ending_description = (
            "تقف أمام البوابة الأخيرة، لكن الغابة "
            "لا تسمح لك بالعبور بعد. "
            "لقد اكتشفت أسرارها، إلا أن اختياراتك "
            "تركت أسئلة لم تجد إجابتها."
        )
        ending_message = "THE FOREST REMEMBERS"

    show_scene(
        ending_title,
        ending_description,
    )

    content = Text(justify="center")

    content.append(
        f"EXPLORER: {ar(name)}\n",
        style=GOLD,
    )

    content.append(
        f"DEMO SCORE: {score}/190\n\n",
        style=SOFT_GREEN,
    )

    content.append(
        ending_message,
        style=GOLD,
    )

    console.print(
        Panel(
            content,
            title="🌲 ✦ THE END ✦ 🌲",
            border_style=GREEN,
            padding=(1, 2),
            expand=False,
        )
    )


def run_demo():
    start_time = time.monotonic()

    evidence = []
    solved_puzzles = []
    discoveries = []

    score = 0
    decision_points = 0
    puzzle_points = 0

    try:
        play_intro()

        console.print(
            Panel(
                Text(
                    "🌲 ELDERGROVE 🌲\n"
                    "THE FORGOTTEN FOREST\n\n"
                    "✦ PRESENTATION DEMO ✦",
                    justify="center",
                    style=GOLD,
                ),
                border_style=GREEN,
                padding=(1, 3),
                expand=False,
            )
        )

        name = get_explorer_name()

        slow_text(
            f"مرحبًا بك يا {name} في غابة إلدرغروف."
        )

        pause("اضغط Enter لدخول الغابة...")

        play_forest()
        show_forest_entry("ar")

        show_scene(
            "البوابة الحجرية القديمة",
            "تقف أمام بوابة حجرية عتيقة، "
            "تغطي سطحها نقوش غامضة لم ترَ مثلها من قبل.",
        )

        play_sound("gate")

        slow_text(
            "وبجانب البوابة، تلاحظ لوحًا حجريًا "
            "تنبعث منه إضاءة غامضة."
        )

        slow_text(
            "لن تتمكن من عبور البوابة "
            "حتى تحل اللغز المنقوش عليه."
        )

        pause("اضغط Enter لبدء اللغز...")

        result = solve_demo_puzzle()

        if result is None:
            return

        puzzle_points = result
        score += puzzle_points

        solved_puzzles.append(
            "اللغز الأول: لوحة المفاتيح"
        )

        evidence.append(
            "حل الألغاز يكشف الطرق المخفية."
        )

        pause()

        slow_text(
            "وفجأة، تسمع همسات خافتة من خلف البوابة..."
        )

        slow_text(
            "الغابة تتذكر كل من يعبر بوابتها.",
            GOLD,
        )

        decision = choose(
            "كيف ستتصرف أمام البوابة؟",
            [
                ("أنصت إلى الهمسات الغامضة", "listen"),
                ("أتفحص النقوش الحجرية", "symbols"),
                ("أدفع البوابة وأواصل طريقي", "push"),
            ],
        )

        if decision is None:
            return

        if decision == "listen":
            memory = "أنصت إلى همسات الغابة"
            decision_points = 40

            slow_text(
                "تكشف لك الهمسات أن الغابة تختبر كل من يدخلها."
            )

            evidence.append(
                "الغابة تتذكر اختيارات المستكشف."
            )

        elif decision == "symbols":
            memory = "بحث عن الرموز القديمة"
            decision_points = 35

            slow_text(
                "تكتشف رمزًا قديمًا يشير إلى ممر مخفي."
            )

            evidence.append(
                "الرموز القديمة تقود إلى أسرار الغابة."
            )

        else:
            memory = "دفع البوابة دون تردد"
            decision_points = 10

            slow_text(
                "تنفتح البوابة بصوت مريب، "
                "وتشعر أن هناك من يراقبك."
            )

            evidence.append(
                "هناك قوة غامضة تراقب المستكشفين."
            )

        score += decision_points

        show_points(
            decision_points,
            "نقطة للقرارات",
        )

        pause()

        show_scene(
            "السر المخفي",
            "بعد عبور البوابة، تبدأ جذور شجرة قديمة "
            "بالتحرك ببطء، لتكشف مكانًا مخفيًا.",
        )

        score += 50

        show_secret_discovery(
            language="ar",
            points=50,
        )

        discoveries.append(
            "السر المخفي بين جذور الشجرة القديمة"
        )

        pause()

        slow_text(
            "خلال رحلتك، جمعت أدلة "
            "تساعدك على فهم أسرار الغابة."
        )

        action = choose(
            "ماذا تريد أن تفعل؟",
            [
                ("فتح دفتر المستكشف", "journal"),
            ],
        )

        if action is None:
            return

        show_journal(
            evidence,
            solved_puzzles,
            discoveries,
        )

        pause("اضغط Enter لعرض نقاطك...")

        show_demo_score(
            score,
            start_time,
            puzzle_points,
            decision_points,
        )

        pause()

        show_scene(
            "الممر الأخير",
            "تصل إلى قوس حجري قديم، "
            "وهناك تتوقف الرياح فجأة...",
        )

        slow_text(
            "الغابة الآن تتذكر رحلتك كاملة.",
            GOLD,
        )

        pause("اضغط Enter لاكتشاف مصيرك...")

        show_demo_ending(
            name,
            memory,
            score,
            decision,
        )

    finally:
        stop_all_audio()
        play_intro()


if __name__ == "__main__":
    run_demo()

    input("\nPress Enter to exit...")
    stop_all_audio()