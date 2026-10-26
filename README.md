# Trip Budget Tracker (CLI)

A terminal app that tracks your travel spending and always tells you how much is left.

> **بالعربي:** تدخل ميزانيتك وتذكرتك، فيوزّع الباقي على الفندق والأكل والفعاليات والاحتياط.
> كل ما تفتحه يسألك وش صرفت، ويعرض لك جدول بالمتبقي وكم تقدر تصرف في اليوم،
> ويحوّل لك من عملة البلد إلى الريال.

Unit 1 project - *Developing Web Applications with Python Bootcamp*.

## Features

1. **Trip setup**: destination, dates, budget currency, destination currency and exchange rate, total budget.
2. **Ticket**: its price is taken from the budget first.
3. **Budget split**: Hotel / Food / Activities / Reserve (default 40 / 25 / 20 / 15).
4. **Expenses** in the local currency are converted to your budget currency.
5. **Summary table** with progress bars, what is left, how much you can spend per day,
   and a bar chart of your spending.
6. **Final report** saved to `reports/`.

## Libraries

| Library | Why |
|---|---|
| [rich](https://github.com/Textualize/rich) | Colored tables, panels and input prompts in the terminal |
| [pyfiglet](https://github.com/pwaller/pyfiglet) | Big ASCII-art title when the app starts |
| [plotext](https://github.com/piccolomo/plotext) | Bar chart of your spending per category inside the terminal |
| [humanize](https://github.com/python-humanize/humanize) | Friendly dates: "today", "yesterday", "your trip starts in 14 days" |
| [pytest](https://docs.pytest.org) | Automatic tests for the budget maths |

## Installation and run

```bash
cd trip-budget-cli
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Run the tests:

```bash
pytest
```

On macOS/Linux use `python3` if `python` is not found.

## Menu

| Option | What it does |
|---|---|
| 1 | Add an expense |
| 2 | Delete an expense (made a mistake? delete it and add it again) |
| 3 | Show the summary |
| 4 | Final report (saved to `reports/`) |
| 5 | Add days to the trip |
| 6 | Cancel the trip (shows the money you keep, saves a report, deletes the data) |
| 0 | Exit (everything is already saved) |

## How the money is calculated

```
Trip budget     = Total budget - Ticket price
Category budget = Trip budget x category %
Left            = Trip budget - Total spent
Daily allowance = Left / days left (counting today)
SAR amount      = local amount / rate      (rate 9: 450 TRY = 50 SAR)
```

Each expense keeps the rate it was converted with.

## Project structure

```
trip-budget-cli/
├── main.py              # entry point
├── requirements.txt     # rich, pyfiglet, plotext, humanize, pytest
├── pytest.ini
├── tripbudget/
│   ├── models.py        # errors + Item, Ticket, Expense, Trip (OOP)
│   ├── storage.py       # save/load data/trip.json, save reports
│   ├── report.py        # summary and final report tables (rich)
│   └── cli.py           # questions, menu and actions
├── tests/
│   └── test_models.py   # pytest tests
├── data/                # created at runtime (in .gitignore)
└── reports/             # created at runtime (in .gitignore)
```

## Unit 1 concepts used

| Lesson | Where |
|---|---|
| 1. CLI & environment | The whole app runs in the terminal |
| 2. Git & GitHub | See `GIT_STEPS.md` |
| 3. Variables, types, operators | Type hints, `float()` casting, f-strings, currency maths |
| 4. Flow control | Menu loop, `if/elif/else`, `for`, `while` |
| 5. Functions & scope | Small functions such as `ask_number`, `ask_date`, `add_expense` |
| 6. Data structures | list (expenses), tuple (categories), dict (split, menu), set (days with no spending) |
| 7. Modules, packages, files | `tripbudget` package, JSON files, `pathlib` |
| 8. Lambda, exceptions, decorators | `format_money` lambda, sort key, custom errors, `try/except/else/finally`, `@safe_action` |
| 9. OOP | `Item` → `Ticket` / `Expense` (inheritance), `Trip`, `@property` |
| 10. venv & pip | Virtual environment, `requirements.txt` with 5 libraries |

## Error handling

- Wrong input (letters, negative numbers, `nan`, wrong date format, end date before start) is refused and asked again.
- A ticket that costs more than the budget asks for the price again.
- A damaged `data/trip.json` shows a clear message instead of crashing.
- `Ctrl+C` exits cleanly. You can type Arabic digits (e.g. `٨٠٠٠`).
