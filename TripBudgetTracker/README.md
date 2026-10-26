# Trip Budget Tracker

Command-line travel budget tracker. The application entry point is `main.py`.

## Run on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Trip data is saved under `data/`, and final reports are saved under `reports/`.

## Run tests

```powershell
python -m pytest
```

The tests also verify that the application, test, and legacy files remain in
their documented locations.

## Layout

- `main.py`: starts the application.
- `tripbudget/`: models, terminal interface, storage and reports.
- `tests/`: budget model tests.
- `legacy/`: original smaller CLI files kept for reference; they are not used by the full app.