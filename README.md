# 🌲 Eldergrove: The Forgotten Forest

**The forest remembers. Will you escape?**

*A fantasy-inspired, story-driven command-line adventure built with Python.*

## Overview

**Eldergrove: The Forgotten Forest** is an interactive command-line adventure game developed using Python.

Players become explorers entering a mysterious ancient forest filled with forgotten stories, magical encounters, hidden locations, and challenging puzzles.

Throughout the adventure, players explore different regions, make decisions, collect evidence, discover secrets, and solve puzzles to uncover the truth behind the forest.

The forest remembers the explorer's actions. Their decisions, achievements, and discoveries contribute to determining their final fate.

This project was developed as part of the **Unit 1 Python Programming Assessment at Tuwaiq Academy**.

---

## ✨ Features

- **Bilingual Gameplay:** Arabic and English language support, with Arabic as the default language.
- **Interactive Exploration:** Three main forest regions containing 12 explorable locations.
- **Story-Driven Adventure:** Nine main story events featuring interactive choices and mysterious encounters.
- **Randomized Puzzles:** Four puzzle stations with a question bank of 20 puzzles, including hints and retry options.
- **Explorer Journal:** Records collected evidence, solved puzzles, and discoveries.
- **Forest Memory System:** Connects evidence and remembers important player choices.
- **Scoring System:** Earn up to 1,000 points through puzzles, evidence, decisions, and hidden secrets.
- **Multiple Endings:** Six possible endings based on player performance and progression.
- **Save and Resume:** Save an adventure and continue playing later.
- **Explorer Records:** Records explorer names, scores, completion times, dates, and endings.
- **Input Validation:** Validates explorer names using Arabic or English letters.
- **Fantasy Terminal Interface:** Rich visual panels, animated narration, colors, and interactive selection menus.
- **Sound Effects:** Atmospheric forest sounds, background music, and event-specific audio effects.
- **Presentation Demo:** A standalone, shortened adventure designed to demonstrate the main gameplay features.
- **Modular Architecture:** Organized Python modules and JSON-based game content.

---

## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python 3.13 | Core programming language |
| JSON | Story content, puzzles, localization, saved progress, and explorer records |
| Rich | Terminal styling, animated text, panels, and visual effects |
| Questionary | Interactive keyboard-driven menus |
| pygame | Background music and sound effects |
| arabic-reshaper | Arabic text shaping in terminal output |
| python-bidi | Bidirectional Arabic text handling |
| Git & GitHub | Version control and project management |

All required third-party Python packages are listed in `requirements.txt`.

---

## 🌳 Game Structure

| Component | Total |
|---|---:|
| Main Regions | 3 |
| Explorable Locations | 12 |
| Main Story Events | 9 |
| Puzzle Stations | 4 |
| Puzzle Questions | 20 |
| Possible Endings | 6 |
| Supported Languages | 2 |
| Maximum Score | 1,000 |

---

## 🎮 How to Play

1. Launch the game and select your preferred language.
2. Start a new adventure and enter your explorer name.
3. Explore available locations and discover hidden areas.
4. Make decisions during story events.
5. Solve puzzles using logic, hints, and retries.
6. Collect evidence and review discoveries in your Explorer Journal.
7. Earn points by completing challenges and uncovering secrets.
8. Save your progress whenever needed.
9. Complete the adventure and discover your final fate.

### In-Game Commands

| Command | Action |
|---|---|
| `N` | Move to the next region |
| `J` | Open the Explorer Journal |
| `S` | View your score |
| `T` | View your playtime |
| `V` | Save your adventure |
| `Q` | Return to the main menu |
| `1–4` | Select available locations |

Interactive menus also support keyboard arrow navigation.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13
- pip
- Git (optional, for cloning the repository)
- A terminal that supports Unicode and ANSI colors

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Abdulmajeed-mo/UNIT-PROJECT-1.git
```

**2. Navigate to the project directory**

```bash
cd UNIT-PROJECT-1
```

**3. Create a virtual environment**

```bash
python -m venv .venv
```

**4. Activate the virtual environment**

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

**5. Install the required dependencies**

```bash
python -m pip install -r requirements.txt
```

### Run the Full Game

From the project root, execute:

```bash
python main.py
```

Follow the instructions displayed in the terminal to begin your adventure.

### Run the Presentation Demo

To launch the shortened presentation experience:

```bash
python -m demo.demo
```

The demo showcases the explorer introduction, puzzle mechanics, interactive decisions, secret discovery, Explorer Journal, scoring system, and a branching ending.

The presentation demo operates independently from the main adventure.

---

## 📁 Project Structure

```text
UNIT-PROJECT-1/
├── assets/
│   └── sounds/
├── demo/
│   └── demo.py
├── game/
│   ├── data/
│   │   ├── story.json
│   │   ├── story_ar.json
│   │   ├── puzzles.json
│   │   ├── puzzles_ar.json
│   │   ├── locations.json
│   │   ├── locations_ar.json
│   │   ├── endings.json
│   │   ├── endings_ar.json
│   │   ├── journal.json
│   │   ├── journal_ar.json
│   │   └── translations.json
│   ├── engine.py
│   ├── story.py
│   ├── puzzles.py
│   ├── exploration.py
│   ├── journal.py
│   ├── scoring.py
│   ├── explorers.py
│   ├── endings.py
│   ├── save_system.py
│   ├── localization.py
│   └── validation.py
├── ui/
│   ├── interface.py
│   ├── effects.py
│   └── audio.py
├── records/
├── saves/
├── tests/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Main Components

| Component | Responsibility |
|---|---|
| `engine.py` | Coordinates the main gameplay flow |
| `story.py` | Manages story events and narrative content |
| `exploration.py` | Handles forest regions and locations |
| `puzzles.py` | Manages randomized puzzle challenges |
| `journal.py` | Tracks evidence, puzzles, and discoveries |
| `scoring.py` | Calculates player rewards and scores |
| `endings.py` | Determines the player's final fate |
| `save_system.py` | Handles saving and loading game progress |
| `explorers.py` | Manages explorer records and achievements |
| `localization.py` | Supports Arabic and English localization |
| `validation.py` | Validates explorer names |
| `effects.py` | Provides terminal animations and visual effects |
| `audio.py` | Handles background music and sound effects |
| `demo.py` | Runs the standalone presentation demonstration |

---

## ⭐ Scoring System

Players can earn points across four categories:

| Category | Maximum Points |
|---|---:|
| Puzzles | 400 |
| Evidence | 250 |
| Decisions | 200 |
| Secrets | 150 |
| **Total** | **1,000** |

### Puzzle Scoring

- Correct answers earn puzzle points.
- Incorrect attempts reduce the available reward.
- Using hints reduces the available reward.
- Successfully solving a puzzle contributes to the explorer's final score.

### Final Fate

The game includes six possible endings, divided into positive and negative outcomes.

The final outcome is determined by the explorer's overall performance, completed puzzles, collected evidence, discoveries, and progression.

Different playthroughs can lead to different outcomes.

---

## 📜 Explorer Journal

The Explorer Journal provides a record of the player's progress throughout the adventure.

It tracks:

- Collected evidence
- Solved puzzles
- Discovered connections
- Important forest discoveries

Certain discoveries are unlocked when the player collects related pieces of evidence.

The Journal acts as both a progression tracker and an important part of the game's exploration system.

---

## 💾 Save System and Explorer Records

The game supports saving and resuming adventures through JSON-based persistence.

Saved progress can include the explorer's identity, current progression, collected evidence, score, and playtime.

The explorer records system maintains completed adventure results, including player names, scores, dates, durations, and endings.

This allows players to review their previous journeys and compare achievements.

---

## 🎵 Audio and Visual Experience

Eldergrove uses a fantasy-inspired terminal interface designed to create an immersive storytelling experience.

Visual and audio features include:

- Animated narrative text
- Rich panels and colored terminal elements
- Interactive keyboard navigation
- Forest atmosphere and background music
- Magical sound effects
- Gate, mystery, discovery, and success effects
- Dramatic transitions and ending sequences

The interface uses forest-inspired green, brown, and gold tones.

---

## 📖 User Stories

- As a player, I want to explore a mysterious forest and uncover hidden secrets.
- As a player, I want to make decisions that influence my adventure.
- As a player, I want to solve randomized puzzles and receive hints when needed.
- As a player, I want to collect evidence and review discoveries.
- As a player, I want to experience the game in Arabic or English.
- As a player, I want to save my progress and continue later.
- As a player, I want my achievements and completion time recorded.
- As a player, I want different possible endings based on my progress.

---

## ✅ Project Status

**Core Development Completed — Unit 1 Project**

The primary features have been implemented, including:

- Main adventure and exploration
- Story events and interactive decisions
- Randomized puzzles and hints
- Explorer Journal and forest discoveries
- Scoring and multiple endings
- Save and load functionality
- Explorer records
- Arabic and English localization
- Name input validation
- Terminal animations and interactive menus
- Background music and sound effects
- Standalone presentation demo

Core gameplay, scoring, save/load functionality, Journal discoveries, and ending selection have been tested during development.

Further refinements and testing may be introduced as needed.

---

## 🎯 Educational Objectives

This project demonstrates practical application of fundamental Python concepts, including:

- Variables and data types
- Conditional statements
- Loops and functions
- Lists, dictionaries, and sets
- Modules and packages
- JSON file handling
- Exception handling
- Object-oriented programming
- Virtual environments and external libraries
- Input validation
- Modular code organization
- Git and GitHub version control

---

## 📄 License

This project was created for educational purposes as part of the **Tuwaiq Academy Python Programming Assessment**.