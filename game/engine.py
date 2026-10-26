import questionary
from rich.panel import Panel
from rich.text import Text

from game.validation import validate_explorer_name
from game.story import load_story, localize_story
from game.puzzles import select_random_puzzles, solve_puzzle
from game.journal import Journal
from game.exploration import Exploration
from game.explorers import Explorer, save_explorer_record
from game.scoring import Scoring
from game.save_system import save_game
from game.endings import determine_fate, display_ending
from game.localization import Localization
from ui.effects import (
    console, show_forest_entry, show_magic_loading,
    show_secret_discovery, show_final_fate, type_narration,
)
from ui.audio import play_intro, play_forest, play_sound, stop_all_audio

FOREST_GREEN = "#2F5249"
ANTIQUE_GOLD = "#C5A46D"
SOFT_GREEN = "#A3B18A"

MENU_STYLE = questionary.Style([
    ("question", "fg:#C5A46D bold"),
    ("pointer", "fg:#C5A46D bold"),
    ("highlighted", "fg:#A3B18A bold"),
    ("selected", "fg:#2F5249"),
    ("disabled", "fg:#858585"),
])


def game_text(loc, english, arabic):
    return loc.format_arabic(arabic if loc.language == "ar" else english)


def narration(text, loc):
    console.print()
    type_narration(text, delay=0.20, style=SOFT_GREEN, formatter=loc.format_arabic)


def choose_exploration_action(exploration, loc):
    choices = []

    for index, location in enumerate(exploration.get_locations(), start=1):
        name = exploration.translate_location(location["name"], loc)
        completed = location["id"] in exploration.completed_locations
        unlocked = exploration.is_unlocked(location)

        if completed:
            icon, status = "✅", loc.display_text("completed")
        elif unlocked:
            icon, status = "🌿", loc.display_text("available")
        else:
            icon, status = "🔒", loc.display_text("locked")

        choices.append(questionary.Choice(
            title=f"{icon} {name} [{status}]",
            value=str(index),
            disabled=status if not unlocked else None,
        ))

    for icon, label, value in [
        ("🌳", "next_region", "n"),
        ("📜", "journal", "j"),
        ("🏆", "view_score", "s"),
        ("⏳", "view_playtime", "t"),
        ("💾", "save_option", "v"),
        ("🚪", "return_menu", "q"),
    ]:
        choices.append(questionary.Choice(
            title=f"{icon} {loc.display_text(label)}", value=value,
        ))

    return questionary.select(
        loc.display_text("select_location"),
        choices=choices, pointer="❯", style=MENU_STYLE,
        use_shortcuts=False,
    ).ask()


def show_forest_memory(event_id, previous_choices, journal, loc):
    messages = []

    if event_id == 4:
        if previous_choices.get(1) == 3:
            messages = [
                ("The mist whispers with a familiar voice.", "يهمس الضباب بصوت مألوف."),
                ("The forest remembers that you listened at the gate.", "تتذكر الغابة أنك أنصت إلى الهمسات عند البوابة."),
            ]
        elif previous_choices.get(1) == 2:
            messages = [
                ("A faded moon symbol appears through the mist.", "يظهر رمز قمر باهت وسط الضباب."),
                ("The forest remembers your discovery at the gate.", "تتذكر الغابة ما اكتشفته عند البوابة."),
            ]

    elif event_id == 6:
        if previous_choices.get(2) == 1:
            messages = [
                ("The stranger knows you spoke honestly to the Watcher.", "يعرف الغريب أنك تحدثت بصدق إلى الحارس.")
            ]
        elif previous_choices.get(2) == 2:
            messages = [
                ("The stranger watches you with suspicion.", "يراقبك الغريب بريبة."),
                ("Your earlier deception has not been forgotten.", "لم يُنسَ خداعك السابق."),
            ]

    elif event_id == 9:
        if "hidden_trials" in journal.discoveries:
            messages.append(
                ("The archway recognizes your understanding of the trials.", "يدرك القوس الحجري أنك فهمت حقيقة الاختبارات.")
            )
        if "forest_memory" in journal.discoveries:
            messages.append(
                ("The forest echoes the memories you uncovered.", "تردد الغابة أصداء الذكريات التي اكتشفتها.")
            )

    for english, arabic in messages:
        console.print(Text(
            f"🌫️ {game_text(loc, english, arabic)}",
            style=SOFT_GREEN,
        ))


def decision_reward(event, selected_choice, choice_index):
    configured = selected_choice.get("decision_points")

    if configured is not None:
        return max(0, min(40, int(configured)))

    if event["id"] == 2 and choice_index == 2:
        return 10

    if event["id"] == 1 and choice_index == 1:
        return 15

    return 40 if selected_choice.get("evidence") else 15


def play_event(event, journal, selected_puzzles, scoring, loc):
    title = event.get("title_ar", event["title"]) if loc.language == "ar" else event["title"]
    description = event.get("description_ar", event["description"]) if loc.language == "ar" else event["description"]

    console.print(Panel(
        Text(loc.format_arabic(title), style=ANTIQUE_GOLD),
        title="🌲 ✦ ELDERGROVE ✦ 🌲",
        border_style=FOREST_GREEN,
        expand=False,
    ))

    narration(description, loc)

    choices = event["choices"]
    puzzle_id = next(
        (str(c["puzzle_id"]) for c in choices if "puzzle_id" in c),
        None,
    )

    if puzzle_id is not None:
        play_sound("mystery")
        show_magic_loading(loc.language)

        if not solve_puzzle(puzzle_id, selected_puzzles, journal, loc):
            return None

        correct_choice = next(
            (c for c in choices if c.get("correct")),
            None,
        )

        if correct_choice is None:
            console.print(game_text(
                loc,
                "Error: Correct story choice not found.",
                "خطأ: لم يتم العثور على الاختيار الصحيح.",
            ))
            return None

        play_sound("success")

        if journal.record_solved_puzzle(puzzle_id):
            puzzle = selected_puzzles.get(puzzle_id, {})
            earned = puzzle.get("earned_points", 0)

            if not isinstance(earned, int) or earned <= 0:
                earned = Scoring.calculate_puzzle_reward(
                    puzzle.get("wrong_attempts", 0),
                    puzzle.get("hint_used", False),
                )

            if scoring.add_points("puzzles", puzzle_id, earned):
                console.print(Text(game_text(
                    loc,
                    f"🔮 +{earned} Puzzle Points!",
                    f"🔮 +{earned} نقطة للألغاز!",
                ), style=ANTIQUE_GOLD))

        selected_choice = correct_choice

    else:
        while True:
            action_choices = []

            for index, choice in enumerate(choices):
                choice_text = (
                    choice.get("text_ar", choice["text"])
                    if loc.language == "ar"
                    else choice["text"]
                )

                action_choices.append(questionary.Choice(
                    title="✨ " + loc.format_arabic(choice_text),
                    value=index,
                ))

            action_choices.append(questionary.Choice(
                title="📜 " + game_text(
                    loc, "Review Journal", "عرض دفتر الرحلة"
                ),
                value="journal",
            ))

            answer = questionary.select(
                game_text(loc, "Choose your action:", "اختر تصرفك:"),
                choices=action_choices,
                pointer="❯",
                style=MENU_STYLE,
                use_shortcuts=False,
            ).ask()

            if answer is None:
                return None

            if answer == "journal":
                play_sound("journal")
                journal.display()
                continue

            selected_choice = choices[answer]
            break

        points = decision_reward(event, selected_choice, answer + 1)

        if scoring.add_points(
            "decisions",
            f"event_{event['id']}",
            points,
        ):
            console.print(Text(game_text(
                loc,
                f"✨ +{points} Decision Points!",
                f"✨ +{points} نقطة للقرارات!",
            ), style=ANTIQUE_GOLD))

    evidence = selected_choice.get("evidence")

    if evidence and journal.add_evidence(evidence):
        if scoring.add_points("evidence", evidence, 25):
            console.print(Text(game_text(
                loc,
                "📜 +25 Evidence Points!",
                "📜 +25 نقطة للأدلة!",
            ), style=SOFT_GREEN))

    result_text = (
        selected_choice.get("result_ar", selected_choice["result"])
        if loc.language == "ar"
        else selected_choice["result"]
    )

    narration(result_text, loc)
    return selected_choice


def build_game_state(
    explorer,
    exploration,
    journal,
    scoring,
    selected_puzzles,
    previous_choices,
    language,
):
    return {
        "language": language,
        "explorer": {
            "name": explorer.name,
            "started_at": explorer.started_at,
            "playtime_seconds": explorer.get_playtime(),
        },
        "exploration": {
            "current_region": exploration.current_region,
            "visited_locations": list(exploration.visited_locations),
            "completed_locations": list(exploration.completed_locations),
        },
        "journal": {
            "evidence": journal.evidence.copy(),
            "solved_puzzles": journal.solved_puzzles.copy(),
            "discoveries": journal.discoveries.copy(),
        },
        "scoring": {
            "scores": scoring.scores.copy(),
            "rewarded_actions": list(scoring.rewarded_actions),
        },
        "selected_puzzles": selected_puzzles,
        "previous_choices": previous_choices.copy(),
    }


def run_game(saved_state=None, language="ar"):
    loc = Localization(language)

    if saved_state is not None:
        loc.set_language(saved_state.get("language", language))

    events = localize_story(load_story(), loc.language)
    events_by_id = {
        event["id"]: event
        for event in events
    }

    journal = Journal(loc)
    exploration = Exploration()
    scoring = Scoring(loc)

    if saved_state is None:
        selected_puzzles = select_random_puzzles()
        previous_choices = {}

        console.print(Panel(
            Text(loc.display_text("game_title"), style=ANTIQUE_GOLD),
            title="🌲 ✦ ELDERGROVE ✦ 🌲",
            border_style=FOREST_GREEN,
            expand=False,
        ))

        console.print(Text(
            loc.display_text("tagline"),
            style=SOFT_GREEN,
        ))

        while True:
            name = input(
                f"\n{loc.display_text('explorer_name')} "
            )

            valid, result = validate_explorer_name(name)

            if valid:
                name = result
                break

            error = (
                result
                if loc.language == "ar"
                else "Use Arabic or English letters only (2–30 letters), without numbers, symbols, or mixed alphabets."
            )

            console.print(loc.format_arabic(error))

        explorer = Explorer(name)

        console.print(Text(
            loc.display_text("welcome", name=explorer.name),
            style=SOFT_GREEN,
        ))

    else:
        explorer_data = saved_state["explorer"]
        exploration_data = saved_state["exploration"]
        journal_data = saved_state["journal"]
        scoring_data = saved_state["scoring"]

        explorer = Explorer(explorer_data["name"])
        explorer.started_at = explorer_data["started_at"]
        explorer.playtime_seconds = float(
            explorer_data["playtime_seconds"]
        )

        exploration.current_region = exploration_data["current_region"]
        exploration.visited_locations = set(
            exploration_data["visited_locations"]
        )
        exploration.completed_locations = set(
            exploration_data["completed_locations"]
        )

        journal.evidence = list(journal_data["evidence"])
        journal.solved_puzzles = [
            str(item)
            for item in journal_data["solved_puzzles"]
        ]
        journal.discoveries = list(
            journal_data.get("discoveries", [])
        )
        journal.check_connections()

        scoring.scores = dict(scoring_data["scores"])
        scoring.rewarded_actions = set(
            scoring_data["rewarded_actions"]
        )

        selected_puzzles = saved_state["selected_puzzles"]
        previous_choices = {
            int(k): v
            for k, v in saved_state["previous_choices"].items()
        }

        console.print(Text(
            f"{game_text(loc, 'Welcome back', 'مرحبًا بعودتك')}: "
            f"{loc.format_arabic(explorer.name)}!",
            style=SOFT_GREEN,
        ))

        console.print(
            f"{game_text(loc, 'Journey started', 'بدأت الرحلة')}: "
            f"{explorer.started_at}"
        )

    input(game_text(
        loc,
        "\nPress Enter to enter the forest...",
        "\nاضغط Enter لدخول الغابة...",
    ))

    show_forest_entry(loc.language)

    finished = False
    explorer.start_session()

    try:
        play_forest()

        while not finished:
            exploration.show_locations(loc)

            answer = choose_exploration_action(
                exploration, loc
            )

            if answer is None:
                break

            if answer == "j":
                play_sound("journal")
                journal.display()
                continue

            if answer == "s":
                play_sound("success")
                scoring.display_score()
                continue

            if answer == "t":
                play_sound("success")
                label = game_text(loc, "Playtime", "مدة اللعب")
                console.print(
                    f"\n{label}: {explorer.get_duration_text()}"
                )
                continue

            if answer == "v":
                save_game(build_game_state(
                    explorer,
                    exploration,
                    journal,
                    scoring,
                    selected_puzzles,
                    previous_choices,
                    loc.language,
                ))
                continue

            if answer == "q":
                console.print(game_text(
                    loc,
                    "Leaving the forest...",
                    "تغادر الغابة...",
                ))
                break

            if answer == "n":
                exploration.move_to_next_region(loc)
                continue

            if not answer.isdigit():
                console.print(game_text(
                    loc,
                    "Invalid option. Please try again.",
                    "خيار غير صحيح، حاول مجددًا.",
                ))
                continue

            location = exploration.visit_location(
                int(answer), loc
            )

            if location is None:
                continue

            location_id = location["id"]

            if location_id in exploration.completed_locations:
                console.print(game_text(
                    loc,
                    "You have already explored this location.",
                    "لقد استكشفت هذا الموقع مسبقًا.",
                ))

                input(game_text(
                    loc,
                    "\nPress Enter to return...",
                    "\nاضغط Enter للعودة...",
                ))
                continue

            event_id = location.get("event_id")

            if event_id == 1:
                play_sound("gate")

            if event_id is not None:
                event = events_by_id.get(event_id)

                if event is None:
                    console.print(game_text(
                        loc,
                        "Error: Story event not found.",
                        "خطأ: لم يتم العثور على حدث القصة.",
                    ))
                    continue

                show_forest_memory(
                    event_id,
                    previous_choices,
                    journal,
                    loc,
                )

                result = play_event(
                    event,
                    journal,
                    selected_puzzles,
                    scoring,
                    loc,
                )

                if result is None:
                    console.print(game_text(
                        loc,
                        "This event could not be completed.",
                        "تعذر إكمال هذا الحدث.",
                    ))
                    continue

                if event_id not in (3, 5, 7, 8):
                    previous_choices[event_id] = (
                        event["choices"].index(result) + 1
                    )

            else:
                narration(
                    (
                        "تستكشف المكان وتكشف أسراره."
                        if loc.language == "ar"
                        else "You explore the area and uncover its secrets."
                    ),
                    loc,
                )

            if location.get("optional", False):
                if scoring.add_points(
                    "secrets",
                    location_id,
                    50,
                ):
                    show_secret_discovery(
                        loc.language,
                        points=50,
                    )

            exploration.complete_location(location_id)

            console.print(Text(game_text(
                loc,
                "✨ Location completed!",
                "✨ اكتمل استكشاف الموقع!",
            ), style=SOFT_GREEN))

            if location_id == "last_passage":
                finished = True
                break

            input(game_text(
                loc,
                "\nPress Enter to continue...",
                "\nاضغط Enter للمتابعة...",
            ))

    finally:
        explorer.pause_session()
        stop_all_audio()
        play_intro()

    if finished:
        show_final_fate(loc.language)

        fate_id = determine_fate(
            scoring,
            journal,
            previous_choices,
            selected_puzzles,
        )

        save_explorer_record(
            explorer,
            scoring.get_total(),
            fate_id,
            loc,
        )

        display_ending(fate_id, loc)

        console.print(Panel(
            Text(
                game_text(
                    loc,
                    "JOURNEY SUMMARY",
                    "ملخص الرحلة",
                ),
                style=ANTIQUE_GOLD,
            ),
            border_style=FOREST_GREEN,
            expand=False,
        ))

        console.print(
            f"{game_text(loc, 'Explorer', 'المستكشف')}: "
            f"{loc.format_arabic(explorer.name)}"
        )

        console.print(
            f"{game_text(loc, 'Journey started', 'بدأت الرحلة')}: "
            f"{explorer.started_at}"
        )

        console.print(
            f"{game_text(loc, 'Playtime', 'مدة اللعب')}: "
            f"{explorer.get_duration_text()}"
        )

        scoring.display_score()
        journal.display()

        console.print(Text(
            game_text(
                loc,
                "🌲 The forest will remember your name.",
                "🌲 ستتذكر الغابة اسمك.",
            ),
            style=ANTIQUE_GOLD,
        ))